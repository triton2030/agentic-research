#!/usr/bin/env python3
"""codex-bridge orchestrator — guarded shared-worktree Codex workers."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cbcommon import scrub_billing_env
from codex_retry import retry_start_async
from codex_sdk_compat import harden_sdk_enums
from codex_defaults import (
    FLEET_THREAD_EPHEMERAL,
    DEFAULT_CODEX_EFFORT,
    DEFAULT_CODEX_MODEL,
    DEFAULT_CODEX_SERVICE_TIER,
    REASONING_EFFORTS,
    WORKER_APPROVAL_MODE,
    WORKER_SANDBOX,
    SDK_BUNDLE_WARNING,
    codex_bin_source,
    resolve_codex_bin,
)
from codex_orchestrate_contract import (
    TaskSpec,
    UsageError,
    codex_status_value,
    dirty_overlaps,
    normalize_tasks,
    worker_status_from_codex_status,
)
from codex_run_ledger import (
    append_event,
    append_heartbeat,
    append_jsonl,
    prepare_run_dir,
    utc_now,
    write_json,
)
from codex_git_scope import (
    GitSnapshot,
    capture_git_snapshot,
    compare_scope,
    is_scope_noise,
)
from codex_progress import ProgressRegistry, ProgressTracker, run_async_turn
from codex_worktrees import (
    WorkerTree,
    WorktreeError,
    close_wave,
    open_wave,
)


def _safe_print(message: str, *, stream: Any = None) -> None:
    # Прогресс и финальный дамп — телеметрия поверх канонического результата
    # на диске: закрытый пайп (| head, оборванный терминал) не должен ронять
    # флот и подменять готовые записи воркеров exception-записями.
    try:
        print(message, file=stream if stream is not None else sys.stderr)
    except OSError:
        pass


def _files_constraint(files: tuple[str, ...], *, isolated: bool = False, subagents: bool = False) -> str:
    """Файловый контракт воркера — канал `developer_instructions` треда.

    Это политика прогона, а не задание: она уходит при thread_start отдельно от
    реплики, поэтому task.prompt остаётся заданием пользователя, а allowlist не
    растворяется в его тексте. Enforcement всё равно живёт в
    preflight/postflight — текст лишь объясняет воркеру рамку.

    В изолированном дереве формулировка другая по существу, а не по вежливости:
    писать вне списка воркер физически может (дерево его), но внесписочная правка
    удержит всю его работу в ветке на ручной разбор. Модели честнее сказать про
    удержание, чем запрещать то, что песочница разрешает.

    Делегация запрашивается здесь же: системный промпт движка молчит про
    субагентов, пока их явно не попросят («Do not spawn sub-agents unless the
    user or applicable AGENTS.md/skill instructions explicitly ask»). Разрешение
    осмысленно только в своём дереве — иначе субагенты пишут в общее.
    """
    joined = ", ".join(files)
    if isolated:
        contract = (
            f"Ты работаешь в отдельном git worktree — это твоя копия проекта. "
            f"В проект будут забраны ТОЛЬКО эти файлы: {joined}. "
            "Изменишь любой другой файл — ВСЯ твоя работа не будет влита автоматически "
            "и уйдёт в ветку на ручной разбор: нужен другой файл — назови его в "
            "ответе, не правь молча. "
            "Не создавай коммитов и не переключай ветки: сбор делает оркестратор."
        )
    else:
        contract = (
            f"Тебе разрешено создавать и редактировать ТОЛЬКО эти файлы: {joined}. "
            "Не трогай никакие другие файлы. Если задача требует иного — опиши это "
            "в ответе, но не делай."
        )
    if subagents:
        contract += (
            " Задача крупная: тебе РАЗРЕШЕНО делить её на собственных субагентов "
            "и работать ими параллельно, оставаясь в границах своего дерева и "
            "своего списка файлов."
        )
    return contract


def _manifest_task_record(task: TaskSpec, *, isolated: bool = False) -> dict[str, Any]:
    """Запись задачи в manifest: контракт задачи + её эффективная инструкция.

    Файловый контракт уходит воркеру каналом `developer_instructions`, минуя
    реплику, поэтому по `prompt` и `allowlist` его текст не восстановить: он
    рендерится backend-кодом, а к моменту разбора прогона код уже другой.
    Audit-владелец прогона — run_dir, значит точный текст (и его длина) лежат
    здесь, до первого хода: инструкция, которой нет в run_dir, для аудита не
    существует."""
    developer_instructions = _files_constraint(
        task.files, isolated=isolated, subagents=task.subagents
    )
    return {
        **task.to_json(),
        "developer_instructions": developer_instructions,
        "developer_instructions_chars": len(developer_instructions),
    }


async def _run_one(codex, sem, task: TaskSpec, defaults: dict[str, Any]) -> dict[str, Any]:
    from openai_codex import ApprovalMode, Sandbox  # импорт после scrub_billing_env
    from openai_codex.generated.v2_all import ReasoningEffort

    prompt = task.prompt
    # В worktree-режиме воркер живёт в своей копии проекта: cwd другой, и контракт
    # говорит про отбраковку вне allowlist, а не про запрет писать. Режим берётся
    # из defaults, а не из наличия дерева: manifest пишет тот же текст до первого
    # хода, и два источника режима разошлись бы в аудите.
    isolated = defaults.get("isolation") == "worktree"
    tree: WorkerTree | None = defaults.get("trees", {}).get(task.id)
    worker_cwd = str(tree.path) if tree is not None else defaults["cwd"]
    files_contract = _files_constraint(
        task.files, isolated=isolated, subagents=task.subagents
    )
    run_dir: Path = defaults["run_dir"]
    effort = ReasoningEffort(defaults["effort"])
    # registry ставит _run_fleet; при прямом вызове воркера его может не быть —
    # тогда прогресс локальный, но ход не падает.
    registry = defaults.get("registry")
    tracker = registry.tracker(task.id) if registry is not None else ProgressTracker()

    async with sem:
        t0 = time.monotonic()
        append_event(run_dir, "worker_start", id=task.id)
        thread_id: str | None = None
        try:
            thread = await retry_start_async(
                lambda: codex.thread_start(
                    cwd=worker_cwd,
                    sandbox=Sandbox.workspace_write,
                    approval_mode=ApprovalMode.auto_review,
                    model=defaults["model"],
                    service_tier=defaults["service_tier"],
                    developer_instructions=files_contract,
                    ephemeral=FLEET_THREAD_EPHEMERAL,
                ),
                run_dir=run_dir,
                operation="thread_start",
                fields={"worker": task.id},
            )
            # Тред воркера персистентен (решение владельца 2026-08-14): Codex
            # Desktop показывает его как чат = живой монитор прогресса. id — в
            # отчёт и в ledger, иначе тред не найти среди остальных.
            thread_id = getattr(thread, "id", None)
            if thread_id:
                append_event(run_dir, "worker_thread", id=task.id, thread_id=thread_id)
            handle = await retry_start_async(
                lambda: thread.turn(
                    prompt,
                    approval_mode=ApprovalMode.auto_review,
                    effort=effort,
                    model=defaults["model"],
                    service_tier=defaults["service_tier"],
                    sandbox=Sandbox.workspace_write,
                ),
                run_dir=run_dir,
                operation="turn_start",
                fields={"worker": task.id},
            )
            result = await run_async_turn(
                handle,
                run_dir=run_dir,
                tracker=tracker,
                extra={"worker": task.id},
            )
            duration_ms = int((time.monotonic() - t0) * 1000)
            codex_status = codex_status_value(getattr(result, "status", ""))
            worker_status = worker_status_from_codex_status(codex_status, result.error)
            worker_ok = worker_status == "completed"
            _safe_print(
                f"[orch] {'✓' if worker_ok else '✗'} {task.id} ({duration_ms}мс)"
                + ("" if worker_ok else f" — {result.error}")
            )
            record = {
                "id": task.id,
                "thread_id": thread_id,
                "worker_status": worker_status,
                "codex_status": codex_status,
                "error": str(result.error) if result.error else None,
                "response": result.final_response,
                "duration_ms": duration_ms,
                "usage": str(getattr(result, "usage", None)),
            }
        except Exception as exc:  # noqa: BLE001 — одна упавшая задача не валит флот
            duration_ms = int((time.monotonic() - t0) * 1000)
            _safe_print(f"[orch] ✗ {task.id} — исключение: {exc}")
            record = {
                "id": task.id,
                "thread_id": thread_id,
                "worker_status": "exception",
                "codex_status": "exception",
                "error": str(exc),
                "response": None,
                "duration_ms": duration_ms,
                "usage": None,
            }

        append_event(
            run_dir,
            "worker_done",
            id=task.id,
            worker_status=record["worker_status"],
            duration_ms=record["duration_ms"],
        )
        append_jsonl(run_dir / "results.jsonl", record)
        if registry is not None:
            registry.finish(task.id)
        defaults["progress"]["completed"] += 1
        return record


async def _heartbeat_loop(
    run_dir: Path,
    heartbeat_sec: int,
    started_monotonic: float,
    progress: dict[str, int],
    registry: ProgressRegistry | None = None,
) -> None:
    try:
        while True:
            await asyncio.sleep(heartbeat_sec)
            # Сводка по живым воркерам: без неё пульс флота говорил только
            # «сколько закрыто», а зависший воркер был неотличим от думающего.
            extra = registry.snapshot() if registry is not None else {}
            append_heartbeat(
                run_dir,
                started_monotonic,
                completed=progress["completed"],
                total=progress["total"],
                **extra,
            )
    except asyncio.CancelledError:
        return


async def _run_fleet(
    tasks: list[TaskSpec],
    defaults: dict[str, Any],
    concurrency: int,
    heartbeat_sec: int,
) -> list[dict[str, Any]]:
    from openai_codex import AsyncCodex, CodexConfig

    # Дрейф движка ChatGPT.app под запиненным SDK: новые enum-значения в
    # ответах не должны ронять воркеров (см. codex_sdk_compat.py).
    harden_sdk_enums()

    sem = asyncio.Semaphore(concurrency)
    defaults["progress"] = {"completed": 0, "total": len(tasks)}
    defaults["registry"] = ProgressRegistry()
    heartbeat_task: asyncio.Task[None] | None = None
    if heartbeat_sec > 0:
        heartbeat_task = asyncio.create_task(
            _heartbeat_loop(
                defaults["run_dir"],
                heartbeat_sec,
                time.monotonic(),
                defaults["progress"],
                defaults["registry"],
            )
        )
    try:
        async with AsyncCodex(
            CodexConfig(
                cwd=defaults["cwd"],
                codex_bin=defaults["codex_bin"],
            )
        ) as codex:
            return await asyncio.gather(*(_run_one(codex, sem, task, defaults) for task in tasks))
    finally:
        if heartbeat_task is not None:
            heartbeat_task.cancel()
            await asyncio.gather(heartbeat_task, return_exceptions=True)


def run_verification(commands: list[str], project: Path, run_dir: Path) -> tuple[str, list[dict[str, Any]]]:
    if not commands:
        return "not_requested", []

    results: list[dict[str, Any]] = []
    status = "passed"
    for index, command in enumerate(commands, start=1):
        started = time.monotonic()
        append_event(run_dir, "verify_start", index=index, command=command)
        proc = subprocess.run(
            command,
            cwd=project,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        item = {
            "command": command,
            "exit_code": proc.returncode,
            "duration_ms": int((time.monotonic() - started) * 1000),
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
        }
        results.append(item)
        append_event(run_dir, "verify_done", index=index, exit_code=proc.returncode)
        if proc.returncode != 0:
            status = "failed"
            break
    return status, results


def build_manifest(
    run_id: str,
    run_dir: Path,
    project: Path,
    tasks: list[TaskSpec],
    allowlist: set[str],
    initial_git: GitSnapshot,
    verify_commands: list[str],
    concurrency: int,
    dry_run: bool,
    codex_runtime: dict[str, Any],
    isolation: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "created_at": utc_now(),
        "dry_run": dry_run,
        "project": str(project),
        "git": initial_git.to_json(),
        "concurrency": concurrency,
        "isolation": isolation,
        "codex": codex_runtime,
        "verify": verify_commands,
        "allowlist": sorted(allowlist),
        "tasks": [
            _manifest_task_record(task, isolated=isolation == "worktree") for task in tasks
        ],
    }


def _orchestrate_paths(run_dir: Path) -> dict[str, str]:
    return {
        "manifest": str(run_dir / "manifest.json"),
        "events": str(run_dir / "events.jsonl"),
        "results": str(run_dir / "results.jsonl"),
        "result": str(run_dir / "result.json"),
    }


def _compact_orchestrate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: payload[key]
        for key in (
            "run_id",
            "run_dir",
            "dry_run",
            "status",
            "ok",
            "fully_verified",
            "worker_status",
            "scope_status",
            "verification_status",
            "codex",
            "paths",
            "task_count",
            "postflight_changed_files",
            "out_of_scope_files",
            "git_head_changed",
            "isolation",
            "wave",
        )
        if key in payload
    }


def _load_tasks(args: argparse.Namespace) -> Any:
    raw = Path(args.tasks).read_text() if args.tasks else sys.stdin.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UsageError(f"Invalid task JSON: {exc}") from exc


@dataclass(frozen=True)
class RunPlan:
    """Всё, что известно о прогоне до первого оплаченного хода.

    Существует, чтобы подготовка перестала быть началом `main()`: раньше проверки,
    манифест и запуск лежали одной лентой, и любая правка одного этапа требовала
    прочитать остальные. Здесь же держится инвариант аудита — то, что записано в
    manifest, и то, с чем пойдёт волна, это один объект, а не две копии полей.
    """

    tasks: list[TaskSpec]
    allowlist: set[str]
    initial_git: GitSnapshot
    codex_runtime: dict[str, Any]
    run_id: str
    run_dir: Path
    paths: dict[str, str]
    manifest: dict[str, Any]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guarded fleet of parallel Codex workers under Claude orchestration.")
    parser.add_argument("--tasks", help="JSON task file (otherwise stdin).")
    parser.add_argument("--project", default=None, help="Project root = worker cwd (default: current directory).")
    parser.add_argument("--concurrency", type=int, default=4, help="Concurrent workers. Default: 4.")
    parser.add_argument("--model", default=DEFAULT_CODEX_MODEL, help=f"Codex model. Default: {DEFAULT_CODEX_MODEL}.")
    parser.add_argument(
        "--effort",
        choices=REASONING_EFFORTS,
        default=DEFAULT_CODEX_EFFORT,
        help=f"Reasoning effort for every Codex turn. Default: {DEFAULT_CODEX_EFFORT}.",
    )
    parser.add_argument(
        "--service-tier",
        default=DEFAULT_CODEX_SERVICE_TIER,
        help="Codex service tier (default: inherit from ~/.codex/config.toml). "
        "Explicit value, e.g. 'priority', is a deliberate per-run fast opt-in.",
    )
    parser.add_argument("--verify", action="append", default=[], help="Verification command to run after workers and scope check.")
    parser.add_argument(
        "--run-dir",
        help="Ledger directory override (default: <project>/_workspace/codex-artifacts/<run_id>).",
    )
    parser.add_argument(
        "--isolation",
        choices=["worktree", "shared"],
        default="worktree",
        help="worktree (default): каждому воркеру свой git worktree — точная атрибуция, "
        "отбраковка правок вне allowlist, свобода писать в основном дереве во время волны. "
        "shared: все воркеры в дереве проекта (прежнее поведение); выбирай, когда задачи "
        "должны видеть правки друг друга или выкладка дерева слишком дорога.",
    )
    parser.add_argument(
        "--no-integrate",
        action="store_true",
        help="worktree: не забирать работу в проект — оставить коммиты в ветках воркеров "
        "для ручного разбора. Деревья при этом не удаляются.",
    )
    parser.add_argument(
        "--keep-worktrees",
        action="store_true",
        help="worktree: не убирать деревья после волны (разбор мусора воркеров). "
        "Помни: каждое дерево — выкладка проекта, чистить придётся руками.",
    )
    parser.add_argument("--allow-dirty-overlap", action="store_true", help="Allow launch when existing dirty files overlap task files.")
    parser.add_argument("--summary-stdout", action="store_true", help="Print compact JSON to stdout; full results stay in result.json/results.jsonl.")
    parser.add_argument("--heartbeat-sec", type=int, default=120, help="Seconds between ledger heartbeat events while Codex workers run; 0 disables.")
    parser.add_argument("--dry-run", action="store_true", help="Validate tasks and write ledger without invoking Codex.")
    return parser


def _plan_run(args: argparse.Namespace, project: Path) -> RunPlan:
    """Проверить всё, что можно проверить до траты кредитов, и записать план.

    Порядок внутри значим: сначала отказы (аргументы, задачи, git, конфликты
    флагов), только потом создание `run_dir`. Иначе каждый отвергнутый запуск
    оставлял бы пустой каталог прогона.
    """
    if args.concurrency < 1:
        raise UsageError("--concurrency must be >= 1.")
    if args.heartbeat_sec < 0:
        raise UsageError("--heartbeat-sec must be >= 0.")
    if not project.is_dir():
        raise UsageError(f"--project must be an existing directory: {project}")
    if args.isolation == "shared" and (args.no_integrate or args.keep_worktrees):
        raise UsageError("--no-integrate/--keep-worktrees apply to --isolation worktree only.")

    tasks = normalize_tasks(project, _load_tasks(args))
    allowlist = {path for task in tasks for path in task.files}
    initial_git = capture_git_snapshot(project, required=not args.dry_run)
    dirty_overlap = dirty_overlaps(initial_git.dirty_files, allowlist)
    if dirty_overlap and not args.allow_dirty_overlap:
        raise UsageError(
            "Dirty files overlap task files; commit/stage them or pass --allow-dirty-overlap: "
            + ", ".join(dirty_overlap)
        )
    if args.isolation == "worktree" and not initial_git.available and not args.dry_run:
        raise UsageError("--isolation worktree requires a git worktree.")

    codex_bin = resolve_codex_bin()
    if codex_bin is None:
        print(SDK_BUNDLE_WARNING, file=sys.stderr)
    codex_runtime = {
        "model": args.model,
        "effort": args.effort,
        "service_tier": args.service_tier,
        "codex_bin": codex_bin,
        "binary_source": codex_bin_source(codex_bin),
        "worker_sandbox": WORKER_SANDBOX,
        "worker_approval_mode": WORKER_APPROVAL_MODE,
        "thread_ephemeral": FLEET_THREAD_EPHEMERAL,
        "heartbeat_sec": args.heartbeat_sec,
        "isolation": args.isolation,
    }

    run_id, run_dir = prepare_run_dir(args.run_dir, project=project)
    paths = _orchestrate_paths(run_dir)
    manifest = build_manifest(
        run_id=run_id,
        run_dir=run_dir,
        project=project,
        tasks=tasks,
        allowlist=allowlist,
        initial_git=initial_git,
        verify_commands=args.verify,
        concurrency=args.concurrency,
        dry_run=args.dry_run,
        codex_runtime=codex_runtime,
        isolation=args.isolation,
    )
    manifest["paths"] = paths
    write_json(run_dir / "manifest.json", manifest)
    append_event(run_dir, "validated", task_count=len(tasks), dry_run=args.dry_run)
    return RunPlan(
        tasks=tasks,
        allowlist=allowlist,
        initial_git=initial_git,
        codex_runtime=codex_runtime,
        run_id=run_id,
        run_dir=run_dir,
        paths=paths,
        manifest=manifest,
    )


def _emit(payload: dict[str, Any], *, run_dir: Path, compact: bool) -> None:
    """Единственный выход прогона: канонический `result.json` плюс проекция в stdout.

    Один владелец на оба вида ответа — иначе dry-run и живой прогон расходятся
    формой, и по run_dir нельзя восстановить, что видел вызывающий.
    """
    write_json(run_dir / "result.json", payload)
    stdout_payload = _compact_orchestrate_payload(payload) if compact else payload
    _safe_print(json.dumps(stdout_payload, ensure_ascii=False, indent=2), stream=sys.stdout)


@dataclass(frozen=True)
class WaveVerdict:
    """Чем закончилась волна: что изменено, что вне рамки, что с интеграцией."""

    scope_status: str
    changed_files: list[str]
    out_of_scope_files: list[str]
    head_changed: bool
    wave: dict[str, Any]
    after_git: GitSnapshot


def _assess_wave(
    args: argparse.Namespace,
    project: Path,
    plan: RunPlan,
    results: list[dict[str, Any]],
    trees: list[WorkerTree],
) -> WaveVerdict:
    """Закрыть волну и вынести вердикт по scope.

    Два режима отвечают на разные вопросы, и это единственное место, где разница
    видна целиком. В shared всё доказательство — общее дерево. В worktree
    атрибуция считается в дереве каждого воркера, поэтому вердикт строится по ней:
    изменения в основном дереве во время волны — работа оркестратора (recall,
    планы, артефакты), и раньше они валили волну (замер 2026-08-14: 68% записей
    out_of_scope по 106 волнам были таким служебным шумом). Они остаются видимыми
    в `main_tree_drift`, но приговором больше не являются.
    """
    # Снимок основного дерева берётся ДО интеграции: после merge он показывал бы
    # нашу же работу и ничего не доказывал.
    after_git = capture_git_snapshot(project, required=True)
    scope = compare_scope(plan.initial_git, after_git, plan.allowlist)
    # run_dir по умолчанию живёт внутри проекта (_workspace/codex-artifacts): его
    # ledger — собственная площадка прогона, не правка проекта, иначе каждый
    # прогон ложно валил бы scope об собственный журнал.
    changed = [f for f in scope.changed_files if not is_scope_noise(project, plan.run_dir, f)]
    drifted = [f for f in scope.out_of_scope_files if not is_scope_noise(project, plan.run_dir, f)]

    if args.isolation != "worktree":
        return WaveVerdict(
            scope_status="passed" if (not drifted and not scope.head_changed) else "failed",
            changed_files=changed,
            out_of_scope_files=drifted,
            head_changed=scope.head_changed,
            wave={"isolation": "shared"},
            after_git=after_git,
        )

    # Статус хода — шлюз интеграции: полуфабрикат упавшего воркера в проект не
    # едет, но фиксируется в его ветке.
    by_id = {record["id"]: record for record in results}
    for tree in trees:
        tree.worker_ok = by_id.get(tree.task_id, {}).get("worker_status") == "completed"
    try:
        wave = close_wave(
            project,
            trees,
            run_id=plan.run_id,
            integrate=not args.no_integrate,
            # Уборка только когда работа забрана: снести дерево, не влив его,
            # значит выбросить правки. `--no-integrate` держит деревья сам.
            cleanup=not args.keep_worktrees and not args.no_integrate,
        )
    except WorktreeError as exc:
        wave = {
            "isolation": "worktree",
            "integration_status": "error",
            "error": str(exc),
            "workers": [t.to_json() for t in trees],
        }
    wave["main_tree_drift"] = drifted

    worker_out_of_scope = sorted({path for tree in trees for path in tree.out_of_scope_files})
    failed = bool(worker_out_of_scope) or wave.get("integration_status") in {"conflict", "error"}
    return WaveVerdict(
        scope_status="failed" if failed else "passed",
        changed_files=sorted({path for tree in trees for path in tree.changed_files}),
        out_of_scope_files=worker_out_of_scope,
        head_changed=scope.head_changed,
        wave=wave,
        after_git=after_git,
    )


def _wave_line(wave: dict[str, Any], task_count: int) -> str:
    """Итог волны одной строкой в stderr — то, что оркестратор видит без чтения JSON.

    Кричит про неубранные деревья: висящее дерево — выкладка всего проекта, и
    молчаливое накопление таких деревьев было исходной болью.
    """
    if wave.get("isolation") != "worktree":
        return ""
    kept = wave.get("kept_branches") or []
    parts = [f" | worktree: влито {len(wave.get('merged') or [])}/{task_count}"]
    if kept:
        parts.append(f"осталось веток {len(kept)}")
    if wave.get("cleanup_done"):
        parts.append("деревья убраны")
    elif wave.get("cleanup_requested"):
        parts.append(f"УБОРКА НЕ ПРОШЛА: {', '.join(wave.get('cleanup_stuck') or [])}")
    else:
        parts.append("деревья оставлены")
    return ", ".join(parts)


def _dry_run_payload(args: argparse.Namespace, plan: RunPlan) -> dict[str, Any]:
    return {
        "run_id": plan.run_id,
        "run_dir": str(plan.run_dir),
        "dry_run": True,
        "status": "validated",
        "ok": True,
        "codex": plan.codex_runtime,
        "paths": plan.paths,
        "task_count": len(plan.tasks),
        # Сухой план обязан говорить, как пойдёт прогон: режим изоляции меняет
        # и контракт воркера, и способ забрать работу.
        "isolation": args.isolation,
        "git": plan.initial_git.to_json(),
        # Ровно тот план, что записан в manifest: два вида одного прогона в
        # одном run_dir не должны расходиться формой.
        "tasks": plan.manifest["tasks"],
    }


def main() -> int:
    args = _build_parser().parse_args()
    project = Path(args.project or os.getcwd()).expanduser().resolve()

    try:
        plan = _plan_run(args, project)
    except OSError as exc:
        print(f"[orch] filesystem error: {exc}", file=sys.stderr)
        return 1
    except UsageError as exc:
        print(f"[orch] {exc}", file=sys.stderr)
        return 2

    run_id, run_dir, tasks = plan.run_id, plan.run_dir, plan.tasks
    initial_git, codex_runtime, paths = plan.initial_git, plan.codex_runtime, plan.paths

    if args.dry_run:
        print(
            f"[orch dry-run] {len(tasks)} tasks, concurrency={args.concurrency}, "
            f"run_dir={run_dir}, binary={codex_runtime['binary_source']}",
            file=sys.stderr,
        )
        _emit(_dry_run_payload(args, plan), run_dir=run_dir, compact=args.summary_stdout)
        return 0

    removed = scrub_billing_env()
    print(
        f"[orch] старт: {len(tasks)} задач, лимит {args.concurrency}, project={project}, "
        f"run_dir={run_dir}, model={args.model}, effort={args.effort}, tier={args.service_tier or 'inherit'}, "
        f"binary={codex_runtime['binary_source']}, "
        f"sandbox={WORKER_SANDBOX}, approval={WORKER_APPROVAL_MODE}"
        + (f" | вырезано из env: {', '.join(removed)}" if removed else " | env чист"),
        file=sys.stderr,
    )
    append_event(run_dir, "codex_start", task_count=len(tasks))

    defaults = {
        "cwd": str(project),
        "model": args.model,
        "effort": args.effort,
        "service_tier": args.service_tier,
        "run_dir": run_dir,
        "codex_bin": codex_runtime["codex_bin"],
        "isolation": args.isolation,
    }

    trees: list[WorkerTree] = []
    if args.isolation == "worktree":
        base = initial_git.git_head or "HEAD"
        try:
            trees = open_wave(
                project, run_id, [(task.id, set(task.files)) for task in tasks], base=base
            )
        except WorktreeError as exc:
            print(f"[orch] worktree isolation failed: {exc}", file=sys.stderr)
            append_event(run_dir, "done", ok=False, worker_status="not_started", scope_status="unknown")
            return 2
        defaults["trees"] = {tree.task_id: tree for tree in trees}
        append_event(run_dir, "worktrees_ready", count=len(trees), base=base)

    try:
        results = asyncio.run(_run_fleet(tasks, defaults, args.concurrency, args.heartbeat_sec))
    except (KeyboardInterrupt, SystemExit):
        # У async-пути нет штатного `turn/interrupt` (он есть только у синхронного
        # `run_turn`), поэтому прерывание волны иначе оставляло бы деревья с
        # незафиксированной работой — и её было бы нечем найти, кроме `git
        # worktree list`. Фиксируем в ветках, деревья держим, ничего не вливаем.
        if trees:
            rescue = close_wave(project, trees, run_id=run_id, integrate=False, cleanup=False)
            append_event(run_dir, "interrupt_requested", rescued=rescue["kept_branches"])
            print(
                "[orch] прервано: работа воркеров зафиксирована в ветках "
                + ", ".join(rescue["kept_branches"] or ["(пусто)"]),
                file=sys.stderr,
            )
        raise

    worker_status = "completed" if all(r["worker_status"] == "completed" for r in results) else "failed"
    verdict = _assess_wave(args, project, plan, results, trees)
    scope_status = verdict.scope_status
    changed_files, out_of_scope_files = verdict.changed_files, verdict.out_of_scope_files
    wave, after_git = verdict.wave, verdict.after_git

    append_event(
        run_dir,
        "scope_done",
        scope_status=scope_status,
        changed_files=changed_files,
        out_of_scope_files=out_of_scope_files,
        git_head_changed=verdict.head_changed,
        isolation=args.isolation,
    )

    if worker_status == "completed" and scope_status == "passed":
        verification_status, verification_results = run_verification(args.verify, project, run_dir)
    elif args.verify:
        verification_status, verification_results = "skipped", []
    else:
        verification_status, verification_results = "not_requested", []

    ok = (
        worker_status == "completed"
        and scope_status == "passed"
        and verification_status in {"passed", "not_requested"}
    )
    payload = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        # `status` читают сводка и доска: без него `codex_progress.py` печатал
        # «status: None» на успешной волне и выглядел сломанным.
        "status": "completed" if ok else "failed",
        "ok": ok,
        "fully_verified": verification_status == "passed",
        "codex": codex_runtime,
        "paths": paths,
        "task_count": len(tasks),
        "worker_status": worker_status,
        "scope_status": scope_status,
        "verification_status": verification_status,
        "isolation": args.isolation,
        "wave": wave,
        "postflight_changed_files": changed_files,
        "out_of_scope_files": out_of_scope_files,
        "git_head_changed": verdict.head_changed,
        "git": {"initial": initial_git.to_json(), "after": after_git.to_json()},
        "results": results,
        "verification_results": verification_results,
    }
    append_event(
        run_dir,
        "done",
        ok=ok,
        worker_status=worker_status,
        scope_status=scope_status,
        verification_status=verification_status,
    )

    _safe_print(
        f"[orch] готово: worker={worker_status} scope={scope_status} "
        f"verify={verification_status} ok={ok}{_wave_line(wave, len(tasks))}"
    )
    _emit(payload, run_dir=run_dir, compact=args.summary_stdout)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
