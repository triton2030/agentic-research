#!/usr/bin/env python3
"""codex-bridge — вызвать Codex как стороннего ревьюера/консультанта из Claude Code.

Зеркало `claude-bridge` (тот гоняет Claude из Codex; этот — Codex из Claude).

Биллинг идёт через ChatGPT-аккаунт (твой `codex login`, auth_mode=chatgpt),
НЕ через API-ключ: перед запуском дочернего codex-процесса скрипт вырезает
OPENAI_API_KEY / CODEX_API_KEY / OPENAI_BASE_URL из окружения, чтобы случайная
переменная не увела ревью на платный API (то же делает claude-bridge с
ANTHROPIC_API_KEY в обратную сторону).

Codex запускается в sandbox read-only c рабочей папкой = корень проекта:
он ВИДИТ все файлы проекта, но ничего не пишет.

Режимы:
  task "..."            задание/вопрос БЕЗ транскрипта (DEFAULT) — Codex видит
                        файлы проекта, как вызов субагента; самый дешёвый и быстрый
  review               сторонний ревьюер хода работы (транскрипт + файлы)
  ask --question "..."  произвольный вопрос с транскриптом и файлами как контекстом

Транскрипт нужен только режимам review/ask; режим task его не подхватывает.
Когда транскрипт нужен, он находится автоматически
(CLAUDE_CODE_SESSION_ID → <id>.jsonl, иначе свежайший .jsonl проекта)
или задаётся явно через --transcript.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from cbcommon import scrub_billing_env
from codex_defaults import (
    BRIDGE_THREAD_EPHEMERAL,
    DEFAULT_CODEX_EFFORT,
    DEFAULT_CODEX_MODEL,
    REASONING_EFFORTS,
    REVIEW_APPROVAL_MODE,
    REVIEW_SANDBOX,
    SDK_BUNDLE_WARNING,
    codex_bin_source,
    resolve_codex_bin,
)
from codex_orchestrate_contract import UsageError, codex_status_value
from codex_orchestrate_state import (
    append_event,
    prepare_run_dir,
    start_heartbeat,
    utc_now,
    write_json,
)

CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"


def encode_project_dir(cwd: Path) -> str:
    """Claude Code кодирует путь проекта в имя папки: /Users/x/y -> -Users-x-y."""
    return str(cwd).replace("/", "-")


def find_transcript(project_cwd: Path, explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.exists() else None
    proj_dir = CLAUDE_PROJECTS / encode_project_dir(project_cwd)
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    if sid:
        by_id = proj_dir / f"{sid}.jsonl"
        if by_id.exists():
            return by_id
    if not proj_dir.exists():
        return None
    candidates = sorted(proj_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f"… [+{len(text) - limit} символов оборвано]"


def _first_nonblank(*values: str | None) -> str | None:
    """Первое значение, непустое после strip. Защищает от задания из одних
    пробелов ('   '): оно truthy, но по смыслу пустое и жгло бы кредиты впустую."""
    for value in values:
        if value and value.strip():
            return value.strip()
    return None


def render_transcript(path: Path, include_thinking: bool) -> str:
    """JSONL-транскрипт Claude Code → читаемый диалог.

    Реплики user и текст assistant — целиком; вызовы инструментов — одной
    строкой; результаты инструментов и (опционально) thinking — усечённо.
    """
    lines: list[str] = []
    for raw in path.read_text(errors="replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        rtype = rec.get("type")
        if rtype not in ("user", "assistant"):
            continue
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")

        if rtype == "user":
            if isinstance(content, str):
                if content.strip():
                    lines.append(f"\n### 👤 Пользователь\n{content.strip()}")
            elif isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_result":
                        body = block.get("content")
                        if isinstance(body, list):
                            body = " ".join(
                                b.get("text", "") for b in body if isinstance(b, dict)
                            )
                        lines.append(f"  ↳ [результат инструмента] {_truncate(str(body or ''), 300)}")
                    elif block.get("type") == "text":
                        lines.append(f"\n### 👤 Пользователь\n{block.get('text', '').strip()}")
            continue

        # assistant
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    txt = block.get("text", "").strip()
                    if txt:
                        lines.append(f"\n### 🤖 Claude\n{txt}")
                elif btype == "thinking" and include_thinking:
                    think = block.get("thinking", "").strip()
                    if think:
                        lines.append(f"\n  💭 _(размышление)_ {_truncate(think, 800)}")
                elif btype == "tool_use":
                    name = block.get("name", "?")
                    inp = block.get("input", {})
                    brief = json.dumps(inp, ensure_ascii=False)
                    lines.append(f"  ⚙️ [инструмент: {name}] {_truncate(brief, 200)}")
    return "\n".join(lines)


TASK_ROLE = """\
Ты — независимый старший эксперт; профессиональную линзу (инженерия, документы,
стратегия…) бери из задания. У тебя read-only доступ ко всем файлам этого
проекта — открывай и проверяй реальный код и документы, ничего не домысливай.
Выполни задание ниже: будь конкретным, опирайся на реальные файлы и точные пути,
не пересказывай очевидное."""


REVIEW_ROLE = """\
Ты — независимый старший ревьюер; профессиональную линзу бери из содержания
работы. Ниже транскрипт рабочей сессии другого
ИИ-агента (Claude Code) с пользователем. У тебя есть read-only доступ ко всем
файлам этого проекта — открывай и проверяй реальный код и документы, не верь
транскрипту на слово.

