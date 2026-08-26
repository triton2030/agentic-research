---
name: 1chat-recall
description: >-
  Use on correction, decision, criterion, preference, or boundary; before
  fresh-window decisions or later questions, durable artifacts, or work changes
  using prior words; for recall/repair. Skip assent.
---

# Chat recall

## Контекст

Слова владельца — датированное evidence, а не вечный профиль. Отдельный hit
может быть точным и уже отменённым; свежий разговор — лишь частично связанным,
но содержать актуальную коррекцию. Поэтому продукт retrieval — применимая
позиция для текущего claim, а не список похожих цитат.

Один holder хранит один разговор. Default-поиск отдельно отдаёт
`topic_candidates` по handle и коротким описаниям topic-файлов и до десяти
`holders` по `session-context` и цитатам. У holder-а видны полный
`session-context`, strongest quote и counts. Scores двух маршрутов не
смешиваются: агент выбирает полный topic либо короткую буквальную цитату, а
holder открывает только при нужной сцене или chronology.

Агент гарантированно читает тело, но может не открыть reference. Поэтому
обычные Capture и Retrieval полностью исполнимы отсюда. References — только
для наблюдаемого исключения: плохого coverage или ремонта повреждённой записи.

## Цель

Полезные слова владельца сохраняются в ходе высказывания, а перед существенным
решением прежняя позиция восстанавливается со сценой, scope, хронологией,
вытеснением и честными gaps. Если применимость не разрешена, результат —
`abstain`, а не уверенная догадка.

## Evidence

Записывай самостоятельный тезис, который вне соседних сообщений меняет будущее
решение, границу, критерий, предпочтение или понимание владельца. Служебное
согласие хода знания не несёт; в сомнении полезный тезис лучше сохранить.

- `quote` — буквальная речь владельца. Сокращение допустимо только
  вычёркиванием по источнику; удаление — только по его слову.
- `selection` — выбранный владельцем агентский вариант. Выбор не доказывает
  одобрение текста рядом.
- `context-note` — только внешняя сцена или референт одной записи, которых нет
  в самой цитате. Не пересказывай тезис и не расширяй его scope.
- `session-context` — однострочная поисковая карточка всего разговора: задачи,
  артефакты, операции, устойчивые имена и полезные синонимы через `;`. Это не
  позиция владельца и не summary решений.

Обычные понятия карточки пиши на языке проекта; устойчивое чужое имя оставляй
рядом как синоним (`мокап/mockup`), точные имена (`Next.js`, `BDR-002`) не
переводи. Scope по умолчанию — текущий проект; cross-project позиция требует
явных слов владельца. Живое слово владельца сильнее любой записи, а
расхождение остаётся видимым.

## Capture

Сначала реши, является ли новая реплика самостоятельным важным тезисом по
критерию Evidence выше. Если нет — не записывай и назови причину. Если да,
прочитай holder текущей сессии: тот же тезис второй раз не пиши, каждый новый
тезис сохраняй отдельно. Для `quote` и `selection` передай полную актуальную
`session-context`: сохрани прежние крупные предметы и добавь новый. В
`context-note` назови одно внешнее обстоятельство, которое исчезнет без
соседних сообщений.

```bash
ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"
SESSION="$CODEX_THREAD_ID"

# Для проекта со слоем topics выбери существующую тему по handle и описанию.
python3 "$ROOT/scripts/chat_capture.py" --list-metadata --project "$PWD"
python3 "$ROOT/scripts/chat_capture.py" \
  --quote "<слова владельца>" \
  --context-note "<сцена, не пересказ>" \
  --session-context "<задачи; артефакты; операции; имена и синонимы>" \
  --source-timestamp "$(date -Iseconds)" \
  --type <речевой-акт> --topic <долгоживущий владелец темы> \
  --agent codex --project "$PWD" --session "$SESSION" --json
```

Текущее время верно только для same-turn capture. Для прежней реплики бери
timestamp из native transcript; дату из воздуха не восстанавливай.
Если проект держит `_ops/chat-recall/topics/`, перед записью запусти
`--list-metadata`: он печатает канонические type и существующие темы с короткими
описаниями из topic-файлов. Выбирай тему из этого слоя; неизвестная тема требует
`--new-topic`. В raw-only проекте обычный capture принимает уже prefiltered
topic handle без inventory scan; широкую проверку тем запускай явно через
`--list-metadata`. Если предмет не принадлежит слою — и только тогда — создай
новую:
`--new-topic "<граница темы одним предложением>"` заводит вместе с записью
маленький файл темы. Имя — долгоживущий владелец предмета латиницей через
дефис; сперва убедись, что близкой темы нет. Выбранный вариант пиши с
`--kind selection`. Повторный capture с актуальной карточкой обновляет
`session-context` даже при уже существующей цитате.

