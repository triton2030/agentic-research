---
description: "Датированный evidence-report о коротких skill descriptions для автоматического вызова по состоянию, возникшему во время длинной работы."
read-before-edit:
  - authoring-canon.md
edit-after-edit:
  - mid-trajectory-trigger-descriptions.md
---

# Research: Mid-Trajectory Trigger Descriptions

Срез на **11 августа 2026**. Допущены только источники с публичной датой
публикации, версии или коммита **не раньше 11 февраля 2026**. Дата доступа не
заменяет дату источника.

## Короткий Ответ

Нет исследования, которое изолированно сравнило бы разные короткие
`description` файлов `SKILL.md` и измерило вероятность их **позднего
автоматического вызова** в Codex или Claude Code.

Составное доказательство, однако, достаточно сильное для рабочей стратегии:

1. В долгой работе нужная capability часто определяется не исходным запросом,
   а текущим состоянием, промежуточным результатом или выведенной подзадачей.
2. Повторный retrieval по `task + current state` лучше одноразового выбора по
   исходной задаче; обученное решение «искать сейчас или продолжать» лучше
   пассивной загрузки или поиска на каждом шаге.
3. Короткое metadata-описание должно различать **функцию, момент применимости и
   ближайшего соседа**. Тематические слова и длина сами по себе не решают
   routing.
4. В Codex каталог остаётся в контексте многошагового turn, поэтому поздний
   model-driven выбор технически возможен. Отдельного host-side event router и
   гарантии recall нет.
5. Если момент обязателен, prose — недостаточный слой: нужен checkpoint, hook,
   orchestrator или явный вызов.

Практический вывод: писать не рекламную аннотацию и не список фраз пользователя,
а короткий предикат:

> `capability + observable current state/event + derived need + nearest exclusion`

## Как Читать Силу Evidence

- **Direct** — проверяет повторный выбор capability по evolving state или
  содержание short description.
- **Runtime** — доказывает, что поздний выбор архитектурно возможен; не
  доказывает его частоту.
- **Adjacent** — исследует близкий механизм tool/skill retrieval; перенос на
  automatic `SKILL.md` invocation явно ограничен.
- **Vendor practice** — показывает реальную авторскую практику поставщика, но
  не причинный эффект формулировки.

## Direct: Вызов По Состоянию Внутри Траектории

### ProactAgent — искать только когда возник дефицит

