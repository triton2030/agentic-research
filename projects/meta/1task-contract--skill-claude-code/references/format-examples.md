# Format Examples

## Example Anchor

Task: fix CSV export loss.
Relevant strategy anchor: `_ops/PROJECT-ROADMAP.md#stage-3-stabilize-export`.
Task file: `_ops/plans/phase-03-stabilize-export/task-02-csv-export-loss.md`.

```md
# Fix CSV export loss

## Цель
CSV export preserves all rows required by the stabilized export Stage.

## Подшаги
- [ ] Reproduce the missing-row case.
- [ ] Patch export filtering.
- [ ] Verify regression coverage.

## Критерии приёмки

### Must
- [ ] Export keeps rows with empty optional fields — **Evidence**: regression test output
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#stage-3-stabilize-export`

### Verification protocol
1. `npm test -- csv-export`
   Expected: relevant regression passes
```
```