Закрой ветку адресом записи и назови, что сохранено. Если записи нет, назови
причину: служебное согласие либо уже сохранённый тезис.

### Самоисправление метаданных текущей сессии

Если тот же `quote` или `selection` уже есть в session-файле, повторный capture
с полной актуальной `session-context` исправляет только этот frontmatter scalar.
`chat_capture.py` возвращает `context-updated`; текст owner-а, source timestamp,
kind, type и topic уже сохранённой записи не переписываются. Это маршрут
текущей сессии, не repair/backfill и не новый durable capture.

### Capture → Reconcile

В проекте с `_ops/chat-recall/topics/` после каждого нового durable capture
`quote`/`selection` с receipt `status: written` сразу прочитай target topic,
даже если он не был загружен; для `--new-topic` прочитай созданный stub. Raw уже
сохранён и остаётся evidence независимо от исхода темы.

Сравни новую реплику с текущими фактами темы. Если более свежие слова явно
конфликтуют с одним старым фактом в том же scope, замени именно этот факт новым
через typed `replace`; каждое `after` цитирует raw anchor. Новая деталь, второй
совместимый факт или усиление той же мысли конфликтом не являются: replace
нужен, только если старое и новое не могут одновременно быть истинны в одном
scope. Не добавляй в тему каждую новую цитату. Нет конфликтующего факта —
`acknowledge-noop`; неясны scope, commitment или chronology — `raw saved;
topic pending`, без догадки и без перетирания темы. Для
`already-present`/`context-updated` этот шаг не запускается.

```bash
python3 "$ROOT/scripts/topic_reconcile.py" acknowledge-noop \
  --project "$PWD" --topic "<receipt.topic>" \
  --session "<receipt.session>" \
  --record-sha256 "<receipt.record_sha256>" \
  --source-anchor "<receipt.anchor>"

PATCH="$(mktemp -t chat-recall-topic.XXXXXX.json)"
python3 "$ROOT/scripts/topic_reconcile.py" prepare \
  --project "$PWD" --topic "<receipt.topic>" --patch "$PATCH"
# Заполни один exact `replace`; новый fact цитирует raw anchor.
python3 "$ROOT/scripts/topic_reconcile.py" apply \
  --project "$PWD" --topic "<receipt.topic>" --patch "$PATCH" \
  --expected-sha256 "<prepare.expected_sha256>" \
  --session "<receipt.session>" --record-sha256 "<receipt.record_sha256>" \
  --source-anchor "<receipt.anchor>"
```

Если apply столкнулся с hash/scope/anchor конфликтом, не перетирай тему:
перечитай её и закрой исходом `raw saved; topic pending`. Локальный delta-path
не двигает batch/horizon.
Структурный отказ helper-а после `status: written` закрывается тем же
`raw saved; topic pending`: finding не заменяет исход ветки и не блокирует
основную работу.

**Recovery audit — отдельный режим.** Вход только при initial migration, заранее
заданном threshold backlog/suspect или disk drift (manifest/topic hash/raw
anchor/apply receipts). Тогда собери fresh disk-derived manifest (run-local)
прямо с диска из
`raw`, `topics` и receipts; детерминированно сгруппируй duplicate/suspect
clusters; зови модель только для conflict clusters; после machine gate проведи
одного pooled auditor и retry только failed topics. Manifest и accounting —
внешнее run evidence, не reader-facing topic; не запускай полный повтор корпуса
по умолчанию.

В разрешённые 20–30% потери качества входят stylistic polish, perfect
sectioning, weak distant-duplicate search и second opinions. Не торгуются:
raw immutability, exact anchors, typed coverage, current-only/no contradictions
и fail-closed apply.

## Retrieval

Сначала спроси корпус сам. Если тема важна и применимую позицию могли обсуждать
раньше, подключи ровно одного фонового субагента для независимого поиска. Его
можно вызвать в начале или позже, когда важность обнаружилась по ходу работы.
Не жди и не останавливай основной ход: собственного поиска обычно достаточно.
Когда субагент вернётся, учти его вердикт и новые адреса в следующем относящемся
к теме решении. Простой запрос, рабочий момент или уточнение отработай локально.

