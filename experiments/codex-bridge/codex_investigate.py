#!/usr/bin/env python3
"""codex-bridge — Codex как ИССЛЕДОВАТЕЛЬ (investigator) из Claude Code.

Средний профиль между read-only ревьюером (`codex_review.py`) и пишущим-в-проект
флотом (`codex_orchestrate.py`): Codex ЧИТАЕТ весь проект и диск; ПРОЕКТ для
записи недостижим на уровне sandbox (workspace_write + cwd=out), а не по
постфактум-проверке. Выходная папка Codex — `run_dir/out/` (cwd); системный temp
(/tmp, $TMPDIR) под workspace_write тоже писчий, но проекта это не касается.

Смысл: Claude — оркестратор, Codex — руки и глаза. Отдаёшь самодостаточное
задание «изучи X, собери Y, напиши отчёт», Codex расследует и складывает артефакты
в `out/`; Claude забирает `result.json` (uniform-контракт) и сливает фан-аут кодом,
а не перечитыванием прозы. Как вызов субагента: транскрипт не тянется.

Биллинг — через ChatGPT-аккаунт (auth_mode=chatgpt), НЕ через API-ключ:
`scrub_billing_env()` вырезает OPENAI_API_KEY / CODEX_API_KEY / OPENAI_BASE_URL
до запуска дочернего codex-процесса (инвариант, см. cbcommon.py).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from cbcommon import first_nonblank, scrub_billing_env
from codex_retry import retry_start
from codex_sdk_compat import harden_sdk_enums
from codex_defaults import (
    BRIDGE_THREAD_EPHEMERAL,
    DEFAULT_CODEX_EFFORT,
    DEFAULT_CODEX_MODEL,
    DEFAULT_CODEX_SERVICE_TIER,
    INVESTIGATE_APPROVAL_MODE,
    INVESTIGATE_SANDBOX,
    REASONING_EFFORTS,
    SDK_BUNDLE_WARNING,
    codex_bin_source,
    resolve_codex_bin,
)
from codex_orchestrate_contract import (
    UsageError,
    codex_status_value,
    codex_turn_completed,
)
from codex_run_ledger import (
    RunResult,
    append_event,
    prepare_run_dir,
    render_prompt_document,
    start_heartbeat,
    utc_now,
    write_json,
)
from codex_git_scope import (
    capture_git_snapshot,
    compare_scope,
)
from codex_progress import ProgressTracker, run_turn


def build_instructions(project_cwd: Path, out_dir: Path) -> str:
    """Роль исследователя и sandbox-контракт — канал `developer_instructions`.

    Это политика прогона, а не задание: она уходит при thread_start отдельно от
    реплики, поэтому user-промпт остаётся чистым заданием, а контракт не тонет
    в его тексте."""
    return (
        "Ты — исследователь-субагент. Тебе дано самодостаточное задание.\n\n"
        f"SANDBOX-КОНТРАКТ:\n"
        f"- ЧИТАТЬ можно свободно весь проект ({project_cwd}) и файловую систему.\n"
        f"- Твоя выходная папка — cwd ({out_dir}). Файлы проекта править НЕЛЬЗЯ "
        "(запись в проект заблокирована sandbox).\n"
        "- Все артефакты (отчёты, находки, черновики, данные) складывай в cwd — "
        "это твоё рабочее место: свободно создавай подпапки и структуру под "
        "задачу (drafts/, data/, archive/ …), переписывай и архивируй своё.\n"
        "- Обязательно в конце запиши `result.md` в cwd — краткое резюме находок "
        "с указателями на созданные артефакты."
    )


def _investigate_paths(run_dir: Path, out_dir: Path) -> dict[str, str]:
    return {
        "manifest": str(run_dir / "manifest.json"),
        "events": str(run_dir / "events.jsonl"),
        "prompt": str(run_dir / "prompt.md"),
        "final": str(run_dir / "final.md"),
        "result": str(run_dir / "result.json"),
        "out": str(out_dir),
    }


def _list_artifacts(out_dir: Path) -> list[str]:
    """Файлы, которые Codex реально создал в своей scratch-папке (относительные пути)."""
    if not out_dir.exists():
        return []
    return sorted(
        str(p.relative_to(out_dir))
        for p in out_dir.rglob("*")
        if p.is_file()
    )


# Ключи компактного stdout фонового прогона (порядок — часть наблюдаемой формы).
COMPACT_KEYS = (
    "run_id",
    "run_dir",
    "dry_run",
    "profile",
    "status",
    "ok",
    "codex",
    "paths",
    "artifacts",
    "scope_status",
    "prompt_chars",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Вызвать Codex как исследователя (читает проект; пишет себе в run_dir/out — проект для записи недостижим)."
    )
    parser.add_argument(
        "task_text",
        nargs="?",
        metavar="ЗАДАНИЕ",
        help="Самодостаточное задание для исследователя (позиционно). Эквивалент --task.",
    )
    parser.add_argument("--task", help="Самодостаточное задание (как вызов субагента).")
    parser.add_argument("--project", default=os.getcwd(), help="Корень проекта для чтения (по умолчанию cwd).")
    parser.add_argument("--model", default=DEFAULT_CODEX_MODEL, help=f"Модель Codex (default: {DEFAULT_CODEX_MODEL}).")
    parser.add_argument(
        "--effort",
        choices=REASONING_EFFORTS,
        default=DEFAULT_CODEX_EFFORT,
        help=f"Reasoning effort для Codex turn (default: {DEFAULT_CODEX_EFFORT}).",
    )
    parser.add_argument(
        "--service-tier",
        default=DEFAULT_CODEX_SERVICE_TIER,
        help="Codex service tier (default: наследуется из ~/.codex/config.toml). "
        "Явное значение, например 'priority', — осознанный opt-in fast на этот прогон.",
    )
    parser.add_argument("--run-dir", help="Fresh ledger directory. out/ создаётся внутри как writable scratch.")
    parser.add_argument("--summary-stdout", action="store_true", help="Компактный JSON в stdout; полный ответ — на диске.")
    parser.add_argument("--heartbeat-sec", type=int, default=120, help="Секунды между heartbeat-событиями; 0 отключает.")
    parser.add_argument("--dry-run", action="store_true", help="Собрать промпт и вывести его, НЕ вызывая Codex.")
    args = parser.parse_args()

    task = first_nonblank(args.task, args.task_text)
    if not task:
        print('Нужно задание: --task "..." или позиционный аргумент.', file=sys.stderr)
        return 2
    if args.heartbeat_sec < 0:
        print("--heartbeat-sec must be >= 0.", file=sys.stderr)
        return 2

    removed = scrub_billing_env()
    project_cwd = Path(args.project).expanduser().resolve()
    if not project_cwd.is_dir():
        print(f"--project не существующая директория: {project_cwd}", file=sys.stderr)
        return 2

    # Investigator ВСЕГДА нуждается в run_dir — out/ живёт внутри него.
    try:
        run_id, run_dir = prepare_run_dir(args.run_dir, project=project_cwd)
    except UsageError as exc:
        print(f"[codex-bridge] {exc}", file=sys.stderr)
        return 2
    out_dir = run_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=False)

    # Задание уходит репликой, роль и sandbox-контракт — каналом
    # developer_instructions при thread_start.
    prompt = task
    dev_instructions = build_instructions(project_cwd, out_dir)
    prompt_document = render_prompt_document(prompt, dev_instructions)
    paths = _investigate_paths(run_dir, out_dir)
    codex_bin = resolve_codex_bin()
    if codex_bin is None:
        print(SDK_BUNDLE_WARNING, file=sys.stderr)
    codex_runtime = {
        "model": args.model,
        "effort": args.effort,
        "service_tier": args.service_tier,
        "codex_bin": codex_bin,
        "binary_source": codex_bin_source(codex_bin),
        "thread_ephemeral": BRIDGE_THREAD_EPHEMERAL,
    }
    (run_dir / "prompt.md").write_text(prompt_document, encoding="utf-8")
    manifest = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "created_at": utc_now(),
        "dry_run": args.dry_run,
        "profile": "investigate",
        "project": str(project_cwd),
        "prompt_chars": len(prompt),
        # Контракт ушёл отдельным каналом; без его длины manifest занижал бы
        # объём реально отправленной инструкции.
        "developer_instructions_chars": len(dev_instructions),
        "codex": dict(codex_runtime),
        "runtime": {
            "sandbox": INVESTIGATE_SANDBOX,
            "approval": INVESTIGATE_APPROVAL_MODE,
            "cwd": str(out_dir),
        },
    }
    write_json(run_dir / "manifest.json", manifest)
    append_event(run_dir, "created", profile="investigate", dry_run=args.dry_run)
    ledger = RunResult(
        run_dir,
        base={
            "run_id": run_id,
            "run_dir": str(run_dir),
            "dry_run": args.dry_run,
            "profile": "investigate",
        },
        codex_runtime=codex_runtime,
        paths=paths,
        prompt_chars=len(prompt),
        compact_keys=COMPACT_KEYS,
        summary_stdout=args.summary_stdout,
    )

    if args.dry_run:
        print(
            f"[codex-bridge] DRY-RUN investigate project={project_cwd} out={out_dir} "
            f"model={args.model} effort={args.effort} tier={args.service_tier or 'inherit'} "
            f"binary={codex_runtime['binary_source']} "
            f"sandbox={INVESTIGATE_SANDBOX} approval={INVESTIGATE_APPROVAL_MODE}"
            + (f" | вырезаны из env: {', '.join(removed)}" if removed else " | env чист"),
            file=sys.stderr,
        )
        ledger.finish(status="validated", ok=True, event="dry_run_done")
        if not args.summary_stdout:
            print(prompt_document)
        return 0

    try:
        from openai_codex import ApprovalMode, Codex, CodexConfig, Sandbox
        from openai_codex.generated.v2_all import ReasoningEffort
    except ImportError:
        print(
            "Пакет openai-codex не установлен. Активируй venv: "
            "experiments/codex-bridge/.venv (pip install openai-codex).",
            file=sys.stderr,
        )
        return 1

    # Дрейф движка ChatGPT.app под запиненным SDK: новые enum-значения в
    # ответах не должны ронять мост (см. codex_sdk_compat.py).
    harden_sdk_enums()

    # Scope-снимок проекта ДО прогона: sandbox уже блокирует запись вне out/, но
    # снимок даёт независимое доказательство «проект не тронут» в ledger (uniform
    # с флотом). Не required: вне git investigator всё равно работает.
    snapshot_before = capture_git_snapshot(project_cwd, required=False)

    print(
        f"[codex-bridge] profile=investigate project={project_cwd} out={out_dir} "
        f"model={args.model} effort={args.effort} tier={args.service_tier or 'inherit'} "
        f"binary={codex_runtime['binary_source']} "
        f"sandbox={INVESTIGATE_SANDBOX} approval={INVESTIGATE_APPROVAL_MODE}"
        + (f" | вырезаны из env: {', '.join(removed)}" if removed else " | env чист"),
        file=sys.stderr,
    )
    append_event(run_dir, "codex_start", profile="investigate")

    started_monotonic = time.monotonic()
    progress = ProgressTracker()
    heartbeat_stop, heartbeat_thread = start_heartbeat(
        run_dir,
        args.heartbeat_sec,
        started_monotonic,
        thread_name="codex-investigate-heartbeat",
        snapshot=progress.snapshot,
        profile="investigate",
    )
    config = CodexConfig(
        cwd=str(out_dir),
        codex_bin=codex_bin,
    )
    try:
        with Codex(config) as codex:
            thread = retry_start(
                lambda: codex.thread_start(
                    cwd=str(out_dir),
                    sandbox=Sandbox.workspace_write,
                    approval_mode=ApprovalMode.deny_all,
                    model=args.model,
                    service_tier=args.service_tier,
                    developer_instructions=dev_instructions,
                    ephemeral=BRIDGE_THREAD_EPHEMERAL,
                ),
                run_dir=run_dir,
                operation="thread_start",
            )
            handle = retry_start(
                lambda: thread.turn(
                    prompt,
                    model=args.model,
                    effort=ReasoningEffort(args.effort),
                    service_tier=args.service_tier,
                    sandbox=Sandbox.workspace_write,
                    approval_mode=ApprovalMode.deny_all,
                ),
                run_dir=run_dir,
                operation="turn_start",
            )
            result = run_turn(handle, run_dir=run_dir, tracker=progress)
    except Exception as exc:  # noqa: BLE001 — показать пользователю причину как есть
        heartbeat_stop.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=1)
        ledger.finish(
            status="exception",
            ok=False,
            event="failed",
            extra={"error": str(exc), "artifacts": _list_artifacts(out_dir)},
            event_fields={"status": "exception", "error": str(exc)},
        )
        print(f"[codex-bridge] ошибка вызова Codex: {exc}", file=sys.stderr)
        return 1
    finally:
        heartbeat_stop.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=1)

    # Провалившийся ход сюда не доходит: штатный сборщик SDK поднимает
    # RuntimeError на TurnStatus.failed (`openai_codex/_run.py`
    # `_raise_for_failed_turn`), и приёмка идёт веткой except выше. Дешёвая
    # проверка `result.error` остаётся страховкой на error при НЕ-failed статусе
    # (interrupted, будущие статусы движка) — она входит в общий финал ниже.
    result_error = getattr(result, "error", None)

    # Scope-проверка ПОСЛЕ: allowlist пуст — проект не должен был измениться вообще.
    # Исключаем ТОЛЬКО собственную область investigator'а: scratch `out/` (сюда
    # Codex пишет по замыслу) и известные ledger-файлы backend-а. Сужение до
    # out/+ledger (а не всё run_dir) не маскирует гипотетическую запись рядом с
    # out/. На деле sandbox её и так блокирует (writable = cwd(out)+системный
    # temp; run_dir-родитель вне workspace), но scope остаётся честным вторым
    # доказательством. Фильтр нужен, когда run_dir лежит внутри worktree и не в
    # .gitignore — иначе ledger дал бы ложный scope=failed.
    scope_status = "not_checked"
    scope_detail: dict[str, object] | None = None
    snapshot_after = capture_git_snapshot(project_cwd, required=False)
    if snapshot_before.available and snapshot_after.available:
        check = compare_scope(snapshot_before, snapshot_after, allowlist=set())
        out_abs = out_dir.resolve()
        ledger_abs = {
            Path(paths[key]).resolve()
            for key in ("manifest", "events", "prompt", "final", "result")
        }

        def _is_own_output(rel_path: str) -> bool:
            abs_path = (project_cwd / rel_path).resolve()
            if abs_path in ledger_abs:
                return True
            try:
                abs_path.relative_to(out_abs)
                return True
            except ValueError:
                pass
            # run_dir теперь по умолчанию внутри проекта: git status сворачивает
            # свежий untracked каталог в одну запись — сам run_dir или его
            # предок (`_workspace/`). Обе записи — своя площадка: в run_dir вне
            # out/ пишет только backend (Codex из cwd=out туда не дотянется —
            # вне workspace). Отдельные файлы-соседи внутри run_dir по-прежнему
            # НЕ своё (выше отфильтрованы только out/ и известный ledger).
            run_abs = run_dir.resolve()
            if abs_path == run_abs:
                return True
            try:
                run_abs.relative_to(abs_path)
                return True
            except ValueError:
                return False

        changed = [f for f in check.changed_files if not _is_own_output(f)]
        out_of_scope = [f for f in check.out_of_scope_files if not _is_own_output(f)]
        scope_status = "passed" if (not out_of_scope and not check.head_changed) else "failed"
        scope_detail = {
            "changed_files": changed,
            "out_of_scope_files": out_of_scope,
            "head_changed": check.head_changed,
        }

    status = codex_status_value(getattr(result, "status", "?"))
    usage = getattr(result, "usage", None)
    final_response = result.final_response or "[пустой ответ Codex]"
    (run_dir / "final.md").write_text(final_response, encoding="utf-8")
    artifacts = _list_artifacts(out_dir)

    print(
        f"[codex-bridge] статус={status} scope={scope_status} "
        f"артефактов={len(artifacts)} usage={usage}",
        file=sys.stderr,
    )

    # Fail-closed по двум независимым осям: turn считается успешным только при
    # точном completed, а scope=failed означает запись вне области investigator.
    # not_checked (нет git) успех не роняет: гарантию несёт sandbox, scope —
    # лишь второе доказательство.
    completed = codex_turn_completed(status, result_error)
    ok = completed and scope_status != "failed"
    failure_reasons: list[str] = []
    if result_error:
        failure_reasons.append(str(result_error))
    elif not completed:
        failure_reasons.append(f"Codex turn did not complete (status={status}).")
    if scope_status == "failed":
        failure_reasons.append("Investigator changed project scope.")
    error = " ".join(failure_reasons) if failure_reasons else None
    extra: dict[str, object] = {
        "artifacts": artifacts,
        "scope_status": scope_status,
        "scope": scope_detail,
        "duration_ms": getattr(result, "duration_ms", None),
        "usage": str(usage),
        "final_response": final_response,
    }
    if error:
        extra["error"] = error
    ledger.finish(
        status=status,
        ok=ok,
        event="done" if ok else "failed",
        extra=extra,
        event_fields={
            "status": status,
            "ok": ok,
            "scope_status": scope_status,
            **({"error": error} if error else {}),
        },
    )

    if args.summary_stdout:
        return 0 if ok else 1
    if not ok:
        print(f"[codex-bridge] {error}", file=sys.stderr)
        return 1
    print(final_response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
