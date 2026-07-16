# Progressive Task Planning Playbook

```text
Я пишу это потому, что без этого нельзя выполнить или проверить следующий ход?
Если нет, не писать.
```

Не строить полную цепочку. Строить следующий проверяемый фронтир.

Этот playbook нужен для работы, где агенту и человеку легко утонуть в будущих
задачах. Модель проста: strategy держит направление, task-файл держит
исполнение, подшаги раскрываются только as-needed.

## Слойная Модель

```text
_ops/GOAL.md
-> _ops/plans/**/task-*.md (только когда нужен durable state)
-> Подшаги внутри task-файла
-> Более глубокая декомпозиция только as-needed
```

- Project contract: outcome, scope, done и stop rules.
- Task-файл: эфемерная execution surface — какой bounded outcome сейчас создаём и как проверим готовность.
- Подшаги: ближайшие исполнимые ходы.
- Более глубокие уровни: только при блокере, риске или отдельном evidence.

Ни один слой не должен выполнять работу соседнего слоя.

## Plays

### Когда Вхожу В Работу

Сверься с `_ops/GOAL.md`: какой outcome задаёт смысл текущей работы, что вне
scope и какие stop rules запрещают удобные shortcuts.

Не ищи execution status в project contract. Если работе нужен durable state,
он живёт в task-файле; обычная in-chat разбивка остаётся в разговоре.

### Когда Начинаю Task

Создай или обнови один task-файл только для bounded outcome, который уже нужен
сейчас.

Минимальный фронтир содержит:

- strategic anchor;
- task outcome;
- ограничения, которые уже важны;
- ближайшие подшаги;
- criteria, без которых нельзя принять результат;
- observable evidence.

Если критерий звучит как защита от воображаемого будущего, не записывай его.

### Когда Выбираю Следующий Task

Используй next-task selection, а не полный roadmap.

Выбери task, который:

- ближе всего продвигает текущий project outcome;
- реально выполним текущими skills, tools и context;
- даст наблюдаемый evidence;
- не требует учитывать то, что пока можно оставить неизвестным.

Это заимствует из Voyager только идею выбора следующего полезного вызова. Не
переноси сюда voyager-specific skill library или curriculum algorithm.

### Когда Подшаг Кажется Большим

Не раскрывай его автоматически.

Раскрывай глубже, если подшаг:

- требует нескольких решений;
- зависит от неизвестного факта;
- несёт риск необратимой или широкой правки;
- требует отдельного evidence;
- блокирует несколько будущих ходов;
- уже провалился при прямом исполнении.

Если подшаг можно выполнить и проверить сразу, не превращай его в мини-план.

### Когда Подшаг Пережил Task

Выноси его в отдельный task-файл только после наблюдаемого сигнала:

- текущий task закрыт, а подшаг остался открытым;
- появился самостоятельный outcome;
- появился отдельный verification protocol;
- появился blocker или dependency вне текущего task;
- подшаг начал обслуживать Stage напрямую, а не только текущую задачу.

Не предсказывай, что подшаг "может пережить" task. Наблюдай, что он пережил.

### Когда Перед Записью

Проверь, что запись служит upstream purpose, а не просто повторяет prompt или
имя файла.

Если purpose звучит как "обновить файл", "добавить раздел" или "починить текст",
сначала найди, какой strategy/task outcome эта запись продвигает.

### Когда После Исполнения

Сравни фактический diff, artifact или command output с criteria и evidence.

Если задача оказалась слишком лёгкой, слишком широкой, неверно выбранной или
потребовала неожиданной декомпозиции, это feedback для следующего task
selection. Не держи этот вывод только в голове.

### Когда Подозреваю Drift

Если chat, git, task closeout или artifact state показывают, что strategy и
execution layer разошлись, не дописывай локальный план. Роуть drift к владельцу
слоя: strategy, task contract или ops sync.

### Когда Увидел Лишнюю Сложность

Strategy даёт не только право не строить будущее заранее, но и право удалять
сложность, которая больше не проходит через текущую траекторию.

Удаляй или сжимай:

- speculative criteria;
- неиспользуемые подшаги;
- future-proof abstractions;
- task notes без evidence;
- файлы, которые стали side-docs вместо owner surfaces.

## Что Не Писать Заранее

Не записывать:

- дальние task chains;
- speculative subtasks;
- criteria "на всякий случай";
- подробные implementation paths для будущих стадий;
- статусы исполнения в strategy;
- evidence до фактической проверки;
- отдельные файлы и заметки, если правильный существующий слой уже есть.

Пустота здесь не недоработка. Это защита от stale planning.

## Failure Modes

**Speculative criteria:** критерий защищает возможное будущее, а не текущий
outcome.

**Fake task chain:** агент пишет длинную цепочку задач, чтобы выглядеть
организованным, но следующий проверяемый ход не становится яснее.

**Status creep into project contract:** чекбоксы, queues, commands или evidence
попадают в `_ops/GOAL.md`.

**Evidence-before-action:** в task-файле появляется доказательство до
фактической проверки.

**Mini-plan inflation:** простой подшаг превращается в самостоятельный план без
блокера, риска или отдельного evidence.

**Skill-body drift:** guide пересказывает `SKILL.md` так подробно, что становится
вторым источником истины.

**Future-proof ballast:** система сохраняет complexity только потому, что она
может понадобиться когда-нибудь.

## Skill Touchpoints

- Approach-choice truth stays in the current owner/context pass: separate goal
  from method, surface consequential branches, and do not freeze scope before
  the decision is clear.
- `1planning` owns durable active/deferred task state and task prerequisites. См.
  `/Users/triton/.codex/skills/1planning/SKILL.md`.
- `1goal` owns project-level goal, scope, done/stop and README on-ramp;
  `1break-down` owns the first in-chat verifiable frontier.
- Substantive-write discipline is distributed through local instructions,
  criteria delivery, owner skills, and direct evidence-closeout by the current
  execution owner.
- Durable user truth не держит отдельный installed skill. Закрепляй её у
  правильного project owner-а или в memory layer только по явной просьбе
  пользователя.
- `1skill-architect` owns skill control-surface changes; `1ia-audit` owns
  structural owner/shape decisions; `1instruction-layer` owns wording and
  placement of instruction prose.

## Research Tie-Back

- HTN supports the layered model: abstract work decomposes into executable tasks,
  but not necessarily to a fixed depth.
- ADaPT supports as-needed decomposition: decompose when the executor cannot
  handle the current subtask.
- Voyager supports next-task selection: choose the next useful challenge from
  current capability and feedback, not a complete prewritten roadmap.
- SayCan supports feasibility filtering: the next action must be useful for the
  goal and doable by the current agent in the current environment.
- PlanBench / LLM+P support external structure: long-horizon plans need
  constraints and verification outside the model's free-form reasoning.