Ищи предмет claim-а, а не только имя артефакта: короткая естественная
формулировка должна описывать, о чём решение.

```bash
uv run --locked --script \
  "${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall/scripts/chat_digest.py" \
  _ops/chat-recall \
  --query "<короткая естественная формулировка предмета>" \
  --json
```

Corpus остаётся локальным: цитаты не отправляй в network tools.

Default возвращает два независимых списка и не смешивает их scores:
`topic_candidates` ищутся по handle и короткому описанию topic-файла, а
`holders` — по `session-context` и буквальным цитатам. Выбери маршрут по задаче:
прочитай полный topic-файл ради текущей тематической карты либо используй
`strongest_quote` и её address ради коротких буквальных слов владельца. Если
смысл цитаты зависит от сцены или chronology, открой её holder. Не пересчитывай
holder ranking по длине файла, числу цитат или counts type/topic; legacy-holder
без `session-context` остаётся видимым и может быть найден по цитатам.

`query_domain` — сырая близость ближайшей raw-записи до слияния quote-каналов;
он ничего не говорит о `topic_candidates`. `off-domain` означает слабый
quote-route, а не отсутствие подходящей темы. `in-domain` тоже не доказывает
наличие искомой позиции: вопрос о незаписанном правиле получает тот же вердикт,
что вопрос о записанном. `abstain` нужен, только если выбранные topic/quote
routes вместе не дают применимого evidence.

Owner evidence остаётся буквальная цитата; topic — производная current-only
карта. Списки кандидатов — варианты чтения, не очередь: открывай только то,
что нужно для текущего claim-а. Свежесть без связи с claim — шум.

Тема может содержать несколько claim-ов с разной лексикой. Coverage должен
охватить материальные фасеты, найденные в карточках и snippets, включая хотя
бы один запрос языком текущей задачи. Если обычная выдача пустая, чрезмерно
широкая, конфликтующая, усечённая или hybrid-route недоступен — прочитай
[reading-the-log](references/reading-the-log.md), чтобы получить bounded
recovery routes и честный coverage packet.

Перед применением выбранной цитаты всегда проверь более поздние слова: повтори
ту же команду с `--since <YYYY-MM-DD даты применяемого evidence>`. Если цитата
зависит от сцены или chronology — в том числе содержит признаки разворота вроде
«теперь», «вместо» или «больше не» — открой holder и разреши хронологию внутри:
поздняя реплика может отменять раннюю, а смена type часто обозначает разворот.
Самодостаточная цитата остаётся коротким маршрутом; полный holder не является
default. Прочитай найденное более новое evidence: исходная выдача его не
заменяет.

Итог ограничивай наблюдаемым coverage: более поздняя позиция найдена либо не
найдена в названных routes.
`truncated=true` не обесценивает уже возвращённые цитаты: он означает неполный
candidate set. Если невидимые candidates не могут изменить текущий claim,
назови gap и продолжай; иначе закрой ветку `abstain`.
Сверь применяемую позицию с `AGENTS.md`, `GOAL.md` и другим живым
project-local owner-ом; при расхождении
предъяви оба адреса, не выбирай молча. Соседняя задача может объяснять claim,
но не задаёт статус текущей.

Закрой ветку применимой позицией, scope, датой, адресами прочитанных topic,
quote или holder evidence, результатом later-check и оставшимися gaps.

## Repair

Повреждённая запись или явный запрос владельца восстановить докаптурную историю
→ прочитай [repairing-the-log](references/repairing-the-log.md), чтобы получить
native provenance, честную хронологию и integrity proof. Обычный historical
retrieval этим маршрутом не является.

## Завершение

Ход завершён, когда каждая активная ветка оставила проверяемый след:

- Capture → Reconcile — адрес raw и ровно один из `topic applied`,
  evidence-backed `acknowledge-noop` или `raw saved; topic pending`; metadata
  self-correction оставляет `context-updated` receipt;
- Retrieval — применимая позиция или `abstain`, адреса прочитанных topic/quote,
  later-check, scope и coverage gaps;
- Repair — восстановленный сигнал и proof provenance/chronology/structure либо
  точный blocker.

Список цитат, верхний hit, неполный holder, цитата без нужной сцены и непомеченный
агентский вывод результатом не являются.
