# Workflow — From Project Reality To Instruction Architecture

Этот workflow должен читаться как причинная цепочка, а не как мёртвый checklist.

Сначала пойми проект. Потом — какую работу в нём должен делать ИИ. Потом — где он будет сбоить. И только после этого проектируй instruction layer.

Порядок rigid. Не переставляй.

## 1. Project Reality And Upstream Health

Сначала классифицируй `_ops`:

- `unbootstrapped` — `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md` или `_ops/learnings.md` отсутствует;
- `stale` — файлы есть, но Goal / Stage / learnings не отражают реальность;
- `hot` — upstream существует и объясняет текущую работу.

Если состояние `unbootstrapped`, не проектируй альтернативную архитектуру поверх root `ops/`, `plans/`, `.codex/` или `.claude/`. Подними `main-strategy` handoff: запустить `references/ensure-ops.sh`, затем вернуться к архитектуре. Legacy surfaces можно читать только как evidence.

Потом прочитай:

- `_ops/PROJECT-PLAN.md` — Goal, Approach & Why, активный Stage, anti-goals если они есть;
- `_ops/INTERVIEW.md` — только preference constraints, которые реально ограничивают архитектурный выбор;
- `_ops/learnings.md` — реальные расхождения ожиданий и реальности;
- корневые и локальные `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`.

Сначала ответь себе на четыре вопроса:

- что это за проект;
- что здесь считается успехом;
- куда он идёт прямо сейчас;
- какой sign of reality уже не помещается в текущий `_ops/`.

`PROJECT-PLAN.md`, `INTERVIEW.md` и `learnings.md` вместе образуют горячий upstream truth layer. Если один из трёх файлов отсутствует — это `unbootstrapped`, а не просто drift. Если Goal / Stage слабы или диалог уже уехал дальше, чем `_ops/` — это `stale upstream`.

Если `unbootstrapped` или `stale` найден, **не harden stale instructions**. Сначала подними `main-strategy` handoff.

## 2. AI Job Map

Теперь определи, какую работу ИИ должен делать в этом проекте сейчас и в ближайших фазах.

Обычно это 2-5 job types, а не бесконечный список. Для каждого job type зафиксируй:

- что агент должен делать;
- какие решения он должен принимать сам;
- чего он не должен делать;
- какие surfaces он трогает: `_ops/`, `AGENTS.md`, skills, код, папки, runtime layer.

Если не можешь сформулировать AI job map, instruction architecture ещё рано проектировать: ты не знаешь, кого именно строишь.

## 3. Pressure And Failure Map

Сначала назови 2-4 pressure fields, которые уже влияют на дизайн или скоро начнут влиять:

- рост числа типов работы;
- рост числа owner surfaces;
- смена модели / tool surface / runtime ограничений;
- появление новых людей, режимов или handoff-сценариев;
- любая другая сила с конкретным ранним сигналом.

Для каждой силы нужен ранний сигнал и объяснение, почему она влияет на design choice уже сейчас.

Потом собирай failure **в классы**, а не в россыпь симптомов. Источники:

1. `_ops/learnings.md`
2. текущий trace, если он есть
3. inversion по AI job map и активному Stage

Отдельным классом всегда проверяй **upstream truth failure**: `unbootstrapped` (нет стандартного `_ops`) и `stale` (есть, но не успевает за реальностью). Иначе архитектура начинает защищать призрак плана или случайный legacy layer.

Для каждого failure class зафиксируй:

- что ломается;
- где текущая система это позволяет;
- какие pressure fields делают это вероятнее;
- чем класс отличается от соседнего.

Если `forces` появляются только в эпилоге после готового решения, значит ты не проектируешь, а оправдываешь выбор задним числом.

## 4. Control Surface Map

Только теперь собирай карту control surfaces.

Смотри в таком порядке:

1. root `AGENTS.md` и subtree-инструкции;
2. repo-local и installed skills;
3. folder ownership и `_ops/` surfaces;
4. hooks, validators, approvals, tool policy и прочий runtime layer;
5. human checkpoints, которые остались после этого.

Жёстко разделяй:

- `реально существует и влияет`;
- `упомянуто текстом, но runtime не доказан`;
- `отсутствует`.

Не начинай с capability inventory до project / AI job / failure map: иначе велика вероятность редактировать control surfaces, не понимая, чему они должны служить.

## 5. Leverage Analysis

Это центр архитектурного мышления.

Вопрос не такой:

> какой фикс закрывает этот симптом?

Вопрос такой:

> какая одна правка меняет default path и схлопывает несколько failure classes сразу?

Для каждого leverage candidate покажи:

- какие failure classes он collapse'ит;
- почему это leverage, а не bundle из мелких patch'ей;
- какой у него reversibility и blast radius;
- в каком owner layer он должен жить;
- почему более сильный слой подходит или не подходит.

Если честного leverage нет, так и скажи. Не изобретай абстракцию ради красивой схемы.

## 6. Instruction Architecture

Теперь выводи instruction architecture как следствие предыдущих шагов, а не как стартовую точку.

Архитектура должна отвечать на пять вопросов:

- **Routing** — какой тип работы куда идёт по умолчанию;
- **Ownership** — кто владеет каким правилом, файлом или surface;
- **Guardrails** — что должно держаться runtime, skill, instruction text или handoff;
- **Escalation** — что отбрасывает ход обратно в `main-strategy` или `task-planner`;
- **Default route for fresh session** — как новый агент входит в проект.

Каждое архитектурное изменение обязано содержать:

- **Fix-layer**: `runtime guardrail` | `local skill` | `instruction text` | `task-planner handoff` | `human checkpoint`
- **Механизм**
- **Почему это следует из project / job / failure map**
- **Backlink**
- **Observable signal**
- **Sunset signal**
- **Owner**

Для major changes добавь proof path:

- `existing evidence`;
- `fresh-context probe`, если он реально запускался;
- `не запускался` с честной причиной.

## 7. Minimize Pass

Перед финальным emit попытайся **убрать**, а не только добавить.

Обязательные вопросы:

- что можно удалить;
- что можно не создавать;
- что можно слить в один owner layer;
- какой новый skill / hook / doc оказался не нужен после leverage analysis.

Если ничего не удалено, ничего не отклонено и ничего не слито, почти наверняка ответ additive-heavy.

Если scope касается папок, здесь и появляются verdicts:

- `keep`
- `archive`
- `remove`
- `do not create`

Chesterton's fence всё ещё обязателен: не удаляй то, чью причину не понимаешь.

## 8. Handoff And Default Route

Финал должен замкнуть петлю:

- `Default route for fresh session`
- `Main-strategy handoff`, если `_ops` `unbootstrapped` или `stale`
- `Task-planner handoff`, если нужен task-level contract

Если `_ops` `unbootstrapped` или `stale`, `Main-strategy handoff` обязан назвать:

- что сделать: bootstrap через `ensure-ops.sh` или пересинхронизировать конкретный файл;
- какой sign of reality туда не попал;
- почему это не owner `system-architect`.

## EVPI Questions

Вопрос допустим только если ответ materially меняет:

- fix-layer;
- owner;
- add vs remove verdict;
- саму форму default route;
- реальность одного из pressure fields.

Не задавай:

- `согласен с моим анализом?`
- открытые вопросы без 2-4 реальных вариантов;
- вопросы, которые меняют только wording.
