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
    # Пути, грязные сразу после создания дерева (post-checkout hook и т.п.):
    # это не работа воркера, и атрибуция такого дерева ненадёжна.
    preexisting: tuple[str, ...] = ()
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
            "preexisting": list(self.preexisting),
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
    # post-checkout hook может испачкать дерево ещё до старта воркера — тогда
    # его правки влились бы как работа воркера (находка аудита 2026-08-14).
    dirty = _git(target, "status", "--porcelain", check=True).stdout.splitlines()
    preexisting = tuple(sorted(line[3:] for line in dirty if len(line) > 3))
    tree = WorkerTree(
        task_id=task_id,
        path=target,
        branch=branch,
        base_commit=base,
        allowlist=frozenset(allowlist),
        preexisting=preexisting,
    )
    if preexisting:
        tree.notes.append(
            "дерево грязное сразу после создания (hook?): " + ", ".join(preexisting[:3])
        )
    return tree


def open_wave(
    project: Path,
    run_id: str,
    footprints: list[tuple[str, set[str]]],
    *,
    base: str,
) -> list[WorkerTree]:
    """Развернуть деревья всей волны или ни одного.

    Открытие живёт рядом с закрытием намеренно: они меняются вместе — стоит
    добавить в дерево ещё что-то (ветку, sparse-checkout, hook), и оба конца
    правятся одним движением.

    Полволны изолировать нельзя: часть воркеров писала бы в общее дерево, и
    атрибуция снова стала бы недоказуемой. Codex на этом шаге ещё не запускался,
    поэтому свернуть созданное безопасно — терять в деревьях нечего.
    """
    trees: list[WorkerTree] = []
    try:
        for task_id, allowlist in footprints:
            trees.append(
                create_worker_tree(project, run_id, task_id, base=base, allowlist=allowlist)
            )
    except WorktreeError:
        for tree in trees:
            remove_worker_tree(project, tree)
            # На свежесозданной ветке нет ни одного коммита — удалять безопасно,
            # а оставленная, она блокировала бы повтор той же волны.
            _git(project, "branch", "-D", tree.branch)
        raise
    return trees


def collect_changes(tree: WorkerTree) -> None:
    """Что воркер изменил в СВОЁМ дереве — это и есть атрибуция.

    Чужих правок внутри быть не может, поэтому деление changed/out_of_scope здесь
    точное, в отличие от aggregate-чека по проекту. Сверка идёт с ЕГО allowlist:
    по union волны файл соседа считался бы своим.

    Diff берётся от base_commit волны, не от HEAD: воркер может закоммитить сам
    (вопреки контракту), и подвижный HEAD сделал бы его работу невидимой —
    «пустой» воркер терял ветку вместе с закоммиченным (находка аудита
    2026-08-14). Отдельный проход по allowlist ловит новый файл, попавший под
    .gitignore: `--exclude-standard` его не видит, а `allow_create` не проверяет
    ignore-правил — целевой файл гиб как «мусор».
    """
    tracked = _git(tree.path, "diff", "--name-only", "-z", tree.base_commit, "--", check=True)
    untracked = _git(tree.path, "ls-files", "--others", "--exclude-standard", "-z", "--", check=True)
    changed = set(_nul_list(tracked.stdout)) | set(_nul_list(untracked.stdout))
    for path in tree.allowlist:
        if path in changed or not (tree.path / path).exists():
            continue
        in_base = _git(tree.path, "cat-file", "-e", f"{tree.base_commit}:{path}")
        if in_base.returncode != 0:  # на диске есть, в базе нет — новый, пусть и ignored
            changed.add(path)
    tree.changed_files = tuple(sorted(changed))
    tree.out_of_scope_files = tuple(path for path in tree.changed_files if path not in tree.allowlist)


