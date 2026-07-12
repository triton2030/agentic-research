# Persistence-First Verification

Use for migrations, UI fallbacks, multi-object writes, or claims about a full
set, count, graph, or saved filter.

## Proof Contract

A click, mutation response, editor contents, toast, or DOM snapshot proves only
an attempted action. Accept persistence through the owning read surface:

| Claim | Proof |
|---|---|
| Hierarchy | IDs and `parent` IDs |
| Complete task/View set | Exhaustive pages, deduplicated IDs |
| View | `view get` plus `view tasks --all` |
| Comment | Comments collection contains the text/ID |
| Checklist | `task get` shows required items resolved |
| Doc/Wiki | Docs read; UI re-open for UI-only promotion |
| Goal/template | Collection returns the created ID |
| Closed/reopen | Closed status `type`, comment readback, status readback |

A custom status named `Done` or `Готово` is not necessarily closed.

## Portfolio Audit

```bash
bin/clickup audit portfolio WORKSPACE_ID LIST_ID
bin/clickup audit portfolio WORKSPACE_ID LIST_ID \
  --expect '{"tasks":{"count":35,"root_count":16}}'
```

`--expect` is a partial JSON projection of the report. Keep only contractual
invariants. Mismatches return exact JSON paths and live values. The audit does
not infer semantics from names; specify expected View filters, counts, or task
type distributions when they matter.

Report UI-only state as unverified without a UI re-open. Preserve unresolved
product decisions as blockers instead of inventing dates, metrics, or owners.
