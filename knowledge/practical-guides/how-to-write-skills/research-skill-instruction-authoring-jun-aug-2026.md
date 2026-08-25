---
description: "Датированный evidence snapshot свежих исследований о содержании, загрузке и проверке Agent Skills и агентных инструкций."
---

# Skill And Instruction Authoring — Research 2026-06–08

Срез публикаций с 25 июня по 25 августа 2026 года. Использовать при создании,
сокращении и проверке `SKILL.md`, system prompts и других durable-инструкций.
Поиск и чтение источников выполнены только через Keenable.

Это Research and Evidence Report, а не portable-канон. Практическим контрактом
владеет [`authoring-canon.md`](authoring-canon.md); продвижение любого вывода в
канон требует отдельного решения и behavioral proof на рабочем model set.

## Модельная Граница

Cutoff владельца — 25 февраля 2026 года: более старые либо не pinned по точной
версии модели панели остаются historical/non-target evidence. Они могут
подсказать failure mode или дизайн comparator, но не доказывают поведение
текущих моделей.

| Раздел | Статус для target-вывода |
| --- | --- |
| Signal or Noise? | Mixed historical/non-target: в основных результатах есть GPT-5.1, а даты остальных точных версий здесь не подтверждены |
| Data Science skill ablations, SkillAlchemy, ACES | Model-unpinned/mixed: полезны для дизайна evaluation, не для прямого переноса rates |
| KDD framework | Mixed/unpinned; judge Sonnet 4.6 старше cutoff |
| ASI-Bench | **Target-supported:** GPT-5.5, GPT-5.6 Sol и Claude Opus 5 |
| SIGIL | Historical/non-target: GPT-4o и GPT-5 |
| Reusability corpus | Model-independent observation; defect frequencies не являются behavioral effect |

Поэтому единственный прямой target-model вывод этого обзора — полная локальная
процедура в сложной задаче заметно сильнее method-level guidance. Остальные
разделы обосновывают, **что измерять** — no-skill, length, routing, live lift,
conflicts и harness — но требуют нового прогона на рабочем model set до
продвижения в правило.

## Ответ В Одной Фразе

**Skill полезен не благодаря наличию или объёму, а когда он релевантен задаче,
добавляет отсутствующую локальную процедуру, загружается в нужный момент и
проверен сравнением с no-skill.** Generic, нерелевантный или постоянно
подмешиваемый skill может ухудшать результат и резко увеличивать стоимость.

## Главные Факты

### 1. Автоматическая Загрузка Skill Не Является Безопасным Дефолтом

