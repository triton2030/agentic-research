# Format Examples

## Example 4: Pulse-check (with strategic map)

**Input:**
> Pulse check — мы уже третий час про agent-creator разговариваем, ты ещё помнишь ради чего?

**Output** (read-only):

```md
## Pulse check

### Recalled
- North Star: репо остаётся компактной operating system для authoring-работы.
- Active line: owner-chain зафиксирован тройкой `project-strategy → instruction-layer → task-contract`.
- This dialog: третий час проектируем agent-creator без привязки к тройке owner'ов.

### Actual
- Goal: "lean operating system for authoring, where a short _ops/ plan directs downstream framing" — _ops/PROJECT-PLAN.md#Goal
- Active stage: "owner-chain stays a tight triple; no fourth owner without proven leverage" — _ops/PROJECT-PLAN.md#Stage <owner-chain>

### Trace
compact _ops/ truth-layer → tight owner triple → dialog is designing a fourth owner outside that triple

### Verdict
drift

### Delta
Recall на North Star и активную линию правильный, но три часа ушли в проектирование agent-creator без baseline-проверки. Активная линия требует сначала доказать leverage одного из существующих owner'ов.
```

## Shape Guide

- `task` mode file: три секции — Цель (одна строка), Подшаги (2-5 action-lines), Критерии приёмки (2-4 `Must`, 0-2 `Must not`, 1-3 verification). Никаких лишних секций.
- `task` mode receipt: ≤ 10 строк, обязательны `Path:` и `Refs applied:`. После receipt — 1-3 строки простым языком, что держать в голове, и агент продолжает работу.
- `strategy-trace` mode: 3-4 chain steps, один verdict, ≤ 2 `Why` bullets, один `Do now`. Файл не пишется.
- `pulse-check` mode: 3-line `Recalled`, 2-line `Actual`, 1-line `Trace` с 3 arrow-separated steps, verdict из `remembered | drift | forgotten`, `Delta` только когда verdict не `remembered`. ≤ 15 строк total. Файл не пишется.
- Два буллета защищают один failure mode → объединить.
- Короткие evidence-rich строки > explanatory mini-paragraphs.
- `Anchored in:` **никогда** не ссылается на путь внутри `_ops/plans/` или на другой task-файл.

