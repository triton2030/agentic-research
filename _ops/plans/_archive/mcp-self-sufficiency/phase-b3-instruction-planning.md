# Phase B3 — Skills: 1instruction-layer + 1planning (Claude + Codex)

**Owner**: subagent (general-purpose)
**Parent plan**: [README](README.md)
**Depends on**: Phase A done
**Parallel with**: B1, B2, B4

## Цель

Переписать 4 SKILL.md в overlay style под новый MCP surface.

## Read FIRST

1. `experiments/md-embedding-server/mcp/README.md` (Phase A output)
2. `experiments/md-embedding-server/mcp/src/server.js`
3. `/Users/triton/Documents/GitHub/agentic-research/_ops/plans/mcp-self-sufficiency/README.md`
4. Current 4 SKILL.md в batch
5. `_ops/AGENTS.md` (если есть) — для понимания planning conventions

## Files in your batch

1. `~/.claude/skills/1instruction-layer/SKILL.md`
2. `~/.claude/skills/1planning/SKILL.md`
3. `~/.codex/skills/1instruction-layer/SKILL.md`
4. `~/.codex/skills/1planning/SKILL.md`

Также проверить references (если в скиле есть):
- `~/.claude/skills/1instruction-layer/references/language-quality-audit.md`
- `~/.claude/skills/1planning/references/archive-and-folders.md`
- Codex side same paths

## Rewrite contract

См. полный contract в [`phase-b1-navigator-graph.md#rewrite-contract`](phase-b1-navigator-graph.md).

## What each skill owns post-rewrite

### `1instruction-layer`

**Owns workflows**: language quality of instruction prose в `AGENTS.md` / `CLAUDE.md` / subtree.
- **Detect duplicate prose**: `md_overlaps` точечно по instruction files
- **Find rule references** (before reword): `md_search` (где правило цитируется)
- **Pre-edit safety**: `md_preflight` или `md_edit_context` preview
- **Section blast radius** (rewriting a section in CLAUDE.md): `md_section_blast_radius`
- **Post-batch verify**: `md_changed` → preflight на touched files
- **Link validity**: `md_check` (wikilinks/anchors)

**Owns interpretation**:
- Lost-in-middle — placement decision (top/bottom vs middle of instruction file)
- Literal-vs-class scope — Opus 4.7 reads «эта секция» literally, не applicable to all sections
- Hyrum unintentional contracts — long-form rules become implicit contracts
- Sycophancy in wording — declarative > tentative

**Owns boundaries**: defers folder graph / Owner Map / system coherence to `1folder-contract`; defers IA shape to `1ia-audit`; defers durable user quote to `1user-said`; defers skill matcher design to `1skill-architect`.

### `1planning`

**Owns workflows**: L1 roadmap + L2 task files + L3 substeps. Only active front. Archive/reconcile.
- **Find existing task by topic** (avoid dupes): `md_search` over `_ops/plans/**`
- **Pre-edit roadmap / task**: `md_preflight`
- **Cold start in unfamiliar project**: `md_orient`
- **What depends on this task**: `md_deps`
- **Post-batch closeout verify**: `md_changed`
- **Inventory plans**: `md_ls _ops/plans/`
- **Task file frontmatter check**: `md_scan`
- **Find prior decisions**: `md_query_by_type --types decision`

**Owns interpretation**:
- Active front only — don't pre-expand the whole task tree
- L2 task contracts anchored by AGENTS.md / CLAUDE.md
- Done state = reconcile with roadmap, then archive (don't accumulate done tasks in active surface)
- Substep granularity ~30 min units; if smaller, fold

**Owns boundaries**: defers project-charter shape to `1strategy-docs`; defers approach-choice thinking to `1strategy`; defers system coherence to `1folder-contract`; defers closeout verification to `1work-review`.

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

`$1xxx` prefix preserved; `~/.codex/skills/` paths preserved in framing.

## Definition of done

- 4 SKILL.md (+ ≤ 2 reference files if exist and touched) rewritten in overlay style
- Workflow → MCP tool mapping clear
- No CLI listings, no duplicated tool spec
- File length ≤ 60% of pre-rewrite

## Report (<500 words)

- Files rewritten + diff size
- Notable workflow → MCP tool decisions
- Anything that surprised (especially: did SKILL.md mix instructions for language-quality vs structure, requiring split)
- Cross-skill boundary findings
