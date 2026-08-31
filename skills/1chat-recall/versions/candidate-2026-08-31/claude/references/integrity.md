# Integrity

## Цель

Диагностировать corpus или восстановить только доказанное evidence, не меняя
primary source и не создавая второй Capture-path.

## Уникальный контекст

[chat_digest.py](../scripts/chat_digest.py) диагностирует через
`uv run --locked --script`, а [chat_recall.py](../scripts/chat_recall.py) читает
runtime transcript через `python3`. Carrier, similarity и metadata сами не
доказывают owner authorship.

## Ход

1. Выполни strict validation target corpus и верни status, diagnostics и
   affected addresses.

   ```bash
   ROOT="${CLAUDE_SKILL_DIR:-$HOME/.claude/skills/1chat-recall}"
   TARGET_PROJECT_ROOT="${TARGET_PROJECT_ROOT:-$PWD}"
   uv run --locked --script "$ROOT/scripts/chat_digest.py" \
     "$TARGET_PROJECT_ROOT/_ops/chat-recall" --check --strict
   ```

2. Для named session/source через runtime `chat_recall.py --help` докажи literal
   text, прямое owner authorship и source address; иначе верни gap.
3. Доказанную единицу передай Capture как `capture-needed` с native timestamp,
   target project/session, source address и context clues.
4. Mutation требует отдельного явного owner request в текущем ходе; backup живёт
   вне corpus, raw/native source не меняется, затем повторяется validation.
