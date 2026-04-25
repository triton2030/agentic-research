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

`INTERVIEW.md` consumption check: назови 1-3 preference constraints, которые меняют routing, owner choices, guardrails, escalation или тон instruction layer. Если релевантных нет — честно отметь `none relevant`. Если текущий диалог дал новый, изменённый или конфликтующий preference signal, сначала подними `main-strategy` handoff на обновление `INTERVIEW.md`; не harden архитектуру поверх устаревшего профиля.

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

Если архитектурный вывод зависит от целостной структурной критики системы, проверь, доступен ли native Codex subagent `brooks` в текущем session inventory. Это может быть система из документов, картинок, бизнес-плана, instruction surfaces, repo-shape, guardrails, runtime layers или их связности. Если доступен, вызови его для read-only structural critique: передай артефакты, owned scope и вопрос «где центральная модель системы ломается, расползается или становится хрупкой?». Не передавай желаемый ответ, не проси Brooks переписать architecture и не меняй его роль внутри `system-architect`. Если `brooks` недоступен, зафиксируй `needed but unavailable` и не симулируй review.

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

Обязательная проверка для root instructions: есть ли прямое routing-правило часто вызывать `task-planner`? Оно должно покрывать обсуждение задачи, уточнение подхода, status/movement, редактирование текста/кода/артефакта, сверку текущей работы с Подшагами / Must / Must-not / Verification protocol task-файла и closeout после выполнения. Если root `AGENTS.md` / `CLAUDE.md` не содержит такого правила, prescription обычно живёт в `instruction text` layer. Не дублируй тело `task-planner`: root docs должны сказать **когда вызывать**, а не переписать lifecycle.

Обязательная проверка для instruction files: есть ли правило смысловой экономии? Модель должна видеть, что надо писать кратко, а каждая строка/предложение должны иметь функцию. Если правила нет, prescription обычно живёт в `instruction text` layer. Не создавай новый раздел ради этого, если можно усилить существующий `Style`, `Minimal footprint`, `Writing rules` или `Before work`.

Обязательная проверка для системных prescriptions: если verdict зависит от связности нескольких системных поверхностей или есть риск, что архитектор видит части вместо целого, архитектурный ответ должен назвать Brooks verdict: `not needed`, `launched`, или `needed but unavailable`. Brooks — critic layer, не owner: итоговый owner остаётся `system-architect`, `task-planner`, execution или human checkpoint по карте выше.

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
- какая строка, предложение или секция не выполняет отдельную работу.

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
- Brooks handoff, если whole-system structural critique материально меняет verdict
- literal root-instruction wording для частого `task-planner`, если fresh-session default route сейчас недостаточно активен.
- literal instruction-economy wording, если fresh-session default route не удерживает краткость и смысловую функцию каждой строки.

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
