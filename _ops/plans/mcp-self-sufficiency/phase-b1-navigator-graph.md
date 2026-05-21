# Phase B1 — Skills: 1md-navigator + 1md-graph (Claude + Codex)

**Owner**: subagent (general-purpose)
**Parent plan**: [README](README.md)
**Depends on**: Phase A done (new MCP tools exist)
**Parallel with**: B2, B3, B4 (disjoint files)

## Цель

Переписать 4 SKILL.md (2 скила × 2 платформы) под новый MCP surface (27 tools, self-sufficient descriptions). Skills становятся **overlay**: учат **когда применять / как интерпретировать** output, НЕ дублируют tool spec.

## Context — после Phase A

- MCP version 0.6.0
- 27 public tools: composite (6) + atomic navigation/content (7) + atomic graph (7) + IA probes (2) + git (1) + mutating (4)
- New tools на MCP: `md_overlaps`, `md_repeated_concepts`, `md_cycles`, `md_check`, `md_scan`, `md_changed`, `md_index`, `md_init`, `md_strip`, `md_profile_sections`, `md_extract` (merge of pick+cat)
- Описания в listTools self-sufficient (WHEN/WHY/INPUT/OUTPUT/ALT/COST)
- CLI остаётся доступен для debugging и hooks; не primary

## Read FIRST

1. `experiments/md-embedding-server/mcp/README.md` — updated catalog (Phase A output)
2. `experiments/md-embedding-server/mcp/src/server.js` — registered tools list
3. `/Users/triton/Documents/GitHub/agentic-research/_ops/plans/mcp-self-sufficiency/README.md` — design rationale
4. Current SKILL.md files (your batch's 4 files) — to understand current shape and what to preserve

## Files in your batch

1. `~/.claude/skills/1md-navigator/SKILL.md`
2. `~/.claude/skills/1md-graph/SKILL.md`
3. `~/.codex/skills/1md-navigator/SKILL.md`
4. `~/.codex/skills/1md-graph/SKILL.md`

## Rewrite contract — overlay style

Each SKILL.md after rewrite should:

**KEEP**:
- Frontmatter (name, description with trigger phrases)
- High-level purpose statement
- Skill boundaries (what owned, what not, what routes to other skills)
- Workflow recipes — но в новой shape (см. ниже)
- Stop rules

**DROP or COMPRESS**:
- Long CLI command listings (they're now in MCP, self-explanatory in listTools)
- Tool spec / arg descriptions (MCP owns those)
- Mode tables that duplicate MCP descriptions
- Examples that just demonstrate CLI invocation

**ADD or REFRAME**:
- **Workflow chapters**: each workflow (W1 orient, W2 find, W3 read-with-context, etc.) is a recipe — **agent intent + which MCP tool first + how to read output**. Tool spec NOT repeated.
- **Interpretation rules**: e.g. for 1md-graph «do not summarize preflight as safe/unsafe — it's evidence not warranty». For 1md-navigator: «search result is reading menu not proof».
- **Boundary clarifications**: routing to other skills

## Workflow recipe template

```markdown
### W<N> — <workflow name>

**Когда**: <trigger / user intent>
**Главный tool**: `md_<X>` — pass <key args>
**Read output как**: <interpretation rule>
**Если нужно глубже**: <next tool / atomic drilldown>
**Не путать с**: <similar workflow that goes elsewhere>
```

Example for 1md-navigator W2:
```
### W2 — Найти где обсуждается X

**Когда**: «где описан X», «найди секции про Y», «какие файлы про Z»
**Главный tool**: `md_search({ corpus, query })`. Для files-level: `scope: 'descriptions'`.
**Read output как**: reading menu, not proof. Top RRF dominates когда #1 > #2 by >25%.
**Если нужно глубже**: `md_extract({ map, ids, extract: true })` для multi-section packet.
**Не путать с**: exact strings / regex → `rg` via `1cli-tools`.
```

## What each skill owns post-rewrite

### `1md-navigator`

**Owns workflows**: W1 orient (cold-start), W2 find (semantic search), W3 read-with-context (linked + semantic), W6 corpus health (`md_audit`), W7 refactor opportunities, W8 semantic-shape query.

**Owns interpretation**:
- Search results = reading menu, не proof
- Overlaps pairs = candidates, not verdicts
- Repeated-concepts = flagship owner-truth signal (subsumes overlaps for owner detection)
- Cluster (через `md_audit`) = topology evidence
- Audit = orchestrated probe with 6 IA-classes; route findings to `1ia-audit` / `1md-graph` etc.
- Refactor proposals = reading list для editorial, не auto-edit

**Owns boundaries**: defers graph schema to `1md-graph`; defers shape verdict to `1ia-audit`; defers code/symbol search to `1cli-tools`.

### `1md-graph`

**Owns workflows**: W4 edit safety (`md_edit_context` / `md_preflight`), W5a delete/rename (`md_impact`), W5b section rename (`md_section_blast_radius`), schema cleanup (`md_init` / `md_strip` mutating), health probe (`md_health` + atomic `md_cycles`/`md_check`/`md_scan`).

**Owns interpretation**:
- Action labels (must-read / must-update / check-only / anchor-drift risk / deferred / cycles) — NEVER summarize as safe-to-edit yes/no
- `edit-after-edit: []` = positive claim, not default
- Schema: `description`, `read-before-edit`, `edit-after-edit` only (3 fields; legacy fields removed)
- Cycles = always a bug (mandatory cascade can't loop)

**Owns boundaries**: defers semantic widening to `1md-navigator search` / `read-related`; defers broad rg/lychee to `1cli-tools`; defers Obsidian UX to `1obsidian`.

## Codex side specifics

- `$1xxx` skill ref prefix in backticks (`$1md-graph`, `$1cli-tools`) — preserve
- Path prefix `~/.codex/skills/` — preserve where used (in setup / framing only, NOT for CLI examples — those now use in-repo path or just MCP tool names)
- Agents files (`agents/openai.yaml`) — out of scope for this batch unless they have stale tool refs

## Anti-patterns to avoid

- ❌ Re-listing every MCP tool's args inside SKILL.md (listTools owns that)
- ❌ Long CLI command examples that don't add interpretation value
- ❌ Duplicating boundaries already in `1md-graph` SKILL.md inside `1md-navigator` and vice versa (use links instead: «see [`1md-graph`] for graph blast radius»)
- ❌ Rewriting frontmatter description unless trigger surface changes
- ❌ Adding new workflow without clear use case from one of the 8 skills

## Definition of done

- 4 SKILL.md (2 Claude + 2 Codex) rewritten in overlay style
- Each workflow chapter follows recipe template (когда / tool / read как / drilldown / не путать)
- No duplicated MCP tool spec
- Boundaries clear: what's owned, what routes elsewhere
- Codex `$1` prefix preserved
- File length ≤ 60% of pre-rewrite (target: descriptions cut, recipes added; net shorter)

## Report (concise, <500 words)

- 4 files rewritten — diff size summary (line count before/after)
- Workflow recipes added (count, names)
- Interpretation rules added (count, names)
- Anything that surprised you (e.g. SKILL.md had content that didn't fit any tool — what to do with it)
- Concerns / cross-skill boundary findings

Don't run smoke. Don't commit. Parent verifies + commits.
