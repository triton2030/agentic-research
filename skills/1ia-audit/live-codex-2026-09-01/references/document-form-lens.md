---
description: "IA lens: information job → reader action → natural document form → validation."
read-when: "Audit/design questions document type, headings, mixed functions or template fit; not for catalog admission."
---

# Document Form Lens

Документная форма — это интерфейс к информации. Аудит проверяет, помогает ли
её композиция читателю сделать нужную работу и будущему агенту найти, проверить
и обновить правильный ответ. Это открытый lens, не каталог типов.

Прогони lens для обеих сторон operation pair из parent `SKILL.md`. Один
правдоподобный trace без material comparison не обосновывает shape change.

## Gate

Пройди одну цепочку:

1. **Reader task:** что primary reader должен суметь сделать?
2. **Information moves:** какие связи должны стать видимыми без реконструкции?
3. **Section grammar:** передают ли порядок, headings и representation эти связи?
4. **Agent operation trace:** `query/trigger → confirmed owner → minimum context
   slice → exact edit anchor → dependent views/holders → bounded validation`.
5. **Evidence:** где текущая форма добавляет friction, ambiguity, context load
   или edit blast radius? Без direct evidence verdict `unknown`.

Information moves — открытый набор. Ниже не types для admission, а примеры того,
какую композиционную работу форма может выполнять:

| Reader task | Нужные moves | Частые формы-примеры |
|---|---|---|
| Ориентироваться / найти | hierarchy, index, definition, cross-reference | overview, map, hub, reference |
| Научиться / выполнить | sequence, example, branch, observable, stop | tutorial, how-to, procedure, runbook |
| Понять / объяснить | cause, context, relationship, counterexample | explanation, narrative, concept model |
| Решить / установить норму | alternatives и trade-offs либо rule, exception, precedence | decision record, policy, standard, ruleset |
| Проверить / обосновать | claim, evidence, method, uncertainty, limitation | analysis, evidence report, assurance case |
| Скоординировать | actor, responsibility, handoff, state, next gate | plan, matrix, blueprint, contract |
| Восстановить произошедшее | chronology, transition, provenance | log, changelog, incident/case record |

## Judgment

- **Primary job first.** Secondary material может быть module/section, если
  обслуживает тот же reader action, lifecycle и validation.
- **Split по независимости.** Разделяй, когда jobs имеют разных readers,
  owners, lifecycle или checks. Несколько headings сами split не доказывают.
- **Agent effect required.** Предлагаемая форма должна наблюдаемо улучшать
  retrieval, context completeness, update locality или edit blast radius. Если
  operation trace не меняется, жанровая разница не является IA evidence.
- **Truth vs teaching/view.** Tutorial, overview или guide может компоновать
  owner truth для reader path; unique durable rule остаётся у canonical owner.
- **Form-task mismatch.** Fail/risky, если section grammar заставляет читателя
  делать не ту работу: policy спрятана в FAQ, evidence выдана как decision,
  reference написан как длинная narrative без lookup surface.
- **Template monoculture.** Одинаковые sections допустимы только когда jobs и
  checks действительно одинаковы. Симметрия headings не является качеством.
- **No catalog invention.** Если нужен admitted reusable type, section contract
  или template, передай `1document-system`; IA verdict должен удержать job,
  natural form и seam независимо от конкретного type name.
