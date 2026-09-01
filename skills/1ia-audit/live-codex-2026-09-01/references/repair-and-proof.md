---
description: "Detailed Gate 5-6 operations for turning a material IA delta into the smallest repair while preserving mutation authority and proof strength."
read-when: "Read only after a material-delta verdict exists; required for final recommendation and for every authorized IA change."
---

# Repair And Proof

Этот файл владеет детальными операциями Gate 5–6. Основной `SKILL.md` владеет
порядком фаз и stop-условиями.

## Gate 5 — Назови Mechanism, Repair И Verdict

1. Сформулируй failure mechanism одним causal statement: какая текущая форма
   заставляет кого сделать какой лишний/ошибочный operation и какой harm следует.
2. Если исходный signal похож на red flag, вернись к прямому route на
   `ia-smell-catalog.md` из основного `SKILL.md` для body/owner checks и
   evidence-to-repair mapping; label smell-а не заменяет mechanism.
3. Проверь, что mechanism объясняет observed delta, а не просто переименовывает
   length, topic similarity или template deviation.
4. Назови smallest repair, который устраняет mechanism. Minimality измеряется
   устранённым operation harm, не размером diff.
5. Сравни 2–3 формы только если они материально различаются по trace, owner,
   lifecycle, validation, reversibility или future constraint; иначе оставь одну.
6. Сохрани один semantic owner и одну normative representation; secondary path
   обслуживай pointer/view, если регулярный второй reading path доказан.
7. Дай current form verdict:
   `pass | risky | fail | unknown | not present`.
8. Дай proposed change decision:
   `accept | reject | defer | not requested`.
9. Проверь согласованность: `pass + accept` требует нового доказанного gain;
   `fail + reject` требует другого repair; подтверждённый неустранённый red flag
   не совместим с `pass`.

**Результат gate:** `mechanism + smallest repair + current verdict + proposed
decision + recommended shape`, все связанные с operation delta.

## Gate 6 — Сохрани Permission И Докажи Результат

1. Отдели shape recommendation от authority на mutation. Назови, что текущий
   intent реально разрешает изменить.
2. Если move/rename/delete, holders, anchors, links, cycles или propagation
   способны изменить operation pair, получи read-only graph-impact evidence до
   final verdict; edge mutation и graph closeout принадлежат их owner-у.
3. В change mode примени только разрешённую shape-правку и минимальные
   supporting edits, необходимые для одного truth и целых routes.
4. После edit повтори ту же baseline/candidate operation: те же trigger, answer,
   reader и scoring dimensions.
5. Проверь direct read/diff, owner/placement, truth/view direction, routes и
   smallest project-owned structural gate.
6. Предскажи правдоподобный bypass: новая форма выглядит чище, но reader всё ещё
   делает прежний wrong turn; split сохраняет duplicate truth; view становится
   новым owner-ом; validation не покрывает новый seam.
7. Для low-risk change counterfactual walkthrough — design-time proxy. Material
   global/risky claim требует clean cold-start with/without или previous-version
   case с заранее названным observable first act.
8. Self-report, заполненный output packet, lint и link validity не доказывают,
   что reader operation улучшилась.
9. Назови один реально affected external owner и unresolved risk; не превращай
   handoff в каталог соседней системы.

**Результат gate:** `permission + applied/proposed scope + repeated operation
evidence + bypass check + claim strength + one handoff/risk`. Недоступен
behavioral run → назови gap; не повышай structural green до cognitive lift.

## Контрастивная Сцена

**Template не оправдывает duplicate truth.** Summary и таблица вручную хранят
один mutable decision и уже расходились. Baseline показывает два edit anchor-а
и дополнительную sync-проверку. Candidate оставляет одну normative
representation и derived view: current form `fail`, candidate `accept`. Если
дубль обязателен section contract-ом, mechanism = `template defect`; label не
смягчает verdict.
