---
description: "Semantic owners and projection contracts for cross-runtime skills."
---

# Shared Skill Owners

Эта папка владеет пакетами, у которых переносимый смысл и runtime-дельты
должны меняться как одно целое. Она не является третьим installed runtime.

## Живые Owners

- `1fresh-eyes` — два runtime owners: `skills/{claude,codex}/1fresh-eyes/`.
  Общая продуктовая пара живёт у Claude owner и не устанавливается.
  Профиль Expansionist принадлежит `agents/expansionist.{md,toml}` этих
  пакетов и дополнительно доставляется в `~/.{claude,codex}/agents/`.
  Остальные native-профили сохраняют существующих владельцев.
  Доставка — по явному manifest из истории `skills/1fresh-eyes/`.
- `1-max-review/portable/` — проверка выбранных файлов или корпуса по исходным
  участкам применимых правил: готовые небольшие пакеты, отдельный координатор
  и общий CLI с учётом покрытия участков и ответов. Luna Max закреплена в теле.
  `platforms/{codex,claude}/references/runtime.md` держат особенности запуска;
  Codex metadata — `platforms/codex/agents/openai.yaml`.
  Локальная история создания и проверки — `_workspace/orchestration/2026-09-19-maxrevie/`.
- `1illustrations-and-charts/portable/` — компактные схемы, SVG и макеты интерфейса рядом со сложным объяснением; переносимое ядро для Claude и Codex. Проектные пути и CSS остаются в документации проекта.
- `1writing-rule/portable/` — личное «Правило письма»: качество любой прозы,
  подробный материал для файлов и маршруты к `1docs-write`, `1folder-tree`
  `1smart-simple` и `1illustrations-and-charts`.
  Codex UI metadata — `platforms/codex/agents/openai.yaml`.
- `1agent-steering/portable/` — общий скилл знания: полное чтение науки
  управления агентами и объяснение её применения при авторинге. Материал —
  `references/steering-science.md`; потребители — `1skill-creation`,
  `1instruction-authoring`, `1goal`. Codex metadata
  живёт в `platforms/codex/agents/openai.yaml`.
- Семья авторинга — пять скилов по различимым моментам запуска, заменили пару
  `1skill-shaping` + `1instruction-shaping`, снятую 2026-08-26 (архивы в
  `skills/1skill-shaping/` и `skills/1instruction-shaping/`; решение владельца —
  `_ops/chat-recall/raw/2026-08-26-201025-claude-4e40828f.md#L15`):
  - `1instruction-authoring/portable/` — местные корневые и папочные
    инструкции. Дельта сильной модели, объяснение важности через ситуацию,
    остаточные критерии и минимальный одновременно необходимый набор.
    `references/discovery.md` находит подтверждённые местные обязательства,
    `writing.md` выбирает носитель, владельца и момент применения,
    `verification.md` разделяет три проверки: смысл, необходимость, доставка.
    Пробы применимости, неприменимости и конфликта выполняются до передачи
    проверяющему ожидаемого ответа. Сохраняются необследованные зоны,
    Maintain-цель зоны, реальные механизмы и нормативное старшинство.
    Принципы — `1instruction-authoring/product-frame.principles.md`;
    история — `skills/1instruction-authoring/`.
  - `1context-refactor/portable/` — ретроспектива всей доступной сессии:
    лишние вызовы инструментов, чтение, переделки, остановки и проверки;
    затем разбор причин и сохранение полезных улучшений. Различает
    наблюдаемую потерю и установленную причину, текст и механизм среды;
    ремонт направляет к владельцу источника в пределах полномочий.
    Переносимый контракт — `SKILL.md`, Codex-вход —
    `platforms/codex/agents/openai.yaml`. История переработки —
    `skills/1context-refactor/work/retrospective-2026-09-24/`.
  - `1skill-creation/portable/` — создание, адресная правка и переработка
    скилов в общей мастерской. Контекст, Задача, необходимые Критерии и Цель
    несут разные смыслы; число разделов и пунктов не задаётся квотой.
    `references/goal-context.md` восстанавливает основания намерения,
    `behavior-protocol.md` отбирает дополнения, `reference-files.md` разводит
    моменты чтения, `skill-short-description.md` управляет вызовом.
    `refactor.md` сохраняет границу заказа и ведёт автора до карты потерь;
    отдельного пишущего агента не требует. `check-approve.md` задаёт три
    независимые роли: смысл, необходимость, применение и результат.
    `install-approved.md` доставляет изменение в пределах уже данного
    разрешения. Принципы — `1skill-creation/product-frame.principles.md`;
    история — `skills/1skill-creation/`.
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
- `1readable-code/portable/` — стратегический взгляд при существенном выборе
  в коде для Claude и Codex; `platforms/codex/agents/openai.yaml` содержит только Codex UI
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
- `1planning/portable/` — единственный скил планирования с 2026-09-25:
  порядок работ с владельцем, эпики, роутеры задач, вопросы и оба Bases.
  Поглотил `1plan-map` и `1plan-task`, раскроенные из него 2026-08-26;
  обратное слияние одобрено владельцем 2026-09-25
  (`mavo3/_ops/chat-recall/2026-09-25-130106-Claude-f6bca69a.md`). Задача —
  роутер: цель, ссылки на места документации с пометкой «зачем», что не
  входит, чеклист проверок; отчётов, доказательств и состояния в файле нет.
  Дословный протокол владельца о декомпозиции в чате сохранён в теле.
  `references/форма-планов.md` — адреса, поля шапки для Bases, разделы и
  проверка; `scripts/check_plans.py` принимает роутер и прежнюю форму до
  закрытия файла; `assets/` — шаблоны и оба Bases без изменений. История —
  `skills/1planning/` (работа — `work/router-2026-09-25/`), снятые пакеты —
  `skills/1plan-map/`, `skills/1plan-task/`.