**4 июня 2026, arXiv v2.** [Ask Only When Needed: Proactive Retrieval from
Memory and Skills for Experience-Driven Lifelong Agents](https://arxiv.org/html/2604.20572)

Агент на каждом шаге выбирает действие среды либо `Retrieve(q_t)`. Полезность
позднего retrieval обучается на паре продолжений из одного промежуточного
состояния: искать или продолжить без поиска. В SciWorld success вырос с 55.50%
у пассивного retrieval baseline до 73.50%, а среднее число раундов снизилось с
27.52 до 18.38; в AlfWorld — 67.18% → 71.28% и 16.42 → 12.73 раунда.

**Доказывает:** решение о загрузке knowledge/skill — отдельная часть политики
внутри траектории; «на старте» и «всегда» хуже need-aware выбора.

**Не доказывает:** retrieval возвращает смесь facts, episodes и skills;
формулировка короткого `description` отдельно не менялась.

### SGDR — task + state лучше task-only

**3 июня 2026, arXiv v1.** [Online Skill Learning for Web Agents via
State-Grounded Dynamic Retrieval](https://arxiv.org/html/2606.04391)

SGDR заново извлекает до пяти skills на каждом decision step по исходной цели и
summary текущей страницы. Description отделено от исполняемой части и кодирует
намерение вместе с применимым состоянием. На WebArena GPT-4.1 получил 37.5%
success против 33.9% у сильного static task-level baseline; среднее число шагов
снизилось с 6.4 до 4.8. В абляции `task + state` обошёл `task-only` на Shopping
34.6% vs 30.3%, Reddit 35.9% vs 32.6%, Map 32.3% vs 30.8%.

**Доказывает:** для позднего routing описание должно представлять не только
класс задачи, но и наблюдаемое состояние применимости.

**Не доказывает:** retrieval запускался системой каждый шаг; модель не решала
сама, когда перечитать каталог. Web-only, без абляции wording или длины.

### COS-PLAY — applicability, completion и abort различаются

**22 апреля 2026, arXiv v1; 26 мая 2026, Agent Skills ’26.**
[Co-Evolving LLM Decision and Skill Bank Agents for Long-Horizon Tasks](https://arxiv.org/abs/2604.20987)
· [workshop version](https://openreview.net/pdf/b9e4edcb3ee1fe01c4af12d1af1f47af1844f9b1.pdf)

В каждый момент агент хранит state summary, intention и active skill; он может
продолжить skill или выбрать новый, когда текущий недоступен, исчерпан или
неэффективен. Интерфейс skill разделяет `Summary`, `Pre-condition`, `Plan`,
`Success/Abort Criteria` и ожидаемое изменение состояния.

**Доказывает:** одного purpose недостаточно, чтобы различить «вызвать сейчас»,
«продолжить» и «сменить». Для stateful skill нужны условия применимости и
окончания.

**Не доказывает:** одновременно менялись retrieval, policy и skill bank;
описание не было независимой переменной.

### PlanBench-XL — late discovery следует за новым missing input

**21 июня 2026, arXiv v1.** [PlanBench-XL: Evaluating Long-Horizon Planning of
LLM Tool-Use Agents in Large-Scale Tool Ecosystems](https://arxiv.org/html/2606.22388)

В 327 задачах с 1,665 tools агент может повторно искать capability по уже
доступным входам или требуемому следующему выходу. Новые tool results создают
следующий derived subgoal. Количество открытых промежуточных типов данных сильно
связано с успехом (`r=0.902`), но число retrieval-вызовов само по себе — нет.

**Вывод:** хороший поздний trigger называет конкретный недостающий вход,
возникший артефакт или требуемый следующий выход; «используй чаще» не является
стратегией.

## Direct: Что Должно Быть В Коротком Description

### SkillRouter — функция и различия важнее сырого metadata

**20 июля 2026, arXiv v5.** [SkillRouter: Skill Routing for LLM Agents at
Scale](https://arxiv.org/html/2603.22455v5)

На registry примерно из 80,000 skills routing только по `name + description`
потерял 37–44 п.п. Hit@1 относительно all-field routing. Сжатые из body
descriptions длиной 40–60 слов восстановили значительную часть качества, но
остались на 7–21 п.п. ниже all-field. Разрыв сохранялся и для descriptions
длиннее 35 слов: сама длина проблему не решает.

Oracle-description отвечало на четыре вопроса:

- что skill делает;
- когда агент должен его использовать;
- чем он отличается;
- какие конкретные операции, inputs/outputs и domain его различают.

В 75 expert-verified core queries и 256 supplementary queries были hard
distractors: тот же domain, но другая функция; та же technology, но другое
применение; чрезмерно общий skill. 88 indirect queries запрещали слова из name
и description и описывали проблему или цель пользователя.

**Доказывает:** description должна выражать операционную функцию и
дискриминаторы, а eval — содержать непрямые positives и функциональные
near-misses.

**Не доказывает:** тестировался initial-task routing. `40–60` слов — setting
этого эксперимента, не универсальный optimum и не доказанный лимит runtime.

### JTPRO — чинить локальный collision, а не раздувать все descriptions

**20 апреля 2026, arXiv v1.** [JTPRO: Joint Tool and Prompt Optimization for
LLM-Based Agents](https://arxiv.org/html/2604.19821)

Rollout-driven optimizer изменил только 55 из 500 tool descriptions; средняя
длина выросла с 86.1 до 100.1 символа. Правки добавляли parameter guidance,
явное preference, отрицательные constraints и cross-tool references. Система
дала 5–20% relative improvement OSR над baselines.

**Вывод:** редактировать description по наблюдаемому miss/collision и ближайшей
границе, а не добавлять общий перечень случаев «на всякий случай».

**Ограничение:** совместно оптимизировались global prompt и schemas; эффект
description отдельно не идентифицирован.

### Tool irrelevance — тематическое и структурное сходство перетриггеривает

**13 апреля 2026, arXiv v1.** [Do LLMs Know Tool
Irrelevance?](https://arxiv.org/html/2604.11322)

Ошибочные tool calls были ниже 0.2% для случайных нерелевантных tools, но
доходили до 41.9% при структурном сходстве и до 90.4% при усилении alignment.

**Вывод:** negative eval должен сохранять лексику, структуру и домен positive,
меняя только смысловую применимость. Лёгкий unrelated negative ничего не
проверяет.

### SkillRet — сигнал capability теряется в длинном запросе

**7 мая 2026, arXiv v1.** [SkillRet: Task-Specific Skill Retrieval for
LLM Agents](https://arxiv.org/html/2605.05726)

Benchmark содержит 17,810 skills, 63,259 training queries и 4,997 eval queries;
task-specific retriever дал +13.1 NDCG@10 над сильнейшим prior baseline. Запросы
не называли skill, а потребность следовала из сценария; 54% задач были
multi-skill.

**Вывод:** проверять indirect intent и derived need, а не только совпадение с
именем. Это retrieval benchmark, не late-invocation experiment.

## Runtime: Может Ли Agent Выбрать Skill Позже

### Codex — может внутри turn, но host не обещает событие

**11 августа 2026, OpenAI Codex commit `279b932`.**
[catalog trigger contract](https://github.com/openai/codex/blob/279b93242cfef379e65da97e87e44b83c5934fd7/codex-rs/ext/skills/src/catalog_prompt.rs#L3-L25)
· [catalog budget and truncation](https://github.com/openai/codex/blob/279b93242cfef379e65da97e87e44b83c5934fd7/codex-rs/ext/skills/src/render.rs#L16-L23)
· [round-robin prefix allocation](https://github.com/openai/codex/blob/279b93242cfef379e65da97e87e44b83c5934fd7/codex-rs/ext/skills/src/render.rs#L314-L355)

Runtime показывает модели каталог `name + description + locator` и требует
использовать skill, если текущая задача явно соответствует description. Один
description ограничен 1,024 символами; общий metadata budget — до 8,000
символов или 2% context window. При переполнении место распределяется по
descriptions равномерно, поэтому сначала исчезают их хвосты.

Датированное описание multi-step agent loop подтверждает, что tool outputs и
prior conversation state возвращаются модели на следующих шагах одного turn:
[OpenAI, From model to agent, 11 марта 2026](https://openai.com/index/equip-responses-api-computer-environment/).

**Следствие из реализации:** после tool result модель снова имеет текущую
историю и каталог и технически может обнаружить новый match. Host не запускает
semantic classifier заново при каждом событии; отдельной гарантии late-trigger
recall нет. Между пользовательскими turns прежний выбор skill нельзя считать
перенесённым: задача должна совпасть заново или skill должен быть назван.

### Claude Code — proactive late call есть, delayed recall не измерен

**10 августа 2026, Anthropic Claude Code 2.1.227.**
[tag commit `54cc51a`](https://github.com/anthropics/claude-code/commit/54cc51a08a5d3900e5abd02ad75a2ce46f3f008c)
· [official platform artifact](https://registry.npmjs.org/@anthropic-ai/claude-code-darwin-arm64/-/claude-code-darwin-arm64-2.1.227.tgz)
· [fresh changelog](https://github.com/anthropics/claude-code/blob/v2.1.227/CHANGELOG.md#L1990-L2015)

В version-pinned artifact каталог one-line descriptions доставляется как
conversation metadata и остаётся доступен на следующих agentic samples. Prompt
модельного `Skill` tool требует вызвать его, когда `task at hand` покрывается
доступным skill; autonomous invocation имеет telemetry trigger
`claude-proactive`. Changelog от **30 апреля 2026** публично фиксирует
`claude_code.skill_activated` с triggers `user-slash`, `claude-proactive` и
`nested-skill`.

В 2.1.227 default catalog budget — 1% context window, maximum одного
description — 1,536 символов; при переполнении часть skills остаётся только с
именем. Это ещё одна причина ставить phase/state discriminator в начало.

**Доказывает:** Claude может model-autonomously вызвать skill после того, как
новая подзадача стала `task at hand`, а не только по исходному user prompt.

**Не доказывает:** runtime не публикует delayed-trigger recall и не содержит
отдельного host event detector «началась фаза X». Точный момент остаётся
вероятностным semantic match модели.

### Реальный OpenAI pattern — phase + event + guard + anti-trigger

**9 июля 2026, OpenAI Codex Security plugin 0.1.11, commit `271262`.**
[commit](https://github.com/openai/plugins/commit/2712622050dde002f7dc7db2f57bb469fd9f8283)
· [finding-discovery](https://github.com/openai/plugins/blob/2712622050dde002f7dc7db2f57bb469fd9f8283/plugins/codex-security/skills/finding-discovery/SKILL.md)
· [validation](https://github.com/openai/plugins/blob/2712622050dde002f7dc7db2f57bb469fd9f8283/plugins/codex-security/skills/validation/SKILL.md)
· [propose-security-hardening](https://github.com/openai/plugins/blob/2712622050dde002f7dc7db2f57bb469fd9f8283/plugins/codex-security/skills/propose-security-hardening/SKILL.md)

Official descriptions используют четыре разных сигнала:

- `Codex is already in the ... phase` — текущее состояние workflow;
- явный user request — стартовый match;
- `after ... scan with reportable findings` — возникшее событие/артефакт;
- `when the top-level ... workflow requests` — guard;
- `Do not use as the primary trigger for full ... scans` — граница с parent.

Это прямой vendor precedent для state/event-trigger descriptions, но не
публичный A/B eval их recall.

### Anthropic optimizer — сильный eval workflow, но не late-trigger study

**6 марта 2026, Anthropic skills commit `b0cbd3d`.**
[skill-creator description optimization](https://github.com/anthropics/skills/blob/b0cbd3df1533b396d281a6886d5132f623393a9c/skills/skill-creator/SKILL.md#description-optimization)

Official workflow называет description главным trigger mechanism и предлагает
20 реалистичных eval queries: 8–10 positives и 8–10 hard near-miss negatives;
casual phrasing, typos, implicit intent, uncommon cases и collisions; три
повтора каждого query; split 60/40; до пяти итераций; выбор лучшей версии по
held-out score. Guidance советует достаточно assertive wording, поскольку
Claude склонен undertrigger.

**Ограничение:** query classifier eval не создаёт состояние внутри длинной
траектории. «Pushy» wording может повысить fire rate вместе с false positives;
precision и момент вызова надо измерять отдельно.

Есть две свежие engineering caveats:

- [issue #556, 7 марта 2026](https://github.com/anthropics/skills/issues/556)
  сообщает ложный 0% trigger rate из-за отличий загрузки skills в `claude -p`;
- [issue #1149, 16 мая 2026](https://github.com/anthropics/skills/issues/1149)
  сообщает crash improve-step без `ANTHROPIC_API_KEY`.

Оба issue открыты на дату среза. Успех harness-команды нельзя принимать за
доказательство реального runtime trigger без наблюдаемого чтения/call trace.

## Real Harnesses: Почему Fire Rate Недостаточен

### Skill-Use

**5 августа 2026, arXiv v1.** [Skill-Use: Can LLMs Actually Use Skills in
Agentic Harnesses?](https://arxiv.org/html/2608.04828)

79 реальных skills, 177 исполняемых задач, 8 LLMs, 2 harnesses. Агент сначала
получает task, name, short description и path, а полный skill должен извлечь в
любой момент execution trajectory. Лучшая Skill Use score — 0.613. Авторы
разделяют Trigger, Compliance и Boundary; broad overlapping descriptions
создают wrong-skill calls, а topical overlap провоцирует out-of-scope use.

**Вывод:** измерять отдельно позднее чтение, выполнение требований и
сдерживание. Факт вызова не равен пользе.

### Wild benchmark

**6 апреля 2026, arXiv v1.** [How Well Do Agentic Skills Work in the
Wild](https://arxiv.org/html/2604.04323)

34,198 public skills, 84 tasks, три повтора. Для Claude force-loaded curated
skills дали 55.4% pass, autonomous curated — 51.2%, curated + distractors —
43.5%. Все curated skills загрузились только в 49% trajectories и в 31% с
distractors. Query-specific refinement поднимал load rate, но не всегда pass
rate: больше вызовов не гарантировало лучший результат.

**Вывод:** optimize utility and timing, не trigger rate в изоляции.

### Skill Retrieval Augmentation

**7 июня 2026, arXiv v3.** [Skill Retrieval Augmentation for Agentic
AI](https://arxiv.org/html/2604.24594)

26,262 skills, 5,400 instances, 636 gold skills. Progressive-disclosure agents
могут загружать skill во время reasoning, но модели часто загружают его с
похожей частотой независимо от того, нужна ли capability задаче.

**Вывод:** доступность late loading не создаёт need-awareness. Это benchmark
initial-request retrieval, поэтому он не доказывает state-trigger wording.

## Adjacent Evidence: Полезно, Но Не Прямой Ответ

- **Июль 2026 — [Dynamic Tool Dependency
  Retrieval](https://aclanthology.org/2026.findings-acl.1680/).** Retrieval по
  исходной задаче и evolving tool plan дал +23%–104% function-call success над
  static retrievers. Tools, не `SKILL.md`; wording не менялся.
- **Июль 2026 — [Beyond Single-Shot: Multi-step Tool Retrieval via Query
  Planning](https://aclanthology.org/2026.findings-acl.2090/).** Планировщик
  создаёт queries под derived subtasks. Подзадачи выводятся при planning; это не
  autonomous skill invocation.
- **16 июня 2026 — [SkillMigrator](https://arxiv.org/html/2606.17645).** Выбор
  по subtask + live page structure снизил LLM-actions успешной web trajectory
  на 8–10%. Нет сравнения с initial-only retrieval.
- **27 мая 2026 — [Graph-of-Skills
  v3](https://arxiv.org/abs/2604.05333).** Dependency-aware bundle дал до
  +25.55% reward и −56.72% tokens. Для обязательной цепочки нужен
  graph/orchestrator, а не одно description.
- **Июль 2026 — [Current Agents Fail to Leverage World Model as a Tool for
  Foresight](https://aclanthology.org/2026.acl-long.623/).** Некоторые агенты
  вызывают simulation реже 1%; forced use ухудшает score до 5%. Это tool
  foresight, не skill metadata.
- **Июль 2026 — [UI-Copilot](https://aclanthology.org/2026.acl-long.904/).**
  Раздельная оптимизация selection и multi-turn execution дала +17.1 п.п.
  AndroidWorld. Это learned GUI policy, не prose description.
- **Июль 2026 — [ToolOmni](https://aclanthology.org/2026.acl-long.1736/).**
  Proactive retrieval внутри reasoning loop и joint retrieval/execution
  улучшили end-to-end success на 10.8%. Это tool training, не automatic
  `SKILL.md` trigger.
- **7 июля 2026 — [Task Decomposition-Guided
  Reranking](https://arxiv.org/html/2607.06283).** Планировщик строит execution
  graph под предсказанные intermediate states до execution; это не событие
  живой траектории.

## Что Из Корпуса Следует Для Authoring

### Рабочая Формула

Это **выведено** из SGDR, ProactAgent, SkillRouter, Codex runtime и OpenAI
Security pattern; ни один источник не тестировал формулу целиком:

> `Use when <observable state/event during work> makes <specific capability>
> necessary, even without an explicit user request. <Operation> produces
> <observable outcome>. Do not use for <nearest parent/sibling case>.`

Для цели «когда агент приступил к определённой части работы» формула становится
phase-conditioned:

> `Use when <work type> has reached <target phase>, evidenced by <artifact or
> state>. <Operation> produces <phase-specific delta>. Do not use before
> <boundary> or for <nearest sibling phase>.`

Порядок важен: state/capability должны пережить обрезку хвоста. `40–60`
английских слов — разумный первый candidate из SkillRouter, но не quota. Хорошее
описание закончено, когда каждая оставшаяся часть меняет решение `use now`,
`not yet` или `use neighbor`.

### Что Называть Trigger

Сильные сигналы:

- phase transition: работа дошла до проверки, решения, handoff или completion;
- artifact event: появился candidate, diff, failure, conflict или missing input;
- derived subtask: продолжение активной цели теперь требует отдельной операции;
- failed/ineffective active route: текущий способ исчерпан;
- upstream event + guard: родительский workflow создал условие и запросил
  дочернее действие.

Слабые сигналы: «сложная задача», «когда полезно», «для качества», «время от
времени», список тематических существительных и повтор имени skill.

### Не Обещать

- Точная description не гарантирует, что модель перечитает каталог в нужный
  момент.
- Больше automatic calls не означает больше успешных задач.
- Вызов не доказывает adherence body.
- Initial-query eval не доказывает late trigger.
- Если moment-of-use обязателен, его нельзя оставлять только probabilistic
  model routing.

### Семантика И Hooks — Не Бинарная Развилка

Это **архитектурный вывод**, а не проверенный paper result:

1. Сначала проверять pure semantic routing по phase/state description.
2. Если late recall нестабилен, общий lifecycle checkpoint может потребовать
   заново сопоставить **весь каталог** с текущим состоянием, не называя skill.
   Выбор остаётся смысловым.
3. Только при неприемлемой цене пропуска жёстко маппить event на конкретный
   skill hook'ом или orchestrator'ом.

Так hook может вернуть внимание к semantic router, не подменяя его таблицей
`phase → skill`.

## Итог

Наиболее доказательная стратегия — сделать короткое description не похожим на
список возможных просьб, а похожим на **state-recognition rule**: какая функция
нужна, какое наблюдаемое состояние уже наступило, что именно skill изменит и
какой ближайший случай он не должен перехватывать. Затем проверять не только
«вызвался ли», а **не вызвался ли раньше**, вызвался ли вскоре после события и
помог ли выполнить задачу.
