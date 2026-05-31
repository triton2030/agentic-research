---
description: "Skill workflow equivalence map for MCP-to-CLI migration and live skill docs."
read-before-edit: []
edit-after-edit: []
---
# Skills Semantic Equivalence

Task-003 reference: MCP -> CLI migration must preserve each affected skill pattern.

Source inputs:

- `docs/mcp-usages-extracted.csv`
- `docs/tool-signatures-snapshot.json`
- `docs/cli-signatures-canonical.md`

### Shared Migration Rules

- Skills call `md <subcommand> ... --json`; MCP tool names stay preserved in `catalog.py` as contract IDs.
- `_envelope` shape stays stable; only invocation syntax changes.
- Mutating/cost-bearing tools use dry-run first and do not receive runnable confirm directives until a transaction token exists. Gated CLI signatures include `--transaction-id`; migrated skills must not say bare `--confirm`.
- Path filters become repeated `--path-include` / `--path-exclude` flags.
- When `_envelope.corpus_state.recommended_action` or `_envelope.next_step[]`
  provides args, migrated skills must preserve them as-is. This keeps
  parent-corpus and path-filter scope intact for nested corpus repairs.
- Enum lists such as `types` may use comma-separated CLI values.
- Legacy helper names such as `md_navigator.py`, `md_graph.py`, `md_navigator` and `md_graph` were removed and are not MCP tools. Do not auto-map them to the nearest `md <subcommand>`; each skill section must choose an explicit `md <subcommand>` replacement.

## 1md-navigator

**Назначение**: Semantic reader for Markdown corpora; owns search, map, extraction and corpus hygiene probes.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_search` | 18 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_orient` | 8 | `md orient CORPUS [--max-heading-level MAX_HEADING_LEVEL] [--top TOP] [--compact] [--expanded] --json` |
| `md_overlaps` | 6 | `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_audit` | 4 | `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_read_related` | 4 | `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json` |
| `md_extract` | 4 | `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json` |
| `md_corpus_scan` | 3 | `md corpus-scan [ROOT] --json` |
| `md_index` | 2 | `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json` |
| `md_init` | 2 | `md init [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_strip` | 2 | `md strip [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--also-related-section] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_profile_sections` | 2 | `md profile-sections CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--limit LIMIT] [--force] [--mode MODE] [--model MODEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_edit_context` | 2 | `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json` |
| `md_repeated_concepts` | 2 | `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_health` | 2 | `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_refactor_candidates` | 2 | `md refactor-candidates CORPUS [--top TOP] [--uniqueness-threshold UNIQUENESS_THRESHOLD] [--owner-confidence-threshold OWNER_CONFIDENCE_THRESHOLD] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json` |
| `md_query_by_type` | 2 | `md query-by-type CORPUS --types TYPES [--filter FILTER] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json` |
| `md_ls` | 2 | `md ls PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] --json` |
| `md_ping` | 2 | `md ping  --json` |

Legacy helper names also found, not MCP tools: `md_navigator` (4).

**CLI invocations после migration**:

- `md_index` -> `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json`
- `md_init` -> `md init [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_strip` -> `md strip [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--also-related-section] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_profile_sections` -> `md profile-sections CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--limit LIMIT] [--force] [--mode MODE] [--model MODEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_orient` -> `md orient CORPUS [--max-heading-level MAX_HEADING_LEVEL] [--top TOP] [--compact] [--expanded] --json`
- `md_corpus_scan` -> `md corpus-scan [ROOT] --json`
- `md_audit` -> `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_read_related` -> `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json`
- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_extract` -> `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json`
- `md_edit_context` -> `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json`
- `md_overlaps` -> `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_repeated_concepts` -> `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_health` -> `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_refactor_candidates` -> `md refactor-candidates CORPUS [--top TOP] [--uniqueness-threshold UNIQUENESS_THRESHOLD] [--owner-confidence-threshold OWNER_CONFIDENCE_THRESHOLD] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json`
- `md_query_by_type` -> `md query-by-type CORPUS --types TYPES [--filter FILTER] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json`
- `md_ls` -> `md ls PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] --json`
- `md_ping` -> `md ping  --json`
- Legacy helper references are not auto-rewritten; each skill section must either name an explicit CLI replacement or keep the helper as a legacy debug fallback/historical reference.

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- threshold/top IA probes keep numeric flags and path filters.
- graph hygiene commands keep path/scan/depth semantics.
- mutating/cost-bearing flow keeps dry-run/confirm/fingerprint safety.
- workflow tools stay agent-facing via `navigator.workflows` and thin CLI wrappers.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Legacy helper mentions may be mechanically rewritten incorrectly if treated as MCP tool names.
- Confirm flow can become unsafe if skill text asks for runnable confirm without transaction id; task-102/103/204 forbid this.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1md-graph

**Назначение**: Frontmatter and Markdown graph hygiene; owns preflight, impact, deps, scan, health and mutating graph tools.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_preflight` | 14 | `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_impact` | 12 | `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_check` | 7 | `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_deps` | 7 | `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_strip` | 6 | `md strip [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--also-related-section] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_section_blast_radius` | 6 | `md section-blast-radius PATH CORPUS --query QUERY [--heading-id HEADING_ID] [--scan SCAN] [--depth DEPTH] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_cycles` | 5 | `md cycles [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_scan` | 5 | `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_health` | 5 | `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_init` | 4 | `md init [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_edit_context` | 4 | `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json` |
| `md_search` | 2 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_read_related` | 2 | `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json` |
| `md_ping` | 2 | `md ping  --json` |

Legacy helper names also found, not MCP tools: `md_graph` (3).

**CLI invocations после migration**:

- `md_check` -> `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_cycles` -> `md cycles [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_scan` -> `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_health` -> `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_init` -> `md init [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_strip` -> `md strip [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--also-related-section] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_edit_context` -> `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json`
- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_section_blast_radius` -> `md section-blast-radius PATH CORPUS --query QUERY [--heading-id HEADING_ID] [--scan SCAN] [--depth DEPTH] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_read_related` -> `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json`
- `md_preflight` -> `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_deps` -> `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_impact` -> `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_ping` -> `md ping  --json`
- Legacy helper references are not auto-rewritten; each skill section must either name an explicit CLI replacement or keep the helper as a legacy debug fallback/historical reference.

**Representative calls to preserve**:

- `md edit-context PATH --mode preview --json`; switch to `--expanded` only when preview shows real obligations; use `--mode strict` only for blockers and anchor-drift risk.
- `md init --paths PATH --dry-run --json` then `md init --paths PATH --confirm --transaction-id <id> --json`; same transaction pattern for `md strip`.

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- graph hygiene commands keep path/scan/depth semantics and output-reading discipline: `must-read`, `must-update`, `check-only`, `anchor-drift risk`, `cycles`, `deferred`.
- mutating/cost-bearing flow keeps dry-run/confirm/fingerprint safety, with `transaction_required` on `md_init` / `md_strip` confirm.
- workflow tools stay agent-facing via `navigator.workflows` and thin CLI wrappers.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Legacy helper mentions may be mechanically rewritten incorrectly if treated as MCP tool names.
- Confirm flow can become unsafe if skill text asks for runnable confirm without transaction id; task-102/103/204 forbid this.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1ia-audit

**Назначение**: Information architecture smell check for Markdown corpus shape and retrieval paths.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_audit` | 20 | `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_search` | 8 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_overlaps` | 8 | `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_repeated_concepts` | 6 | `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_extract` | 4 | `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json` |
| `md_toc` | 4 | `md toc PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] --json` |
| `md_refactor_candidates` | 2 | `md refactor-candidates CORPUS [--top TOP] [--uniqueness-threshold UNIQUENESS_THRESHOLD] [--owner-confidence-threshold OWNER_CONFIDENCE_THRESHOLD] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json` |
| `md_read_related` | 2 | `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json` |
| `md_importance` | 2 | `md importance CORPUS [--top TOP] [--sort-by SORT_BY] --json` |
| `md_deps` | 2 | `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_health` | 2 | `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_impact` | 2 | `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |

**CLI invocations после migration**:

- `md_audit` -> `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_overlaps` -> `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_repeated_concepts` -> `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_extract` -> `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json`
- `md_toc` -> `md toc PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] --json`
- `md_refactor_candidates` -> `md refactor-candidates CORPUS [--top TOP] [--uniqueness-threshold UNIQUENESS_THRESHOLD] [--owner-confidence-threshold OWNER_CONFIDENCE_THRESHOLD] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json`
- `md_read_related` -> `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json`
- `md_importance` -> `md importance CORPUS [--top TOP] [--sort-by SORT_BY] --json`
- `md_deps` -> `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_health` -> `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_impact` -> `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- threshold/top IA probes keep numeric flags and path filters.
- graph hygiene commands keep path/scan/depth semantics.
- workflow tools stay agent-facing via `navigator.workflows` and thin CLI wrappers.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1instruction-layer

**Назначение**: Instruction wording, placement and duplicate-rule cleanup for AGENTS/CLAUDE/skills.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_audit` | 5 | `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_overlaps` | 3 | `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_search` | 3 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_check` | 3 | `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_repeated_concepts` | 2 | `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_extract` | 2 | `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json` |
| `md_edit_context` | 2 | `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json` |
| `md_deps` | 2 | `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_preflight` | 2 | `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_section_blast_radius` | 2 | `md section-blast-radius PATH CORPUS --query QUERY [--heading-id HEADING_ID] [--scan SCAN] [--depth DEPTH] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_impact` | 2 | `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |

**CLI invocations после migration**:

- `md_overlaps` -> `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_repeated_concepts` -> `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_audit` -> `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_extract` -> `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json`
- `md_edit_context` -> `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json`
- `md_deps` -> `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_preflight` -> `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_section_blast_radius` -> `md section-blast-radius PATH CORPUS --query QUERY [--heading-id HEADING_ID] [--scan SCAN] [--depth DEPTH] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_impact` -> `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_check` -> `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- threshold/top IA probes keep numeric flags and path filters.
- graph hygiene commands keep path/scan/depth semantics.
- workflow tools stay agent-facing via `navigator.workflows` and thin CLI wrappers.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1planning

**Назначение**: Recursive planning over roadmap, task files and closeout evidence.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_search` | 4 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_orient` | 2 | `md orient CORPUS [--max-heading-level MAX_HEADING_LEVEL] [--top TOP] [--compact] [--expanded] --json` |
| `md_ls` | 2 | `md ls PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] --json` |
| `md_extract` | 2 | `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json` |
| `md_preflight` | 2 | `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_edit_context` | 2 | `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json` |
| `md_deps` | 2 | `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_repeated_concepts` | 2 | `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_scan` | 2 | `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_query_by_type` | 2 | `md query-by-type CORPUS --types TYPES [--filter FILTER] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json` |

**CLI invocations после migration**:

- `md_orient` -> `md orient CORPUS [--max-heading-level MAX_HEADING_LEVEL] [--top TOP] [--compact] [--expanded] --json`
- `md_ls` -> `md ls PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] --json`
- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_extract` -> `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json`
- `md_preflight` -> `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_edit_context` -> `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json`
- `md_deps` -> `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_repeated_concepts` -> `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_scan` -> `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_query_by_type` -> `md query-by-type CORPUS --types TYPES [--filter FILTER] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json`

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- threshold/top IA probes keep numeric flags and path filters.
- graph hygiene commands keep path/scan/depth semantics.
- workflow tools stay agent-facing via `navigator.workflows` and thin CLI wrappers.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1strategy

**Назначение**: Moment strategy and decision-thinking over current project context.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_search` | 3 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_extract` | 1 | `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json` |
| `md_read_related` | 1 | `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json` |
| `md_orient` | 1 | `md orient CORPUS [--max-heading-level MAX_HEADING_LEVEL] [--top TOP] [--compact] [--expanded] --json` |
| `md_query_by_type` | 1 | `md query-by-type CORPUS --types TYPES [--filter FILTER] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json` |
| `md_impact` | 1 | `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_preflight` | 1 | `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |

**CLI invocations после migration**:

- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_extract` -> `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json`
- `md_read_related` -> `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json`
- `md_orient` -> `md orient CORPUS [--max-heading-level MAX_HEADING_LEVEL] [--top TOP] [--compact] [--expanded] --json`
- `md_query_by_type` -> `md query-by-type CORPUS --types TYPES [--filter FILTER] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json`
- `md_impact` -> `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_preflight` -> `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- graph hygiene commands keep path/scan/depth semantics.
- workflow tools stay agent-facing via `navigator.workflows` and thin CLI wrappers.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1strategy-docs

**Назначение**: Goal, README and roadmap shape owner.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

- No direct MCP tool references found in `SKILL.md`; migration check is references/default-prompt only.

**CLI invocations после migration**:

- No direct MCP replacement required in `SKILL.md`; verify references and generated catalog links.

**Semantic patterns preserved**:

- No direct MCP tool semantics in `SKILL.md`; generated catalog/reference wording is the migration surface.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Verify no stale MCP wording remains in this skill references/default prompt.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1folder-contract

**Назначение**: Folder graph, Owner Decision Map and structural guardrails.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_search` | 6 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_deps` | 4 | `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_repeated_concepts` | 4 | `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_cycles` | 3 | `md cycles [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_check` | 3 | `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_impact` | 3 | `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_overlaps` | 2 | `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_health` | 2 | `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_index` | 1 | `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json` |
| `md_scan` | 1 | `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_preflight` | 1 | `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |

**CLI invocations после migration**:

- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_deps` -> `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_repeated_concepts` -> `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_overlaps` -> `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_cycles` -> `md cycles [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_health` -> `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_check` -> `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_index` -> `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json`
- `md_scan` -> `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_impact` -> `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_preflight` -> `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- threshold/top IA probes keep numeric flags and path filters.
- graph hygiene commands keep path/scan/depth semantics.
- mutating/cost-bearing flow keeps dry-run/confirm/fingerprint safety.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Confirm flow can become unsafe if skill text asks for runnable confirm without transaction id; task-102/103/204 forbid this.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1assumption-audit

**Назначение**: Assumption and semantic predicate audit.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_search` | 9 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_overlaps` | 3 | `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_read_related` | 1 | `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json` |
| `md_index` | 1 | `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json` |

Legacy helper names also found, not MCP tools: `md_navigator` (1).

**CLI invocations после migration**:

- `md_overlaps` -> `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_read_related` -> `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json`
- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_index` -> `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json`
- Legacy helper references are not auto-rewritten; each skill section must either name an explicit CLI replacement or keep the helper as a legacy debug fallback/historical reference.

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- threshold/top IA probes keep numeric flags and path filters.
- mutating/cost-bearing flow keeps dry-run/confirm/fingerprint safety.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Legacy helper mentions may be mechanically rewritten incorrectly if treated as MCP tool names.
- Confirm flow can become unsafe if skill text asks for runnable confirm without transaction id; task-102/103/204 forbid this.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1work-review

**Назначение**: Closeout and acceptance review after meaningful work.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_preflight` | 4 | `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_check` | 4 | `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_health` | 4 | `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_status` | 3 | `md status CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_index` | 3 | `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json` |
| `md_edit_context` | 2 | `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json` |
| `md_search` | 2 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_extract` | 2 | `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json` |
| `md_cycles` | 2 | `md cycles [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_scan` | 2 | `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_audit` | 2 | `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_impact` | 2 | `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_read_related` | 2 | `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json` |

**CLI invocations после migration**:

- `md_preflight` -> `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_check` -> `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_health` -> `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_edit_context` -> `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json`
- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_extract` -> `md extract --map-data MAP_DATA [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json`
- `md_cycles` -> `md cycles [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_scan` -> `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_audit` -> `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_impact` -> `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_read_related` -> `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json`
- `md_status` -> `md status CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_index` -> `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json`

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- threshold/top IA probes keep numeric flags and path filters.
- graph hygiene commands keep path/scan/depth semantics.
- mutating/cost-bearing flow keeps dry-run/confirm/fingerprint safety.
- workflow tools stay agent-facing via `navigator.workflows` and thin CLI wrappers.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Confirm flow can become unsafe if skill text asks for runnable confirm without transaction id; task-102/103/204 forbid this.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1skill-architect

**Назначение**: Skill contract, trigger, packaging and installed-skill architecture.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_index` | 3 | `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json` |
| `md_search` | 3 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_overlaps` | 3 | `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |

Legacy helper names also found, not MCP tools: `md_navigator` (1).

**CLI invocations после migration**:

- `md_index` -> `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json`
- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_overlaps` -> `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- Legacy helper references are not auto-rewritten; each skill section must either name an explicit CLI replacement or keep the helper as a legacy debug fallback/historical reference.

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`.
- threshold/top IA probes keep numeric flags and path filters.
- mutating/cost-bearing flow keeps dry-run/confirm/fingerprint safety.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Legacy helper mentions may be mechanically rewritten incorrectly if treated as MCP tool names.
- Confirm flow can become unsafe if skill text asks for runnable confirm without transaction id; task-102/103/204 forbid this.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1smart-simple

**Назначение**: Dense rewrite and simplification with corpus/context checks.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

| Tool | Hits | Representative CLI equivalent |
|---|---:|---|
| `md_index` | 6 | `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json` |
| `md_search` | 2 | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| `md_overlaps` | 2 | `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| `md_audit` | 2 | `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |

Legacy helper names also found, not MCP tools: `md_navigator` (4).

**CLI invocations после migration**:

- `md_search` -> `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json`
- `md_index` -> `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json`
- `md_overlaps` -> `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- `md_audit` -> `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json`
- Legacy helper references are not auto-rewritten; each skill section must either name an explicit CLI replacement or keep the helper as a legacy debug fallback/historical reference.

**Representative calls to preserve**:

- Per-span dedupe search: `md search CORPUS --query "<unit gist>" --limit 3 --json`; the `limit=3` value is semantic because the skill compares top-1 ownership against nearby alternatives.
- Folder optimization warmup: `md index FOLDER --dry-run --json`; after dry-run returns `transaction_id`, use `md index FOLDER --confirm --transaction-id <id> --json`. Do not migrate to bare `--confirm`.
- Duplicate probe: `md overlaps FOLDER --threshold 0.85 --top 20 --json`; both numbers are live skill thresholds.
- Audit orchestration: `md audit FOLDER --json` remains the product path for cluster + overlaps signals.
- Cluster topology: use `md cluster FOLDER --k N --json` when a standalone read-only cluster signal is needed; keep `md audit` for the broader health packet.

**Semantic patterns preserved**:

- query/scope/limit patterns become explicit CLI flags with `--json`, especially `--limit 3`.
- threshold/top IA probes keep concrete `--threshold 0.85` and `--top 20`.
- mutating/cost-bearing flow keeps dry-run/confirm/fingerprint safety via `--transaction-id`.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.
- Legacy helper mentions may be mechanically rewritten incorrectly if treated as MCP tool names.
- Confirm flow can become unsafe if skill text asks for runnable confirm without transaction id; task-102/103/204 forbid this.
- Cold index or OpenRouter access can change response path; task-204 and envelope next_step keep repair guidance.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Spot-check representative commands above against snapshot parity tests.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.

## 1cli-tools

**Назначение**: CLI evidence routing and helper references for repo work.

**Когда срабатывает**: см. live `SKILL.md`; platforms represented: claude, codex.

**MCP usage сейчас**:

- No direct MCP tool references found in `SKILL.md`; migration check is references/default-prompt only.

**CLI invocations после migration**:

- No direct MCP replacement required in `SKILL.md`; verify references and generated catalog links.

**Semantic patterns preserved**:

- No direct MCP tool semantics in `SKILL.md`; generated catalog/reference wording is the migration surface.

**Что может сломаться (risk)**:

- CLI flag drift from MCP schema; mitigated by `tests/test_catalog_contract.py` and `docs/cli-signatures-canonical.md`.

**Test plan**:

- After migration, run one trigger prompt for this skill and verify first tool command is `md ... --json`, not `mcp__md-mcp__*`.
- Verify no stale MCP wording remains in this skill references/default prompt.

**What becomes possible**:

- The skill can discover current tool docs with `md tools --json` after installation, without MCP registration.