- `1smart-simple` — tracked owner отсутствует; живые пакеты
  `~/.claude/skills/1smart-simple/` и `~/.codex/skills/1smart-simple/` —
  единственная правда (v4, 2026-09-06; история — `skills/1smart-simple/`).
  На него маршрутизируют `1skill-creation/reference-files.md` (случай проверки
  нагрузки), `1instruction-authoring/writing.md` и
  `1document-system/overgrown.md`.
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
  2026-09-18 — адресная правка по слову владельца «порядок знаний»: владелец читает
  имена в порядке показа; третий критерий приёмки — пересказ по именам, а где
  порядок чтения есть, и что читать раньше; порядок соседей показывается в
  отображении, не вложенностью, способом инструкции базы (в mavo3 — цифра в
  начале имени); история — `skills/1folder-tree/work/order-2026-09-18/`.
- `1index/portable/` держит подтверждённые маршруты к источникам, включая локальную навигацию по задачам при авторинге инструкций.
- `1interview-tool/portable/` исследует будущие ошибки исполнения документов
  и создаёт Markdown-интервью с полноценными вариантами. Разобранные формы
  сохраняются как архив контекста в `_ops/interviews/_archive/`, не канон.
  Codex invocation metadata — `platforms/codex/agents/openai.yaml`.
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
- `1readable-code/portable/` — стратегический взгляд при существенном выборе
  в коде для Claude и Codex; `platforms/codex/agents/openai.yaml` содержит только Codex UI
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
- `1index/portable/` держит подтверждённые маршруты к источникам, включая локальную навигацию по задачам при авторинге инструкций.
- `1interview-tool/portable/` исследует будущие ошибки исполнения документов
  и создаёт Markdown-интервью с полноценными вариантами. Разобранные формы
  сохраняются как архив контекста в `_ops/interviews/_archive/`, не канон.
  Codex invocation metadata — `platforms/codex/agents/openai.yaml`.
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
  `1folder-tree`, тело только знание, происхождение в сносках.
  `references/проверка-документов.md` — распределённая проверка оснований,
  достаточности для читателя и согласованности связей; основной агент принимает
  результат. Добавлена 2026-09-14; прежняя история пакета ниже. С 2026-09-09
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
имя агента и runtime-тесты. Поиск выполняет сам рабочий агент в обоих рантаймах
(решение владельца 2026-09-14). Правь оба дерева адресно: копирование
runtime-теста целиком уже стирало Codex-специфичные проверки.

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
