"""Изоляция воркеров флота в отдельных git worktrees и закрытие волны.

Зачем: shared worktree не доказывает, кто из воркеров что написал (AGENTS.md,
«Воркер пишет под контрактом»), а параллельная запись оркестратора в то же дерево
ложно валила postflight scope. Замер 2026-08-14 по 106 боевым волнам: 41 упала по
`scope_status`, и 68% записей `out_of_scope_files` — служебные файлы самого
оркестратора (`_workspace/`, `_ops/chat-recall/`, планы), не работа воркеров.

Своё дерево на воркера даёт то, чего иначе нет: атрибуцию (diff считается в его
дереве), отбраковку лишнего (запись вне allowlist уезжает вместе с деревом) и
свободу оркестратору писать в основном дереве во время волны.

Здесь только порядок закрытия волны и его защиты. Инвентарь, ручная уборка и
разбор конфликтов — готовым `git worktree` / `git merge` по рецепту в
`~/.claude/skills/1codex/references/fleet.md`: обёртки над ними этот модуль не
держит. Цена изоляции — выкладка рабочего дерева на воркера (замер: 22 МБ для
agentic-research, 650–780 МБ для mavo-short2), поэтому уборка идёт в том же
прогоне, а не остаётся на память оркестратора.

Модуль SDK-free: только git и файловая система.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Вне проекта: внутри деревья пачкали бы git status и postflight scope. Отдельно
# от `~/.codex/worktrees` намеренно — те создаёт Codex Desktop/CLI, и там может
# лежать незабранная работа владельца.
FLEET_WORKTREE_HOME = Path.home() / ".codex-bridge" / "worktrees"
BRANCH_PREFIX = "codex-fleet"


class WorktreeError(Exception):
    """Ошибка git-изоляции; вызывающий решает, валить ли волну."""


@dataclass
class WorkerTree:
    task_id: str
    path: Path
    branch: str
    base_commit: str
    # Свой allowlist, не union волны: с union воркер A мог править файл воркера B,
    # и правка проходила как in-scope — то самое, что изоляция должна была
    # исключить.
    allowlist: frozenset[str] = frozenset()
    # Успех хода воркера. Дерево воркера, чей ход не завершился, не вливается:
    # его правки — полуфабрикат, и статус хода обязан быть шлюзом интеграции.
    worker_ok: bool = True
    changed_files: tuple[str, ...] = ()
    out_of_scope_files: tuple[str, ...] = ()
    commit: str | None = None
    integration_status: str = "pending"
    integration_error: str | None = None
    cleanup_status: str = "pending"
    notes: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "worktree": str(self.path),
            "branch": self.branch,
            "base_commit": self.base_commit,
            "worker_ok": self.worker_ok,
            "changed_files": list(self.changed_files),
            "out_of_scope_files": list(self.out_of_scope_files),
            "commit": self.commit,
            "integration_status": self.integration_status,
            "integration_error": self.integration_error,
            "cleanup_status": self.cleanup_status,
            "notes": list(self.notes),
        }


def _git(cwd: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise WorktreeError(f"git {' '.join(args)}: {(proc.stderr or proc.stdout).strip()}")
    return proc


def _nul_list(data: str) -> list[str]:
    return [part for part in data.split("\0") if part]


def create_worker_tree(
    project: Path,
    run_id: str,
    task_id: str,
    *,
    base: str,
    allowlist: set[str] | frozenset[str] = frozenset(),
) -> WorkerTree:
    """Дерево воркера на новой ветке от `base`.

    Ветка, а не detached: работа забирается одним `git merge` и удаляется одной
    командой, иначе пришлось бы cherry-pick-ать по sha.
    """
    target = FLEET_WORKTREE_HOME / run_id / task_id
    if target.exists():
        raise WorktreeError(f"worktree path already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    branch = f"{BRANCH_PREFIX}/{run_id}/{task_id}"
    _git(project, "worktree", "add", "-b", branch, str(target), base, check=True)
    return WorkerTree(
        task_id=task_id,
        path=target,
        branch=branch,
        base_commit=base,
        allowlist=frozenset(allowlist),
    )


def collect_changes(tree: WorkerTree) -> None:
    """Что воркер изменил в СВОЁМ дереве — это и есть атрибуция.

    Чужих правок внутри быть не может, поэтому деление changed/out_of_scope здесь
    точное, в отличие от aggregate-чека по проекту. Сверка идёт с ЕГО allowlist:
    по union волны файл соседа считался бы своим.
    """
    tracked = _git(tree.path, "diff", "--name-only", "-z", "HEAD", "--", check=True)
    untracked = _git(tree.path, "ls-files", "--others", "--exclude-standard", "-z", "--", check=True)
    changed = sorted(set(_nul_list(tracked.stdout)) | set(_nul_list(untracked.stdout)))
    tree.changed_files = tuple(changed)
    tree.out_of_scope_files = tuple(path for path in changed if path not in tree.allowlist)


def commit_worker_tree(tree: WorkerTree, *, message: str) -> None:
    """Коммит ТОЛЬКО файлов из его allowlist.

    Точечный `git add -- <files>` вместо `add -A` защищает и scope, и диск:
    сборочный мусор воркера (node_modules, кэши) в коммит не идёт и уезжает с
    деревом. Именно он раздул `~/.codex/worktrees` до 7.3 ГБ к 2026-08-14.

    Коммит делается и для провалившегося воркера: фиксация ≠ интеграция. Иначе
    уборка снесла бы его дерево вместе с недоделанной работой, и разбирать было
    бы нечего.
    """
    in_scope = [path for path in tree.changed_files if path in tree.allowlist]
    if not in_scope:
        tree.integration_status = "empty"
        tree.notes.append("ни одного изменения в своём allowlist")
        return
    _git(tree.path, "add", "--", *in_scope, check=True)
    _git(tree.path, "commit", "--no-verify", "-m", message, check=True)
    tree.commit = _git(tree.path, "rev-parse", "HEAD", check=True).stdout.strip()


def integrate_worker_tree(project: Path, tree: WorkerTree) -> None:
    """Забрать ветку воркера одним merge.

    `--no-ff` намеренно: отдельный merge-коммит на воркера — единственное место,
    где после уборки видно, кто писал эти файлы. Конфликт означает нарушенный
    file-disjoint контракт или уехавшую базу: merge откатывается, ветка остаётся,
    работа не теряется.
    """
    if tree.commit is None:
        return
    if not tree.worker_ok:
        # Ход не завершился — правки полуфабрикат. Ветка с коммитом остаётся для
        # разбора, в проект не идёт.
        tree.integration_status = "held_failed_worker"
        tree.notes.append(f"ход воркера не завершён; работа зафиксирована в {tree.branch}")
        return
    if tree.out_of_scope_files:
        # Запись вне своего списка — сорванный контракт. Отбраковать её одну
        # нельзя честно: воркер мог опираться на неё в файлах, которые в списке.
        tree.integration_status = "held_out_of_scope"
        tree.notes.append(
            f"писал вне своего списка ({', '.join(tree.out_of_scope_files[:3])}); "
            f"работа зафиксирована в {tree.branch}"
        )
        return
    merge = _git(project, "merge", "--no-ff", "--no-verify", "-m", f"codex fleet: {tree.task_id}", tree.branch)
    if merge.returncode == 0:
        tree.integration_status = "merged"
        return
    tree.integration_status = "conflict"
    tree.integration_error = (merge.stderr or merge.stdout).strip()
    _git(project, "merge", "--abort")
    tree.notes.append(f"работа цела в ветке {tree.branch}, забрать вручную")


def remove_worker_tree(project: Path, tree: WorkerTree) -> None:
    """Снести дерево; ветку — только когда работа уже забрана.

    `--force` нужен всегда: в дереве остаётся неотслеживаемый мусор воркера, без
    него git отказывается удалять непустой worktree.

    Статус ставится по факту с диска, а не по факту вызова: неудачное удаление,
    выданное за уборку, и есть тот молчаливый рост, из-за которого накопилось
    7.3 ГБ.
    """
    _git(project, "worktree", "remove", "--force", str(tree.path))
    if tree.path.exists():
        shutil.rmtree(tree.path, ignore_errors=True)
    _git(project, "worktree", "prune")

    if tree.path.exists():
        tree.cleanup_status = "tree_stuck"
        tree.notes.append(f"дерево не удалилось: {tree.path}")
        return

    work_is_home = tree.integration_status in {"merged", "empty"}
    if not work_is_home:
        tree.cleanup_status = "branch_kept"
        tree.notes.append(f"ветка {tree.branch} оставлена: работа не в проекте")
        return

    dropped = _git(project, "branch", "-D", tree.branch)
    if dropped.returncode == 0:
        tree.cleanup_status = "removed"
    else:
        tree.cleanup_status = "branch_stuck"
        tree.notes.append(f"ветка {tree.branch} не удалилась: {(dropped.stderr or '').strip()}")


def close_wave(
    project: Path,
    trees: list[WorkerTree],
    *,
    run_id: str,
    integrate: bool,
    cleanup: bool,
) -> dict[str, Any]:
    """Собрать → коммит → merge → убрать.

    Порядок не переставляется: пока работа не забрана, дерево и ветка не
    удаляются. Отказ на интеграции превращает уборку в «оставить ветку» — потеря
    правок дороже висящего worktree.

    Коммит идёт всегда, даже когда интеграция не заказана: без него `--no-integrate`
    вместе с уборкой снёс бы деревья с незафиксированной работой. Фиксация — не
    интеграция.
    """
    for tree in trees:
        collect_changes(tree)
        commit_worker_tree(tree, message=f"codex fleet {run_id}: {tree.task_id}")

    if integrate:
        for tree in trees:
            integrate_worker_tree(project, tree)
    else:
        for tree in trees:
            if tree.integration_status == "pending":
                tree.integration_status = "held"

    if cleanup:
        for tree in trees:
            remove_worker_tree(project, tree)
        run_home = FLEET_WORKTREE_HOME / run_id
        if run_home.exists() and not any(run_home.iterdir()):
            run_home.rmdir()

    conflicts = [t.task_id for t in trees if t.integration_status == "conflict"]
    held = [t.task_id for t in trees if t.integration_status.startswith("held")]
    if not integrate:
        status = "held"
    elif conflicts or held:
        status = "conflict" if conflicts else "partial"
    else:
        status = "integrated"

    # Уборка честная: считается по факту с диска, а не по тому, что её просили.
    stuck = [t.task_id for t in trees if t.cleanup_status in {"tree_stuck", "branch_stuck"}]
    cleanup_done = cleanup and not stuck
    return {
        "isolation": "worktree",
        "integration_status": status,
        "merged": [t.task_id for t in trees if t.integration_status == "merged"],
        "conflicts": conflicts,
        "held": held,
        "kept_branches": [
            t.branch for t in trees
            if t.cleanup_status != "removed" and t.integration_status != "empty"
        ],
        "cleanup_done": cleanup_done,
        "cleanup_requested": cleanup,
        "cleanup_stuck": stuck,
        "workers": [t.to_json() for t in trees],
    }
