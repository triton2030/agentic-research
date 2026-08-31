---
description: "Semantic owners and projection contracts for cross-runtime skills."
---

# Shared Skill Owners

Эта папка владеет пакетами, у которых переносимый смысл и runtime-дельты
должны меняться как одно целое. Она не является третьим installed runtime.

## Живые Owners

- Семья авторинга — пять скилов по различимым моментам запуска, заменили пару
  `1skill-shaping` + `1instruction-shaping`, снятую 2026-08-26 (архивы в
  `skills/1skill-shaping/` и `skills/1instruction-shaping/`; решение владельца —
  `_ops/chat-recall/raw/2026-08-26-201025-claude-4e40828f.md#L15`):
  - `1instruction-authoring/portable/` — создание и переписывание агентных
    инструкций проекта (v9, 2026-09-01). Функция — предотвратить критичный
    конфликт: доставить в точку работы правду, которую сильная модель по
    привычке нарушит и из этой точки не увидит. Тело — трёхшаговый роутер (семь шагов сведены к трём двумя причинными замерами 2026-09-01);
    владеет `references/discovery.md` (обнаружение критичного вычитанием
    привычки агента из правды проекта, семь вопросов зоны),
    `references/writing.md` (размещение, форма единицы, бюджет головы зоны) и
    `agents/zone-reader.md` (веерное чтение папок с возвратом заявленных в
    тексте связей). Бюджет считает не файл, а голову агента в зоне: корневая
    инструкция плюс папочная плюс протокол скила, к которому зона отсылает.
    Причинной пробы пакет не содержит — решение владельца 2026-08-31;
    `references/verification.md` и `agents/zone-scout.md` сняты, история — в
    `skills/1instruction-authoring/cut.md`;
  - `1context-refactor/portable/` — рефактор контекста: мета-анализ прошедшего
    диалога — найти шероховатости (лишнее чтение, переделки, долгая работа),
    установить причину, чинить настоящего виновника (инструкции, документ,
    скил, слова владельца); весь переносимый контракт теперь помещается в
    `SKILL.md`;
  - `1skill-creation/portable/` — создание, рефактор и кнопка запуска скилов
    одним пакетом (v14, 2026-09-01; предшественники и снапшоты —
    `skills/1skill-authoring/`, `skills/1skill-refactor/` и
    `skills/1skill-routing/`). Тело — единственный router независимых стадий;
    references друг друга не вызывают, кроме `refactor.md`, который запускает
    `goal-context.md` и возвращает агента в полный протокол создания. Пакет
    владеет `goal-context.md`, `skill-short-description.md`,
    `behavior-protocol.md`, `reference-files.md`, `agent-defaults.md`,
    `refactor.md`, `check-approve.md` и `install-approved.md`, а также парой
    `agents/check-instructions.md` + `agents/check-trajectory.md`. Намерение
    скила состоит из четырёх разделов в порядке Уникальный контекст, Задача,
    Цель, Критерии принятия; протокол поведения и reference-файлы идут после
    них и только по требованию владельца либо по выходу гейта
    `behavior-protocol.md` — метод «сломанный джин», решение владельца
    2026-08-31. Бюджет пофайловый: до 20 самостоятельных единиц, где единица —
    отдельная инструкция или ограничение; эти четыре раздела в счёт не входят
    при пределе в пять Критериев принятия на файл, а сумма тела и одного
    reference-файла ограничением не является. Пакет производит
    `product-frame.principles.md` скила в его папке-истории; композиция
    управляющего текста — в `science/how-to-command-agents-with-text.md`.
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
- `1orchestration/portable/` — общий минимальный контракт делегирования и
  разгрузки активных наборов для Claude и Codex;
  `platforms/codex/agents/openai.yaml` содержит только Codex UI metadata.
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
  - `1plan-task/portable/` — изолированность задач: самодостаточный жёстко
    ограниченный task-файл, режимы, доказательства, fresh-reader; владеет
    размещением, схемой, контекстом, бюджетом, work/report, state/lifecycle,
    closure, handoff и retention.
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
У `1chat-recall` различаются `allowed-tools`, переменные сессии, пути запуска и
имя агента — а тесты сверяются с этими строками. Правь оба дерева руками:
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
