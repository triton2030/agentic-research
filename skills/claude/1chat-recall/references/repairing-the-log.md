# Repairing and backfilling recall

Quote или selection — asset. Правила обращения с речью владельца и запрет
отправлять цитаты в network tools — `SKILL.md`, раздел «Слова владельца —
актив»; здесь только то, что добавляет ремонт: provenance, хронология и
доказательство целостности.

## Admission

Маршрут открывается для двух случаев и по названным заранее project и
конкретной session либо ограниченному набору sessions:

- repair уже существующей записи с diagnostics или сомнительным provenance;
- явный owner-запрос восстановить полезные тезисы из project/session,
  существовавших до применения `1chat-recall`.

Не сюда: обычный historical retrieval · соседний чат, который пришлось бы
угадывать · unrelated conversations · своя запись текущей сессии (её metadata
исправляется по разделу «Самоисправление метаданных текущей сессии» в Capture,
а repair-инварианты на неё не действуют).

Backfill не импортирует разговор целиком: к каждому найденному сообщению заново
применяется usefulness gate тела.

## Evidence order

Для каждого тезиса или diagnostic:

1. native transcript названной session;
2. exact unique text fragment в локальных Claude/Codex transcripts;
3. bounded semantic/manual search по локальной истории — чтобы найти exact
   native record;
4. явный gap, если record не найден.

Semantic match сам по себе exact evidence не является; filename, frontmatter,
raw time и `unknown` capture не разрешают.

Реплики прежних ходов Claude-сессии читай локально:

```bash
ROOT="${CLAUDE_SKILL_DIR}"
SESSION="${CLAUDE_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-}}"

python3 "$ROOT/scripts/chat_recall.py" --session-id "$SESSION"
```

Repair чужой сессии требует explicit `--session-id` этой сессии.

## Честная хронология

Сохраняй timestamp исходного сообщения, а не время ремонта (копия правила тела —
правь вместе). Precision выводится из формата `--source-timestamp`: ISO с
таймзоной → `exact`, ISO без неё → `minute`, `YYYY-MM-DD` → `date`, `unknown` —
только для `--kind note`. `exact` допустим только после сверки с native text или
выбранной option.

Знай цену огрубления: writer не сериализует precision, поэтому любая не-exact
запись читается валидатором как `unmarked-approximate`, а naive ISO — ещё и как
`timezone-missing`. Чистую запись даёт только timezone-aware ISO; несверенное
время всё равно огрубляй, но диагностику назови в отчёте, а не оставляй молча.

Имя файла, frontmatter date и заголовок holder-а следуют самой ранней
сохранённой source-date этой session и меняются вместе. Сама по себе запись с
precision `date` rename не запускает, но уже сохранённая date-запись войдёт в
минимум и сдвинет holder при следующем exact/minute capture — проверяй имя после
записи.

Writer переиспользует holder только для точной пары `(agent, session)`:
различие `codex`/`Codex` или смена agent создают второй holder. Уникальность
session по корпусу — забота validator-а, и сейчас она нарушена, так что дубли
ищи прогоном, а не предположением.

## Repair metadata

Сохраняй один semantic type. Невосстановимый type — `неопределено`,
невосстановимый topic — `без-темы`. Repair sentinels не ставятся свежей quote, и
existing quote или selection не превращается в note ради sentinel. Duplicate
holders объединяются только внутри одного project corpus и одной session.

## Mutation boundary

В read-only задаче покажи backlog и corpus не переписывай. При разрешённой
mutation сначала сохрани checksums и backup untracked originals вне scanned
corpus.

После repair/backfill докажи целостность:

- multiset прежних texts и raw blocks не уменьшился;
- новые quotes существуют в native source;
- исходные timestamps и session сохранены честно;
- каждый record находится локальным поиском и открывается по exact file:line;
- diagnostics исправлены либо остаются явно видимыми;
- один project corpus содержит не более одного holder на session.

Недоказуемая целостность — не повод закрыть ветку молча: точный blocker —
что именно не сходится и на каком record, если record существует, — допустимое
завершение ремонта.
