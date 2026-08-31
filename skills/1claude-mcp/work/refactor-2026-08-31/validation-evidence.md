# Validation evidence — exact candidate before approval

## Exact bytes

- Candidate tree:
  `skills/1claude-mcp/work/refactor-2026-08-31/draft/`.
- Aggregate SHA-256 over sorted per-file SHA-256 records:
  `33e8028a47c7a40d484855962875935bd1c69741f157d1f0933665a5398efcfe`.
- Package size: 229 lines across `SKILL.md`, eleven references and
  `agents/openai.yaml`; old package size: 301 lines.

## Mechanical evidence

| Check | Result |
| --- | --- |
| System `skill-creator/scripts/quick_validate.py` | `Skill is valid!` |
| `rumdl check` on 24 history/candidate Markdown files | No issues |
| `md check --paths skills/1claude-mcp --json` | 24 targets, 0 issues |
| YAML parse of `agents/openai.yaml` | pass |
| Frontmatter parse and description length | pass; 195 characters |
| Every Markdown link target exists | pass |
| Every reference is routed exactly once from `SKILL.md` | pass; 11/11 |
| Global-artifact path scan | no user, repo or bridge-local runtime path |
| `git diff --check` on owned changes | pass |

## Semantic evidence

- Current host exposes all four named tools:
  `mcp__claude_mcp__claude_ask`, `claude_session`, `claude_observe` and
  `claude_sessions` under the same namespace.
- `experiments/claude-bridge/src/claude-policy.js:11-24` proves
  `profile: opus_advisor`, `requestedModel: opus`, `claude-opus-5`, default
  `xhigh` and optional `max`.
- `experiments/claude-bridge/src/claude-result.js:33-35,71-113` proves native
  session/model gates and the accepted one-shot evidence fields.
- `experiments/claude-bridge/src/ask-server.js:136-225` proves blocking ask,
  stateful session, bounded observe and read-only session inspection surfaces.
- `reference-map.md` counts separately violable predicates; no file exceeds
  twenty units.

## Residual risks

- No live Anthropic call was made against an uninstalled draft; doing so would
  test the old installed skill and spend an external call without proving draft
  installation.
- Installation, owner/projection parity and bridge regression tests remain
  intentionally pending until unconditional owner approval.
- Official Anthropic prompting guidance is volatile; the skill keeps only the
  current Opus deltas and records the official page in `cut.md`.
