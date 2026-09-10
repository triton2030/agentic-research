---
description: "Semantic owners and projection contracts for cross-runtime skills."
---

# Shared Skill Owners

Эта папка владеет пакетами, у которых переносимый смысл и runtime-дельты
должны меняться как одно целое. Она не является третьим installed runtime.

## Живые Owners

- `1agent-steering/portable/` — общий скилл знания: полное чтение науки
  управления агентами и объяснение её применения при авторинге. Материал —
  `references/steering-science.md`; потребители — `1skill-creation`,
  `1instruction-authoring`, `1plan-map`, `1plan-task`, `1goal`. Codex metadata
  живёт в `platforms/codex/agents/openai.yaml`.
- Семья авторинга — пять скилов по различимым моментам запуска, заменили пару
  `1skill-shaping` + `1instruction-shaping`, снятую 2026-08-26 (архивы в
  `skills/1skill-shaping/` и `skills/1instruction-shaping/`; решение владельца —
  `_ops/chat-recall/raw/2026-08-26-201025-claude-4e40828f.md#L15`):
  - `1instruction-authoring/portable/` — создание и переписывание агентных
    инструкций проекта (v12, 2026-09-02). Функция — предотвратить критичный
    конфликт: доставить в точку работы правду, которую сильная модель по
    привычке нарушит и из этой точки не увидит. Форма: Уникальный контекст,
    Задача, Цель, Критерии принятия; тело — трёхшаговый роутер, единиц 6.
    С v12 критерий 1 требует у каждой единицы слоя причину её нарушения, а
    правило «Содержимое старше строки» запрещает писать и усиливать
    инструкцию, которой противоречат код или документы зоны, и отсылает
    повторившееся нарушение в `1context-refactor` (решение владельца
    2026-09-02, `_ops/chat-recall/2026-09-02-151925-claude-0c84f259.md#L24`
    и `#L28`).
    Обе стадии держатся Задачей, Целью и Критериями принятия:
    `references/discovery.md` (обнаружение критичного вычитанием привычки агента
    из правды проекта, семь вопросов зоны, 11 единиц, 5 критериев),
    `references/writing.md` (адресат обязательства, размещение, форма единицы,
    бюджет головы зоны, 17 единиц, 4 критерия) и `agents/zone-reader.md` (веерное чтение
    папок с возвратом заявленных в тексте связей и механизмов, 8 единиц).
    У обязательства есть адресат помимо строки: цель зоны, её критерий или
    механизм проекта — по доктрине
    `science/how-to-command-with-goal-not-procedure.md`. Цель зоны пишется
    Maintain-целью по KAOS и проверяется отрицанием на пустоту, критерий —
    только контрмерой названному препятствию.
    Бюджет считает не файл, а голову агента в зоне: корневая инструкция плюс
    папочная плюс протокол скила, к которому зона отсылает; сумма называется
    числом и предъявляется владельцу, а не подгоняется. Причинной пробы пакет не
    содержит — решение владельца 2026-08-31; `references/verification.md` и
    `agents/zone-scout.md` сняты, история — в
    `skills/1instruction-authoring/cut.md`;
  - `1context-refactor/portable/` — рефактор контекста: мета-анализ прошедшего
    диалога — найти шероховатости (лишнее чтение, переделки, долгая работа),
    установить причину, чинить настоящего виновника (инструкции, документ,
    скил, слова владельца); весь переносимый контракт теперь помещается в
    `SKILL.md`. С 2026-09-02 контекст скила называет, что содержимое зоны
    сильнее инструкции, а ремонт файла инструкций отдаёт `1instruction-authoring`
    (`_ops/chat-recall/2026-09-02-151925-claude-0c84f259.md#L28`);
  - `1skill-creation/portable/` — создание, рефактор и кнопка запуска скилов.
    С 2026-09-08 тело служит примером семи условных наборов знаний и инструкций.
    Порядок: Контекст → Задача → необходимые Критерии принятия → Цель → условия.
    Контекст передаёт неизвестный мир; критерии добавляют невыводимые уточнения;
    Цель работает как главный принцип выбора при неопределённости и конфликте.
    Важность и сложность решения оправдывают отдельный случай активации.
    Намерение — `references/goal-context.md`, допуск дополнительного содержания —
    `behavior-protocol.md`, границы режимов — `reference-files.md`, вызов —
    `skill-short-description.md`. `refactor.md` восстанавливает намерение и
    проверяет потери; `check-approve.md` использует две независимые роли;
    `install-approved.md` отвечает за точную доставку. Продуктовая правда —
    `1skill-creation/product-frame.principles.md`; история — `skills/1skill-creation/`.
  У каждого `platforms/codex/agents/openai.yaml` — только Codex UI metadata.
  Reference-файл живёт ровно у одного владельца; соседи ссылаются относительно.

