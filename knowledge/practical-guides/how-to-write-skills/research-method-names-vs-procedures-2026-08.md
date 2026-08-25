---
description: "Датированный evidence snapshot о том, когда имя известного метода может заменить полную процедуру в агентной инструкции."
---

# Method Names Instead Of Procedures — Research 2026-08

Срез источников на 25 августа 2026 года. Использовать при сокращении skills,
system prompts, `AGENTS.md` и заданий агентам. Поиск и чтение источников
выполнены только через Keenable.

Это evidence snapshot, а не portable-канон. Практическим skill-authoring
контрактом владеет [`authoring-canon.md`](authoring-canon.md).

## Ответ В Одной Фразе

**Голое имя метода не является надёжной заменой процедуре.** На актуальных
frontier-моделях указанный метод без полной процедуры теряет примерно 20–26
пунктов в проектных научных задачах. Сжатие становится защищаемым, когда кроме
имени остаются триггер, ключевые инварианты или decision rules, наблюдаемый
результат и stop/verification.

Рабочая форма:

> наблюдаемый trigger → имя канонического метода → ключевые инварианты или
> decision rules → наблюдаемый evidence → stop

Если порядок сам обеспечивает корректность, безопасность или воспроизводимость,
процедура остаётся SOP либо загружается через progressive disclosure.

## Что Именно Проверялось

Вопрос исследования: сохраняет ли агент поведение, если развёрнутую процедуру
заменить названием или высокоуровневым описанием знакомого метода?

Основной evidence допускался только для моделей, выпущенных не раньше
25 февраля 2026 года. Дата статьи сама по себе свежесть не доказывает.

Полезно различать три вмешательства:

1. **Голый ярлык:** только имя метода или книги.
2. **Методический каркас:** имя плюс ограничения, инварианты и decision rules.
3. **Процедура:** шаги, порядок, параметры, recovery и проверки.

Исследования ниже хорошо сравнивают каркас с процедурой. Чистый голый ярлык на
текущем model set пока не получил достаточного прямого теста.

## Прямой Evidence: ASI-Bench

