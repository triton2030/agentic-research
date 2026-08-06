---
read-when: "Failure mode назван (`language-failure-modes.md`), пора выбрать repair и выдать находку."
---

# Аудит Качества Instruction Prose — Judgment И Findings

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
model-specific claim либо подтверждён релевантной записью `divergences-contract.md`,
либо сформулирован как model-agnostic wording risk.