- `1md-search/portable/` — общий cognitive/tool core для
  Codex и Claude; `platforms/codex/agents/openai.yaml` — только Codex UI и
  invocation metadata. Сосед `1md-read` снят 2026-08-22 по решению владельца,
  архив в `skills/1md-read/`.
- `1deep-agents/portable/` — общий framework-routing, trace и synthesis
  contract; runtime launch deltas для Codex `spawn_agent` и Claude `Agent`
  живут в одной адресуемой reference, а Codex UI metadata — в
  `platforms/codex/agents/openai.yaml`.
- `1readable-code/portable/` — общий стратегический pre-code контекст для
  Claude и Codex; `platforms/codex/agents/openai.yaml` содержит только Codex UI
  metadata.
- `1orchestration` с 2026-09-06 имеет два runtime owners:
  `skills/codex/1orchestration/` — выбор фоновых Luna Max, Opus и собственных
  субагентов ради скорости, стоимости и качества; поглотил `1codex-bg-threads`.
  `skills/claude/1orchestration/` — основное исполнение через отдельный `1codex`,
  дешёвые собственные агенты и собственные Opus для аудита; та же рабочая память.
  Общий portable owner снят; установка
  обоих пакетов — `sync_simple_projections.py 1orchestration --write --install`.
  С 2026-09-02 поручение несёт причину результата и причину у каждой строки
  дельты (`_ops/chat-recall/2026-09-02-151925-claude-0c84f259.md#L25`).
- `1local-rules/portable/` — общая локальная дельта для project-local `2*`
  скилов Claude и Codex; `platforms/codex/agents/openai.yaml` содержит только
  Codex UI metadata.
- `1product-shaping/portable/` создаёт чистые Product Principles + Frame и
  журнал обоснований; `1use-principles/portable/` применяет их к развилкам и
  пустотам.
- Семья планирования — тройка по моментам запуска, раскроена 2026-08-26 из
  монолита `1planning` (решение владельца —
  `_ops/chat-recall/raw/2026-08-26-220614-claude-4ee6bbef.md`; карта раскройки
  и снимок — `skills/1planning/`):
  - `1planning/portable/` — страж и когнитивный протокол в чате: любая мысль
    «что дальше», спор о допуске задачи, доказанная пошаговая декомпозиция по
    книжным методикам до любых план-файлов; владеет router-ом и стадиями
    опоры, допуска, среза, режима, контекста и утверждения;
  - `1plan-map/portable/` — эпики и верхний уровень проекта: рамки и принципы
    до состава, карта от GOAL, дашборд Obsidian; владеет формой и состоянием
    эпика, словарём/frontier, structural/state validation, независимой
    приёмкой и bootstrap/update дашборда;
  - `1plan-task/portable/` — изолированность задач: файл задачи как промпт
    для чужого окна; пять критериев принятия (лазейки закрыты проверкой,
    цитаты адресом до строки, бюджет 20, состояние тем же ходом, цель не
    переписывается) вместо инструкций; владеет схемой и шаблоном файла,
    размещением, бюджетом, state/lifecycle и closure.
  - С 2026-09-09 у эпика и задачи раздел и поле «Основания» (адреса GOAL,
    утверждённых решений в `_docs` и слов владельца) вместо «Канон»; чекер
    читает прежнее имя как legacy, существующие планы не мигрировались.
    Снимок эпика сохраняет прежний payload-ключ, поэтому записанные снимки
    живых задач не обесценены. Версии — `versions/installed-2026-09-09/`,
    тесты против живого owner — `skills/1plan-map/work/grounds-2026-09-09/`.
