# Planning Surface Ownership Criteria

## Зона ответственности

Когда работа меняет README, `_ops/PROJECT-ROADMAP.md`, `_ops/plans/**`,
stage/task model или связь между strategy, roadmap и task surfaces.

## Цель

Planning surfaces отражают текущий режим проекта: polygon by default, staged
planning только когда он реально выбран, и каждый слой держит свою функцию.

## Критерии

Rule: В этом repo instructions не делают roadmap, stages или task list обязательным маршрутом обычной работы.
Why: Проект работает как полигон: движение начинается от текущей просьбы, knowledge и релевантных criteria.

Rule: `_ops/GOAL.md` держит outcome-first контракт проекта (что делаем, in scope, NOT in scope, definition of done, stop rules); корневой `README.md` — короткий контекст и reader on-ramp; `_ops/PROJECT-ROADMAP.md` переводит выбранную рамку в текущий режим движения.
Why: User signal: стратегический скил должен быть хранителем основной цели через `_ops/GOAL.md`, README больше не главный strategy-документ а контекстный файл; roadmap не должен становиться полной стратегией или дублировать GOAL.

Rule: `1strategy` владеет **momentum decision-thinking при выполнении задач** (approach-choice в моменте конкретной работы, варианты, goal-alignment check, mental tools, ground-check для частной задачи, обсуждение raw desire подхода) и автоматически срабатывает на «думать про стратегию» / «думать стратегически» — даже в автономной работе перед нетривиальной развилкой. Использует existing GOAL как context; файлов не пишет. `1strategy-docs` владеет **thinking + writing** трёх strategy документов: goal-formation, scope, definition of done, stop rules, project charter shape (`_ops/GOAL.md`), README narrative (`README.md`), ROADMAP shape (`_ops/PROJECT-ROADMAP.md`). Goal-formation — internal work, не делегируется в `1strategy`. Mental tools — shared toolkit, canonical home в `1strategy/references/internal-tools.md`, оба скила читают через явный path. `1planning` владеет recursive planning content: `_ops/PROJECT-ROADMAP.md` content updates (current path сдвинулся, Stage closed), `_ops/plans/**/task-*.md` и подшаги внутри task-файла.
Why: User signal (2026-05-18): пользователь явно попросил разделить старый `1strategy` на два скила. User signal (2026-05-19, revision): первоначальный split (thinking-vs-commit) leaked ownership — `1strategy-docs` владел файлом GOAL, но мышление в этот файл шло из `1strategy`. Пользователь поднял проблему: «скил стратегии это скил при любой стратегической мысли или обсуждении, который тригерится моментно и часто, он использует цель при разговорах о стратегии но не должен писать, а вот решать что такое цель думать о цели и формировать её должен скил стратегических документов». Пересмотрено на document-level ownership (DDD bounded contexts): artifact-owner владеет и мышлением, и записью. Это лечит ownership leak и shallow abstraction: `1strategy-docs` теперь deep document-driven thinker для goal-formation, `1strategy` — momentum decision-thinking при выполнении задач. Mental tools остаются shared toolkit с canonical home в `1strategy/references/`. Roadmap shape остаётся у `1strategy-docs`; content updates по-прежнему у `1planning`.

Rule: `1planning` сужает фокус постепенно: Level 1 roadmap/current path -> Level 2 task files -> Level 3 subtasks, не раскрывая всё возможное дерево заранее.
Why: User signal: в проекте может быть 10 фаз, в каждой 10 задач, в каждой 10 подзадач; полное раннее раскрытие создаёт 1000 stale задач вместо управляемой рекурсии.

Rule: `1planning` использует `1ia-audit`, когда планирование меняет форму задач, фаз, файлов, папок, workstream, knowledge area, owner truth, retrieval path или future-growth structure.
Why: User signal: IA-аудит важен для планирования не только в Markdown, потому что план сам материализует информационную архитектуру будущей работы.

Rule: Аудит качества декомпозиции внутри `1planning` живёт как requested ref-mode: по запросу он готовит clean-context субагентов с planning contract и релевантной экспертной линзой.
Why: User signal: пользователь хочет вызывать одного или много параллельных агентов, чтобы они особенно усердно проверяли качество roadmap/task/subtask разбиения без смешивания с основным окном.

Rule: `_ops/plans/**` используется только по явному запросу для активной сложной работы.
Why: В polygon-режиме task-файлы не являются backlog или активным списком задач.

