# Repairing and backfilling recall

Quote или selection — asset. Повреждённая metadata не оправдывает удаление,
сокрытие или переписывание owner evidence.

## Admission

Открывай этот route только для:

- repair уже существующей записи с diagnostics или сомнительным provenance;
- явного owner-запроса восстановить полезные тезисы из project/session,
  существовавших до применения `1chat-recall`.

Backfill не является обычным historical retrieval и не импортирует разговор
целиком.

Своя запись текущей сессии — не этот маршрут: её правит абзац самоисправления
в Capture, и repair-инварианты на неё не действуют.

## Scope

До чтения назови project и конкретную session либо ограниченный набор sessions.
Не угадывай соседний чат и не импортируй unrelated conversations.

Для каждого найденного сообщения заново примени usefulness gate. Сохраняй
только самостоятельные тезисы владельца, а не весь transcript.

## Evidence order

Для каждого тезиса или diagnostic:

1. native transcript указанной session;
2. exact unique text fragment в локальных Claude/Codex transcripts;
3. bounded semantic/manual search по локальной истории;
4. filename, frontmatter или raw time только в пределах того, что они прямо
   поддерживают;
5. `unknown`, если provenance не восстановлен.

Semantic match сам по себе не является exact evidence. Quotes не отправляются в
network tools.

Runtime-команду чтения session задаёт корневой `SKILL.md`. Codex использует
explicit `--repair-session`; Claude — explicit `--session-id`.

## Capture и chronology

Сохраняй исходный timestamp сообщения, а не время ремонта. Exact допускается
только после сверки native text или выбранной option.

Approximate запись получает явные `source`, `precision` и при необходимости
`source-ref`. Допустимы `exact`, `minute`, `date`, `unknown`.

Один session создаёт один holder. Имя файла, frontmatter date и заголовок
следуют самой ранней сохранённой source-date этой session.

`quote` остаётся deletion-only owner text. AskUserQuestion/Plan option —
`selection`. Agent-authored explanation — `note`. Malformed block остаётся
`raw`, пока его структура не восстановлена.

## Repair metadata

- Сохраняй один semantic type.
- Невосстановимый type — `неопределено`.
- Невосстановимый topic — `без-темы`.
- Repair sentinels не используются для свежей quote.
- Existing quote или selection не превращается в note ради sentinel.
- Duplicate holders объединяются только внутри одного project corpus и одной
  session.

## Mutation boundary

В read-only задаче покажи backlog и не переписывай corpus. При разрешённой
mutation сначала сохрани checksums и backup untracked originals вне scanned
corpus.

После repair/backfill докажи:

- multiset прежних texts/raw blocks не уменьшился;
- новые quotes существуют в native source;
- исходные timestamps и session сохранены честно;
- каждый record находится локальным поиском и открывается по exact file:line;
- diagnostics исправлены либо остаются явно видимыми;
- один project corpus содержит не более одного holder на session.
