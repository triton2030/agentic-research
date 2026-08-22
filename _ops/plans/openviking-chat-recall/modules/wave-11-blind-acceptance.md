---
kind: module-card
wave: 11
state: planned
role: blind-reader-and-matched-comparator
reader-model: gpt-5.6-luna
reader-thinking: max
grader-model: claude-opus-5
---

# Модуль — blind acceptance и matched Wiki-vs-holders comparator

[parent: task.md](../task.md) · веха 5 · gate: frozen Wave 10 candidate

## Contribution

Проверить не красоту библиотеки, а её полезность: тот же fresh agent, вопросы и
answer schema сравнивают Wiki route с прямым holder route по correctness,
currentness, provenance, calibration и стоимости чтения.

## Isolation

- Gold/questions замораживаются до чтения candidate Wiki.
- Wiki arm и holders arm получают одинаковые model version, system/task prompt,
  context policy, timeout, retry policy и answer schema.
- Readers не видят implementation receipts и не редактируют candidate/gold.
- Full answers оценивают независимые graders с адресуемым source evidence.

## Inputs

- five locked Wave 5 cases: stable, supersession/current, contested/scope,
  provenance/history route, no-gold abstain;
- frozen full-build candidate и source lock Wave 10;
- восстановленный 11-question comparator как broad routing/usefulness set.

## Ownership

- `scripts/run_blind_acceptance.py`, `tests/test_blind_acceptance.py` — один
  harness owner.
- Separate Luna Max Wiki readers и holder readers пишут disjoint arm receipts.
- Read-only Opus graders владеют case verdicts, не arm writers.
- Root один пишет `artifacts/full-build/acceptance/route-verdict.json`.

Один independent Opus falsifier проверяет isolation и aggregation; missing
return помечается UNKNOWN, а не заменяется self-report.

## Metrics

Case score: 0.50 factual correctness + 0.20 provenance + 0.20
chronology/currentness + 0.10 calibration. Probe route thresholds, а не
owner-approved business facts:

- factual и chronology/currentness не ниже 90%;
- provenance не ниже 80%, calibration не ниже 90%;
- total Wiki не хуже holders более чем на 5 percentage points;
- Wiki улучшает не менее чем на 25% median tokens, elapsed time или evidence
  reads без ухудшения другой material cost dimension более чем на 10%.
- Visible Wiki/source quote text ratio не выше 0.20; band 0.10–0.20 ожидаем,
  но ratio ниже 0.10 принимается только при отдельном completeness PASS.

## Hard failures

- superseded/uncertain claim выдан как settled current;
- invented provenance, missing holder route или confident no-gold answer;
- answer зависит от candidate Wiki при создании gold;
- arm configurations различаются или receipts не позволяют matched comparison;
- privacy leak, silent skip либо material UNKNOWN.
- ответ опирается на project knowledge file, которого не было в quote input;
- Wiki сохраняет superseded решение рядом с актуальным или превращает change
  history в default knowledge.

## Receipts

На case/arm: reads, discovery operations, context/answer tokens, elapsed time,
cache/retries/status, cited source IDs, gaps и grader result. Quotes и private
corpus content в receipt запрещены.

## Return

Harness owner возвращает commit/tests/isolation proof. Readers и graders —
per-case packets. Root публикует PASS, FAIL или UNKNOWN по каждому criterion и
route verdict. Без доказанной экономии Wiki остаётся candidate, даже если
correctness PASS.

## Prohibitions

Не менять Wiki, holders, gold или thresholds после просмотра результатов; не
использовать Graphiti иначе чем supplementary baseline.
