# Retrieval

## Цель

Для одного решения вернуть evidence-backed position владельца либо `abstain`.

## Уникальный контекст

[chat_digest.py](../scripts/chat_digest.py) независимо ранжирует `topic_candidates`
из `topics.md` и `holders` из session/quote metadata; ни один маршрут сам не
является позицией. Запускай helper через `uv run --locked --script`. Выбранный
holder читается целиком, потому что отдельная цитата может быть уточнена поздними
словами или применимым live owner-ом.

## Ход

1. Сформулируй claim и выполни обычный hybrid поиск в target corpus.

   ```bash
   ROOT="${CLAUDE_SKILL_DIR:-$HOME/.claude/skills/1chat-recall}"
   TARGET_PROJECT_ROOT="${TARGET_PROJECT_ROOT:-$PWD}"
   uv run --locked --script "$ROOT/scripts/chat_digest.py" \
     "$TARGET_PROJECT_ROOT/_ops/chat-recall" --query "<claim>" --json
   ```

2. Сначала используй `holders`. Если выдача содержит только подходящие
   `topic_candidates`, выбери boundary по description и повтори поиск по его
   handle через `--query "<handle>" --topic "<handle>"`. Topic description —
   только маршрут, не owner evidence; его score не смешивается с holder score.
3. Если diagnostic говорит `hybrid runtime не подготовлен`, один раз выполни
   `--prepare` тем же helper-ом и повтори query; если bootstrap недоступен,
   используй `--lexical`. Открой каждый выбранный session holder целиком и прочти
   записи хронологически; затем расширяй поиск только тем, что может изменить
   ответ — различающей лексикой, поздними словами или live owner.
   Если hybrid queue не освобождается до ограниченного deadline, helper
   возвращает явную ошибку; не обходи очередь запуском dense-поиска.
4. Для важной темы после основного поиска запусти ровно одного дешёвого
   доступного фонового субагента через нативный механизм текущего runtime:
   в Claude запусти в фоне `Agent` с `subagent_type: general-purpose`, без
   `context: fork`, и явно выбери самую дешёвую доступную модель.
   Не жди его и продолжай исходную работу. В brief оставь read-only corpus-only
   независимый поиск по claim и выбранному handle; попроси вернуть только
   address, date, age и gaps. Его результат не есть position: при возврате сам
   снова прочти адресованные holders.
   Если дешёвый нативный субагент недоступен, не подменяй его дорогим:
   продолжай собственный поиск и назови этот gap.
5. Для каждой найденной цитаты сохрани в ответе абсолютную дату (`date`) и
   относительный возраст на момент поиска (`age`: часы или дни назад). В JSON и
   в человекочитаемом выводе эти поля обязательны, вместе с address. Если
   проверенная новая цитата в том же scope явно ссылается на старую через
   `supersedes`, и helper
   подтверждает совпадающую topic и более новый timestamp, обычный query
   возвращает новую как действующую позицию; `--timeline` может показать обе
   записи в хронологическом порядке. Не вытесняй цитаты из другого scope только
   из-за более поздней даты. `contested`, `note`, `raw` и записи без absolute
   timestamp не становятся decision position: верни `abstain`/`contested`, а
   диагностическую chronology оставь только в явном timeline/repair output.
   Затем верни position либо `abstain`, scope, date, addresses и gaps.
