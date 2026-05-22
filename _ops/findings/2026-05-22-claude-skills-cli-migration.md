# Claude skills CLI migration evidence — 2026-05-22

## Scope

Claude skill files only, under the current `AGENTS.md` exception: explicit user
request + `1skill-architect`. No `CLAUDE.md`, `.claude/settings*`, hooks or
runtime configs were edited.

## Updated

- `/Users/triton/.claude/skills/1md-navigator/SKILL.md`
- `/Users/triton/.claude/skills/1md-navigator/references/setup.md`
- `/Users/triton/.claude/skills/1md-navigator/references/tool-catalog.md`
- `/Users/triton/.claude/skills/1md-graph/SKILL.md`
- `/Users/triton/.claude/skills/1ia-audit/SKILL.md`
- `/Users/triton/.claude/skills/1instruction-layer/SKILL.md`
- `/Users/triton/.claude/skills/1instruction-layer/references/language-quality-audit.md`
- `/Users/triton/.claude/skills/1assumption-audit/SKILL.md`
- `/Users/triton/.claude/skills/1planning/SKILL.md`
- `/Users/triton/.claude/skills/1strategy/SKILL.md`
- `/Users/triton/.claude/skills/1strategy-docs/SKILL.md`
- `/Users/triton/.claude/skills/1folder-contract/SKILL.md`
- `/Users/triton/.claude/skills/1work-review/SKILL.md`
- `/Users/triton/.claude/skills/1skill-architect/SKILL.md`
- `/Users/triton/.claude/skills/1smart-simple/SKILL.md`
- `/Users/triton/.claude/skills/1cli-tools/references/markdown-track.md`
- `/Users/triton/.claude/skills/1cli-tools/references/tool-map.md`

## Checks

- `python3 experiments/md-embedding-server/scripts/sync-skill-docs.py --check` → `Claude/Codex skill docs are CLI-migrated; tool catalogs are fresh.`
- `rg --pcre2 '<stale md tool-id / MCP / invalid md command pattern>' /Users/triton/.claude/skills /Users/triton/.codex/skills` → 0 matches.
- `diff ~/.codex/skills/1md-navigator/references/tool-catalog.md ~/.claude/skills/1md-navigator/references/tool-catalog.md` → empty.
- `wc -l .../tool-catalog.md` → 443 lines in each catalog.
- `find ~/.claude/skills/1md-navigator ~/.claude/skills/1md-graph ~/.codex/skills/1md-navigator ~/.codex/skills/1md-graph -name '*.py' -o -name '*.sh'` → 0 matches.

## Notes

- Extended Claude skills are declarative edits only. The broader extended-skill
  `find` sees one pre-existing helper, `/Users/triton/.claude/skills/1cli-tools/scripts/probe-tools.sh`;
  no executable files were added by this migration.
- An accidental broad rewrite briefly touched unrelated Claude skills; those
  non-target MCP wording regressions were repaired and re-scanned before this
  finding was written.

## Best-Practice Fit

pass — hot-path examples now use real `md <subcommand>` CLI syntax, generated
catalogs are identical across Claude/Codex, and transaction examples require
`--dry-run` then `--confirm --transaction-id <id>`.
