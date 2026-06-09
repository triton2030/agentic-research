# Claude-версия

Снимок обновлён 2 июня 2026 по живой Claude-поверхности. Это справочная карта,
а не источник поведения: если файл расходится с `~/.claude/settings.json`,
`~/.claude/skills/*/SKILL.md` или локальным `AGENTS.md`, выигрывает live
surface.

## Живой Контур

В `~/.claude/skills` сейчас нет отдельных `1start-here`, `1user-truth` и
`1work-review`. Поэтому локальные документы не должны маршрутизировать работу
через эти handles как через installed skills.

Активные hooks из `~/.claude/settings.json`:

- `PreToolUse` для `Edit|Write|MultiEdit|NotebookEdit` ->
  `~/.claude/hooks/md-graph-pre-edit-reminder.py`;
- `PreToolUse` для `Grep` -> `~/.claude/hooks/md-search-pre-grep-reminder.py`.

`SessionStart`, `UserPromptSubmit`, `criteria-gate.py`,
`prompt-submit-reminder.py`, `session-start.sh` и `stop-work-review.py` в live
settings не подключены. Файл `~/.claude/hooks/user-prompt-all-messages.py`
существует как hook script, но текущим `settings.json` не wired.

Корневой проектный `CLAUDE.md` остаётся shim-ом `@AGENTS.md`; hot-path правда
про этот репозиторий живёт в `AGENTS.md`, `_ops/GOAL.md`,
`_ops/PROJECT-ROADMAP.md`, `_ops/project-graph.md`, `_ops/rules/**` и живых
skills.

## Работа От 0 До Готово

`1strategy` выбирает подход и развилки. `1strategy-docs` держит shape
`README.md`, `_ops/GOAL.md` и `_ops/PROJECT-ROADMAP.md`. `1planning` держит
roadmap/task content и L1/L2/L3 decomposition.

Финальная сверка не является отдельным installed `1work-review`: текущий
execution owner закрывает работу через прямой evidence-closeout. Для большой
независимой проверки используется `auditor` / `1fresh-eyes` по явному запросу
или подтверждённому brief.

## Пользовательская Правда

Отдельного live `1user-truth` нет. Durable user truth нельзя выводить из
догадки: нужен прямой user signal и правильный owner.

Текущие маршруты:

- project/instruction rule -> `AGENTS.md`, `_ops/rules/**`,
  `1instruction-layer` или `1folder-contract`;
- scope/done/stop -> `_ops/GOAL.md` через `1strategy-docs`;
- planning/task state -> `_ops/PROJECT-ROADMAP.md` / `_ops/plans/**` через
  `1planning`;
- временная проблема или self-learning finding -> `_ops/findings/**` через
  `1findings`;
- durable memory outside repo -> memory layer только по явной просьбе
  пользователя.

`_ops/user-said/**`, если есть, остаётся сырой manual archive, не auto-capture
и не источник решений без отдельного прохода.

## Выбор Подхода

`1strategy` раскрывает consequential options до плана: цель против метода,
скрытая цена, риски, reversibility и owner route. `1assumption-audit` остаётся
ручным ground-check уже выбранного подхода. `1step-back` нужен, когда неверна
сама рамка.

## Планирование

Единый live owner трёх уровней — `1planning`:

- L1 -> `_ops/PROJECT-ROADMAP.md`;
- L2 -> task-файлы в `_ops/plans/**`;
- L3 -> подшаги внутри task-файла.

Старые `1roadmap` и `1tasks` не являются live skills; их прежний смысл
распределён между `1strategy-docs` и `1planning`.

## Исполнение

Перед substantive работой агент читает локальный project truth, если он меняет
маршрут, риск или проверку. Для Markdown:

- broad navigation/search -> `1md-navigator`;
- bounded reading selected files/sections -> `1md-reader`;
- graph/frontmatter/blast-radius -> `1md-graph`;
- exact stale references / CLI evidence -> `1cli-tools`.

Runtime guardrail на Claude стороне сейчас узкий: pre-edit Markdown graph
reminder и pre-grep search reminder. Остальная дисциплина держится в локальных
instructions, owner skills и evidence-closeout, а не в retired hooks.

## Самоулучшение

`1instruction-layer` владеет wording и placement instruction prose.
`1folder-contract` владеет owner boundaries, `_ops/project-graph.md` и выбором
механизма. `1skill-architect` владеет `SKILL.md`, trigger surface, references,
agents metadata и hook-script structure. Runtime/settings правятся только после
live settings/hook pass.

`1md-navigator`, `1md-reader` и `1md-graph` имеют разные owners и не заменяют
друг друга: search/IA-refactor, bounded reading и graph safety соответственно.

## Retired Routes

- `1start-here` -> заменён локальным context/owner pass через инструкции и
  live skills.
- `1user-truth` -> заменён owner-specific durable truth routing.
- `1work-review` -> заменён прямым evidence-closeout текущего owner-а.
- `criteria-gate.py`, `prompt-submit-reminder.py`, `session-start.sh`,
  `stop-work-review.py` -> не wired в текущем `~/.claude/settings.json`.
