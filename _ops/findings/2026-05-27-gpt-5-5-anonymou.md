# Findings — 2026-05-27 — gpt-5-5 — sess:anonymou

- 10:59 — embedding prefix freshness risk | experiments/md-embedding-server/src/navigator/index_build.py + sections.py | content_hash excludes contextual prefix, so graph-enriched prefix would need explicit context digest/invalidation before index-time enrichment
