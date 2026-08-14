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

from cbcommon import first_nonblank, scrub_billing_env
from codex_retry import retry_start
from codex_sdk_compat import harden_sdk_enums
from codex_defaults import (
    BRIDGE_THREAD_EPHEMERAL,
    DEFAULT_CODEX_EFFORT,
    DEFAULT_CODEX_MODEL,
    DEFAULT_CODEX_SERVICE_TIER,
    REASONING_EFFORTS,
    REVIEW_APPROVAL_MODE,
    REVIEW_SANDBOX,
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
from codex_progress import ProgressTracker, run_turn

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
Выполни задание из сообщения пользователя: будь конкретным, опирайся на реальные
файлы и точные пути, не пересказывай очевидное."""


REVIEW_ROLE = """\
Ты — независимый старший ревьюер; профессиональную линзу бери из содержания
работы. В сообщении пользователя — транскрипт рабочей сессии другого
ИИ-агента (Claude Code) с пользователем. У тебя есть read-only доступ ко всем
файлам этого проекта — открывай и проверяй реальный код и документы, не верь
транскрипту на слово.

Дай стороннее ревью ХОДА РАБОТЫ:
- что упущено, какие риски и неверные допущения;
- где агент выбрал слабый подход и что было бы лучше;
- что проверить или переделать прежде, чем считать работу готовой.
Будь конкретным и опирайся на файлы. Не пересказывай транскрипт."""


ASK_ROLE = """\
В сообщении пользователя — транскрипт рабочей сессии ИИ-агента (Claude Code) с
пользователем как контекст и вопрос к тебе. У тебя read-only доступ ко всем
файлам проекта — сверяйся с ними, а не с пересказом."""



def _review_target(args, payload: str | None) -> dict:
    """git-таргет для нативного `review/start`.

    Четыре формы поддерживает сам движок; `custom` с инструкциями — то, от чего
    официальный плагин OpenAI отказывается, а мы отдаём.
    """
    if args.commit:
        return {"type": "commit", "sha": args.commit}
    if args.base:
        return {"type": "baseBranch", "branch": args.base}
    if payload:
        return {"type": "custom", "instructions": payload}
    return {"type": "uncommittedChanges"}


def build_instructions(mode: str) -> str | None:
    """Инвариантная роль режима — она уходит каналом `developer_instructions`
    (thread_start/thread_resume), а не вклеивается в реплику.

    Разделение не косметическое: роль относится к треду, а не к ходу, поэтому
    в диалоге её не надо повторять текстом, и она не конкурирует с заданием за
    внимание. mode=diff роли не получает вовсе — контракт ревью несёт сам
    движок (`review/start`)."""
    if mode == "task":
        return TASK_ROLE
    if mode == "review":
        return REVIEW_ROLE
    if mode == "ask":
        return ASK_ROLE
    return None


def build_prompt(mode: str, transcript_md: str, payload: str | None) -> str:
    """User-промпт: только задание/вопрос и, где нужен, транскрипт сессии."""
    if mode == "task":
        return f"===== ЗАДАНИЕ =====\n{payload}"
    if mode == "review":
        return (
            f"===== ТРАНСКРИПТ СЕССИИ =====\n{transcript_md}\n"
            f"===== КОНЕЦ ТРАНСКРИПТА =====\n\n"
            f"Теперь дай ревью."
        )
    # ask
    return (
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


def _session_short() -> str | None:
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    return sid[:8] if sid else None


def _topic_from_payload(payload: str | None) -> str:
    return " ".join((payload or "").split())[:80]


def _append_registry_event(project_cwd: Path, event: dict) -> None:
    """Append-only реестр диалогов: provenance для --continue (доверяем только
    тредам этого проекта) + статусная доска для других агентов (тема, сессия,
    последняя активность). События start/continue/archive; legacy-строки без
    "event" читаются как start. Продолжение чужого треда через
    --continue-foreign оставляет continue-событие — тред «усыновляется»
    проектом, дальше --continue работает без override."""
    path = _dialog_registry_path(project_cwd)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def _dialog_thread_known(project_cwd: Path, thread_id: str) -> bool:
    path = _dialog_registry_path(project_cwd)
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        # Доверие дают только start/legacy/continue: archive чужого треда не
        # должен «легализовать» его для --continue без --continue-foreign.
        if entry.get("event") in ("archive", "unarchive"):
            continue
        if entry.get("thread_id") == thread_id:
            return True
    return False


# Ключи компактного stdout фонового прогона (порядок — часть наблюдаемой формы).
COMPACT_KEYS = (
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
        choices=("task", "review", "ask", "diff"),
        default="task",
        help=(
            "task (default): задание без транскрипта; review/ask: с транскриптом сессии; "
            "diff: НАТИВНЫЙ code review движка по git-таргету (не промпт)."
        ),
    )
    parser.add_argument("--base", metavar="REF", help="mode=diff: ревью против базовой ветки.")
    parser.add_argument("--commit", metavar="SHA", help="mode=diff: ревью одного коммита.")
    parser.add_argument("--task", help="Задание для режима task (как вызов субагента, без транскрипта).")
    parser.add_argument("--question", help="Вопрос для режима ask.")
    parser.add_argument("--project", default=os.getcwd(), help="Корень проекта (по умолчанию cwd).")
    parser.add_argument("--transcript", help="Путь к .jsonl транскрипту (по умолчанию — автопоиск текущей сессии).")
    parser.add_argument("--model", default=DEFAULT_CODEX_MODEL, help=f"Модель Codex (default: {DEFAULT_CODEX_MODEL}).")
    parser.add_argument(
        "--effort",
        choices=REASONING_EFFORTS,
        # None-sentinel, а не готовый дефолт: mode=diff обязан отличать «усилие
        # заказали явно» от «взяли дефолт». Сравнение с DEFAULT_CODEX_EFFORT для
        # этого не годится — когда дефолтом стал xhigh (2026-08-14), явный
        # `--effort xhigh` в diff-режиме перестал печатать предупреждение,
        # и пользователь молча думал, что заказал глубину.
        default=None,
        help=f"Reasoning effort для Codex turn (default: {DEFAULT_CODEX_EFFORT}).",
    )
    parser.add_argument(
        "--service-tier",
        default=DEFAULT_CODEX_SERVICE_TIER,
        help="Codex service tier (default: наследуется из ~/.codex/config.toml). "
        "Явное значение, например 'priority', — осознанный opt-in fast на этот прогон.",
    )
    parser.add_argument("--include-thinking", action="store_true", help="Включить блоки размышлений Claude в транскрипт.")
    parser.add_argument("--max-chars", type=int, default=200_000, help="Бюджет транскрипта; при превышении остаётся свежий хвост.")
    parser.add_argument(
        "--run-dir",
        help="Fresh ledger directory override (default: <project>/_workspace/codex-artifacts/<run_id>).",
    )
    parser.add_argument(
        "--summary-stdout",
        action="store_true",
        help="Print compact JSON to stdout; full data is written to the run_dir.",
    )
    parser.add_argument("--heartbeat-sec", type=int, default=120, help="Seconds between ledger heartbeat events; 0 disables.")
    parser.add_argument("--dry-run", action="store_true", help="Собрать промпт и вывести его, НЕ вызывая Codex (не тратит кредиты).")
    parser.add_argument(
        "--dialog",
        action="store_true",
        help="Персистентный тред: thread_id в ledger/stderr, разговор можно продолжить через --continue (след в Desktop-истории).",
    )
    parser.add_argument(
        "--no-dialog",
        action="store_true",
        help="Снять авто-диалог на тяжёлом усилии (xhigh/max/ultra): одиночный эфемерный выстрел.",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Проверить движок без прогона: аккаунт, эффективный конфиг, наследуемый tier. Кредиты не тратит.",
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
    parser.add_argument(
        "--topic",
        help="Тема диалога для реестра (--dialog): видна другим агентам в codex_threads.py list; default — первые 80 симв. задания.",
    )
    args = parser.parse_args()

    if args.doctor:
        # Проверка здоровья движка идёт ДО всякой валидации задания: спрашивают
        # её как раз тогда, когда прогон не получается.
        scrub_billing_env()
        from codex_preflight import check, render  # noqa: PLC0415 — после scrub

        report = check(cwd=str(Path(args.project).expanduser().resolve()))
        print(render(report))
        return 0 if report.get("ok") else 1

    # Задание/вопрос берём из любого источника, чтобы вызов не падал из-за того,
    # каким флагом он записан: --task, --question или позиционный аргумент.
    payload = first_nonblank(args.task, args.question, args.task_text)

    if args.mode == "diff" and args.base and args.commit:
        print("mode=diff: --base и --commit взаимоисключимы.", file=sys.stderr)
        return 2
    effort_explicit = args.effort is not None
    if not effort_explicit:
        args.effort = DEFAULT_CODEX_EFFORT
    if args.mode == "diff" and effort_explicit:
        # Молча проглотить флаг было бы хуже всего: пользователь думает, что
        # заказал глубину, а нативный ревьюер работает на конфиге движка.
        print(
            f"[codex-bridge] mode=diff: --effort {args.effort} НЕ применяется — "
            "нативный review/start усилие не принимает, оно наследуется из "
            "конфига движка (в ledger: effort=inherit).",
            file=sys.stderr,
        )
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

    # Роль отправляется отдельным каналом (developer_instructions) и в
    # user-промпт не попадает. В --continue она уходит повторно при
    # thread_resume: роль идемпотентна, а вот переклейка её в текст реплики
    # ломала бы диалог сменой рамки на каждом ходе.
    dev_instructions = build_instructions(args.mode)
    if args.mode == "diff":
        # Промпта нет вовсе: контракт ревью несёт сам движок. В prompt.md
        # кладём таргет, чтобы audit-владелец не врал пустотой.
        prompt = f"[нативный review/start] target={json.dumps(_review_target(args, payload), ensure_ascii=False)}"
    elif args.continue_thread:
        # Продолжение диалога: контекст первой реплики уже в треде.
        prompt = payload
    else:
        prompt = build_prompt(args.mode, transcript_md, payload)
    prompt_document = render_prompt_document(prompt, dev_instructions)
    transcript_name = transcript_path.name if transcript_path else "—"
    # Single source for the codex block written to every ledger payload, so the
    # audit owner (run_dir) records thread_ephemeral uniformly: result["codex"].
    codex_bin = resolve_codex_bin()
    if codex_bin is None:
        print(SDK_BUNDLE_WARNING, file=sys.stderr)
    # Тред заводится только явным --dialog. Раньше тяжёлое усилие включало его
    # само; это решало за вызывающего дважды — навязывало персистентный тред
    # одноразовому вопросу и спорило с инвариантом владельца «тред только у
    # пишущего воркера» (2026-08-14). Глубина мышления не доказывает, что
    # будет второй ход.
    # Диалог требует персистентный тред: resume работает только по rollout на
    # диске («no rollout found» для эфемерных — проверено живым пробником).
    thread_persistent = bool(args.dialog or args.continue_thread)
    codex_runtime = {
        "model": args.model,
        # mode=diff идёт через review/start, который effort не принимает, а
        # thread_start его не несёт: усилие там НАСЛЕДУЕТСЯ из конфига движка.
        # Ledger обязан говорить это прямо — иначе аудит врёт так же, как врал
        # бы «применённый tier».
        "effort": "inherit" if args.mode == "diff" else args.effort,
        "service_tier": args.service_tier,
        "codex_bin": codex_bin,
        "binary_source": codex_bin_source(codex_bin),
        "thread_ephemeral": BRIDGE_THREAD_EPHEMERAL and not thread_persistent,
        "thread_persistent": thread_persistent,
        "resumed_from_thread": args.continue_thread,
    }
    # Every reviewer turn gets one audit owner. --run-dir is only an override;
    # ordinary foreground calls use the project-local default.
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
        # Роль ушла отдельным каналом; без её длины manifest занижал бы объём
        # реально отправленной инструкции.
        "developer_instructions_chars": len(dev_instructions or ""),
        "codex": dict(codex_runtime),
        "runtime": {
            "sandbox": REVIEW_SANDBOX,
            "approval_mode": REVIEW_APPROVAL_MODE,
            "heartbeat_sec": args.heartbeat_sec,
        },
        "paths": paths,
    }
    write_json(run_dir / "manifest.json", manifest)
    (run_dir / "prompt.md").write_text(prompt_document, encoding="utf-8")
    append_event(run_dir, "validated", dry_run=args.dry_run, mode=args.mode)
    ledger = RunResult(
        run_dir,
        base={
            "run_id": run_id,
            "run_dir": str(run_dir),
            "dry_run": args.dry_run,
            "mode": args.mode,
        },
        codex_runtime=codex_runtime,
        paths=paths,
        prompt_chars=len(prompt),
        compact_keys=COMPACT_KEYS,
        summary_stdout=args.summary_stdout,
    )

    if args.dry_run:
        print(f"[codex-bridge dry-run] транскрипт={transcript_name} "
              f"промпт={len(prompt)} симв. режим={args.mode} "
              f"model={args.model} effort={args.effort} tier={args.service_tier or 'inherit'} "
              f"binary={codex_runtime['binary_source']} "
              f"run_dir={run_dir} "
              f"sandbox={REVIEW_SANDBOX} approval={REVIEW_APPROVAL_MODE}", file=sys.stderr)
        ledger.finish(
            status="validated",
            ok=True,
            event="done",
            # Dry-run валидирует CLI/prompt/реестр, но НЕ существование треда и
            # не создание нового — не выдаём сильных заявлений.
            extra={"resume_checked": False} if thread_persistent else None,
            event_fields={"dry_run": True, "ok": True},
        )
        if args.summary_stdout:
            return 0
        print(prompt_document)
        return 0

    # Гарантия биллинга через аккаунт: до импорта/запуска codex убираем API-ключи.
    removed = scrub_billing_env()

    try:
        from openai_codex import ApprovalMode, Codex, CodexConfig, Sandbox
        from openai_codex.generated.v2_all import ReasoningEffort
    except ImportError as exc:
        error = (
            "Пакет openai-codex не установлен. Активируй venv: "
            "experiments/codex-bridge/.venv (pip install openai-codex)."
        )
        ledger.finish(
            status="unavailable",
            ok=False,
            event="failed",
            extra={"error": f"{error} ({exc})"},
            event_fields={"status": "unavailable", "error": str(exc)},
        )
        print(error, file=sys.stderr)
        return 1

    # Дрейф движка ChatGPT.app под запиненным SDK: новые enum-значения в
    # ответах не должны ронять мост (см. codex_sdk_compat.py).
    harden_sdk_enums()

    print(
        f"[codex-bridge] режим={args.mode} транскрипт={transcript_name} "
        f"({len(transcript_md)} симв.) project={project_cwd} "
        f"model={args.model} effort={args.effort} tier={args.service_tier or 'inherit'} "
        f"binary={codex_runtime['binary_source']} "
        f"run_dir={run_dir} "
        f"sandbox={REVIEW_SANDBOX} approval={REVIEW_APPROVAL_MODE}"
        + (f" | вырезаны из env: {', '.join(removed)}" if removed else " | env чист"),
        file=sys.stderr,
    )
    append_event(
        run_dir,
        "codex_start",
        mode=args.mode,
        operation="thread_resume" if args.continue_thread else "thread_start",
        requested_thread_id=args.continue_thread,
    )

    config = CodexConfig(
        cwd=str(project_cwd),
        codex_bin=codex_bin,
    )
    started_monotonic = time.monotonic()
    progress = ProgressTracker()
    heartbeat_stop, heartbeat_thread = start_heartbeat(
        run_dir,
        args.heartbeat_sec,
        started_monotonic,
        thread_name="codex-review-heartbeat",
        snapshot=progress.snapshot,
        mode=args.mode,
    )
    try:
        with Codex(config) as codex:
            if args.continue_thread:
                thread = retry_start(
                    lambda: codex.thread_resume(
                        args.continue_thread,
                        cwd=str(project_cwd),
                        sandbox=Sandbox.read_only,
                        approval_mode=ApprovalMode.deny_all,
                        model=args.model,
                        service_tier=args.service_tier,
                        developer_instructions=dev_instructions,
                    ),
                    run_dir=run_dir,
                    operation="thread_resume",
                )
            else:
                thread = retry_start(
                    lambda: codex.thread_start(
                        cwd=str(project_cwd),
                        sandbox=Sandbox.read_only,
                        approval_mode=ApprovalMode.deny_all,
                        model=args.model,
                        service_tier=args.service_tier,
                        developer_instructions=dev_instructions,
                        ephemeral=codex_runtime["thread_ephemeral"],
                    ),
                    run_dir=run_dir,
                    operation="thread_start",
                )
            codex_runtime["thread_id"] = getattr(thread, "id", None)
            if args.continue_thread:
                event = {
                    "event": "continue",
                    "thread_id": args.continue_thread,
                    "run_id": run_id,
                    "run_dir": str(run_dir),
                    "at": utc_now(),
                    "session": _session_short(),
                }
                if args.continue_foreign:
                    # Усыновлённый тред должен получить тему — иначе доска
                    # покажет его следующему агенту безымянным.
                    event["topic"] = args.topic or _topic_from_payload(payload)
                _append_registry_event(project_cwd, event)
            elif args.dialog and codex_runtime["thread_id"]:
                topic = args.topic or _topic_from_payload(payload)
                # Тема уходит и в движок: персистентный тред виден в Codex
                # Desktop и в нативном thread/list, и без имени он там —
                # безымянный чат. Наш реестр остаётся владельцем связки
                # thread → run_dir, которой движок не знает.
                try:
                    thread.set_name(topic)
                except Exception as exc:  # noqa: BLE001 — имя не критично для хода
                    print(
                        f"[codex-bridge] имя треда не задано ({exc}); в реестре тема есть",
                        file=sys.stderr,
                    )
                _append_registry_event(project_cwd, {
                    "event": "start",
                    "thread_id": codex_runtime["thread_id"],
                    "run_id": run_id,
                    "run_dir": str(run_dir),
                    "created_at": utc_now(),
                    "topic": topic,
                    "session": _session_short(),
                })
            if thread_persistent:
                print(
                    f"[codex-bridge] thread_id={codex_runtime['thread_id']} "
                    f"(persistent; продолжение: --continue {codex_runtime['thread_id']})",
                    file=sys.stderr,
                )
                append_event(
                    run_dir,
                    "thread",
                    thread_id=codex_runtime["thread_id"],
                    persistent=True,
                )
            if args.mode == "diff":
                # НАТИВНЫЙ ревьюер движка (`review/start`), а не наш промпт:
                # у Codex для дифов есть выделенный режим со своим контрактом.
                # Высокоуровневого метода в SDK нет — зовём RPC и собираем
                # TurnHandle руками, чтобы переиспользовать поток, прогресс и
                # штатный interrupt.
                from openai_codex.api import TurnHandle  # noqa: PLC0415

                target = _review_target(args, payload)
                append_event(run_dir, "review_target", target=target)
                response = codex._client._request_raw(  # noqa: SLF001
                    "review/start",
                    {
                        "threadId": codex_runtime["thread_id"],
                        "delivery": "inline",
                        "target": target,
                    },
                )
                review_thread_id = response.get("reviewThreadId") or codex_runtime["thread_id"]
                turn_id = (response.get("turn") or {}).get("id")
                if not turn_id:
                    raise RuntimeError("review/start не вернул turn.id")
                codex_runtime["review_thread_id"] = review_thread_id
                handle = TurnHandle(codex._client, review_thread_id, turn_id)  # noqa: SLF001
            else:
                # turn() вместо run(): тот же ход, но с доступом к потоку
                # нотификаций — активность уезжает в ledger, heartbeat перестаёт
                # быть слепым. TurnResult собирает штатный сборщик SDK.
                handle = retry_start(
                    lambda: thread.turn(
                        prompt,
                        model=args.model,
                        effort=ReasoningEffort(args.effort),
                        service_tier=args.service_tier,
                        sandbox=Sandbox.read_only,
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
            extra={"error": str(exc)},
            event_fields={
                "status": "exception",
                "error": str(exc),
                "requested_thread_id": args.continue_thread,
            },
        )
        print(f"[codex-bridge] ошибка вызова Codex: {exc}", file=sys.stderr)
        return 1
    finally:
        heartbeat_stop.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=1)

    # Провалившийся ход сюда не доходит: штатный сборщик SDK поднимает
    # RuntimeError на TurnStatus.failed (`openai_codex/_run.py`
    # `_raise_for_failed_turn`), и приёмка идёт веткой except выше. Проверка
    # `result.error` остаётся дешёвой страховкой на error при НЕ-failed статусе
    # (interrupted, будущие статусы движка) — семантика та же, носитель один.
    result_error = getattr(result, "error", None)
    usage = getattr(result, "usage", None)
    status = codex_status_value(getattr(result, "status", "?"))
    completed = codex_turn_completed(status, result_error)
    print(
        f"[codex-bridge] статус={status} "
        f"время={getattr(result, 'duration_ms', '?')}мс usage={usage}",
        file=sys.stderr,
    )

    final_response = result.final_response or "[пустой ответ Codex]"
    if result_error:
        error = str(result_error)
    elif not completed:
        error = f"Codex turn did not complete (status={status})."
    else:
        error = None
    (run_dir / "final.md").write_text(final_response, encoding="utf-8")
    extra: dict[str, object] = {
        "duration_ms": getattr(result, "duration_ms", None),
        "usage": str(usage),
        "final_response": final_response,
    }
    if error:
        extra["error"] = error
    ledger.finish(
        status=status,
        ok=completed,
        event="done" if completed else "failed",
        extra=extra,
        event_fields={
            "status": status,
            "ok": completed,
            **({"error": error} if error else {}),
        },
    )
    if args.summary_stdout:
        return 0 if completed else 1
    if not completed:
        print(f"[codex-bridge] {error}", file=sys.stderr)
        return 1

    print(final_response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
