# CLI Signatures Canonical

Generated from `src/md_cli/catalog.py`.

| Tool | Command | CLI signature |
|---|---|---|
| md_audit | `md audit` | `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| md_coherence_audit | `md coherence-audit` | `md coherence-audit PATH [--anchor ANCHOR] [--scan SCAN] [--depth DEPTH] [--token-budget TOKEN_BUDGET] --json` |
| md_check | `md check` | `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_cluster | `md cluster` | `md cluster CORPUS [--k K] [--seed SEED] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--cache-dir CACHE_DIR] [--expanded] --json` |
| md_corpus_scan | `md corpus-scan` | `md corpus-scan [ROOT] --json` |
| md_canon_check | `md canon-check` | `md canon-check FILE [CORPUS] [--mode MODE] [--limit LIMIT] [--max-claims MAX_CLAIMS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--rerank] [--expanded] --json` |
| md_cycles | `md cycles` | `md cycles [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_deps | `md deps` | `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_edit_context | `md edit-context` | `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] [--expanded] --json` |
| md_extract | `md extract` | `md extract [--map-data MAP_DATA] [--map-stdin] [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json` |
| md_health | `md health` | `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_impact | `md impact` | `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_importance | `md importance` | `md importance CORPUS [--top TOP] [--sort-by SORT_BY] --json` |
| md_index | `md index` | `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] [--cleanup-shadowed] [--vacuum] --json` |
| md_init | `md init` | `md init [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_ls | `md ls` | `md ls PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] [--expanded] --json` |
| md_orient | `md orient` | `md orient CORPUS [--max-heading-level MAX_HEADING_LEVEL] [--top TOP] [--compact] [--expanded] --json` |
| md_overlaps | `md overlaps` | `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| md_ping | `md ping` | `md ping  --json` |
| md_preflight | `md preflight` | `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_profile_sections | `md profile-sections` | `md profile-sections CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--limit LIMIT] [--force] [--mode MODE] [--model MODEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_query_by_type | `md query-by-type` | `md query-by-type CORPUS --types TYPES [--filter FILTER] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json` |
| md_read_related | `md read-related` | `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] [--expanded] --json` |
| md_refactor_candidates | `md refactor-candidates` | `md refactor-candidates CORPUS [--top TOP] [--uniqueness-threshold UNIQUENESS_THRESHOLD] [--owner-confidence-threshold OWNER_CONFIDENCE_THRESHOLD] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] [--expanded] --json` |
| md_repeated_concepts | `md repeated-concepts` | `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| md_scan | `md scan` | `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_search | `md search` | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_search_read | `md search-read` | `md search-read CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--token-budget TOKEN_BUDGET] [--expanded] --json` |
| md_semantic_neighbors | `md semantic-neighbors` | `md semantic-neighbors TARGET CORPUS [--limit LIMIT] [--expanded] [--token-budget TOKEN_BUDGET] [--cache-dir CACHE_DIR] --json` |
| md_section_blast_radius | `md section-blast-radius` | `md section-blast-radius PATH CORPUS --query QUERY [--heading-id HEADING_ID] [--scan SCAN] [--depth DEPTH] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_status | `md status` | `md status CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--expanded] --json` |
| md_strip | `md strip` | `md strip [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--also-related-section] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_toc | `md toc` | `md toc PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] --json` |
| md_walk | `md walk` | `md walk PATH --anchor ANCHOR [--scan SCAN] [--depth DEPTH] [--token-budget TOKEN_BUDGET] --json` |
