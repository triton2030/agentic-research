## Цель

Создаём полигон знаний, критериев и рабочих контрактов, который помогает
будущей ИИ-сессии проектировать и улучшать skills, agents, prompts и
instruction files под `GPT-5.5` и `Claude Opus 4.7`.

Источник: `_ops/GOAL.md#Что делаем`. Цитата синхронизируется при правке
`_ops/GOAL.md` в том же ходу через `1folder-contract` (Goal-цитата sync —
bilateral контракт между `1strategy-docs` и `1folder-contract`).

## Папочный граф

Central index папочных зависимостей и veto-class — `_ops/project-graph.md`
(owner: `1folder-contract`). Читай первым при substantive работе, чтобы
видеть какие папки задевает локальная просьба. Сам граф живёт там; здесь
только указатель.

## MUST

Сначала прочитай `AGENTS.md`. Для внешнего обзора проекта читай `README.md`.
Для рабочего контракта (что в scope, что нет, definition of done, stop rules)
читай `_ops/GOAL.md`.

Skill contracts сильнее старых repo notes: если живой `SKILL.md` и корневая
инструкция расходятся, следуй `SKILL.md`.

Канон этого репо пишется только под `GPT-5.5` и `Claude Opus 4.7`; старые
model-neutral советы не использовать как baseline без свежей проверки.

Для Claude Opus 4.7: outcome-first контракты, явные success criteria,
constraints, validation, stop rules. Старый process-heavy stack не переносить
по инерции.

`_ops/GOAL.md` — главный контракт проекта (owner `1strategy-docs`):
outcome, in scope, NOT in scope, definition of done, stop rules.
Goal-formation thinking (scope / done / stop / charter shape) — internal
work у `1strategy-docs`, не делегируется. Momentum decision-thinking при
выполнении конкретной задачи (approach-choice в моменте, goal-alignment
check) — `1strategy`. Hook-loaded цитата эссенции в `AGENTS.md` и этом
файле синхронизируется при правке GOAL через `1folder-contract` (sync
живёт там, поскольку это часть architectural contract проекта).

`_ops/PROJECT-ROADMAP.md` — текущая рамка движения проекта. Shape файла
(формат, что туда идёт) — `1strategy-docs`; content updates (current path
сдвинулся, Stage closed, position update) — `1planning`. Не дублирует
Goal-блок из GOAL.md; пишет только current path / mode.

`README.md` — короткий контекст и reader on-ramp (owner `1strategy-docs`):
vision, approach, motivation, как читать репо. Не главный strategy-документ —
этот ярлык переехал на `_ops/GOAL.md`. Одна страница.

Рабочие слои:
- `_ops/GOAL.md`: outcome-first контракт.
- `_ops/PROJECT-ROADMAP.md`: текущая рамка движения без обязательной цепочки стадий.
- `_ops/user-said/YYYY-MM-DD.md`: сырые цитаты пользователя по дням.
  Это legacy/manual архив; auto-capture отключён. Обработка manual —
  пользователь сам решает, что превращать в правило, инструкцию или decision.
- `_ops/plans/**`: временная task-поверхность только по явному запросу для
  активной сложной работы.

`INTERVIEW.md` и `LEARNINGS.md` больше не являются live owner surfaces. Не
восстанавливай их. Важная durable цитата пользователя может остаться в
`_ops/user-said/` только как manual raw archive; дальнейшая обработка
(поменять ли AGENTS / CLAUDE, обновить ли GOAL, завести ли decision) —
отдельным manual проходом.

Moment layer работает через runtime и инструкционный слой, не через отдельный
скил-перед-работой:

- **Intent grounding + turn-id tracking** — UserPromptSubmit hook
  (`~/.claude/hooks/user-prompt-all-messages.py`): на каждом prompt
  бампает `session-state.turn_id` (так per-turn skill_invocations
  / markers работают корректно); на `turn_id == 1` инжектит intent
  directive; параллельно пишет prompt в
  `experiments/all-my-messages/{slug}.md` analytics log. Три
  ответственности слиты в один hook после refactor 2026-05-22.
- **Session-state shared memory** между hooks и skills — JSON в
  `~/.claude/state/session-{session_id}.json` через CLI
  `~/.claude/skills/1start-here/scripts/session-state.py`; schema —
  `~/.claude/skills/1start-here/references/session-state-schema.md`.
- **Task-level anchor** перед нетривиальной работой — это правило: до
  содержательного ответа на substantive imperative («сделай / напиши / fix /
  implement / build / поправь») прочитать `_ops/GOAL.md` (контракт scope/done),
  `_ops/PROJECT-ROADMAP.md` (current path), `_ops/project-graph.md` (граф
  папок) и релевантные agent instructions (root + subtree).