Дай стороннее ревью ХОДА РАБОТЫ:
- что упущено, какие риски и неверные допущения;
- где агент выбрал слабый подход и что было бы лучше;
- что проверить или переделать прежде, чем считать работу готовой.
Будь конкретным и опирайся на файлы. Не пересказывай транскрипт."""


def build_prompt(mode: str, transcript_md: str, payload: str | None) -> str:
    if mode == "task":
        return f"{TASK_ROLE}\n\n===== ЗАДАНИЕ =====\n{payload}"
    if mode == "review":
        return (
            f"{REVIEW_ROLE}\n\n"
            f"===== ТРАНСКРИПТ СЕССИИ =====\n{transcript_md}\n"
            f"===== КОНЕЦ ТРАНСКРИПТА =====\n\n"
            f"Теперь дай ревью."
        )
    # ask
    return (
        "Ниже транскрипт рабочей сессии ИИ-агента (Claude Code) с пользователем, "
        "как контекст. У тебя read-only доступ ко всем файлам проекта — сверяйся с ними.\n\n"
        f"===== ТРАНСКРИПТ СЕССИИ (контекст) =====\n{transcript_md}\n"
        f"===== КОНЕЦ ТРАНСКРИПТА =====\n\n"
        f"===== ВОПРОС =====\n{payload}"
    )


def _review_paths(run_dir: Path) -> dict[str, str]:
    return {
        "manifest": str(run_dir / "manifest.json"),
        "events": str(run_dir / "events.jsonl"),
        "prompt": str(run_dir / "prompt.md"),
        "final": str(run_dir / "final.md"),
        "result": str(run_dir / "result.json"),
    }


DIALOG_REGISTRY_NAME = "dialog-threads.jsonl"


def _dialog_registry_path(project_cwd: Path) -> Path:
    return project_cwd / "_workspace" / "codex-artifacts" / DIALOG_REGISTRY_NAME


def _register_dialog_thread(project_cwd: Path, thread_id: str | None, run_id: str | None) -> None:
    """Реестр provenance: --continue по умолчанию доверяет только тредам,
    созданным --dialog в этом же проекте (чужой Desktop/API-тред несёт
    непроверенные роль и контекст)."""
    if not thread_id:
        return
    path = _dialog_registry_path(project_cwd)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"thread_id": thread_id, "run_id": run_id, "created_at": utc_now()}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _dialog_thread_known(project_cwd: Path, thread_id: str) -> bool:
    path = _dialog_registry_path(project_cwd)
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            if json.loads(line).get("thread_id") == thread_id:
                return True
        except json.JSONDecodeError:
            continue
    return False


def _compact_review_payload(payload: dict[str, object]) -> dict[str, object]:
    return {
        key: payload[key]
        for key in (
            "run_id",
            "run_dir",
            "dry_run",
            "mode",
            "status",
            "ok",
            "codex",
            "paths",
            "prompt_chars",
        )
        if key in payload
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Вызвать Codex как ревьюера/консультанта из Claude Code.")
    parser.add_argument(
        "task_text",
        nargs="?",
        metavar="ЗАДАНИЕ",
        help="Задание для режима task (позиционно). Эквивалент --task.",
    )
    parser.add_argument(
        "--mode",
        choices=("task", "review", "ask"),
        default="task",
        help="task (default): задание без транскрипта; review/ask: с транскриптом сессии.",
    )
    parser.add_argument("--task", help="Задание для режима task (как вызов субагента, без транскрипта).")
    parser.add_argument("--question", help="Вопрос для режима ask.")
    parser.add_argument("--project", default=os.getcwd(), help="Корень проекта (по умолчанию cwd).")
    parser.add_argument("--transcript", help="Путь к .jsonl транскрипту (по умолчанию — автопоиск текущей сессии).")
    parser.add_argument("--model", default=DEFAULT_CODEX_MODEL, help=f"Модель Codex (default: {DEFAULT_CODEX_MODEL}).")
    parser.add_argument(
        "--effort",
        choices=REASONING_EFFORTS,
        default=DEFAULT_CODEX_EFFORT,
        help=f"Reasoning effort для Codex turn (default: {DEFAULT_CODEX_EFFORT}).",
    )
    parser.add_argument("--include-thinking", action="store_true", help="Включить блоки размышлений Claude в транскрипт.")
    parser.add_argument("--max-chars", type=int, default=200_000, help="Бюджет транскрипта; при превышении остаётся свежий хвост.")
    parser.add_argument("--run-dir", help="Fresh ledger directory for background-safe runs.")
    parser.add_argument("--summary-stdout", action="store_true", help="Print compact JSON to stdout; full data is written to --run-dir.")
    parser.add_argument("--heartbeat-sec", type=int, default=120, help="Seconds between ledger heartbeat events; 0 disables.")
    parser.add_argument("--dry-run", action="store_true", help="Собрать промпт и вывести его, НЕ вызывая Codex (не тратит кредиты).")
    parser.add_argument(
        "--dialog",
        action="store_true",
        help="Персистентный тред: thread_id в ledger/stderr, разговор можно продолжить через --continue (след в Desktop-истории).",
    )
    parser.add_argument(
        "--continue",
        dest="continue_thread",
        metavar="THREAD_ID",
        help="Продолжить существующий тред: задание уходит следующей репликой, роль и контекст уже в треде.",
    )
    parser.add_argument(
        "--continue-foreign",
        action="store_true",
        help="Осознанный override: продолжить тред НЕ из реестра диалогов этого проекта (чужой контекст и роль не проверены).",
    )
    args = parser.parse_args()

    # Задание/вопрос берём из любого источника, чтобы вызов не падал из-за того,
    # каким флагом он записан: --task, --question или позиционный аргумент.
    payload = _first_nonblank(args.task, args.question, args.task_text)

    if args.mode == "task" and not payload:
        print('Режим task требует задание: --task "..." или позиционный аргумент.', file=sys.stderr)
        return 2
    if args.mode == "ask" and not payload:
        print("Режим ask требует --question (или --task / позиционный аргумент).", file=sys.stderr)
        return 2
    if args.continue_thread is not None:
        # Пустая переменная ($THREAD_ID) молча превращала бы продолжение в НОВЫЙ
        # ephemeral-тред — потеря контекста без ошибки. Fail closed.
        args.continue_thread = args.continue_thread.strip()
        if not args.continue_thread:
            print(
                "--continue получил пустой THREAD_ID (потерянная переменная?) — отказ, "
                "иначе вместо продолжения молча начался бы новый тред.",
                file=sys.stderr,
            )
            return 2
    if args.continue_thread and args.mode != "task":
        print(
            "--continue несовместим с --mode review/ask: тред уже несёт контекст, транскрипт не подмешивается.",
            file=sys.stderr,
        )
        return 2
    if args.heartbeat_sec < 0:
        print("--heartbeat-sec must be >= 0.", file=sys.stderr)
        return 2

    project_cwd = Path(args.project).expanduser().resolve()

    if (
        args.continue_thread
        and not args.continue_foreign
        and not _dialog_thread_known(project_cwd, args.continue_thread)
    ):
        print(
            f"--continue {args.continue_thread}: тред не найден в реестре диалогов проекта "
            f"({_dialog_registry_path(project_cwd)}). По умолчанию продолжаются только треды, "
            f"созданные --dialog в этом проекте; чужой тред — осознанно через --continue-foreign.",
            file=sys.stderr,
        )
        return 2

    # Транскрипт нужен только режимам с контекстом сессии. Режим task его не тянет
    # — это и есть его смысл: дешёвый, быстрый вызов «как субагент».
    transcript_path: Path | None = None
    transcript_md = ""
    if args.mode in ("review", "ask"):
        transcript_path = find_transcript(project_cwd, args.transcript)
        if transcript_path is None:
            print(
                f"Транскрипт не найден. Искал по CLAUDE_CODE_SESSION_ID и в "
                f"{CLAUDE_PROJECTS / encode_project_dir(project_cwd)}. Передай --transcript явно.",
                file=sys.stderr,
            )
            return 1

        transcript_md = render_transcript(transcript_path, include_thinking=args.include_thinking)
        if len(transcript_md) > args.max_chars:
            head = transcript_md[: args.max_chars // 5]
            tail = transcript_md[-(args.max_chars * 4 // 5):]
            transcript_md = f"{head}\n\n… [середина транскрипта оборвана для бюджета] …\n\n{tail}"

    if args.continue_thread:
        # Продолжение диалога: роль и контекст первой реплики уже в треде.
        prompt = payload
    else:
        prompt = build_prompt(args.mode, transcript_md, payload)
    transcript_name = transcript_path.name if transcript_path else "—"
    # Single source for the codex block written to every ledger payload, so the
    # audit owner (runs/) records thread_ephemeral uniformly: result["codex"].
    codex_bin = resolve_codex_bin()
    if codex_bin is None:
        print(SDK_BUNDLE_WARNING, file=sys.stderr)
    # Диалог требует персистентный тред: resume работает только по rollout на
    # диске («no rollout found» для эфемерных — проверено живым пробником).
    thread_persistent = bool(args.dialog or args.continue_thread)
    codex_runtime = {
        "model": args.model,
        "effort": args.effort,
        "codex_bin": codex_bin,
        "binary_source": codex_bin_source(codex_bin),
        "thread_ephemeral": BRIDGE_THREAD_EPHEMERAL and not thread_persistent,
        "thread_persistent": thread_persistent,
        "resumed_from_thread": args.continue_thread,
    }
    run_id: str | None = None
    run_dir: Path | None = None
    paths: dict[str, str] | None = None
    # Персистентный диалог обязан иметь audit owner: run_dir создаётся даже без
    # явных флагов, иначе rollout жил бы только в Desktop store без ledger.
    if args.run_dir or args.summary_stdout or thread_persistent:
        try:
            run_id, run_dir = prepare_run_dir(args.run_dir, project=project_cwd)
        except UsageError as exc:
            print(f"[codex-bridge] {exc}", file=sys.stderr)
            return 2
        paths = _review_paths(run_dir)
        manifest = {
            "run_id": run_id,
            "run_dir": str(run_dir),
            "created_at": utc_now(),
            "dry_run": args.dry_run,
            "mode": args.mode,
            "project": str(project_cwd),
            "transcript": str(transcript_path) if transcript_path else None,
            "prompt_chars": len(prompt),
            "codex": dict(codex_runtime),
            "runtime": {
                "sandbox": REVIEW_SANDBOX,
                "approval_mode": REVIEW_APPROVAL_MODE,
                "heartbeat_sec": args.heartbeat_sec,
            },
            "paths": paths,
        }
        write_json(run_dir / "manifest.json", manifest)
        (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
        append_event(run_dir, "validated", dry_run=args.dry_run, mode=args.mode)

    if args.dry_run:
        print(f"[codex-bridge dry-run] транскрипт={transcript_name} "
              f"промпт={len(prompt)} симв. режим={args.mode} "
              f"model={args.model} effort={args.effort} "
              f"binary={codex_runtime['binary_source']} "
              f"sandbox={REVIEW_SANDBOX} approval={REVIEW_APPROVAL_MODE}", file=sys.stderr)
        if run_dir is not None and run_id is not None and paths is not None:
            payload = {
                "run_id": run_id,
                "run_dir": str(run_dir),
                "dry_run": True,
                "mode": args.mode,
                "status": "validated",
                "ok": True,
                "codex": dict(codex_runtime),
                "paths": paths,
                "prompt_chars": len(prompt),
            }
            if thread_persistent:
                # Dry-run валидирует CLI/prompt/реестр, но НЕ существование
                # треда и не создание нового — не выдаём сильных заявлений.
                payload["resume_checked"] = False
            write_json(run_dir / "result.json", payload)
            append_event(run_dir, "done", dry_run=True, ok=True)
            if args.summary_stdout:
                print(json.dumps(_compact_review_payload(payload), ensure_ascii=False, indent=2))
                return 0
        print(prompt)
        return 0

    # Гарантия биллинга через аккаунт: до импорта/запуска codex убираем API-ключи.
    removed = scrub_billing_env()

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

    print(
        f"[codex-bridge] режим={args.mode} транскрипт={transcript_name} "
        f"({len(transcript_md)} симв.) project={project_cwd} "
        f"model={args.model} effort={args.effort} "
        f"binary={codex_runtime['binary_source']} "
        f"sandbox={REVIEW_SANDBOX} approval={REVIEW_APPROVAL_MODE}"
        + (f" | вырезаны из env: {', '.join(removed)}" if removed else " | env чист"),
        file=sys.stderr,
    )
    if run_dir is not None:
        append_event(
            run_dir,
            "codex_start",
            mode=args.mode,
            operation="thread_resume" if args.continue_thread else "thread_start",
            requested_thread_id=args.continue_thread,
        )

    config = CodexConfig(cwd=str(project_cwd), codex_bin=codex_bin)
    started_monotonic = time.monotonic()
    heartbeat_stop, heartbeat_thread = start_heartbeat(
        run_dir,
        args.heartbeat_sec,
        started_monotonic,
        thread_name="codex-review-heartbeat",
        mode=args.mode,
    )
    try:
        with Codex(config) as codex:
            if args.continue_thread:
                thread = codex.thread_resume(
                    args.continue_thread,
                    cwd=str(project_cwd),
                    sandbox=Sandbox.read_only,
                    approval_mode=ApprovalMode.deny_all,
                    model=args.model,
                )
            else:
                thread = codex.thread_start(
                    cwd=str(project_cwd),
                    sandbox=Sandbox.read_only,
                    approval_mode=ApprovalMode.deny_all,
                    model=args.model,
                    ephemeral=codex_runtime["thread_ephemeral"],
                )
            codex_runtime["thread_id"] = getattr(thread, "id", None)
            if args.dialog and not args.continue_thread:
                _register_dialog_thread(project_cwd, codex_runtime["thread_id"], run_id)
            if thread_persistent:
                print(
                    f"[codex-bridge] thread_id={codex_runtime['thread_id']} "
                    f"(persistent; продолжение: --continue {codex_runtime['thread_id']})",
                    file=sys.stderr,
                )
                if run_dir is not None:
                    append_event(
                        run_dir,
                        "thread",
                        thread_id=codex_runtime["thread_id"],
                        persistent=True,
                    )
            result = thread.run(
                prompt,
                model=args.model,
                effort=ReasoningEffort(args.effort),
                sandbox=Sandbox.read_only,
                approval_mode=ApprovalMode.deny_all,
            )
    except Exception as exc:  # noqa: BLE001 — показать пользователю причину как есть
        heartbeat_stop.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=1)
        if run_dir is not None and run_id is not None and paths is not None:
            payload = {
                "run_id": run_id,
                "run_dir": str(run_dir),
                "dry_run": False,
                "mode": args.mode,
                "status": "exception",
                "ok": False,
                "error": str(exc),
                "codex": dict(codex_runtime),
                "paths": paths,
                "prompt_chars": len(prompt),
            }
            write_json(run_dir / "result.json", payload)
            append_event(
                run_dir,
                "failed",
                status="exception",
                error=str(exc),
                requested_thread_id=args.continue_thread,
            )
            if args.summary_stdout:
                print(json.dumps(_compact_review_payload(payload), ensure_ascii=False, indent=2))
        print(f"[codex-bridge] ошибка вызова Codex: {exc}", file=sys.stderr)
        return 1
    finally:
        heartbeat_stop.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=1)

    if getattr(result, "error", None):
        if run_dir is not None and run_id is not None and paths is not None:
            payload = {
                "run_id": run_id,
                "run_dir": str(run_dir),
                "dry_run": False,
                "mode": args.mode,
                "status": codex_status_value(getattr(result, "status", "failed")),
                "ok": False,
                "error": str(result.error),
                "codex": dict(codex_runtime),
                "paths": paths,
                "prompt_chars": len(prompt),
            }
            write_json(run_dir / "result.json", payload)
            append_event(
                run_dir,
                "failed",
                status=payload["status"],
                error=str(result.error),
                requested_thread_id=args.continue_thread,
            )
            if args.summary_stdout:
                print(json.dumps(_compact_review_payload(payload), ensure_ascii=False, indent=2))
        print(f"[codex-bridge] Codex вернул ошибку: {result.error}", file=sys.stderr)
        return 1

    usage = getattr(result, "usage", None)
    status = codex_status_value(getattr(result, "status", "?"))
    print(
        f"[codex-bridge] статус={status} "
        f"время={getattr(result, 'duration_ms', '?')}мс usage={usage}",
        file=sys.stderr,
    )

    final_response = result.final_response or "[пустой ответ Codex]"
    if run_dir is not None and run_id is not None and paths is not None:
        (run_dir / "final.md").write_text(final_response, encoding="utf-8")
        payload = {
            "run_id": run_id,
            "run_dir": str(run_dir),
            "dry_run": False,
            "mode": args.mode,
            "status": status,
            "ok": True,
            "codex": dict(codex_runtime),
            "paths": paths,
            "prompt_chars": len(prompt),
            "duration_ms": getattr(result, "duration_ms", None),
            "usage": str(usage),
            "final_response": final_response,
        }
        write_json(run_dir / "result.json", payload)
        append_event(run_dir, "done", status=status, ok=True)
        if args.summary_stdout:
            print(json.dumps(_compact_review_payload(payload), ensure_ascii=False, indent=2))
            return 0

    print(final_response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
