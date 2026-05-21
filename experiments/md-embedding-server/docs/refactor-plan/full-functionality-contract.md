---
description: "Full functionality contract that md-tools-v2 must preserve for current skills."
read-before-edit:
  - "[[current-skill-usage-map.md]]"
  - "[[compatibility-and-migration.md]]"
edit-after-edit:
  - "[[jobs-and-moments.md]]"
  - "[[public-capability-contract.md]]"
  - "[[validation-and-release-gates.md]]"
---
# Full Functionality Contract

v2 переписывает код, а не скилы. Поэтому этот документ описывает весь
функционал, который текущие Codex/Claude skills ожидают от `md-mcp`,
`md_navigator.py` и `md_graph.py`.

Переключение v2 считается успешным только если skills продолжают работать
после замены backend-ссылки, MCP registration path, env vars or compatibility
shim.

## Source Evidence

Проверены текущие installed skills в:

- `/Users/triton/.codex/skills/**`
- `/Users/triton/.claude/skills/**`

Главная команда:

```bash
rg -n 'md_[a-z_]+' /Users/triton/.codex/skills /Users/triton/.claude/skills \
  --glob 'SKILL.md' --glob 'references/**' --glob 'agents/**'
```

## Global Compatibility Requirements

v2 должна сохранить:

- MCP server name and discoverability model for `md-mcp`.
- Existing public `md_*` tool names or compatibility aliases.
- Tool descriptions rich enough for agents to choose tools without rewriting
  skills.
- Read-only / lazy-write / mutating / destructive annotations.
- Guard pattern: `dry_run:true` before mutating or cost-bearing live runs,
  `confirm:true` for live mutation.
- Text-result compatibility unless a separate structured-output migration is
  explicitly planned.
- CLI fallback commands used in skill prose.
- Error classes for missing index, stale index, missing API key, bad path,
  confirm required and timeout.

## Priority Skill Compatibility

Особый приоритет: `1md-navigator`, `1md-graph` and `1strategy`. Эти скилы
должны использовать v2 как привыкли, без переписывания recipes.

### `1md-navigator`

Ожидает, что MCP остаётся главным путём, а CLI - fallback для отладки.

Критичные привычные сценарии:

- cold-start corpus orientation: `md_orient`;
- semantic file/section search: `md_search`, including `scope: descriptions`;
- packet reading after search/map: `md_extract`;
- linked context reading: `md_read_related`;
- corpus health and IA signals: `md_audit`, `md_overlaps`,
  `md_repeated_concepts`;
- refactor and typed-section probes: `md_refactor_candidates`,
  `md_query_by_type`, `md_profile_sections`;
- runtime setup and guards: `md_ping`, `md_index`, `md_init`, `md_strip`.

Compatibility requirement: same tool names, same core args, same result
families, same warm-index and cost-guard behavior.

### `1md-graph`

Ожидает, что graph tools возвращают action labels, not binary safe/unsafe.

Критичные привычные сценарии:

- pre-edit packet: `md_edit_context`;
- graph-only check: `md_preflight`;
- delete/rename radius: `md_impact`;
- forward/reverse edges: `md_deps`;
- section rewrite radius: `md_section_blast_radius`;
- repo graph health: `md_health`, `md_cycles`, `md_check`, `md_scan`;
- changed-file review: `md_changed`;
- schema cleanup: `md_init`, `md_strip`;
- runtime check: `md_ping`.

Compatibility requirement: preserve `must-read`, `must-update`,
`check-only`, `anchor-drift`, `cycles`, `has_blockers`, broken-link classes
and dry-run/confirm semantics.

### `1strategy`

Ожидает, что tools помогают проверить почву решения, а не заменить мышление.

Критичные привычные сценарии:

- ground-check existing project truth: `md_search`;
- extract top candidate sections: `md_extract`;
- read GOAL and related context: `md_read_related`;
- orient in new corpus/sub-project: `md_orient`;
- list decisions and open questions: `md_query_by_type`;
- resolve ambiguous semantic search with rerank: `md_search` with rerank;
- price one-way door edits: `md_impact` and `md_preflight`.

Compatibility requirement: strategy calls must stay cheap, bounded and
interpretable. v2 cannot turn these into broad slow audits by default.

## Navigation And Reading

| Tool | Required functionality | Skill consumers |
|---|---|---|
| `md_orient` | status + map + importance for cold-start corpus orientation, no embeddings | `1md-navigator`, `1planning`, `1strategy` |
| `md_ls` | list Markdown files with descriptions, heading counts and optional link counts | `1md-navigator`, `1planning` |
| `md_toc` | heading ids for later extraction | `1ia-audit` |
| `md_search` | semantic + lexical search, `scope: descriptions`, optional rerank, path filters | `1md-navigator`, `1strategy`, `1planning`, `1ia-audit`, `1instruction-layer`, `1folder-contract`, `1skill-architect`, `1smart-simple`, `1work-review` |
| `md_extract` | extract selected files/sections from map/search output | `1md-navigator`, `1strategy`, `1planning`, `1ia-audit`, `1instruction-layer`, `1work-review` |
| `md_read_related` | linked-neighborhood packet, preview/full modes | `1md-navigator`, `1md-graph`, `1strategy`, `1ia-audit`, `1work-review` |
| `md_importance` | graph centrality / hub candidates without embeddings | `1ia-audit` |

Compatibility note: `md_search` is the highest-blast tool. It must preserve
ranking fields, scope behavior, output maps usable by extract, stale-index
behavior and rerank metadata.

## Graph And Edit Safety