[ASI-Bench](https://arxiv.org/abs/2608.17271) содержит 60 project-level
исследовательских задач в 11 научных областях. Цель, данные, требуемые
артефакты и scoring остаются постоянными, а руководство последовательно
убирается:

- `B1`: научный фон, метод, уравнения, implementation steps, параметры и
  полная процедура;
- `B2`: указан intended method или класс метода и релевантные ограничения, но
  процедура и implementation decisions удалены;
- `B3`: остаются цель, данные, ограничения и outputs; метод выбирает агент.

Результаты конфигураций на моделях, чей release прошёл cutoff:

| Agent × model | Release | B1 | B2 | Потеря B2 |
| --- | --- | ---: | ---: | ---: |
| Codex × GPT-5.5 xhigh | 2026-04-23 | 57.57 | 35.28 | −22.29 п.п. / −38.7% |
| Codex × GPT-5.6 Sol xhigh | 2026-07-09 | 62.75 | 42.96 | −19.79 п.п. / −31.5% |
| Codex × GPT-5.6 Sol ultra | 2026-07-09 | 71.78 | 49.57 | −22.21 п.п. / −30.9% |
| Codex × Claude Opus 5 | 2026-07-24 | 72.29 | 45.80 | −26.49 п.п. / −36.6% |

Направление одинаково во всех четырёх конфигурациях: модель знает названный
метод, но значительно хуже превращает его в полный исполнимый workflow.

Короткий prompt не сделал весь run дешевле:

- `B1`: 4.35 млн токенов и 37.8 минуты на задачу в среднем;
- `B2`: 6.91 млн токенов и 49.7 минуты;
- `B2` потребовал на 59% больше токенов и на 32% больше времени.

Агент компенсировал удалённую процедуру поиском, реконструкцией шагов и
итерациями. Поэтому экономия input tokens не равна экономии total tokens.

### Граница Вывода

`B2` — не чистое однословное имя: в нём могут оставаться класс метода,
подходящие численные подходы и ограничения. Следовательно, исследование прямо
доказывает слабость **method-level guidance без операционализации**, а перенос
на голый ярлык является консервативным inference: ещё меньше информации не
имеет основания работать лучше.

Большинство строк ASI-Bench усредняют три независимых run; Claude Opus 5 в
первой версии таблицы имеет один run. Это свежий препринт, а не peer-reviewed
результат.

## Дополняющий Evidence: Уровень Абстракции Skill

[Skill Availability and Presentation Granularity](https://arxiv.org/abs/2605.31408)
проверяет более полезную для authoring развилку: можно ли сохранить содержание,
но поднять его уровень абстракции.

Дизайн: 30 oracle-validated SkillsBench tasks, 6 conditions, 5 trials на
каждую task-condition-model cell, всего 1 800 runs. Модели:

- GPT-5.5, выпущенная 23 апреля 2026 года;
- DeepSeek V4-Flash, выпущенная 24 апреля 2026 года.

Сравнивались:

- high abstraction: principles, invariants и decision rules;
- low abstraction: checklist-like operational steps, concrete placeholders и
  recovery checks.

Low abstraction минус high abstraction:

- GPT-5.5: `+0.7` п.п.;
- DeepSeek V4-Flash: `−6.7` п.п.;
- оба 95% bootstrap confidence intervals пересекают ноль.

Добавление одного worked example к medium-abstraction версии дало только
`+0.7` и `+1.3` п.п.; интервалы также пересекли ноль.

При этом наличие любого task-relevant skill относительно no-skill давало
намного больший сигнал: `+26.7…36.0` п.п. для GPT-5.5 и `+18.0…26.0` п.п. для
DeepSeek V4-Flash.

**Интерпретация:** подробный checklist не показал устойчивого преимущества над
компактными principles/invariants. Но high-abstraction condition сохранял
существенное знание; это не доказательство достаточности одного названия.

## Сведённый Вывод Для Авторинга

### Имя Метода Можно Оставить Как Указатель, Если

- метод канонический и модель с высокой вероятностью знает один и тот же
  канон;
- локальная версия не отклоняется от канона;
- trigger наблюдаем и отделяет use от skip;
- рядом сохранены инварианты или decision rules, от которых зависит результат;
- adherence оставляет проверяемый след;
- есть stop condition;
- потеря процедуры проверена matched ablation на target model и задачах.

### Нельзя Оставлять Только Имя, Если

- у метода несколько распространённых трактовок;
- локальная процедура отличается от публичного канона;
- важны порядок, обязательные проверки, recovery или safety gates;
- шаг содержит редкое предметное знание, которого может не быть в весах;
- ошибка выглядит правдоподобно и не обнаруживается outcome-only проверкой;
- агенту придётся заново изобретать workflow в каждом run.

### Предпочтительная Архитектура

Имя и короткий контракт живут в active context; полная процедура доступна
по progressive disclosure. Имя маршрутизирует, но не притворяется самой
процедурой.

```text
Когда <наблюдаемый trigger> — примени <канонический метод>.
Сохрани <ключевые инварианты / decision rules>.
Докажи применение через <artifact, test или trace>.
Остановись при <criterion>; при <order-sensitive / local deviation> прочитай SOP.
```

## Что Исключено Из Основного Evidence

- [Scaffold, Not Vocabulary?](https://arxiv.org/abs/2606.06454) наиболее прямо
  сравнивает labels-only scaffold и полную Popperian procedure, но frontier-run
  использует Claude Sonnet 4.6, выпущенную 17 февраля 2026 года — на восемь
  дней раньше cutoff. Small-model tier использует ещё более старую
  Qwen2.5-Coder. Результат сохранён как adjacent evidence, не как основание
  текущего вывода.
- [What Fits Into Few Tokens](https://arxiv.org/abs/2606.11045) показывает, что
  task-specific ML strategy может пережить сжатие до 16–32 токенов, но paper
  не pin'ит точную версию `Claude Opus`, а короткие prompts содержат плотные
  параметры архитектуры, optimizer и schedule — это не голое имя метода.
- [SkillReducer](https://arxiv.org/abs/2603.29919) сокращает descriptions на
  48% и skill bodies на 39%, сохраняя core procedural rules. В model panel есть
  модели за пределами cutoff; работа подтверждает structured compression, но
  не label-only замену.

## Source Ledger

### Исследования

- [ASI-Bench](https://arxiv.org/abs/2608.17271) — matched guidance gradient,
  project-level scientific agents, B1/B2/B3.
- [Skill Availability and Presentation Granularity](https://arxiv.org/abs/2605.31408)
  — high-abstraction principles/invariants против operational checklist.
- [Scaffold, Not Vocabulary?](https://arxiv.org/abs/2606.06454) — наиболее
  прямой labels-only контроль, исключённый по cutoff.
- [What Fits Into Few Tokens](https://arxiv.org/abs/2606.11045) — compressed
  task-specific strategy, model version не pinned.
- [SkillReducer](https://arxiv.org/abs/2603.29919) — structured skill
  compression с сохранением core rules.

### Release Evidence

- [OpenAI: Introducing GPT-5.5](https://openai.com/index/introducing-gpt-5-5)
  — 23 апреля 2026.
- [OpenAI: GPT-5.6](https://openai.com/index/gpt-5-6) — 9 июля 2026.
- [Anthropic release notes](https://docs.anthropic.com/en/release-notes/claude-apps)
  — Sonnet 4.6: 17 февраля; Opus 5: 24 июля 2026.
- [DeepSeek V4 Preview](https://www.deepseek.com/en/news/v4-preview/) —
  V4-Flash: 24 апреля 2026.

## Downstream Owners

- Portable skill-authoring truth: [`authoring-canon.md`](authoring-canon.md).
- Wording и instruction density:
  [`research-instruction-wording-adherence-2026-08.md`](research-instruction-wording-adherence-2026-08.md).
- Полная инженерия compliance:
  [`science/how-to-make-llm-obey.md`](../../../science/how-to-make-llm-obey.md).
- Promotion вывода в live skill или instruction требует отдельной проверки на
  текущем model set; этот snapshot сам runtime behavior не меняет.
