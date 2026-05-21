# Phase B4 — Skills: 1strategy + 1work-review (Claude + Codex)

**Owner**: subagent (general-purpose)
**Parent plan**: [README](README.md)
**Depends on**: Phase A done
**Parallel with**: B1, B2, B3

## Цель

Переписать 4 SKILL.md в overlay style под новый MCP surface.

## Read FIRST

1. `experiments/md-embedding-server/mcp/README.md` (Phase A output)
2. `experiments/md-embedding-server/mcp/src/server.js`
3. `/Users/triton/Documents/GitHub/agentic-research/_ops/plans/mcp-self-sufficiency/README.md`
4. Current 4 SKILL.md в batch

## Files in your batch

1. `~/.claude/skills/1strategy/SKILL.md`
2. `~/.claude/skills/1work-review/SKILL.md`
3. `~/.codex/skills/1strategy/SKILL.md`
4. `~/.codex/skills/1work-review/SKILL.md`

Также:
- `~/.claude/skills/1strategy/references/internal-tools.md` (если есть — обычно describes mental tools, не MCP — likely no rewrite needed)
- `~/.codex/skills/1work-review/agents/openai.yaml` (если есть — обычно agent definition; out of scope unless stale tool refs)

## Rewrite contract

См. полный contract в [`phase-b1-navigator-graph.md#rewrite-contract`](phase-b1-navigator-graph.md).

## What each skill owns post-rewrite

### `1strategy`

**Read-only skill** — momentum decision-thinking при выполнении задач. Approach-choice, ground-check, mental tools (OODA, first-principles, premortem, adversarial). НЕ пишет файлов.

**Owns workflows**:
- **Ground-check «было ли решение уже зафиксировано»**: `md_search` across `_ops/user-said/`, `_ops/findings/`, GOAL, AGENTS, CLAUDE
- **Read GOAL с context**: `md_read_related _ops/GOAL.md`
- **Cold-start orientation**: `md_orient` (unfamiliar project)
- **Find prior decisions / open questions**: `md_query_by_type --types decision` / `--types open-question`
- **Quick folder inventory**: `md_ls`
- **Multi-section batch read** для thinking context: `md_extract`

**Owns interpretation** (mental tools shared с `1strategy-docs`):
- OODA orient — read terrain before responding
- First-principles — strip assumed structure, derive
- Premortem — imagine failure mode, work backward
- Adversarial self-play — pose worst-case challenge to current path
- One-way vs two-way doors — reversibility filter

**Owns boundaries**: NO writes (this is internal thinking, не doc-writing). For goal/scope/done writes → `1strategy-docs`. For task contract writes → `1planning`. For durable user quote → `1user-said`.

### `1work-review`

**Closeout / post-execution gate**. After substantive write → compare diff with GOAL / anchor docs, route findings, output summary с маркером.

**Owns workflows**:
- **What changed in this batch**: `md_changed` (главный tool; runs preflight on every touched .md from git diff)
- **Closeout safety per file**: `md_preflight`
- **Verify changes match acceptance criteria**: `md_search` (find references to what was changed)
- **Overall graph health после batch**: `md_health`
- **Link validity after rename/move**: `md_check`
- **Cycle introduction check**: `md_cycles`
- **Holder updates after rename/delete**: `md_impact`
- **Frontmatter still valid**: `md_scan`

**Owns interpretation**:
- Anchor docs need explicit re-read after consequential turn (stale-anchor failure mode)
- `applied` / `read-now-only` / `missing` / `not applicable` labels for each anchor
- Closeout = compare with DoD от task contract, не just smoke pass
- Routes state changes к owner skills via canonical routing matrix

**Owns boundaries**: doesn't itself fix anything (read-only audit). Routes to owners: graph repair → `1md-graph`, prose placement → `1instruction-layer`, task state → `1planning`, etc. Subagent execution → `1fresh-eyes`.

## Workflow recipe template (same as B1)

```markdown
### <Workflow name>

**Когда**: <trigger>
**Главный tool**: `md_<X>({ args })`
**Read output как**: <interpretation>
**Если нужно глубже**: <drilldown>
**Не путать с**: <similar elsewhere>
```

## Codex specifics

`$1xxx` prefix preserved.

## Definition of done

- 4 SKILL.md rewritten in overlay style
- 1strategy stays read-only; workflows refactored to MCP tools but no writes
- 1work-review's closeout sweep uses `md_changed` as main entry, atomics for drilldown
- No CLI listings
- File length ≤ 60% of pre-rewrite

## Report (<500 words)

- Files rewritten + diff size
- Did 1strategy SKILL.md require splitting mental-tools content (probably belongs in `references/internal-tools.md` not main SKILL.md)?
- Did 1work-review's «applied / read-now-only / missing» labelling survive rewrite?
- Cross-skill boundary findings
