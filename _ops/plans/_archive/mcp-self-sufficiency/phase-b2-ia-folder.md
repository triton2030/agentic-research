# Phase B2 — Skills: 1ia-audit + 1folder-contract (Claude + Codex)

**Owner**: subagent (general-purpose)
**Parent plan**: [README](README.md)
**Depends on**: Phase A done
**Parallel with**: B1, B3, B4

## Цель

Переписать 4 SKILL.md в overlay style под новый MCP surface. **Без дублирования tool spec.**

## Read FIRST

1. `experiments/md-embedding-server/mcp/README.md` (Phase A output)
2. `experiments/md-embedding-server/mcp/src/server.js` (registered tools)
3. `/Users/triton/Documents/GitHub/agentic-research/_ops/plans/mcp-self-sufficiency/README.md`
4. Current 4 SKILL.md в batch

## Files in your batch

1. `~/.claude/skills/1ia-audit/SKILL.md`
2. `~/.claude/skills/1folder-contract/SKILL.md`
3. `~/.codex/skills/1ia-audit/SKILL.md`
4. `~/.codex/skills/1folder-contract/SKILL.md`

## Rewrite contract — overlay style

См. полный contract в [`phase-b1-navigator-graph.md#rewrite-contract`](phase-b1-navigator-graph.md). Краткое:

- KEEP: frontmatter, purpose, boundaries, workflows (в новой shape), stop rules
- DROP: long CLI listings, tool spec duplication, mode tables
- ADD: workflow recipes (когда / tool / read как / drilldown / не путать), interpretation rules

## What each skill owns post-rewrite

### `1ia-audit`

**Owns workflows**: IA smell check для surface. Probes mapping:
- **Discovery gaps** → `md_audit` (class `discovery_gaps`) + `md_search --scope descriptions` (owner detection)
- **Smeared owner truth** → `md_repeated_concepts` (flagship probe) + `md_overlaps` (pair-wise evidence) + `md_audit` (class `smeared_owner_truth`)
- **Function split** → `md_audit` (class `intra_file_drift`) + `md_toc` + `md_extract` для прочесть несколько секций
- **Tight duplicates** → `md_audit` (class `tight_duplicates`) + `md_overlaps` точечно
- **Template family / view vs truth** → `md_audit` (class `template_family`)
- **Cluster vs folder** → `md_audit` (class `cluster_folder_mismatch`)
- **Retrieval path** → `md_search` (probe «может ли future agent найти», quality of top result)
- **Container fit, future growth, drift cost, naming, distribution balance** — manual judgment, MCP не покрывает

**Owns interpretation**:
- Metrics ≠ verdict: metric → smell → file evidence → IA judgment → smallest repair
- One overlap pair = candidate not proof; repeated-concept across many files = strong owner-truth signal
- `md_audit --json` → packet to feed `1fresh-eyes` lens subagents (structured evidence packet)
- Refactor proposals (через `md_refactor_candidates`) = reading list, не auto-edit

**Owns boundaries**: defers graph repair to `1md-graph`; defers prose placement to `1instruction-layer`; defers user quote capture to `1user-said`; subagent execution to `1fresh-eyes`.

### `1folder-contract`

**Owns workflows**: architectural blueprint maintenance.
- **System coherence audit**: `md_health` (graph overview) + `md_overlaps` / `md_repeated_concepts` (smeared truth across instruction files) + `md_search` (Owner Map references actually exist + ownership leak detection)
- **Owner Decision Map maintenance**: `md_search` (find where domain mentioned) + `md_check` (Owner Map wikilinks valid)
- **Folder graph (`project-graph.md`) maintenance**: `md_ls` (folder inventory) + `md_deps` (downstream of GOAL.md)
- **Goal-цитата sync** (CLAUDE.md ↔ AGENTS.md): `md_search` (find quote across files) + `md_changed` (after GOAL edit, what re-checks)
- **Detect ownership leaks**: `md_overlaps` (smeared truth) + `md_repeated_concepts` (concept-graph)
- **Cycle detection in obligations**: `md_cycles`

**Owns interpretation**:
- Hub with many holders + no clear owner declaration = smeared owner-truth candidate
- Orphan instruction file = unanchored content
- `edit-after-edit` cycle resisting removal = candidate merge / two files smearing one canon
- Goal-цитата drift = system coherence failure (Goal должен быть source of truth)

**Owns boundaries**: defers language quality of prose to `1instruction-layer`; defers IA container shape to `1ia-audit`; defers thinking-about-goal to `1strategy-docs`; defers durable user quote to `1user-said`.

## Workflow recipe template

```markdown
### <Workflow name>

**Когда**: <trigger / user intent>
**Главный tool**: `md_<X>({ <key args> })`
**Read output как**: <interpretation rule>
**Если нужно глубже**: <atomic drilldown>
**Не путать с**: <similar workflow elsewhere>
```

## Codex side specifics

- `$1xxx` skill ref prefix preserved
- `~/.codex/skills/` paths preserved in framing
- `agents/openai.yaml` out of scope unless stale tool refs

## Definition of done

- 4 SKILL.md rewritten in overlay style
- IA smell → MCP probe mapping table в `1ia-audit` clear and current
- System coherence audit workflow в `1folder-contract` references real MCP tools
- No CLI command listings (MCP-only invocation surface)
- File length ≤ 60% of pre-rewrite

## Report (<500 words)

- 4 files rewritten — diff size summary
- Smell → probe mapping table contents (for 1ia-audit)
- Coherence audit workflow steps (for 1folder-contract)
- Anything surprising or unfit (e.g. concept in old SKILL.md that doesn't map to any MCP tool)
- Cross-skill boundary findings

Don't run smoke. Don't commit.
