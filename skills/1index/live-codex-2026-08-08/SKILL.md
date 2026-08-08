---
name: 1index
description: >
  Используй при создании, обновлении или аудите корневого `INDEX.md`, а также
  когда по ходу другой работы обнаружился важный неочевидный owner, section или
  reading order: без отдельного gate эта дельта теряется либо INDEX становится
  деревом файлов и второй truth. Сохраняй только повторяемые или owner-backed
  reader intents, где маршрут меняет следующий ход cold-start agent.
---

# Intent Index

## Почему Здесь Нужен Отдельный Controller

Без скилла агент естественно начинает с видимого дерева: превращает папки и
owners в «намерения», добавляет правдоподобные ссылки и получает полный на вид
INDEX. Этот default разумен — filenames доступны раньше реальных reader jobs, а
lint и link check награждают структурную правильность. Но такой файл повторяет
root navigation, не сокращает discovery и может незаметно пересказывать truth.

Наблюдаемый tell: секцию можно восстановить из названий папок с той же ценой,
либо у неё нет конкретного ответа на вопрос «где cold-start agent ожидал искать
это и какой следующий ход изменится после ссылки». Поздняя полировка этот
провал не обнаруживает.

## Продуктовая Сцена И Мера

Текущая сессия находит навигационную дельту и передаёт её; будущая cold-start
сессия с тем же reader job открывает достаточный owner/section set в нужном
порядке, не повторяя уже оплаченный discovery. Для этого создай короткий root
`INDEX.md`, который отвечает: «для этой задачи что читать, в каком порядке и
зачем».

Главная мера — предотвращённый повторный поиск у следующего агента. Локальный
proxy — **сколько вероятных неверных или дорогих первых ходов предотвращает
каждая строка**, а не покрытие корпуса.

INDEX — неполный handoff/navigation cache. Linked owners сохраняют всю truth;
miss не доказывает отсутствие информации и переходит в live discovery.

## Controller: Докажи Дельту Маршрута

Допускай секцию только после двух независимых gates.

**1. Reader job устойчив.** Нужен хотя бы один источник:

- Founder явно назвал будущую работу;
- live GOAL/task/roadmap/backlog делает её текущей или ближайшей;
- тот же reader job либо retrieval friction наблюдался минимум дважды.

Формулируй intent действием исполнителя, а не зоной, типом файла или именем
команды. Agent-only прогноз не является evidence. Если сигнал неясен, исключи
затронутую секцию; задай один discriminating question только когда без него
нельзя построить полезный router вообще.

**2. Route delta наблюдаема.** До записи секции зафиксируй в рабочем черновике:

```text
reader job | ожидаемый route/first hop | фактический owner/section/order |
какой следующий read/action меняется
```

Хотя бы одна ссылка секции обязана содержать material mismatch в owner, section
или обязательном порядке. Пустое поле, очевидный route или только более
красивый порядок ссылок означает reject, даже когда сам intent реален. Это
proxy вместо самоотчёта «маршрут полезен».

После admission собери минимальный reading set:

- сохрани только ссылки, которые меняют следующий ход или необходимый порядок;
- ставь section anchor, когда дельта живёт внутри файла;
- ранжируй по важности для reader job; при равной важности используй
  `constraint → decision/owner → implementation/evidence`;
- к ссылке пиши действие — что там узнать, увидеть или сделать, — а не claim;
- добавляй alias только если он реально помогает найти intent под другой
  формулировкой;
- допускай очевидную ссылку лишь как необходимую ступень к неочевидной.

## Thought Demonstrations

**Default и anti-example.** Агент видит `docs/product.md`, `docs/ui.md` и
`apps/web/` и пишет секцию «Работаю над интерфейсом» с этим порядком. Форма
гладкая, ссылки валидны, но root navigation восстановит тот же set; route-delta
proof пуст. Секцию нужно удалить, а не снабдить ещё aliases.

**Переход.** В условном проекте повторяется работа с ценой. Cold-start agent
начнёт с money owner, но material eligibility constraint находится в разделе
cross-cutting rules. Intent допускается: money owner задаёт необходимый первый
шаг, затем exact section предотвращает вероятный пропуск. Роль ссылки говорит
«проверить eligibility constraint», не копирует само правило.

**Перенос.** При работе с тестами неожиданный fixture contract внутри большой
spec проходит тот же gate. Новая тема не требует нового правила: сохраняется
структура `ожидание → фактический section → изменившийся следующий ход`.

## Запись И Достижимость

Когда в любой разрешённой работе обнаружилась material route delta для
admitted reader job, обнови INDEX в той же работе, пока evidence и причина
неожиданности ещё в контексте. Это handoff, а не backlog. В read-only режиме
назови stale/missing route и продолжи через live discovery без молчаливой
правки.

Перед edit прочитай effective project instructions, существующую root
navigation, current goal и ближайших execution owners. Эквивалентный live
intent-router обновляй вместо второго INDEX. Известные bodies читай через
`1md-read`; неизвестный owner или section ищи через `1md-search`. Если эти
handles недоступны, используй эквивалентный bounded reader/search и не выводи
маршрут из filename или heading.

При записи либо аудите точной формы прочитай
[index-contract.md](references/index-contract.md): он владеет compact schema,
output pruning tests и root instruction pointer. Оставь один pointer в
effective root instruction chain каждого поддерживаемого runtime; если
placement неясен, не изобретай второй instruction owner.

Change/fix разрешает только scoped edits; проверяй dirty worktree по точному
target и не перезаписывай пересекающиеся чужие изменения.

## Authority И Feedback

INDEX разрешает intent, optional aliases, reading order, links/anchors и
короткое действие ссылки. Status, decision, numeric value, policy, product
promise и rationale остаются только у linked owner. Изменение owner content не
требует sync, пока маршрут не изменился.

Controller не сработал, если INDEX растёт по file categories, роли ссылок
пересказывают содержание, либо секции не могут показать material
`ожидание → реальность` mismatch. В таком случае повтори admission, а не
полируй schema.

## Evidence И Stop

Проверь отдельно:

- Markdown и package structure — live lint/validator;
- links и anchors — graph/link owner проекта;
- route behavior — один admitted non-obvious hit, один obvious reject и один
  safe miss с возвратом в live discovery;
- truth boundary — роль ссылки остаётся верной при изменении owner content без
  изменения маршрута;
- deletion — удаление каждой секции заметно повышает цену либо риск
  повторяемого discovery.

Не называй semantic перенос доказанным только по lint или заполненной schema.
Остановись на независимом полезном router: не расширяй ход до docs-system
refactor, owner migration или исправления всех найденных документов. Не создавай
INDEX, если evidence даёт только дерево файлов, уже есть эквивалентный live
router либо работа требует угадать material business truth.