- **Closeout** перед claim «готово» — `1work-review` сравнивает diff с
  Definition of done из GOAL, evidence работ.

Начало работы в repo/project, новый проект, отсутствующая базовая
shape-структура или вопрос «какой skill брать?» → `1start-here`.

Strategy thinking разделён по двум слоям:

- **Momentum decision-thinking при выполнении задач** (approach-choice в моменте,
  варианты, goal-alignment check, mental tools, ground-check для частной задачи,
  обсуждение raw desire подхода) — `1strategy`. Срабатывает часто, перед любой
  нетривиальной развилкой даже в автономной работе. Использует existing GOAL
  как context; файлов не пишет.
- **Goal-formation thinking** (что должно быть целью / scope / done / stop,
  project charter shape, README narrative, ROADMAP shape) — `1strategy-docs`.
  Думает internal работой и пишет GOAL / README / ROADMAP. Mental tools читает
  из `1strategy/references/internal-tools.md` (shared toolkit). Не делегирует
  thinking в `1strategy`.

Mental tools (OODA, first-principles, inversion, premortem, adversarial
self-play) — общий toolkit; canonical ownership у `1strategy`, оба скила
используют через явный read.

Recursive planning (Level 1 roadmap content / current path → Level 2 task-файлы → Level 3
подшаги, archive/reconcile) живёт в `1planning`. Активный уровень
материализуется только по явному запросу; всё дерево заранее не разворачивается.
Task-файл ссылается на агентные инструкции, которые меняют scope, red lines
или verification. Unresolved approach branches при выполнении задачи /
domain prerequisites / missing-middle questions — в `1strategy`. Unresolved
goal/scope/done shape — в `1strategy-docs`. По явному запросу `1planning` может
прогнать clean-context decomposition audit через субагентов (см.
`references/decomposition-audit-agents.md`).

Instruction слой разделён по двум скилам:
- **Формулировка отдельного правила / placement текста инструкции / language
  quality аудит** (lost-in-middle, Hyrum unintentional contracts, spec
  literalism, sycophancy в формулировках) — `1instruction-layer`.
- **Architectural blueprint проекта / folder graph / Owner Decision Map /
  выбор structural mechanism (hook / skill / text) / system coherence audit /
  hook-loaded Goal-цитата sync** — `1folder-contract`.

Уже выбранная skill-работа идёт в `1skill-architect`; уже выбранная
runtime/tooling работа: в Claude — `1start-here` (runtime delegate).

`knowledge/` — основной input-layer: перед созданием или правкой skill / agent /
instruction file начинай с ближайшего `wisdom-*` и одного guide/practical guide.
Для создания или правки skills сначала читай
`knowledge/practical-guides/how-to-write-skills/`, затем live `SKILL.md` и
platform-specific контекст.

Новые и изменяемые skill-поверхности (`SKILL.md`, `agents/openai.yaml`,
skill references) писать на русском. Английский оставлять только для кода,
команд, API/tool names, путей, handles, точных цитат, model/product names и
trigger words, которые должны остаться английскими.

`_ops/plans/**` — эфемерная execution surface; создавай лениво только под
активную сложную задачу по явному запросу и не используй как источник истины
или список задач.

Новый проект или отсутствующий `_ops` work-shape не собирать руками. На стороне
Claude запускай `bash ~/.claude/skills/1start-here/scripts/init-three-level.sh
[/path]`; скрипт fill-missing и idempotent — создаёт skeleton'ы `README.md` /
`AGENTS.md` / `CLAUDE.md` / `_ops/GOAL.md`, минимальный `_ops/PROJECT-ROADMAP.md`
(current path TBD), пустой `_ops/project-graph.md` skeleton, пустые папки
`_ops/{plans,interviews,findings,user-said}` с `_archive/` и `.gitkeep`. Файлы
внутри добавляют owner-скилы по мере проекта.

GitHub здесь — backup локального `main`, не branch/PR collaboration flow.

## Язык

Главное правило: с пользователем писать и разговаривать только на русском, если
он явно не попросил другой язык.

Сложные программистские вещи объясняй простым русским языком. Английский
оставляй для кода, команд, API, имён файлов, цитат и точных handles.

В планах, проектах и обсуждениях избегай программистского жаргона. Можно
использовать язык веб- и UI-дизайна: поверхности, тени, иконки, дизайн-система,
компоненты, вёрстка.
