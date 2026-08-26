---
description: "Датированный evidence snapshot о содержании, объёме, доставке, проверке и безопасности root instructions AGENTS.md и CLAUDE.md."
---

# Root Instructions — Research 2026-08

Срез публикаций с 25 июня по 26 августа 2026 года о persistent context files,
system prompts и always-on instructions coding agents. Исходный поиск и чтение
выполнены через Keenable; дополнение 26 августа найдено отдельным литературным
проходом и сверено по телам первичных работ.

Это Research and Evidence Report, а не инструкция и не portable-канон.
Практическими выводами владеют
[`perfect-system-prompts.md`](perfect-system-prompts.md),
[`perfect-context-engineering.md`](perfect-context-engineering.md) и
[`agents/runtime-layer.md`](../agents/runtime-layer.md).

## Модельная Граница

Текущий рабочий набор владельца — GPT-5.6, Claude Opus 5 и Claude Fable 5.
GPT-5.5, Claude 4.x, GPT-5-mini, Gemini 2.5 Flash, GPT-5.2, GPT-4o, Llama и
версии без точного совпадения с этим набором — historical/non-target evidence.

| Evidence | Статус для target-вывода |
| --- | --- |
| Context-file ablation | GPT-5.5 и Sonnet 4.6 — historical evidence |
| Instruction Stacking Collapse | Historical/non-target panel; только гипотеза о conflict mechanism |
| VeyraBench | Model panel не совпадает с текущим target set; формат/scale rates не переносить |
| CSE | GPT-5.5 и Claude 4.7 — historical evidence; constraint taxonomy и multiplicative collapse — гипотеза механизма, не target threshold |
| Harness-IF | Opus 4.7/GPT-5.5 и другие non-target builds; surfaces и against-prior — design evidence, не универсальная иерархия |
| Anthropic Claude 5 report | **Target-supported vendor evidence** для Claude 5, но без открытой методологии и без раздельного benchmark Opus/Fable |
| Bad Memory | GPT-5.5 и Claude 4.x rows — historical evidence |
| Guardrails as Scapegoats | Historical/non-target |
| CAPO | Model-unpinned для этой границы; переносится только multi-threshold evaluation design |
| Configuration Smells | Model-independent observational corpus, не причинный эффект |

Следовательно, прямой target-supported материал здесь ограничен vendor-отчётом
Claude 5 о сокращении always-on system prompt. Результаты GPT-5.5, Claude 4.x
и несовпадающих панелей сохраняются как historical/design evidence: они задают
гипотезы и форму проверки, но не числовое portable-правило для GPT-5.6, Opus 5
или Fable 5.

## Ответ В Одной Фразе

**Root-файл оправдан как короткая persistent Delta: неочевидные gotchas,
локальные границы, дорогие команды и точные проверки; repository tour,
общеизвестные советы, task-specific workflows и механически проверяемые правила
платят постоянный context tax без доказанного роста correctness.**

## Главные Факты

### Context Files Не Показали Общего Роста Correctness

[Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250)
сравнил `none`, `always_on` и `selective` delivery на 17 реальных задачах из
трёх Python repositories, Claude Code и Codex CLI, 288 evaluated runs.

| Agent | None | Always-on | Selective |
| --- | ---: | ---: | ---: |
| Claude Code / Sonnet 4.6 | 53.3% | 55.6% | 55.6% |
| Codex / GPT-5.5 | 58.8% | 56.9% | 52.9% |

Различия не были значимыми: `p = 1.000` у Claude и `p = 0.66` у Codex.
Manipulation probe на 36 cells не нашёл случая, где реальный `AGENTS.md`
стабильно превратил near-miss в pass.

Контекст всё же менял способ работы. На `opshin` предупреждения о дорогом test
suite сократили wall-clock Claude примерно на 24%, а слепые полные
`pytest`-прогоны — с 3.67 до 1.67 при selective delivery.

**Граница:** выборка мала — 15–17 задач и три repositories. Работа ограничивает
эффект correctness диапазоном примерно до 10–15 п.п., но не доказывает ноль и
не тестирует специально написанные task-critical root rules.

### Стек Правил Разрушается, Но Механизм Не Сведён К Конфликтам

