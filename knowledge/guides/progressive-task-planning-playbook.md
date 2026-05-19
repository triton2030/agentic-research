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
PROJECT-ROADMAP.md
-> _ops/plans/phase-NN-*/task-MM-*.md
-> Подшаги внутри task-файла
-> Более глубокая декомпозиция только as-needed
```

- Strategy: куда и почему идём.
- Task-файл: эфемерная execution surface — какой bounded outcome сейчас создаём и как проверим готовность.
- Подшаги: ближайшие исполнимые ходы.
- Более глубокие уровни: только при блокере, риске или отдельном evidence.

Ни один слой не должен выполнять работу соседнего слоя.

## Plays

### Когда Захожу В Stage

Сверься с `PROJECT-ROADMAP.md`: какой Stage задаёт смысл текущей работы и
какие Anti-goals запрещают удобные shortcuts.

Не ищи execution status в strategy. Статусы живут в task-файлах.

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

- ближе всего продвигает текущий Stage;
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

**Status creep into strategy:** чекбоксы, queues, commands или evidence попадают
в `PROJECT-ROADMAP.md`.

**Evidence-before-action:** в task-файле появляется доказательство до
фактической проверки.

**Mini-plan inflation:** простой подшаг превращается в самостоятельный план без
блокера, риска или отдельного evidence.

**Skill-body drift:** guide пересказывает `SKILL.md` так подробно, что становится
вторым источником истины.

**Future-proof ballast:** система сохраняет complexity только потому, что она
может понадобиться когда-нибудь.

## Skill Touchpoints

- `1strategy` owns strategy truth. См. `/Users/triton/.codex/skills/1strategy/SKILL.md`.
- `1strategy` owns unresolved approach branches and consequential
  domain questions. См.
  `/Users/triton/.codex/skills/1strategy/SKILL.md`.
- `1planning` owns roadmap/task-files and task prerequisites. См.
  `/Users/triton/.codex/skills/1planning/SKILL.md`.
- Substantive-write discipline is distributed through local instructions,
  criteria delivery, owner skills, and `1work-review`.
- `1work-review` owns post-action review. См. `/Users/triton/.codex/skills/1work-review/SKILL.md`.
- `1user-truth` owns durable user truth. См.
  `/Users/triton/.codex/skills/1user-truth/SKILL.md`.
- `1skill-architect` owns skill control-surface changes; `1folder-contract`
  owns structural folder/runtime controls; `1instruction-layer` owns wording
  and placement of instruction prose.

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