Rule: В `_ops/plans/` и каждой папке внутри неё должна быть `_archive/` для неактивных task-файлов и plan-веток.
Why: User signal: задачи не всегда закрываются; если верхний слой изменился, старый нижний слой надо архивировать, чтобы он не управлял работой по инерции. В staged mode каждая stage folder обязательна и должна иметь свой `_archive/`; в polygon mode папки создаются лениво, но как только папка создана — `_archive/` обязателен.

Rule: Выполненные task/plan-файлы уходят в `_ops/plans/_archive/` или ближайший `_archive/` только после проверки фактического закрытия; если архивной папки нет, её создают перед переносом.
Why: User signal: активные plans должны показывать живую работу, а архив нужен, чтобы полезная информация из выполненных планов не исчезала и не превращалась в обязательное чтение.

Rule: Старые task-файлы нельзя использовать как текущее направление без явного пользовательского сигнала.
Why: Исторические task-файлы возвращают старую roadmap-модель.

Rule: Когда проект работает по стадиям, task-файлы выходят из `_ops/PROJECT-ROADMAP.md`: Stage, current mode или current path становятся якорем задачи. **Class-rule:** каждая Stage в `## Stages` chain ROADMAP materializes как отдельная папка `_ops/plans/<stage-slug>/` с собственным `_archive/`; task-файлы этой стадии живут только внутри её папки, не в корне `_ops/plans/`. Polygon-mode проект (нет `## Stages` chain в ROADMAP) использует domain-anchored folders или flat task в корне `_ops/plans/`. Lazy-vs-mandatory зависит от mode: в staged mode stage folder обязательна; в polygon mode папки создаются лениво.
Why: User signal: «задачи всегда выходят из дорожной карты. И если меняется дорожная карта, то задачи тоже должны поменяться». User signal (2026-05-19): «каждая стадия должна быть отдельной папкой задач» — закрепляет class-rule mapping Stage → folder. Cross-stage task — сигнал что либо stage shape неверный, либо task на самом деле два. Если Stage переименован/split/merged, stage folder переименован/split/merged до continuing execution.

Rule: Если roadmap edit меняет outcome, scope, NOT in scope, stop rules или подход — это работа `1strategy-docs` (он думает goal-formation internal работой и пишет GOAL/README/ROADMAP shape, не делегируя thinking в `1strategy`). Если меняется только decision подхода для конкретной задачи без задевания goal/scope, это `1strategy` (momentum decision-thinking).
Why: Roadmap должен переводить выбранный подход в текущую картину пути. Goal-formation — document-driven deep thinking, живёт у владельца документа; momentum approach-choice в моменте — у `1strategy`. Раньше split был thinking-vs-commit, теперь document-level ownership лечит ownership leak.

Rule: Shared task-files и criteria по возможности ссылаются на file paths, planning levels и roadmap anchors, а не на platform-specific skill names.
Why: Codex и Claude могут иметь разные live skill handles; shared content не должен провоцировать переименование owner-скиллов между агентами.

Rule: Human-facing заголовки в roadmap и task-файлах должны быть короткими, русскими и понятными без агентного жаргона; exact handles, commands и paths оставлять только там, где они действительно нужны.
Why: User signal: пользователю не нравятся длинные смешанные русско-английские заголовки задач и roadmap; в разных проектах сложные заголовки быстро становятся тяжёлыми для чтения.

Rule: Skill handles, commands, paths, metadata keys, service labels и status labels не переводятся в roadmap/task-файлах.
Why: Русский человекочитаемый заголовок не должен создавать второй псевдоним для служебной сущности, которую агент и интерфейс знают по английскому handle.

Rule: В task-файлах раздел upstream-опор называется `Применимые критерии и инструкции` и включает не только `_ops/criteria/*.md`, но и агентные инструкции, которые меняют scope, red lines или проверку задачи.
Why: User signal: задачи пишутся не только по критериям принятия, но и по агентным инструкциям.

Rule: Связи между `_ops/PROJECT-ROADMAP.md`, task-файлами в `_ops/plans/**` и `_ops/criteria/*.md` держатся прозой внутри owner-скилов; `1md-graph` frontmatter (`read-before-edit` / `edit-after-edit`) для этой связки не применяется.
Why: User signal: «прозой гибче и меньше риска что будет мусор за которым надо будет следить»; в полигон-режиме `_ops/plans/**` редкий, frontmatter-инфраструктура без нагрузки становится мусором, требующим поддержки.
