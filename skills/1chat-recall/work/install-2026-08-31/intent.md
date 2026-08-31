# Намерение corpus-only версии `1chat-recall`

Статус: `израсходовано`: этот черновик прошёл проверку потерь и установлен как
`versions/installed-2026-08-31/`. Состояние больше не маршрутизирует работу.

## Основание

- Владелец требует, чтобы обычный поиск читал только ранее записанные цитаты:
  `_ops/chat-recall/2026-08-29-150002-codex-01a04cf3.md:28`.
- Владелец одобрил предложенные `Цель` и `Уникальный контекст` и потребовал
  установить скил: тот же holder, `:30`.
- Предыдущий candidate и его verification остаются evidence сохранённой
  Capture/Retrieval/metadata функции:
  `skills/1chat-recall/versions/candidate-2026-08-31/` и
  `skills/1chat-recall/work/recheck-2026-08-30/verification.md`.

## FAST

- **Зачем:** будущий агент понимает применимую позицию владельца и продолжает
  работу без повторного расспроса.
- **Функция:** сохранять материальные слова в quote corpus и возвращать из него
  адресуемое evidence либо честный gap.
- **Как:** темы и два уровня контекста ведут к holder и цитате; выбранный holder
  читается целиком, когда решение зависит от сцены или chronology; более свежие
  слова и live owner ограничивают применимость.

## Commander's intent

### Цель

Помочь агенту восстановить применимую позицию владельца из ранее сохранённых
цитат и продолжить текущую работу без повторного расспроса. Если evidence
недостаточно или его применимость неясна — вернуть gap.

### Уникальный контекст

Корпус состоит из файлов сохранённых цитат: один файл на разговор. `topics.md`,
`session-context` и `context-note` помогают найти holder и цитату, но сами не
являются словами владельца. Сцена и chronology могут требовать чтения holder
целиком; поздние слова и live owner могут изменить прежнюю позицию. Обычный
поиск не читает native transcript Claude или Codex.

## Сохранённый протокол

> «они же должны читать мои цитаты из папки цитат, только те, которые до этого
> записали»

Capture продолжает полностью читать карту тем, выбирать существующую boundary
или создавать новую, обновлять полный `session-context` и писать короткий
keyword-like `context-note` одной атомарной операцией. Retrieval ищет quote
corpus и открывает выбранный holder, когда без сцены или порядка нельзя честно
применить цитату. Native transcript разрешён только отдельным явным owner
request на Repair/backfill named session и не заменяет пустой Retrieval.

## Проверка потерь

- **Сохранено:** topics map, new-topic, `session-context`, `context-note`,
  literal evidence, date/age, same-scope supersedes, full-holder reading,
  hybrid/lexical search, Capture и explicit Repair.
- **Поглощено commander's intent:** запрет raw transcript в обычном Retrieval.
- **Снято:** автоматическая доступность Repair/Validation по одному внутреннему
  решению агента; цена снятия отсутствует для обычного поиска, а explicit owner
  maintenance route сохранён.
- **Hard lines:** helper commands, atomic Capture, provenance, same-scope
  supersedes и explicit authority нельзя безопасно вывести только из цели.

Active set `SKILL.md`: 11 самостоятельных единиц. Capture: 20. Retrieval:
20–23 по условной ветке. Integrity: 10 для validation и до 20 только после
явного owner request на Repair.
