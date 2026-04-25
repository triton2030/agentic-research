# Format Examples

## Example 3: Strategy-trace (with strategic map)

**Input:**
> Сделай `strategy-trace`: я хочу добавить четвёртый owner-skill в chain, чтобы он проверял finished drafts.

**Output** (read-only, ничего в файл не пишется):

```md
## Trace target
Я хочу добавить четвёртый owner-skill в chain, чтобы он проверял finished drafts.

## Strategic chain
1. Goal: репо должно оставаться компактной operating system для authoring-работы.
   **Anchored in**: `_ops/PROJECT-PLAN.md` — `Goal`
2. Active stage: owner-chain зафиксирован как `project-strategy → instruction-layer → task-contract`.
   **Anchored in**: `_ops/PROJECT-PLAN.md` — `Stage <owner-chain>`
3. Anti-goal: не расширять owner-chain без доказанного leverage.
   **Anchored in**: `_ops/PROJECT-PLAN.md` — `Anti-goals`
4. Observed target: запрос предлагает добавить четвёртого owner'а.
   **Anchored in**: user request

## Verdict
drift

## Why
- Запрос расширяет зафиксированную тройку вместо того, чтобы ужесточить одного из существующих.
- Нет baseline или leverage-proof, которого требует текущая стратегия перед ростом owner-chain.

## Do now
- Оставить owner-chain из трёх слоёв и встроить проверку в существующего owner'а, либо эскалировать в `project-strategy`.
```