- `1smart-simple` — tracked owner отсутствует; живые пакеты
  `~/.claude/skills/1smart-simple/` и `~/.codex/skills/1smart-simple/` —
  единственная правда (v4, 2026-09-06; история — `skills/1smart-simple/`).
  На него маршрутизируют `1skill-creation/reference-files.md` (случай проверки
  нагрузки), `1instruction-authoring/writing.md`,
  `1document-system/overgrown.md` и `1plan-task` (C3).
- `1folder-tree/portable/` — дом, имя и проверка дерева базы документов
  проекта: карта владельца и источник сборки для агента. Установлен
  2026-09-09 из внешнего пакета `kb-tree.skill` с переименованием по решению
  владельца; триггер — русские фразы владельца «дерево папок»,
  «информационная архитектура», «куда положить файл», «как назовём папку»,
  «в какой папке что должно храниться»
  (`_ops/chat-recall/2026-09-09-165057-claude-code-ad6a2458.md#L18`).
  2026-09-10 — полный рефактор по `1skill-creation` вместе с `1docs-write`
  (история и карта потерь — `skills/1folder-tree/`): два критерия «Критично» —
  ни одна папка не смешивает файлы и подпапки (`/Users/triton/Documents/My_projects/mavo3/_ops/chat-recall/2026-09-10-125652-claude-code-c2a5de2f.md#L20`), имя файла — сторона
  вещи, имя папки — вещь словами владельца; три критичные инструкции (сначала
  `AGENTS.md` базы; любое движение существующего — предложение владельцу; дом и
  имя здесь, текст внутри файла — `1docs-write`); пять наборов по моменту
  применения. Проектное — корень, язык имён, полки, роли, планы и цель —
  объявляет `AGENTS.md` базы. Утверждено владельцем и установлено 2026-09-10
  (`_ops/chat-recall/2026-09-10-135753-claude-code-c2a5de2f.md#L22`). Парные примеры — `references/`;
  `platforms/codex/agents/openai.yaml` — только Codex UI metadata.
  Потребитель — `1docs-write` (дом, имя, отсылки).
- `1index/portable/` держит карты оплаченных поиском маршрутов.
- `1interview-tool/portable/` создаёт адресуемую plain-Markdown форму и держит
  lifecycle `решения владельца → настоящие owners → архив`; Codex invocation
  metadata живёт в `platforms/codex/agents/openai.yaml`.
- `1document-system/portable/` — запись долгоживущего в документы проекта: где
  живёт ответ, каким деловым типом он назван и что вообще считается
  установленным. Пакет — тело плюс четыре стадии по состоянию дома
  (`existing-home`, `new-home`, `derivative`, `overgrown`): агент читает тело и
  стадию своего случая, а не все требования сразу. С 2026-09-02 связь решённого с
  его причиной и соседями держат метаданные документа, а не проза в теле
  (`_ops/chat-recall/2026-09-02-151925-claude-0c84f259.md#L27`).
- `1md-search/portable/` — общий cognitive/tool core для
  Codex и Claude; `platforms/codex/agents/openai.yaml` — только Codex UI и
  invocation metadata. Сосед `1md-read` снят 2026-08-22 по решению владельца,
  архив в `skills/1md-read/`.
- `1deep-agents/portable/` — общий framework-routing, trace и synthesis
  contract; runtime launch deltas для Codex `spawn_agent` и Claude `Agent`
  живут в одной адресуемой reference, а Codex UI metadata — в
  `platforms/codex/agents/openai.yaml`.
