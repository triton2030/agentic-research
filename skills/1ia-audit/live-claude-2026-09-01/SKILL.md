---
name: 1ia-audit
description: >-
  Use when reader-operation evidence must decide the local split, merge, move,
  or truth/view seam of one document, section, or container. Not for
  semantic-owner or multi-document system changes.
---

# IA-Аудит

## Продукт И Режим

Верни evidence-backed решение о natural form одного bounded surface:

- **audit** — оцени current form и proposed change;
- **design** — выбери form, placement, truth/view и seam;
- **change** — примени только разрешённую shape-правку внутри подтверждённой
  authority.

Audit/review остаётся read-only. Рекомендация сама не разрешает mutation.

## Decision Standard

Видимая композиция легко подменяет устройство информации: length, headings,
близкие темы и симметрия выглядят как готовый verdict. Они только номинируют
вопрос. Natural form — наименьшая структура, в которой primary reader находит,
понимает, меняет и проверяет mutable answer у одного owner-а без false seams и
independently editable copies.

Держи состояние:

`admission/authority → current trace → candidate trace → material delta →
mechanism/repair → permission/proof`.

Каждая фаза обязана породить наблюдаемый результат до следующей. Это decision
traces и адресуемые artifacts, не требование раскрывать private chain-of-thought.
Новое evidence опровергло premise, owner или job — отбрось зависимый downstream
state и перестрой его из подтверждённых facts.

## Phase Controller

### 1. Admission И Authority

Сначала прочитай
[`admission-and-authority.md`](references/admission-and-authority.md). Он
владеет Gate 0–1.

Выход фазы: `bounded subjects + reader action + mutable answer + materiality +
premise status + confirmed|unresolved authority + jobs`.

`Not material` завершает IA-вопрос без redesign. `Unresolved` authority не
разрешает положительный shape verdict. При спорных information moves, section
grammar или mixed functions прочитай
[`document-form-lens.md`](references/document-form-lens.md).

### 2. Operation Pair И Delta

Только после Фазы 1 прочитай
[`operation-comparison.md`](references/operation-comparison.md). Он владеет
Gate 2–4.

Выход фазы: `baseline trace + candidate trace on the same job +
new/removed/moved hops + truth/view direction + evidence-backed net
materiality`.

Неодинаковая конкретность traces даёт `unknown`. Нет material delta — нет
IA-улучшения. Для evidence gaps прочитай
[`cli-evidence-tips.md`](references/cli-evidence-tips.md); для greenfield,
второго reading axis или cross-cutting candidate —
[`design-patterns.md`](references/design-patterns.md). Tool rank и pattern не
заменяют operation trace.

### 3. Repair И Proof

Только после material-delta verdict прочитай
[`repair-and-proof.md`](references/repair-and-proof.md). Он владеет Gate 5–6.

Выход фазы: `causal mechanism + smallest repair + current verdict + proposed
decision + recommended shape + allowed scope + repeated-operation evidence +
one risk`.

Если signal похож на red flag, прочитай
[`ia-smell-catalog.md`](references/ia-smell-catalog.md). Smell label открывает
body/owner check, но не заменяет mechanism.

## Короткая Демонстрация

**Длина не создаёт seam.** Один owner меняет три большие секции вместе, reader
использует их вместе, validator проверяет одним контрактом. Candidate split
добавляет owner-discovery hops и opens без независимого lifecycle: current form
получает `pass`, proposed split — `reject`.

## Authority И Вывод

IA владеет information job, natural form и seam одного bounded surface. Она не
создаёт reusable system types, system-wide homes или folder axes; не
переназначает semantic owner-а и не исполняет graph, instruction, planning или
runtime mutations.

Не публикуй весь controller без запроса на audit report. Верни минимальный
проверяемый packet:

```text
Mode + bounded surface; reader action + mutable answer
Authority: confirmed evidence | unresolved
Baseline trace ↔ candidate trace; changed hops; material delta
Mechanism + smallest repair; current verdict + proposed decision
Permission + proof strength + one risk/handoff
```

## Готово / Стоп

Готово, когда subjects и jobs не смешаны, authority подтверждена или явно
unresolved, traces одинаково конкретны, material delta доказана либо честно
отсутствует, verdict согласован с repair, а proof не повышен по proxy.

Вернись к последней непройденной фазе, если trace абстрактен, baseline
карикатурен, signal назван evidence или recommendation появилась до delta.
Повтор bypass-а либо смена рабочего model set reopen-ит mechanism; сначала
проверь меньший operator, не добавляй checklist по инерции.

Остановись до mutation, если intent не разрешает слой. В read-only режиме верни
решение и exact unresolved gap.
