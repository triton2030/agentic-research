---
description: "Instruction wording audit: literal scope, accidental mandate, Hyrum, frame capture и text-level duplicate."
read-when: "Спорен смысл конкретной формулировки; не для root/subtree placement или runtime loading."
---

# Аудит Качества Instruction Prose

Проверь, создаёт ли wording ложный scope, mandate, frame или duplicate.
Root/subtree topology → `audit-placement-structure.md`; load-bearing meaning и
criteria → `audit-meaning-criteria.md`; named model-specific tell →
`llm-divergences.md`.

## Failure Modes И Repair

| Failure mode | Direct evidence | Repair |
|---|---|---|
| **Literal scope** | Rule называет один instance, хотя observed obligation относится к классу. | Назвать точный class/surface и исключение; не надеяться на молчаливое обобщение. |
| **Accidental mandate / Hyrum** | Descriptive «обычно», example, comment или section placement исполняются как обязательное правило. | Разделить descriptive и prescriptive: `default X; deviate when Y`, либо удалить no-op. |
| **Frame capture / sycophancy** | Текст копирует пользовательскую рамку и защищает симптом, а не recurring mechanism. | Назвать observed failure и outcome, который должен измениться; не сохранять случайную формулировку как canon. |
| **Risk-word overclaim** | `MUST` / `NEVER` / `CRITICAL` стоят на preference, которое runtime не обеспечивает. | Обычный язык для guidance; сильное слово только для hard invariant + enforcement handoff. |
| **Lost-in-the-middle** | Load-bearing rule теряется среди длинного unrelated middle и это видно в trace/repeat failure. | Поднять rule в hot path или заменить depth коротким owner pointer; line count сам finding не доказывает. |
| **Text-level duplicate** | Один meaning повторён в root/subtree или instruction/skill description. | Один owner + pointer; разный moment допускает короткий conscious refresher без второй truth. |

## Judgment

1. Процитируй exact wording и назови observed/credible misread; stylistic taste не
   является finding.
2. Подтверди intended owner meaning direct read-ом. Если нужен semantic/exact или
   graph evidence за пределами прочитанного — route через `cli-recipes.md`.
3. Выбери один repair: delete, narrow scope, separate descriptive/prescriptive,
   replace with owner pointer, rewrite exact wording или enforcement handoff.
4. Сохрани conscious freshness только когда тот же owner meaning нужен в другом
   lifecycle moment; другая папка сама по себе этого не доказывает.

## Findings Contract

```text
Failure mode: <named mechanism>
Exact evidence: <file + wording + observed/credible misread>
Owner meaning: <confirmed intent/source>
Repair: <one exact rewrite/delete/pointer>
Risk after repair: <only unresolved gap>
```

Готово, когда каждая находка имеет named mechanism, evidence и exact repair, а
model-specific claim либо подтверждён релевантной записью `llm-divergences.md`,
либо сформулирован как model-agnostic wording risk.