def commit_worker_tree(tree: WorkerTree, *, message: str) -> None:
    """Зафиксировать в ветке ВСЁ изменённое воркером — отбор происходит на merge.

    Ветка — страховка от потери: она переживает уборку деревьев. Если коммитить
    только allowlist, held-воркера нельзя разобрать вручную — его правка по
    списку могла опираться на внесписочную, а та погибла бы с деревом. Поэтому
    фиксация полная, а фильтр «только свой список» живёт в integrate: воркер с
    внесписочными правками не вливается вовсе.

    Диск это не раздувает: gitignored-мусор (node_modules, кэши) сюда не
    попадает — `collect_changes` ходит с `--exclude-standard`, а ветка чистого
    воркера удаляется сразу после merge.

    Коммит делается и для провалившегося воркера: фиксация ≠ интеграция.
    """
    if not tree.changed_files:
        tree.integration_status = "empty"
        tree.notes.append("изменений нет")
        return
    # -f: новый allowlist-файл может попадать под .gitignore — без -f git его
    # молча пропустит, и «зафиксировано всё» станет ложью.
    _git(tree.path, "add", "-f", "--", *tree.changed_files, check=True)
    committed = _git(tree.path, "commit", "--no-verify", "-m", message)
    if committed.returncode != 0:
        # Воркер мог закоммитить всё сам — тогда стейджить нечего, но работа уже
        # в истории ветки; головной коммит и есть фиксация.
        status = _git(tree.path, "status", "--porcelain", check=True).stdout.strip()
        if status:
            raise WorktreeError(
                f"git commit failed in {tree.path}: {(committed.stderr or committed.stdout).strip()}"
            )
        tree.notes.append("воркер коммитил сам; фиксация — головной коммит его ветки")
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
    if tree.preexisting:
        # Изоляция скомпрометирована ещё до воркера — что здесь чьё, недоказуемо.
        tree.integration_status = "held_dirty_birth"
        tree.notes.append(f"работа зафиксирована в {tree.branch}; разбирать вручную")
        return
    # База обязана остаться в истории HEAD. Прямой коммит поверх — норма (мои
    # recall/планы во время волны), а вот reset/rebase назад делает merge
    # контрабандой: он принёс бы разницу веток истории как «работу воркера».
    ancestor = _git(project, "merge-base", "--is-ancestor", tree.base_commit, "HEAD")
    if ancestor.returncode != 0:
        tree.integration_status = "held_base_rewritten"
        tree.notes.append(
            f"HEAD переписан ниже базы волны ({tree.base_commit[:8]}); "
            f"работа цела в {tree.branch}, вливать вручную"
        )
        return
    # Merge именно записанного SHA, не имени ветки: между аудитом изменений и
    # merge на ветку мог успеть лечь чужой коммит (поздний субагент воркера) —
    # tip-у это сошло бы с рук, SHA — нет (находка аудита 2026-08-14).
    merge = _git(project, "merge", "--no-ff", "--no-verify", "-m", f"codex fleet: {tree.task_id}", tree.commit)
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
    if work_is_home and tree.commit is not None:
        tip = _git(project, "rev-parse", tree.branch)
        if tip.returncode == 0 and tip.stdout.strip() != tree.commit:
            # На ветку успел лечь коммит ПОСЛЕ влитого SHA — force-delete снёс
            # бы его молча. Оставить на разбор.
            tree.cleanup_status = "branch_ahead"
            tree.notes.append(f"ветка {tree.branch} ушла вперёд влитого коммита — оставлена")
            return
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
        # Незабранная работа, не «ветка осталась»: merged-ветка при
        # --keep-worktrees — норма и в разборе не нуждается.
        "kept_branches": [
            t.branch for t in trees
            if t.integration_status not in {"merged", "empty"}
            or t.cleanup_status in {"branch_stuck", "branch_ahead"}
        ],
        "cleanup_done": cleanup_done,
        "cleanup_requested": cleanup,
        "cleanup_stuck": stuck,
        "workers": [t.to_json() for t in trees],
    }