- `1readable-code/portable/` — общий стратегический pre-code контекст для
  Claude и Codex; `platforms/codex/agents/openai.yaml` содержит только Codex UI
  metadata.
- `1orchestration` с 2026-09-06 имеет два runtime owners:
  `skills/codex/1orchestration/` — выбор фоновых Luna Max, Opus и собственных
  субагентов ради скорости, стоимости и качества; поглотил `1codex-bg-threads`.
  `skills/claude/1orchestration/` — основное исполнение через отдельный `1codex`,
  дешёвые собственные агенты и собственные Opus для аудита; та же рабочая память.
  Общий portable owner снят; установка
  обоих пакетов — `sync_simple_projections.py 1orchestration --write --install`.
- `1local-rules/portable/` — общая локальная дельта для project-local `2*`
  скилов Claude и Codex; `platforms/codex/agents/openai.yaml` содержит только
  Codex UI metadata.
- `1product-shaping/portable/` создаёт чистые Product Principles + Frame и
  журнал обоснований; `1use-principles/portable/` применяет их к развилкам и
  пустотам.
- Семья планирования — тройка по моментам запуска, раскроена 2026-08-26 из
  монолита `1planning` (решение владельца —
  `_ops/chat-recall/raw/2026-08-26-220614-claude-4ee6bbef.md`; карта раскройки
  и снимок — `skills/1planning/`):
  - `1planning/portable/` — страж и когнитивный протокол в чате: любая мысль
    «что дальше», спор о допуске задачи, доказанная пошаговая декомпозиция по
    книжным методикам до любых план-файлов; владеет router-ом и стадиями
    опоры, допуска, среза, режима, контекста и утверждения;
  - `1plan-map/portable/` — эпики и верхний уровень проекта: рамки и принципы
    до состава, карта от GOAL, дашборд Obsidian; владеет формой и состоянием
    эпика, словарём/frontier, structural/state validation, независимой
    приёмкой и bootstrap/update дашборда;
  - `1plan-task/portable/` — изолированность задач: файл задачи как промпт
    для чужого окна; пять критериев принятия (лазейки закрыты проверкой,
    цитаты адресом до строки, бюджет 20, состояние тем же ходом, цель не
    переписывается) вместо инструкций; владеет схемой и шаблоном файла,
    размещением, бюджетом, state/lifecycle и closure.
- `1index/portable/` держит карты оплаченных поиском маршрутов.
- `1interview-tool/portable/` создаёт адресуемую plain-Markdown форму и держит
  lifecycle `решения владельца → настоящие owners → архив`; Codex invocation
  metadata живёт в `platforms/codex/agents/openai.yaml`.
- `1document-system/portable/` — письмо и существенная правка одного документа
  проекта: стандартное деловое имя типа как адрес, жанровая дисциплина и
  вытеснение замещённого вместо дописывания рядом (v2, 2026-09-01; v1 из 24
  файлов снят, снапшот — `skills/1document-system/v1-2026-08-09/`). Пакет — два
  файла: тело и `references/type-selection.md`, который открывается только
  тогда, когда тип документа корпусом ещё не задан. Имена типов, разделы и
  метаданные уступают живому реестру проекта, жанровые запреты — никогда.
  `platforms/codex/agents/openai.yaml` — только Codex UI metadata.