[Signal or Noise?](https://arxiv.org/abs/2608.23067) сравнил 31 публичный
WebDev skill на 50 проектах и 1 000 упорядоченных задачах в четырёх моделях.
Загрузка target skill:

- снизила средний `Pass@2` на 1.3–4.2%;
- увеличила расход токенов на 72–394%;
- помогла только в 17–36% пар `skill × project`.

Length-matched control показал два разных механизма вреда: Sonnet и Qwen
страдали преимущественно от длины, GPT-5.1 и DeepSeek — от вводящего в
заблуждение содержания. Эффекты конкретного skill почти не переносились между
моделями: только 4% пар дали пользу всем четырём моделям.

В leave-one-out анализе самыми устойчиво полезными оказались короткие
anti-pattern rules. Positive rules были нейтральны в среднем, а code examples
помогали DeepSeek и Qwen, не меняли GPT-5.1 и вредили Sonnet.

**Граница:** это WebDev benchmark на публичных skills; результат не доказывает,
что любой skill вреден. Он доказывает необходимость routing, no-skill baseline,
length-matched control и проверки на каждой target model.

### 2. Generic LLM-Generated Skills Могут Не Добавлять Capability

[Do LLM-Generated Skills Make Better AI Data Scientists?](https://arxiv.org/abs/2607.07504)
провёл 10 584 запуска: 56 задач, девять model configurations и абляции core
procedure, examples и reference notes.

| Condition | Pass rate |
| --- | ---: |
| No-Skill | 68.3% |
| Full | 67.5% |
| Core-Only | 67.5% |
| Core + Examples | 68.5% |
| Core + References | 67.3% |
| Length-matched irrelevant control | 66.9% |

Ни full skill, ни одна абляция не дали статистически надёжного улучшения;
все `p ≥ 0.396`. Full превысил length-matched control лишь на 0.6 п.п.,
95% CI `[−2.2, 3.4]`, `p = 0.775`.

**Граница:** skills были single-shot, плоскими и family-level; исследование не
проверяет retrieval, multi-turn execution и expert-authored task-specific
skills. Оно опровергает дефолт «сгенерировать общий skill и всегда prepend».

### 3. Evidence-Grounded Skill Creation Может Сравняться С Human-Curated

[SkillAlchemy](https://arxiv.org/abs/2608.23417) строит skill в четыре
различимых слоя:

1. обнаруживает требования, пропущенные в кратком brief;
2. собирает контрастный source evidence;
3. допускает процедуру только в доказанном scope;
4. компилирует принятые правила и scoped examples в skill package.

На 87 SkillsBench tasks, пяти запусках на задачу и четырёх agent-model
configurations метод получил:

- `+19.9` п.п. против no-skill;
- `+8.6` п.п. против сильнейшего automated baseline;
- `55.8% avg@5` против `54.4%` у human-curated skills.

Это поддерживает не конкретный Markdown-шаблон, а порядок авторинга:
requirement discovery → evidence → scope admission → compilation. В Media
задачах метод всё ещё терял execution-critical steps и параметры.

### 4. Статический Quality Score Не Предсказывает Живой Эффект

[Evaluating Skills, Not Just Agents](https://arxiv.org/abs/2608.20614)
исследовал 145 реальных skills в Claude Code, Codex, OpenCode и Terminus-2.
В 947 парных task cases:

- средний composite Skill Lift составил `0.2134`, 95% CI
  `[0.1967, 0.2301]`;
- lift был положительным в 72.8% случаев, нулевым в 18.1% и отрицательным в
  9.2%;
- structural score и LLM-judge score практически не коррелировали с live lift:
  Spearman `ρ = −0.0169` и `ρ = −0.0250` соответственно.

Статический просмотр не видит, обнаружил ли агент skill, выбрал ли правильный
script, передал ли верные arguments, столкнулся ли с другим skill и не сломала
ли поведение смена модели. Поэтому evaluation assets — часть авторства skill,
а не post-hoc украшение.

### 5. Релевантный Workflow Чаще Улучшает Adherence, Чем Goal Completion

[A Framework for Evaluating Agentic Skills at Scale](https://kdd-eval-workshop.github.io/agenticai-evaluation-kdd2026/assets/papers/35_A_Framework_for_Evaluating_.pdf)
проверил около 500 skills, 1 000 задач и 19 agent-model configurations — около
38 000 траекторий. Доступ к релевантному skill поднял общий score на 5.5–22.1
пункта во всех конфигурациях.

Большинство моделей и без skill часто завершали базовую задачу; основной
прирост пришёл из instruction-following — соблюдения библиотек, naming rules,
структуры, запрещённых паттернов и обязательных шагов.

**Граница:** в treatment агенту явно сообщали, что релевантный skill доступен;
исследование не измеряет реальную вероятность auto-trigger. Judge был один,
Sonnet 4.6, а корпус смещён к software engineering.

### 6. Method-Level Guidance Не Заменяет Операционализацию Сложной Процедуры

[ASI-Bench](https://arxiv.org/abs/2608.17271) держит неизменными 60 сложных
проектных задач, данные и outputs, последовательно убирая методическое
руководство. При переходе от полной процедуры (`B1`) к method class и
constraints без implementation steps (`B2`):

| Agent × model | B1 | B2 | Потеря |
| --- | ---: | ---: | ---: |
| Codex × GPT-5.5 xhigh | 57.57 | 35.28 | −22.29 п.п. |
| Codex × GPT-5.6 Sol xhigh | 62.75 | 42.96 | −19.79 п.п. |
| Codex × GPT-5.6 Sol ultra | 71.78 | 49.57 | −22.21 п.п. |
| Codex × Claude Opus 5 | 72.29 | 45.80 | −26.49 п.п. |

`B2` также потребовал на 59% больше total tokens и на 32% больше времени, чем
полная процедура: агент компенсировал пропуск поиском и реконструкцией.

Полная граница вывода и соседний evidence принадлежат отдельному snapshot:
[`research-method-names-vs-procedures-2026-08.md`](research-method-names-vs-procedures-2026-08.md).

### 7. Обязательный Порядок И Проверки Ненадёжно Хранятся Только В Prose

[SIGIL](https://arxiv.org/abs/2607.27309) сравнил обычный `SKILL.md` с
скомпилированным typed harness на 30 skills:

| Condition | gpt-4o | gpt-5 |
| --- | ---: | ---: |
| Выполнено обязательных шагов из prose | 56% | 68% |
| Выполнено обязательных шагов через harness | 86% | 86% |

Полная процедура выполнялась в 28% prose-runs против 65% harness-runs.
Медианный расход harness составил 0.58 от prose execution.

В код или typed mechanism разумно переносить fixed tool choice, control flow,
validation и детерминированные запреты. Open-ended synthesis, taste и judgment
остаются model-owned. Работа использовала только две OpenAI-модели и 30 skills;
точные rates нельзя считать универсальными.

### 8. Большинство Публичных Skills Имеют Packaging И Routing Defects

[What Keeps Agent Skills from Being Reusable?](https://arxiv.org/abs/2608.08453)
проанализировал 138 133 уникальных `SKILL.md` из 20 556 repositories:

- 91.8% имели хотя бы один обнаруженный defect;
- 67.0% — routing defect;
- 52.3% — отсутствующее trigger guidance;
- 44.3% — дублирование имени как H1;
- 32.1% — слишком много inline examples;
- средний skill содержал 2.5 defects.

419 zero-defect exemplars из крупных repositories разделились на два жизнеспособных
стиля — minimal-and-precise и structured-workflow — но разделяли пять свойств:
trigger-complete description, отсутствие name-as-heading, imperative body,
project-specific knowledge и отсутствие install/changelog/license prose.

Это corpus observation и rule-based defect taxonomy, а не причинный тест:
частота свойства не доказывает, что само свойство повышает task success.

## Сведённые Следствия Для Авторинга

Следствия ниже являются evidence-bounded inference, не новым каноном.
Пункты, кроме границы «method-level guidance ≠ полная процедура», — гипотезы
для target-model evaluation, а не уже доказанные свойства GPT-5.6 или Claude 5.

1. **Admission:** skill нужен для повторяемой локальной Delta, а не для общего
   знания, которое модель уже применяет без помощи.
2. **Routing:** `description` должна точно различать use, skip и соседние
   задачи; нерелевантный skill не загружается.
3. **Core:** в active body остаются outcome, scope, decision rules,
   anti-patterns, evidence и stop. Generic tutorials и примеры «на всякий
   случай» не являются безопасным дефолтом.
4. **Disclosure:** references, examples и редкие детали загружаются только в
   момент необходимости.
5. **Procedure boundary:** execution-critical steps, параметры и recovery
   нельзя сжимать до одного имени метода; детерминированные обязательства
   переносятся в script, validator, hook или typed harness.
6. **Evaluation:** минимальный causal test — одинаковые task, model, harness и
   settings в `no-skill` и `with-skill`; для длинного skill добавляется
   length-matched irrelevant control.
7. **Model conditioning:** utility и вред проверяются отдельно на каждой
   target model; marketplace popularity и результат другой модели не являются
   переносимым доказательством.

## Противоречивый И Отрицательный Evidence

Две группы результатов не противоречат друг другу после учёта treatment:

- SkillAlchemy и scale-evaluation дают большой positive lift, когда skill
  evidence-grounded, task-relevant и явно доступен агенту.
- WebDev и data-science ablations дают ноль или отрицательный эффект, когда
  skill generic, постоянно injected, избыточен для лёгкой задачи или не
  совпадает с моделью.

Следовательно, claim «skills помогают» слишком широкий. Защищаемый claim:
**релевантный и проверенный skill может помочь; само наличие skill пользы не
предсказывает.**

## Что Не Доказано

- Нет универсальной длины `SKILL.md`, безопасной для всех моделей и harnesses.
- Нет универсального победителя между examples, rules и full procedures.
- Нет доказательства, что imperative style или отсутствие H1 сами по себе
  причинно улучшают task success.
- Нет общего production threshold количества одновременно resident skills.
- Нет основания переносить benchmark delta между моделями без matched eval.
- Статический lint необходим для структуры и безопасности, но не доказывает
  behavioral utility.

## Confidence

| Claim | Confidence | Причина |
| --- | --- | --- |
| Нужен live no-skill comparator | High | Два крупных paired исследования и отрицательные абляции |
| Generic always-loaded skill может вредить | High для изученных domains | Matched и length-matched controls |
| Релевантный evidence-grounded skill может дать крупный lift | Medium–High | Несколько benchmarks, но преимущественно препринты |
| Anti-patterns лучше examples по умолчанию | Medium | Прямая абляция, но один WebDev benchmark и model dependence |
| Mandatory procedure лучше обеспечить механизмом | Medium | Сильный SIGIL effect, но 30 skills и две модели |
| Corpus-style traits причинно улучшают utility | Low | Наблюдательная выборка без behavioral ablation |

## Source Ledger

- [Signal or Noise?](https://arxiv.org/abs/2608.23067) — controlled WebDev
  injection, length control и component ablation; 24 августа 2026.
- [SkillAlchemy](https://arxiv.org/abs/2608.23417) — evidence-grounded skill
  creation; 24 августа 2026.
- [Evaluating Skills, Not Just Agents](https://arxiv.org/abs/2608.20614) —
  paired live Skill Lift; 24 августа 2026.
- [A Framework for Evaluating Agentic Skills at Scale](https://kdd-eval-workshop.github.io/agenticai-evaluation-kdd2026/assets/papers/35_A_Framework_for_Evaluating_.pdf)
  — 500 skills × 19 configurations; 15 июля 2026.
- [Do LLM-Generated Skills Make Better AI Data Scientists?](https://arxiv.org/abs/2607.07504)
  — component and length controls; 9 июля 2026.
- [ASI-Bench](https://arxiv.org/abs/2608.17271) — guidance gradient on
  project-level scientific tasks; август 2026.
- [SIGIL](https://arxiv.org/abs/2607.27309) — prose skill versus typed harness;
  31 июля 2026.
- [What Keeps Agent Skills from Being Reusable?](https://arxiv.org/abs/2608.08453)
  — corpus defects and exemplar traits; 11 августа 2026.

## Downstream Owners

- Portable skill-authoring truth: [`authoring-canon.md`](authoring-canon.md).
- Wording и instruction density:
  [`research-instruction-wording-adherence-2026-08.md`](research-instruction-wording-adherence-2026-08.md).
- Method names versus procedures:
  [`research-method-names-vs-procedures-2026-08.md`](research-method-names-vs-procedures-2026-08.md).
- Полная инженерия compliance:
  [`science/how-to-make-llm-obey.md`](../../../science/how-to-make-llm-obey.md).
