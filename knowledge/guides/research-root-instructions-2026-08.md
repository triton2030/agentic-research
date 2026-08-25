---
description: "Датированный evidence snapshot о содержании, объёме, доставке, проверке и безопасности root instructions AGENTS.md и CLAUDE.md."
---

# Root Instructions — Research 2026-08

Срез публикаций с 25 июня по 25 августа 2026 года о persistent context files,
system prompts и always-on instructions coding agents. Поиск и чтение
источников выполнены только через Keenable.

Это Research and Evidence Report, а не инструкция и не portable-канон.
Практическими выводами владеют
[`perfect-system-prompts.md`](perfect-system-prompts.md),
[`perfect-context-engineering.md`](perfect-context-engineering.md) и
[`agents/runtime-layer.md`](../agents/runtime-layer.md).

## Модельная Граница

Cutoff владельца — 25 февраля 2026 года. Из model-specific результатов ниже
прямо допустимы для target-вывода только GPT-5.5, Claude Opus 5 и Claude Fable
5. Sonnet 4.6 (17 февраля), GPT-5-mini, Gemini 2.5 Flash, GPT-5.2, GPT-4o,
Llama и версии без подтверждённой даты — historical/non-target evidence.

| Evidence | Статус для target-вывода |
| --- | --- |
| Context-file ablation | GPT-5.5 row — target-supported; Sonnet 4.6 row — historical |
| Instruction Stacking Collapse | Historical/non-target panel; только гипотеза о conflict mechanism |
| VeyraBench | Model panel здесь не pinned по cutoff; формат/scale rates не переносить |
| Anthropic Claude 5 report | **Target-supported vendor evidence**, но без открытой методологии |
| Bad Memory | GPT-5.5 rows — target-supported; остальные rows — historical/non-target |
| Guardrails as Scapegoats | Historical/non-target |
| CAPO | Model-unpinned для этой границы; переносится только multi-threshold evaluation design |
| Configuration Smells | Model-independent observational corpus, не причинный эффект |

Следовательно, target-supported часть показывает три вещи: GPT-5.5 не получил
общего роста correctness от always-on context в малой выборке; Claude 5 vendor
сократил always-on system prompt; GPT-5.5 подвержен некоторым persistent-file
атакам. Остальные числа сохраняются для дизайна проверки и не поддерживают
portable правило о текущих моделях.

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

### Стек Правил Разрушается Через Конфликты

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
5. **Instruction budget:** считать active obligations и pairwise conflicts,
   а не только строки или токены.
6. **Mechanism boundary:** hard invariant обеспечивается hook, schema,
   validator, sandbox, permission или test; root prose — не enforcement.
7. **Integrity:** auto-loaded root и memory files — privileged persistent
   surface; изменение проверяет source, authority и diff.
8. **Evaluation:** сравнивать `none`, `always_on` и `selective`; измерять
   correctness, cost, tool use и каждый обязательный behavior отдельно.
9. **Model conditioning:** placement, compilation и examples проверяются на
   target model.

## Contradiction Audit — 25 Августа 2026

| Current owner | Вердикт |
| --- | --- |
| `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, project `AGENTS.md` | Прямого противоречия нет: 16, 26 и 81 строк; persistent owner/project Delta, а не auto-generated repository tour |
| [`perfect-system-prompts.md`](perfect-system-prompts.md) | Совместим: отделяет stable frame от task spec, удаляет повторы, obsolete process и runtime compensation |
| [`perfect-context-engineering.md`](perfect-context-engineering.md) | Совместим; изменений не потребовал, integrity-boundary остаётся в этом датированном evidence snapshot |
| [`authoring-canon.md`](../practical-guides/how-to-write-skills/authoring-canon.md) | Совместим: no-skill comparator, progressive disclosure, interface-first tools и workflow только для order-sensitive failure |
| [`wisdom-skills-plugins.md`](../wisdom-skills-plugins.md) | Уточнён overbroad перенос постоянного индекса: resident delivery — крайний вариант, не enforcement |
| [`science/how-to-make-llm-obey.md`](../../science/how-to-make-llm-obey.md) | Числовой ориентир уточнён cost/security/evaluation boundary; исходный замер сохранён |

## Что Не Доказано

- Что root instructions вообще не повышают correctness.
- Что любой root-файл нужно сократить на 80% или до 200 строк.
- Что Markdown, plain text, system placement или user placement универсально
  лучше.
- Что on-demand delivery всегда лучше always-on.
- Что один benchmark переносится на все models, repositories и long-horizon
  tasks.
- Что prose может заменить runtime enforcement для high-risk действия.

## Confidence

| Claim | Confidence | Причина |
| --- | --- | --- |
| Generic repository tour не имеет доказанного correctness lift | Medium | Прямой, но малый paired study + vendor guidance |
| Большой стек конфликтующих правил снижает adherence | High в synthetic constraints | Два verifier-based benchmarks |
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
