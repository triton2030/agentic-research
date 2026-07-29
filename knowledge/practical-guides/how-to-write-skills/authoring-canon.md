---
description: "Короткий практический канон: когда писать skill, как держать scope, description, body и проверку по риску."
read-before-edit: []
edit-after-edit: []
---

# Authoring Canon

Практический канон написания скиллов под рабочий model set из `_ops/GOAL.md`.
Системные `skill-creator` tools владеют scaffolding и validation mechanics; их
step list не является универсальной формой body или обязательным authoring
ritual.

## Когда Писать Скилл

Писать, если одновременно верно:

- повторяется момент, в котором агенту нужна одна и та же профессиональная
  Delta;
- есть отдельный trigger, по которому агент должен сам выбрать скилл;
- внутри есть неочевидный критерий решения, failure mode, развилка, gotcha или
  проверка, которые меняют результат;
- без скилла агент уже ошибается, плавает, тратит лишние ходы или забывает
  локальную экспертизу.

Не писать, если это разовая задача, общий совет, сырая теория, правило для
`AGENTS.md`, script без reasoning-части или reference без повторяемого
decision/action contract.

## Scope

Один скилл — один повторяемый момент и один связный результат или решение. Он
проектируется по моменту применения, а не по профессии, теме или каталогу
возможностей.

Слишком узкий скилл заставляет грузить несколько скиллов на один кейс. Слишком
широкий плохо триггерится и тащит лишний контекст. Нормальный scope можно
объяснить одной фразой: “когда пользователь хочет X, агент делает Y через Z”.

## `description`

`description` — главный routing contract. Всё “когда использовать” должно быть
во frontmatter, потому что body загружается только после выбора скилла.

Первая фраза — hot zone: она должна самостоятельно назвать главный use case и
trigger words. Codex может сократить `description` или не включить skill в
budgeted initial list.

Хороший `description`:

- в первой фразе несёт главный use case и trigger words;
- говорит `Use when...`, а не просто “helps with...”;
- описывает intent пользователя, а не внутреннюю механику;
- содержит boundaries, skip-cases и adjacent near-misses;
- достаточно настойчивый, чтобы не undertrigger;
- достаточно точный, чтобы не перетриггерить соседние задачи;
- остаётся в portable ceiling 1024 символа; platform-specific discovery limits
  и shortening держит `platform-deltas.md`.

Routing evidence использует representative trigger phrases и настоящие
near-misses. Выборка должна быть достаточна, чтобы проверить заявленный
trigger и живые collisions; фиксированное число prompts этого не доказывает.

## Тело `SKILL.md`

Сначала выбери форму тела.

**Outcome/decision contract — default** для judgment, design и quality skills:

- результат, который должен стать истинным;
- главный критерий выбора при конфликте;
- материальные boundaries и настоящие invariants;
- falsifiable acceptance/evidence;
- условные reference/tool routes;
- stop и handoff.

**Workflow contract — исключение** для хрупких, необратимых, safety-critical или
tool-bound операций, где порядок сам является частью корректности. Оставляй
только минимальную обязательную последовательность; не превращай
профессиональное суждение в стадии ради управляемого вида.

Не учить модель очевидному. Добавлять то, чего агент не знает без скилла:
локальные conventions, API-паттерны, failure modes, команды, схемы, критерии и
реальные поправки пользователя.

Если skill учит tool use, сначала спроектировать выразительный
description/schema: понятные параметры, enum, constraints и output contract.
Примеры добавлять, только если interface не передаёт неочевидный формат, вкус
или известный failure mode; серия примеров не заменяет хороший interface.

## Progressive Disclosure

Структура должна тратить контекст по мере необходимости:

- frontmatter: `name`, `description`;
- `SKILL.md`: короткий рабочий playbook;
- `references/`: длинные детали, по одной теме на файл;
- `scripts/`: хрупкая или детерминированная логика;
- `assets/`: шаблоны и ресурсы результата.

Если reference длинный, дай короткое содержание и явный trigger чтения. Не
дублируй одно правило в `SKILL.md` и reference.

## Жёсткость

Общий принцип — `knowledge/wisdom-llm.md`: подразумеваемое держи как критерии
готовности + гейт сверки, не как процедуру; пошаговый порядок оправдан только для
хрупкой/необратимой операции или когда порядок сам — требование продукта. В
остальных skills шагов по умолчанию нет: outcome, decision criteria, evidence и
stop оставляют модели свободу пути, но не свободу объявить успех на глаз.

Для `GPT-5.6` сначала удаляй obsolete scaffolding, повторы, generic brevity и
process для уже надёжного поведения. Outcome, evidence, stop rules и короткие
defaults сильнее длинного self-check stack; новое правило добавляй только под
измеренный failure mode.
Общий Claude skill core должен работать на `Claude Opus 5` и `Claude Fable
5`; model routing остаётся в вызывающем prompt/runtime, не в portable body.
Для обоих явно называть scope, authority, обязательный tool/subagent policy,
evidence, output и stop только там, где они меняют ход. Для Fable-brief
добавлять реальный outcome и причину constraints; старый process scaffolding
сначала удалять и возвращать только под измеренный failure mode.
Claude-specific context assembly держит `knowledge/wisdom-claude-code.md`.
Portable consequence: один owner контракта, lightweight guide + progressive
disclosure и жёсткость только под high-risk boundary или измеренный failure.

## Если Скилл Делегирует

Subagents — не generic quality mode. Включай их в skill contract, только если у
повторяемой задачи есть независимые evidence streams, files или leaf
implementation и fan-out меняет latency, context hygiene или качество.

Orchestrating skill должен определить:

- критерий разделения и какие потоки независимы;
- какие результаты обязательны и должен ли root ждать все потоки;
- worker return contract: summary, адресуемый evidence, gaps и blockers;
- write ownership/isolation для каждого worker;
- root как owner conflict resolution, synthesis, integration и final validation.

Если состав потоков зависит от задачи, задавай decision rule, а не фиксированное
число агентов. Model/effort routing держи в platform/model delta, не в portable
skill core. Общий operational baseline — `knowledge/agents/multi-agent.md`;
GPT-5.6 routing — `knowledge/wisdom-gpt-5.6.md`.

## Доказательство

Скилл нельзя считать хорошим по тексту, но proof loop должен соответствовать
риску. Тяжёлые проверки не являются ритуалом для каждого маленького скила.

Evidence покрывает ровно заявленные свойства:

- admission — реальный повторяемый момент, Delta и failure evidence;
- routing — representative use/skip/near-miss cases и живые collisions;
- structure — platform validator и доступность нужных bundled resources;
- behavior — observable output assertion на реалистичной задаче;
- relative improvement — baseline или previous version, только когда заявлено
  сравнение;
- distribution — metadata/projection sync, только когда эти поверхности есть.

Глобальный, частый, рискованный, collision-prone или already-regressed surface
повышает требуемую различающую силу evidence. Это не делает каждый возможный
check обязательным. Для model-specific claim прогон фиксирует фактически
resolved model; requested alias сам по себе runtime не доказывает.

## Типовые Провалы

- Тема вместо повторяемого decision/action contract.
- `description` без trigger phrases и near-miss boundaries.
- Body-only “When to use”.
- Процедура по умолчанию там, где модели нужен outcome и критерии решения.
- Длинный процесс ради успокоения автора.
- Большой menu без главного decision standard.
- Дубли между `SKILL.md` и `references/`.
- Скрытая зависимость от чата.
- Нет validation или stop condition.
- Новый скилл создан раньше, чем проверен существующий live handle.