- `1docs-write/portable/` — запись одного знания о продукте в базу
  документов: статус по словам владельца (`1chat-recall`), дом по
  `1folder-tree`, тело только знание, происхождение в сносках. С 2026-09-09
  `_docs` — единственный дом продуктовой правды рядом с GOAL: слой `_canon` и
  скил `1canon-write` сняты
  (`_ops/chat-recall/2026-09-09-111723-claude-code-571bf7e3.md#L17`; снятый
  пакет — `skills/1canon-write/`). 2026-09-10 — полный рефактор по
  `1skill-creation` вместе с `1folder-tree` (история — `skills/1docs-write/`):
  три критерия «Критично» — тело в двух режимах (знание целиком либо знак
  пробела, объявленный `AGENTS.md` базы, например `[!question]`), в теле нет
  состояния проекта, предложения агента и расхождения с кодом только в чат
  (`/Users/triton/Documents/My_projects/mavo3/_ops/chat-recall/2026-09-10-125652-claude-code-c2a5de2f.md#L27`, `#L29`–`#L32`; P-008 в `skills/1docs-write/product-frame.principles.md`);
  три критичные инструкции (не пересказывай скил; свежее слово владельца
  сначала в корпус; код — свидетельство о реализации, не источник намерения);
  семь наборов по моменту применения; один reference «разбор старого
  документа» вместо трёх прежних режимов; `scripts/doc_map.py` выводит карту
  description и aliases без записи. Дешёвые после кода детали для сборки —
  в документ решением владельца 2026-09-10 (`/Users/triton/Documents/My_projects/mavo3/_ops/chat-recall/2026-09-10-125652-claude-code-c2a5de2f.md#L38`, снимает решение
  2026-09-05 `…cfb9aa25.md#L21`). Утверждено и установлено 2026-09-10
  (`_ops/chat-recall/2026-09-10-135753-claude-code-c2a5de2f.md#L22`). `platforms/codex/agents/openai.yaml` — только Codex UI metadata.

`skills/codex/<name>/` и `skills/claude/<name>/` — tracked projections owner-а.
`~/.codex/skills/<name>/` и `~/.claude/skills/<name>/` — installed projections
следующего уровня. Их не редактируют напрямую.

## Product Owners

`1chat-recall/`, `1handoff/` и `1hermes/` владеют только общей продуктовой
правдой `product-frame*.md` — Frame и, где она уже существует, Principles.
Они не становятся source owner-ами runtime package и не входят в projection
sync. Поведение остаётся у tracked или live `SKILL.md`; при расхождении product
intent и runtime нужен явный reconcile, а не копия пары в оба runtime.

**Их runtime-деревья расходятся намеренно, и файлы между ними не копируются.**
У `1chat-recall` различаются `allowed-tools`, переменные сессии, пути запуска,
имя агента, раздел «Психолог» тела и Контекст роли `agents/psychologist.md`
(субагент сессии в Claude, тред проекта в Codex) — а тесты сверяются с этими
строками. Правь оба дерева руками:
2026-08-28 копирование tracked-теста из `skills/claude/1chat-recall/` в
`skills/codex/` уронило два контрактных теста и стёрло codex-специфичные
проверки.

Runtime `1hermes` с 2026-08-22 tracked: `skills/claude/1hermes/` и
`skills/codex/1hermes/` — owner-ы своих семей, установленные пути стали
симлинками. Общего portable-ядра у них нет и не планируется: копии расходятся
намеренно (`--isolated` только у Claude, `agents/openai.yaml` только у Codex),
поэтому правку кода вноси в обе руками, а не через sync.

## Синхронизация

После правки source owner-а передай имена изменённых пакетов позиционными
аргументами. Например, для текущей группы:

```bash
python3 skills/shared/sync_simple_projections.py \
  1product-shaping 1use-principles 1planning 1index --write --install
python3 skills/shared/sync_simple_projections.py \
  1product-shaping 1use-principles 1planning 1index --check
```

Generic script собирает все portable files и непересекающуюся runtime delta.
Он отказывается удалять unexpected projection files: их provenance сначала
разрешается явно.

Special-manifest скрипт `1skill-architect/sync_projections.py` вышел из
обращения вместе со скилом; он лежит в
`skills/1skill-architect/shared-owner-2026-08-08/`.

Special-manifest скрипт копирует явный manifest и удаляет только названные
obsolete runtime-файлы. Неизвестные лишние файлы он не удаляет: `--check`
останавливается, чтобы projection не стала скрытым вторым owner-ом.
