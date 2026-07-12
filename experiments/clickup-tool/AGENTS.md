---
depends-on:
  - ../../AGENTS.md
---

# ClickUp Control

`ARCHITECTURE.md` is the architecture owner. Read it before changing runtime
entry points, module ownership, API boundaries, credentials, plugin transport,
or the shared skill contract. Update it when those facts change.

## Invariants

- Never print, commit, copy, or place the ClickUp token in plugin/skill files.
- Keep `src/clickup_control/` and `bin/` as the runtime owner. Plugin and skill
  surfaces stay thin and call this runtime.
- Read operations may run directly. Every API mutation requires a one-use,
  body-bound preview token; bulk, merge, and delete flows require user review.
- Keep the official OAuth ClickUp connector for semantic search and common
  composites; this API control plane complements it.
- Treat Chat v3 as experimental and UI-only Automations, Dashboards, and
  Whiteboards as desktop/browser fallbacks.

## Verification

```bash
uv run pytest
uv run ruff check .
bin/clickup doctor --live
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/clickup-control/skills/1clickup
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/clickup-control
claude plugin validate plugins/clickup-control --strict
```