[Instruction Stacking Collapse](https://arxiv.org/abs/2608.02639) складывает
до 20 verifier-checked инструкций:

| Model | 1 правило | 5 правил | 20 правил |
| --- | ---: | ---: | ---: |
| Claude Sonnet 4.6 | 96.4% | 82.7% | 60.4% |
| GPT-5-mini | 96.4% | 84.5% | 20.0% |
| Gemini 2.5 Flash | 95.9% | 82.3% | 43.3% |

Из 216 логически совместимых пар 15.3% проваливались чаще индивидуального
ожидания; ещё 15 пар были логически несовместимы. Valid JSON, например,
конфликтовал с Markdown headings и несколькими структурными требованиями.

LLM compiler дал `+11.8` п.п. GPT-5-mini и `+5.0` Gemini, но `−6.7` п.п.
Sonnet 4.6. Semantic compilation помогает слабым targets, но не является
универсальной ручкой для frontier model.

[Constraint Saturation Evaluation / CSE](https://arxiv.org/abs/2608.12426)
даёт другой механизм на 15 моделях, 36 типах ограничений и `k=1–12`. У GPT-5.5
strict all-pass становится ниже 50% при семи ограничениях, у Claude 4.7 Opus —
при шести; к `k>=10` success почти нулевой у всей панели. Но co-failures в CSE
почти независимы: небольшое падение надёжности каждого правила перемножается,
а остаточная связь в основном идёт через общий output feature. Structural
constraints деградируют примерно вдвое быстрее lexical; непрерывный контроль
во время генерации предсказывает потерю лучше одной категории правила.

Работы сходятся на эффекте accumulation и расходятся в объяснении основного
механизма. Поэтому root-аудит должен искать и логические конфликты, и число
независимо активных обязательств; объявлять pairwise conflict универсальной
причиной нельзя.

### Нагрузка — Не Однородные «Единицы Знаний»

Instruction-count benchmarks считают обязательства, которые надо выполнить
совместно. Справочный факт платит другую цену: его надо сначала извлечь, а
удерживать и проверять на каждом действии — только если из него выведено
поведенческое правило.

| Содержимое root | Основной риск |
| --- | --- |
| `код лежит в src/` | retrieval нужного факта в нужный момент |
| `не редактируй tests/` | постоянное распознавание применимости и veto действия |
| `перед каждым edit выполни A→B→C` | несколько зависимых обязательств + состояние процедуры |
| `минимизируй diff` | широкий criterion, повторно влияющий на выбор маршрута |

Одна строка может содержать несколько атомарных требований; сотня справочных
фактов не равна сотне одновременно активных constraints. И наоборот, один
короткий запрет, противоречащий default модели, может быть дороже длинной
ориентировки.

[Harness-IF](https://arxiv.org/abs/2608.11727) подтверждает обе оговорки на
operational rules coding agents. Against-prior accuracy у каждой из 12 моделей
была ниже общей на 3.6–7.4 п.п. (в среднем 5.81). В отдельном конфликтном
пилоте system prompt, project file и user instruction pooled-уровнем опередили
tool и skill descriptions; prompt depth не объяснил precedence. Это не
универсальный surface ranking: controlled pilot мал, а main-panel surfaces
имели разную admissibility и состав правил.

### Формат Не Спасает Перегруженную Инструкцию

[Prompt Design at Scale / VeyraBench](https://arxiv.org/abs/2607.19257)
проверил 10–160 правил, четыре формата и system/user placement: 4 800 trials
на пяти моделях.

- perfect-response rate стал практически нулевым к 80 правилам и нулевым к
  160 во всех форматах и placements;
- Markdown не имел устойчивого преимущества;
- placement влиял не меньше формата, но направление зависело от модели;
- заметный обвал начинался примерно после 20–40 synthetic rules.

Это exact-string constraints в одном синтетическом домене. Работа опровергает
магическое форматирование, но не задаёт универсальный line или character cap.

### Claude 5 Перенёс Контекст Из Always-On Prompt В Другие Surface

[Anthropic: The new rules of context engineering](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
сообщает, что для Opus 5 и Fable 5 удалено более 80% Claude Code system prompt
без измеримой потери на внутренних coding evaluations.

Рекомендации Anthropic:

- judgement и окружающий код вместо множества defensive rules;
- lightweight `CLAUDE.md`: назначение repo кратко, большинство токенов —
  неочевидные gotchas;
- review и verification как selectively loaded skills;
- tool-use инструкции в schema/description самого tool;
- code, tests, HTML artifacts и rubrics вместо пересказа;
- не повторять правило в system prompt, tool descriptions и root files.

Это vendor report без опубликованных tasks, sample size и confidence
intervals. Число 80% нельзя превращать в норму для любого root-файла.

### Auto-Loaded Root Files — Persistent Attack Surface

[Bad Memory](https://arxiv.org/abs/2607.14611) внедрял payloads в
`CLAUDE.md`, `AGENTS.md`, behavior и knowledge files Claude Code и Codex.

Примеры single-probe attack success:

- credential exfiltration в auto-loaded root: 80% Haiku 4.5, 30% GPT-5.2,
  0% Opus 4.7 и GPT-5.5;
- vulnerable-package instruction: 90% Opus 4.7 и 80% GPT-5.5;
- brand-targeting behavior: 100% GPT-5.5.

Отказ модели не очищал persistent state. У Opus 4.7 средний multi-attack ASR
был 18.3%, но persistence — 93.3%: опасная строка оставалась для следующей
сессии или другой модели.

Следствие: изменения high-impact root/memory files требуют provenance, exact
diff review и permission boundary. Retrieved external content нельзя
автоматически продвигать в trusted instructions.

### Generic Safety Prose Может Создать Failure Vocabulary

[Guardrails as Scapegoats](https://arxiv.org/abs/2607.19449) добавил в system
prompt общую фразу о privacy и data security при silent tool failures. Доля
unfaithful safety refusals выросла в 15.6 раза: с 0.25% до 3.95%, `p < 0.001`.

Работа использует более старые GPT-4o/Llama модели и узкий synthetic setup.
Она не доказывает, что safety instructions вредны; она показывает, что лозунг
не заменяет typed error handling, exact policy и наблюдаемый tool state.

### Prompt Следует Проверять По Нескольким Порогам

[CAPO](https://arxiv.org/abs/2608.16068) оптимизирует system prompt по отдельным
thresholds: task success, tool use, escalation, prompt/trajectory length,
safety и format. CAPO достиг всех заданных thresholds во всех шести
комбинациях `tau2-bench domain × task model`; fixed-score и Pareto baselines —
максимум в одной комбинации.

Высокий task score сам по себе не оправдывает лишние tool calls, over-refusal,
небезопасность или раздувание prompt.

### Configuration Smells — Наблюдение, Не Причинность

[Configuration Smells in AGENTS.md Files](https://arxiv.org/abs/2606.15828),
поданный до окна и обновлённый 30 июля, просмотрел 100 популярных root files:

- Lint Leakage — 62%;
- Context Bloat — 42%;
- Skill Leakage — 35%;
- хотя бы один smell — 91% файлов.

Это observational catalog и automated detectors. Число 200 строк из taxonomy
не является доказанным performance threshold.

## Сведённые Следствия Для Авторинга

1. **Resident admission:** строка остаётся в root, если применяется к
   большинству задач scope, не выводится быстро из repo и меняет observable
   action/check.
2. **Persistent Delta:** приоритет — gotchas, дорогие команды, authority,
   deliberate exceptions, non-obvious validation и настоящие red lines.
3. **Не root:** repository tour, package inventory, общие best practices,
   lint/style rules, one-off task, длинный workflow и редкие examples.
4. **Progressive disclosure:** task/domain procedure живёт в skill/reference;
   tool behavior — в schema/description.
5. **Instruction budget:** считать active obligations, maintenance cost,
   зависимости, расхождение с model default и pairwise conflicts, а не строки,
   токены или все справочные факты как равные слоты.
6. **Mechanism boundary:** hard invariant обеспечивается hook, schema,
   validator, sandbox, permission или test; root prose — не enforcement.
7. **Integrity:** auto-loaded root и memory files — privileged persistent
   surface; изменение проверяет source, authority и diff.
8. **Evaluation:** сравнивать `none`, `always_on` и `selective`; измерять
   correctness, cost, tool use и каждый обязательный behavior отдельно.
9. **Model conditioning:** placement, compilation и examples проверяются на
   target model.

## Contradiction Audit — 26 Августа 2026

| Current owner | Вердикт |
| --- | --- |
| `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, project `AGENTS.md` | Прямого противоречия нет: 16, 26 и 81 строк; persistent owner/project Delta, а не auto-generated repository tour |
| [`perfect-system-prompts.md`](perfect-system-prompts.md) | Совместим: отделяет stable frame от task spec, удаляет повторы, obsolete process и runtime compensation |
| [`perfect-context-engineering.md`](perfect-context-engineering.md) | Совместим; изменений не потребовал, integrity-boundary остаётся в этом датированном evidence snapshot |
| [`authoring-canon.md`](../practical-guides/how-to-write-skills/authoring-canon.md) | Совместим: no-skill comparator, progressive disclosure, interface-first tools и workflow только для order-sensitive failure |
| [`wisdom-skills-plugins.md`](../wisdom-skills-plugins.md) | Уточнён overbroad перенос постоянного индекса: resident delivery — крайний вариант, не enforcement |
| [`science/how-to-make-llm-obey.md`](../../science/how-to-make-llm-obey.md) | Уточнены неоднородность правил, disagreement о механизме и граница `constraint ≠ fact`; старый замер сохранён как отдельная постановка |

## Что Не Доказано

- Что root instructions вообще не повышают correctness.
- Что любой root-файл нужно сократить на 80% или до 200 строк.
- Что Markdown, plain text, system placement или user placement универсально
  лучше.
- Что on-demand delivery всегда лучше always-on.
- Что один benchmark переносится на все models, repositories и long-horizon
  tasks.
- Что существует общий лимит «10–20 единиц знаний»: constraints, retrieval
  фактов и процедуры измеряют разные способности.
- Что информация бесплатна: её retrieval и применение могут провалиться; не
  доказано лишь равенство её стоимости активному ограничению.
- Что prose может заменить runtime enforcement для high-risk действия.

## Confidence

| Claim | Confidence | Причина |
| --- | --- | --- |
| Generic repository tour не имеет доказанного correctness lift | Medium | Прямой, но малый paired study + vendor guidance |
| Большой стек активных правил снижает adherence | High в synthetic constraints | Три verifier-based benchmarks |
| Pairwise conflicts — главный механизм collapse | Medium–Low | Instruction Stacking Collapse поддерживает; CSE находит почти независимое накопление |
| Тип и maintenance demand меняют стоимость правила | Medium–High в synthetic constraints | CSE: structural ≈2× lexical; противоречие default подтверждает Harness-IF |
| Progressive disclosure уменьшает resident tax | Medium–High | Vendor deployment + независимый skill evidence |
| Root prose не является hard enforcement | High | Runtime и security experiments |
| Auto-loaded files требуют integrity review | High | Stored-injection на Claude Code и Codex |
| Конкретный безопасный line/token cap | Low | Format, placement и model effects нестабильны |

## Source Ledger

- [Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250) —
  root-context ablation; 28 июля 2026.
- [Instruction Stacking Collapse](https://arxiv.org/abs/2608.02639) — rule
  count, conflicts и compilation; 31 июля 2026.
- [Prompt Design at Scale](https://arxiv.org/abs/2607.19257) — format,
  placement и instruction-count scale; 22 июля 2026.
- [Large Language Models Can Follow Instructions, But Not Many at Once / CSE](https://arxiv.org/abs/2608.12426)
  — `k=1–12`, constraint taxonomy и multiplicative collapse; 12 августа 2026.
- [Harness-IF](https://arxiv.org/abs/2608.11727) — operational rules across
  instruction surfaces и against-prior control; август 2026.
- [Anthropic context engineering for Claude 5](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
  — first-party deployment report; 24 июля 2026.
- [Bad Memory](https://arxiv.org/abs/2607.14611) — persistent instruction-file
  injection; 16 июля 2026.
- [Guardrails as Scapegoats](https://arxiv.org/abs/2607.19449) — generic safety
  language ablation; 23 июля 2026.
- [CAPO](https://arxiv.org/abs/2608.16068) — constraint-aware prompt
  optimization; 18 августа 2026.
- [Configuration Smells in AGENTS.md Files](https://arxiv.org/abs/2606.15828)
  — observational root-file taxonomy; revised 30 июля 2026.

## Downstream Owners

- System prompts: [`perfect-system-prompts.md`](perfect-system-prompts.md).
- Context assembly: [`perfect-context-engineering.md`](perfect-context-engineering.md).
- Runtime enforcement: [`agents/runtime-layer.md`](../agents/runtime-layer.md).
- Instruction-carrier compliance:
  [`science/how-to-make-llm-obey.md`](../../science/how-to-make-llm-obey.md).
- Skills:
  [`research-skill-instruction-authoring-jun-aug-2026.md`](../practical-guides/how-to-write-skills/research-skill-instruction-authoring-jun-aug-2026.md).
