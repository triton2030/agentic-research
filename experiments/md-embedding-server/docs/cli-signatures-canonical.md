# Canonical CLI Signatures

Generated from `md_cli.catalog`.

| Tool | CLI subcommand | Canonical signature |
|---|---|---|
| md_audit | audit | `md audit CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_changed | changed | `md changed [--scan SCAN] [--depth DEPTH] [--base BASE] [--since SINCE] [--staged] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_check | check | `md check [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_corpus_scan | corpus-scan | `md corpus-scan [ROOT] --json` |
| md_cycles | cycles | `md cycles [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_deps | deps | `md deps PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_edit_context | edit-context | `md edit-context PATH [--mode MODE] [--scan SCAN] [--depth DEPTH] [--query QUERY] [CORPUS] --json` |
| md_extract | extract | `md extract [--map-data MAP_DATA] [--map-stdin] [--files FILES] [--headings HEADINGS] [--extract] [--token-budget TOKEN_BUDGET] --json` |
| md_health | health | `md health [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_impact | impact | `md impact PATH [--scan SCAN] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_importance | importance | `md importance CORPUS [--top TOP] [--sort-by SORT_BY] --json` |
| md_index | index | `md index CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--batch-size BATCH_SIZE] [--batch-pause-ms BATCH_PAUSE_MS] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--allow-nested-corpus] --json` |
| md_init | init | `md init [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_ls | ls | `md ls PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] --json` |
| md_orient | orient | `md orient CORPUS [--max-heading-level MAX_HEADING_LEVEL] [--top TOP] [--compact] --json` |
| md_overlaps | overlaps | `md overlaps CORPUS [--threshold THRESHOLD] [--top TOP] [--min-tokens MIN_TOKENS] [--include-same-file] [--max-heading-level MAX_HEADING_LEVEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_ping | ping | `md ping  --json` |
| md_preflight | preflight | `md preflight PATH [--scan SCAN] [--depth DEPTH] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_profile_sections | profile-sections | `md profile-sections CORPUS [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--limit LIMIT] [--force] [--mode MODE] [--model MODEL] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_query_by_type | query-by-type | `md query-by-type CORPUS --types TYPES [--filter FILTER] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] --json` |
| md_read_related | read-related | `md read-related --paths PATHS [--scan SCAN] [--include INCLUDE] [--mode MODE] [--anchor-aware] [--token-budget TOKEN_BUDGET] [--semantic-radius SEMANTIC_RADIUS] [--check-links] [--link-distance-threshold LINK_DISTANCE_THRESHOLD] --json` |
| md_refactor_candidates | refactor-candidates | `md refactor-candidates CORPUS [--top TOP] [--uniqueness-threshold UNIQUENESS_THRESHOLD] [--owner-confidence-threshold OWNER_CONFIDENCE_THRESHOLD] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--compact] --json` |
| md_repeated_concepts | repeated-concepts | `md repeated-concepts CORPUS [--threshold THRESHOLD] [--top TOP] [--min-files MIN_FILES] [--min-sections MIN_SECTIONS] [--min-tokens MIN_TOKENS] [--top-members TOP_MEMBERS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_scan | scan | `md scan [--paths PATHS] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_search | search | `md search CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_search_read | search-read | `md search-read CORPUS --query QUERY [--scope SCOPE] [--limit LIMIT] [--candidates CANDIDATES] [--max-heading-level MAX_HEADING_LEVEL] [--rerank] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] [--token-budget TOKEN_BUDGET] --json` |
| md_section_blast_radius | section-blast-radius | `md section-blast-radius PATH CORPUS --query QUERY [--heading-id HEADING_ID] [--scan SCAN] [--depth DEPTH] [--limit LIMIT] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_status | status | `md status CORPUS [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_strip | strip | `md strip [--paths PATHS] [--confirm] [--dry-run] [--transaction-id TRANSACTION_ID] [--fingerprint FINGERPRINT] [--also-related-section] [--path-include PATH_INCLUDE] [--path-exclude PATH_EXCLUDE] --json` |
| md_toc | toc | `md toc PATH [--max-heading-level MAX_HEADING_LEVEL] [--match MATCH] [--with-tokens] [--with-link-counts] --json` |
| md_walk | walk | `md walk PATH --anchor ANCHOR [--scan SCAN] [--depth DEPTH] [--token-budget TOKEN_BUDGET] --json` |
