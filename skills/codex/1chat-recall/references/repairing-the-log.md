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
3. bounded semantic/manual search по локальной истории, чтобы найти exact native
   record;
4. явный gap, если record не найден: filename, frontmatter, raw time и
   `unknown` не разрешают capture.

Semantic match сам по себе не является exact evidence. Quotes не отправляются в
network tools.

Реплики прежних ходов Codex-сессии читай локально:

```bash
ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"
python3 "$ROOT/scripts/chat_recall.py" read
```

Внутри runtime используй `search "<фрагмент>" --scope user` и `show <id>`;
repair чужой сессии требует explicit `--repair-session`.

## Capture и chronology

Сохраняй исходный timestamp сообщения, а не время ремонта. `exact` precision
допускается только после сверки native text или выбранной option — иначе
понижай до `minute` или `date`.

`chat_capture.py` принимает любую валидную precision (exact/minute/date);
`unknown` разрешён только для `--kind note`. Legacy approximate metadata старых
записей остаётся видимой диагностикой; writer её не создаёт, но добавляет новую
чистую запись в тот же holder — существующие грязные строки не переписываются.

Один session создаёт один holder. Имя файла, frontmatter date и заголовок
следуют самой ранней сохранённой exact/minute source-date этой session; запись
с precision `date` не двигает имя holder-а.

`quote` остаётся deletion-only owner text (копия горячего правила; правь
вместе). AskUserQuestion/Plan option — `selection`. Agent-authored explanation
— `note`. Malformed block остаётся `raw`, пока его структура не восстановлена.

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
