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

Judgment и findings contract — [`language-quality-findings.md`](language-quality-findings.md).
