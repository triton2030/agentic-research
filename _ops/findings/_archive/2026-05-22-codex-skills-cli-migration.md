# Codex skills CLI migration evidence — 2026-05-22

## Scope

Codex-side migration. The earlier Claude-side handoff/blocker was superseded
by a later explicit user request plus the current `AGENTS.md` skill exception;
Claude-side evidence now lives in
`_ops/findings/2026-05-22-claude-skills-cli-migration.md`.

## Updated

- `/Users/triton/.codex/skills/1md-navigator/SKILL.md`
- `/Users/triton/.codex/skills/1md-navigator/references/setup.md`
- `/Users/triton/.codex/skills/1md-navigator/references/index-lifecycle.md`
- `/Users/triton/.codex/skills/1md-navigator/references/tool-catalog.md`
- `/Users/triton/.codex/skills/1md-navigator/agents/openai.yaml`
- `/Users/triton/.codex/skills/1md-graph/SKILL.md`
- `/Users/triton/.codex/skills/1md-graph/agents/openai.yaml`
- `/Users/triton/.codex/skills/1instruction-layer/SKILL.md`
- `/Users/triton/.codex/skills/1assumption-audit/SKILL.md`
- `/Users/triton/.codex/skills/1work-review/SKILL.md`
- `/Users/triton/.codex/skills/1skill-architect/SKILL.md`
- `/Users/triton/.codex/skills/1strategy/references/ground-check.md`
- `/Users/triton/.codex/skills/1ia-audit/references/md-evidence-probes.md`

No new executable files were added to skill folders.

## Checks

- `rg --pcre2 '<stale md tool-id / MCP / invalid md command pattern>' /Users/triton/.codex/skills` → 0 matches
- `python3 scripts/sync-skill-docs.py --check` → `Claude/Codex skill docs are CLI-migrated; tool catalogs are fresh.`
- `md --version` → `md-tools 0.7.0`
- `md tools --json | ...` → 29 tools
- `uv run pytest tests/ -q` → 174 passed
- `bash scripts/run-tests.sh -q` → 174 passed

## Best-Practice Fit

pass — hot paths now point at `md` CLI and generated catalog without turning
SKILL.md into duplicated tool documentation; `agents/openai.yaml` stayed in sync
where it mentioned execution behavior.

Fresh-eyes follow-up accepted and repaired stale plain `md_*` command tokens,
invalid `md map` / `md headings` / `md read` style commands, false-green sync
checks, and over-eager index-before-work metadata.