| Tool | Required functionality | Skill consumers |
|---|---|---|
| `md_edit_context` | combined pre-edit packet: graph obligations + related context; modes `preview`, `full`, `strict` | `1md-graph`, `1md-navigator`, `1planning`, `1instruction-layer`, `1work-review` |
| `md_preflight` | graph-only blockers, must-read, must-update, anchor-drift signal | `1md-graph`, `1strategy`, `1planning`, `1instruction-layer`, `1folder-contract`, `1work-review` |
| `md_impact` | delete/rename blast radius for file links, graph edges and body links | `1md-graph`, `1strategy`, `1ia-audit`, `1instruction-layer`, `1folder-contract`, `1work-review` |
| `md_deps` | forward and reverse graph edges with depth | `1md-graph`, `1planning`, `1ia-audit`, `1instruction-layer`, `1folder-contract` |
| `md_section_blast_radius` | hard graph layer + soft semantic layer for section rewrite | `1md-graph`, `1instruction-layer` |
| `md_changed` | git-diff-driven preflight for touched `.md` files | `1md-graph`, `1planning`, `1instruction-layer`, `1folder-contract`, `1work-review` |
| `md_health` | repo-level graph health summary | `1md-graph`, `1folder-contract`, `1ia-audit`, `1work-review` |
| `md_cycles` | edit-after-edit cycle detection | `1md-graph`, `1folder-contract`, `1work-review` |
| `md_check` | wikilink, anchor and markdown-link validation | `1md-graph`, `1instruction-layer`, `1folder-contract`, `1work-review` |
| `md_scan` | frontmatter schema and legacy-field issues | `1md-graph`, `1planning`, `1folder-contract`, `1work-review` |

Compatibility note: graph output must keep action labels. Skills read
`must-read`, `must-update`, `check-only`, `anchor-drift`, `cycles`,
`has_blockers` and broken-link classes as evidence, not binary safety.

## Audit, IA And Semantic Health

| Tool | Required functionality | Skill consumers |
|---|---|---|
| `md_audit` | corpus health packet: discovery gaps, smeared owner truth, tight duplicates, template family, intra-file drift, cluster-folder mismatch | `1md-navigator`, `1ia-audit`, `1instruction-layer`, `1smart-simple`, `1work-review` |
| `md_overlaps` | pair-level semantic overlap candidates with threshold and top controls | `1md-navigator`, `1ia-audit`, `1instruction-layer`, `1folder-contract`, `1skill-architect`, `1smart-simple` |
| `md_repeated_concepts` | concept graph over repeated meaning across files | `1md-navigator`, `1ia-audit`, `1instruction-layer`, `1folder-contract`, `1planning` |
| `md_refactor_candidates` | human-reviewed refactor proposal candidates, never auto-edit | `1md-navigator`, `1ia-audit` |
| `md_query_by_type` | section profile query by open-question, decision, definition, rule, example and related types | `1md-navigator`, `1strategy`, `1planning` |
| `md_profile_sections` | profile cache creation, heuristic or LLM mode, cost guarded | `1md-navigator` |

Compatibility note: these tools are not optional from the skill perspective.
They may move to another backend layer internally, but the current skills still
expect them as evidence-gathering tools.

## Index, Runtime And Mutations

| Tool | Required functionality | Skill consumers |
|---|---|---|
| `md_ping` | server health, version and resolved script paths | `1md-navigator`, `1md-graph` |
| `md_status` | index freshness without HTTP or writes | `1work-review` |
| `md_index` | dry-run estimate, confirm-required live indexing, sticky model behavior, path filters | `1md-navigator`, `1skill-architect`, `1smart-simple`, `1work-review`, `1folder-contract` |
| `md_init` | add graph frontmatter template with dry-run/confirm | `1md-graph`, `1md-navigator` |
| `md_strip` | remove legacy/unknown graph fields and optional related section with dry-run/confirm | `1md-graph`, `1md-navigator` |

Compatibility note: stateful tools must be explicit about cost and side
effects. v2 cannot make these silently read-only or silently mutating.

## CLI Fallback Surface

Skills still mention CLI fallback. v2 must either preserve these commands or
provide a shim:

- `md_navigator.py map`
- `md_navigator.py headings`
- `md_navigator.py search`
- `md_navigator.py pick`
- `md_navigator.py read`
- `md_navigator.py read-related`
- `md_navigator.py overlaps`
- `md_navigator.py repeated-concepts`
- `md_navigator.py cluster`
- `md_navigator.py audit`
- `md_navigator.py index`
- `md_navigator.py status`
- `md_navigator.py profile-sections`
- `md_navigator.py refactor-candidates`
- `md_navigator.py query-by-type`
- `md_navigator.py manifest`
- `md_graph.py preflight`
- `md_graph.py impact`
- `md_graph.py deps`
- `md_graph.py health`
- `md_graph.py cycles`
- `md_graph.py check`
- `md_graph.py scan`
- `md_graph.py changed`
- `md_graph.py init`
- `md_graph.py strip`

If any CLI command changes shape, the migration doc must name the compatibility
shim before code switch.

## Link Switch Contract

The preferred migration target is:

1. Keep current skill recipes unchanged.
2. Point MCP registration to v2 server.
3. Preserve `MD_NAVIGATOR_SCRIPT` and `MD_GRAPH_SCRIPT` override semantics.
4. Keep old script names available through wrapper or symlink if skills or
   humans use CLI fallback.
5. Run workflow replay before changing any installed skill text.

This means v2 can reorganize code internally, but cannot use "we will rewrite
skills" as a migration strategy.
