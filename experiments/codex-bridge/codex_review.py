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
  review               сторонний ревьюер хода работы (транскрипт + файлы)
  ask --question "..."  произвольный вопрос с транскриптом и файлами как контекстом

Транскрипт текущей сессии Claude Code находится автоматически
(CLAUDE_CODE_SESSION_ID → <id>.jsonl, иначе свежайший .jsonl проекта)
или задаётся явно через --transcript.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from cbcommon import scrub_billing_env

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


REVIEW_ROLE = """\
Ты — независимый старший инженер-ревьюер. Ниже транскрипт рабочей сессии другого
ИИ-агента (Claude Code) с пользователем. У тебя есть read-only доступ ко всем
файлам этого проекта — открывай и проверяй реальный код и документы, не верь
транскрипту на слово.

Дай стороннее ревью ХОДА РАБОТЫ:
- что упущено, какие риски и неверные допущения;
- где агент выбрал слабый подход и что было бы лучше;
- что проверить или переделать прежде, чем считать работу готовой.
Будь конкретным и опирайся на файлы. Не пересказывай транскрипт."""


def build_prompt(mode: str, transcript_md: str, question: str | None) -> str:
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
        f"===== ВОПРОС =====\n{question}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Вызвать Codex как ревьюера/консультанта из Claude Code.")
    parser.add_argument("--mode", choices=("review", "ask"), default="review")
    parser.add_argument("--question", help="Вопрос для режима ask.")
    parser.add_argument("--project", default=os.getcwd(), help="Корень проекта (по умолчанию cwd).")
    parser.add_argument("--transcript", help="Путь к .jsonl транскрипту (по умолчанию — автопоиск текущей сессии).")
    parser.add_argument("--model", help="Модель Codex (по умолчанию из ~/.codex/config.toml, обычно gpt-5.5).")
    parser.add_argument("--include-thinking", action="store_true", help="Включить блоки размышлений Claude в транскрипт.")
    parser.add_argument("--max-chars", type=int, default=200_000, help="Бюджет транскрипта; при превышении остаётся свежий хвост.")
    parser.add_argument("--dry-run", action="store_true", help="Собрать промпт и вывести его, НЕ вызывая Codex (не тратит кредиты).")
    args = parser.parse_args()

    if args.mode == "ask" and not args.question:
        print("Режим ask требует --question.", file=sys.stderr)
        return 2

    project_cwd = Path(args.project).expanduser().resolve()

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

    prompt = build_prompt(args.mode, transcript_md, args.question)

    if args.dry_run:
        print(f"[codex-bridge dry-run] транскрипт={transcript_path.name} "
              f"промпт={len(prompt)} симв. режим={args.mode}", file=sys.stderr)
        print(prompt)
        return 0

    # Гарантия биллинга через аккаунт: до импорта/запуска codex убираем API-ключи.
    removed = scrub_billing_env()

    try:
        from openai_codex import ApprovalMode, Codex, CodexConfig, Sandbox
    except ImportError:
        print(
            "Пакет openai-codex не установлен. Активируй venv: "
            "experiments/codex-bridge/.venv (pip install openai-codex).",
            file=sys.stderr,
        )
        return 1

    print(
        f"[codex-bridge] режим={args.mode} транскрипт={transcript_path.name} "
        f"({len(transcript_md)} симв.) project={project_cwd}"
        + (f" | вырезаны из env: {', '.join(removed)}" if removed else " | env чист"),
        file=sys.stderr,
    )

    config = CodexConfig(cwd=str(project_cwd))
    try:
        with Codex(config) as codex:
            thread = codex.thread_start(
                cwd=str(project_cwd),
                sandbox=Sandbox.read_only,
                approval_mode=ApprovalMode.deny_all,
                model=args.model,
            )
            result = thread.run(prompt)
    except Exception as exc:  # noqa: BLE001 — показать пользователю причину как есть
        print(f"[codex-bridge] ошибка вызова Codex: {exc}", file=sys.stderr)
        return 1

    if getattr(result, "error", None):
        print(f"[codex-bridge] Codex вернул ошибку: {result.error}", file=sys.stderr)
        return 1

    usage = getattr(result, "usage", None)
    print(
        f"[codex-bridge] статус={getattr(result, 'status', '?')} "
        f"время={getattr(result, 'duration_ms', '?')}мс usage={usage}",
        file=sys.stderr,
    )

    print(result.final_response or "[пустой ответ Codex]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
