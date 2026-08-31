# Integrity

## Цель

Диагностировать corpus или восстановить только доказанное evidence, не меняя
primary source и не создавая второй Capture-path.

## Уникальный контекст

[chat_digest.py](../scripts/chat_digest.py) диагностирует сохранённый corpus через
`uv run --locked --script`. Только явно заказанный владельцем Repair или backfill
может читать named runtime transcript через
[chat_recall.py](../scripts/chat_recall.py) и `python3`; это не Retrieval и не
fallback пустого поиска. В Codex прямой ввод приходит как
`response_item.message` с `role: user`, `input_text` и `user.text`; helper
отбрасывает delegation-wrapper и любой non-human provenance marker. Carrier,
similarity и metadata сами не доказывают owner authorship.

## Ход

1. Выполни strict validation target corpus и верни status, diagnostics и
   affected addresses.

   ```bash
   ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"
   TARGET_PROJECT_ROOT="${TARGET_PROJECT_ROOT:-$PWD}"
   uv run --locked --script "$ROOT/scripts/chat_digest.py" \
     "$TARGET_PROJECT_ROOT/_ops/chat-recall" --check --strict
   ```

2. Только после явного owner request для named session/source через runtime
   `chat_recall.py --help` докажи literal text, прямое owner authorship и source
   address; иначе не читай transcript и верни gap.
3. Доказанную единицу передай Capture как `capture-needed` с native timestamp,
   target project/session, source address и context clues.
4. Mutation требует отдельного явного owner request в текущем ходе; backup живёт
   вне corpus, raw/native source не меняется, затем повторяется validation.
