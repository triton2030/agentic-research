"""JSON Schema definitions for stable agent-facing `--json` outputs.

Why a schema layer at all: agent consumers parse `--json` output across
sessions and across runtimes. Without a versioned contract, a print
tweak in `render_search` silently breaks downstream pickers. The schemas
also let test suites assert "every result row has these fields" without
hand-rolling assertions.

Not every diagnostic `--json` command is listed here. A command belongs
in `ALL_SCHEMAS` when other agents/tools are expected to parse it as a
stable machine contract. Debug JSON may stay undocumented, but the README
must say so when a new command is added.

Versioning rule: bump `SCHEMA_VERSION` on any change that removes a
field, renames a field, or tightens a type. Adding optional fields is
non-breaking and does not bump.

Consumers read these schemas as data: `ALL_SCHEMAS[name]` for one schema,
`ALL_SCHEMAS` for the whole map, plus `SCHEMA_VERSION` / `SCHEMA_DIALECT`.
"""

from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "4.0.0"
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


_SEARCH_RESULT_ROW: dict[str, Any] = {
    "type": "object",
    "required": [
        "section_id",
        "file_id",
        "relative_path",
        "start_line",
        "heading_chain",
        "token_count",
        "rrf_score",
        "fields_hit",
    ],
    "properties": {
        "section_id": {
            "type": "string",
            "description": "Stable handle for `pick --headings`. Shape "
                           "`<file_id>.<heading_idx>` or `<file_id>.desc`.",
        },
        "file_id": {"type": "integer", "minimum": 1},
        "relative_path": {"type": "string"},
        "start_line": {"type": "integer", "minimum": 1},
        "level": {"type": "integer", "minimum": 0, "maximum": 6},
        "heading_text": {"type": "string"},
        "heading_chain": {
            "type": "string",
            "description": "`A > B > C` chain of ancestor headings.",
        },
        "file_description": {"type": "string"},
        "file_title": {"type": "string"},
        "token_count": {"type": "integer", "minimum": 0},
        "score_sources": {
            "type": "object",
            "description": "Per-engine raw scores (bm25, dense). Present only with --expanded.",
        },
        "rrf_score": {
            "type": "number",
            "description": "Reciprocal Rank Fusion score. Higher = better. "
                           "Used as final ranking when rerank is off.",
        },
        "rerank_score": {
            "type": ["number", "null"],
            "description": "Cross-encoder relevance score (Cohere-compatible). "
                           "Higher = better. Present only when `--rerank` was "
                           "applied; null otherwise.",
        },
        "fields_hit": {
            "type": "array",
            "items": {
                "enum": ["description", "title", "heading", "body"],
            },
            "description": "Which BM25F columns contained query tokens "
                           "(after lemmatization). Empty + dense_distance "
                           "set ⇒ Dense-only hit, morphology miss likely.",
        },
        "snippet": {
            "type": "string",
            "description": "Word-bounded excerpt around the first match.",
        },
    },
}


SEARCH_SCHEMA: dict[str, Any] = {
    "$schema": SCHEMA_DIALECT,
    "$id": "md-navigator/search.json",
    "title": "md-navigator search output",
    "type": "object",
    "required": ["root", "query", "scope", "engine", "stats", "results"],
    "properties": {
        "root": {"type": "string"},
        "query": {"type": "string"},
        "scope": {"enum": ["sections", "descriptions"]},
        "engine": {
            "type": "object",
            "required": ["bm25f", "dense", "embed_model", "embedding_api_url"],
            "properties": {
                "bm25f": {"type": "boolean"},
                "dense": {"type": "boolean"},
                "embed_model": {"type": "string"},
                "embedding_api_url": {"type": "string"},
                "rerank": {
                    "type": "boolean",
                    "description": "True when cross-encoder rerank was applied "
                                   "to top-N RRF candidates before final limit.",
                },
                "rerank_model": {
                    "type": ["string", "null"],
                    "description": "Rerank model id when `rerank` is true.",
                },
                "rerank_top_n": {
                    "type": ["integer", "null"],
                    "description": "How many RRF candidates were sent to the cross-encoder. "
                                   "null when rerank is false.",
                },
                "rerank_api_url": {
                    "type": ["string", "null"],
                    "description": "Rerank endpoint actually used. null when rerank is false.",
                },
                "path_include": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "fnmatch-style globs applied to filter "
                                   "results by relative_path. Empty = no filter.",
                },
                "path_exclude": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "fnmatch-style globs whose matches are "
                                   "dropped after include. Empty = no filter.",
                },
            },
        },
        "stats": {
            "type": "object",
            "properties": {
                "files_indexed": {"type": "integer"},
                "items_indexed": {"type": "integer"},
                "sections_subchunked": {"type": "integer"},
                "embeddings_cached": {"type": "integer"},
                "embeddings_computed": {"type": "integer"},
                "bm25_hits": {"type": "integer"},
                "dense_hits": {"type": "integer"},
                "dropped_stale_path": {"type": "integer"},
            },
        },
        "weights": {
            "type": "object",
            "additionalProperties": {"type": "number"},
        },
        "results": {
            "type": "array",
            "items": _SEARCH_RESULT_ROW,
        },
    },
}


_SEARCH_READ_ROW: dict[str, Any] = {
    "type": "object",
    "required": [
        "section_id",
        "file_id",
        "relative_path",
        "start_line",
        "heading_chain",
        "token_count",
    ],
    "properties": {
        "section_id": {"type": "string"},
        "file_id": {"type": "integer", "minimum": 1},
        "relative_path": {"type": "string"},
        "start_line": {"type": "integer", "minimum": 1},
        "heading_chain": {"type": "string"},
        "heading_text": {"type": "string"},
        "token_count": {"type": "integer", "minimum": 0},
        "included_token_count": {"type": "integer", "minimum": 0},
        "truncated_by_budget": {"type": "boolean"},
        "rrf_score": {"type": ["number", "null"]},
        "rerank_score": {"type": ["number", "null"]},
        "snippet": {"type": "string"},
        "content": {"type": "string"},
        "description": {"type": ["string", "null"]},
    },
}


SEARCH_READ_SCHEMA: dict[str, Any] = {
    "$schema": SCHEMA_DIALECT,
    "$id": "md-navigator/search-read.json",
    "title": "md-navigator search-read output",
    "type": "object",
    "required": [
        "root",
        "query",
        "scope",
        "engine",
        "stats",
        "sections",
        "expanded",
        "token_total",
        "token_budget",
        "dropped_by_budget",
    ],
    "properties": {
        "root": {"type": "string"},
        "query": {"type": "string"},
        "scope": {"enum": ["sections", "descriptions"]},
        "engine": SEARCH_SCHEMA["properties"]["engine"],
        "stats": SEARCH_SCHEMA["properties"]["stats"],
        "sections": {"type": "array", "items": _SEARCH_READ_ROW},
        "expanded": {"type": "boolean"},
        "view": {"enum": ["map", "expanded"]},
        "candidate_token_total": {"type": "integer", "minimum": 0},
        "token_total": {"type": "integer", "minimum": 0},
        "token_budget": {"type": "integer", "minimum": 0},
        "token_budget_defaulted": {"type": "boolean"},
        "read_next": {"type": "array"},
        "dropped_by_budget": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["section_id", "relative_path", "tokens"],
                "properties": {
                    "section_id": {"type": "string"},
                    "relative_path": {"type": "string"},
                    "tokens": {"type": "integer", "minimum": 0},
                    "included_tokens": {"type": "integer", "minimum": 0},
                    "reason": {"enum": ["truncated", "over_budget"]},
                },
            },
        },
        "empty": {"type": "boolean"},
    },
}


MAP_SCHEMA: dict[str, Any] = {
    "$schema": SCHEMA_DIALECT,
    "$id": "md-navigator/map.json",
    "title": "md-navigator map / headings output",
    "type": "object",
    "required": ["root", "file_count", "files"],
    "properties": {
        "root": {"type": "string"},
        "file_count": {"type": "integer"},
        "description_gap_count": {"type": "integer"},
        "heading_count": {"type": "integer"},
        "token_count": {"type": "integer"},
        "expanded": {"type": "boolean"},
        "view": {"enum": ["map", "expanded"]},
        "summary": {
            "type": "object",
            "description": "Folded corpus shape: file_count, description_gaps, folders[].",
        },
        "match": {"type": "string"},
        "match_terms": {"type": "array", "items": {"type": "string"}},
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "relative_path", "description", "title", "headings"],
                "properties": {
                    "id": {"type": "integer", "minimum": 1},
                    "path": {"type": "string"},
                    "relative_path": {"type": "string"},
                    "description": {"type": "string"},
                    "title": {"type": "string"},
                    "heading_count": {"type": "integer"},
                    "tokens": {"type": "integer"},
                    "matched_terms": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "headings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["id", "line", "level", "text"],
                            "properties": {
                                "id": {"type": "string"},
                                "line": {"type": "integer"},
                                "level": {"type": "integer", "minimum": 1, "maximum": 6},
                                "text": {"type": "string"},
                                "tokens": {"type": "integer"},
                            },
                        },
                    },
                },
            },
        },
    },
}


STATUS_SCHEMA: dict[str, Any] = {
    "$schema": SCHEMA_DIALECT,
    "$id": "md-navigator/status.json",
    "title": "md-navigator status output (when --json)",
    "type": "object",
    "required": ["corpus", "index_path", "state"],
    "properties": {
        "command": {"type": "string"},
        "corpus": {"type": "string"},
        "index_path": {"type": "string"},
        "index_exists": {"type": "boolean"},
        "last_touched": {"type": ["string", "null"]},
        "model": {"type": "string"},
        "path_scope": {
            "type": "object",
            "properties": {
                "include": {"type": ["array", "null"], "items": {"type": "string"}},
                "exclude": {"type": ["array", "null"], "items": {"type": "string"}},
            },
        },
        "state": {
            "enum": ["FRESH", "HEALTHY", "NEEDS_WARMUP", "NO_INDEX", "ERROR", "EMPTY", "DEPENDENCY_ERROR"],
        },
        "scopes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "scope",
                    "added_sections",
                    "removed_sections",
                    "reused",
                    "pending_chunks",
                    "total_sections_in_scope",
                ],
                "properties": {
                    "scope": {"enum": ["sections", "descriptions"]},
                    "added_sections": {"type": "integer"},
                    "removed_sections": {"type": "integer"},
                    "pending_files": {"type": "array"},
                    "removed_files": {"type": "array"},
                    "reused": {"type": "integer"},
                    "pending_chunks": {"type": "integer"},
                    "total_sections_in_scope": {"type": "integer"},
                },
            },
        },
        "folder_breakdown": {"type": "array"},
        "excluded": {"type": "object"},
        "added_sections": {"type": "integer"},
        "removed_sections": {"type": "integer"},
        "pending_chunks": {"type": "integer"},
        "pending_files": {"type": "array"},
        "removed_files": {"type": "array"},
        "drift_count": {"type": "integer"},
        "metadata_mismatch": {"type": "boolean"},
        "delta_too_large": {"type": "boolean"},
        "max_auto_embed": {"type": "integer"},
        "recommended_action": {"type": ["object", "null"]},
    },
}


OVERLAPS_SCHEMA: dict[str, Any] = {
    "$schema": SCHEMA_DIALECT,
    "$id": "md-navigator/overlaps.json",
    "title": "md-navigator overlaps output (--json)",
    "type": "object",
    "required": ["root", "threshold"],
    "properties": {
        "root": {"type": "string"},
        "threshold": {"type": "number"},
        "min_tokens": {"type": "integer"},
        "include_same_file": {"type": "boolean"},
        "expanded": {"type": "boolean"},
        "view": {"enum": ["map", "expanded"]},
        "indexed": {
            "type": "object",
            "properties": {
                "files": {"type": "integer"},
                "sections": {"type": "integer"},
                "chunks": {"type": "integer"},
            },
        },
        "pairs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["a", "b", "similarity"],
                "properties": {
                    "similarity": {"type": "number", "minimum": 0, "maximum": 1},
                    "a": {"$ref": "#/$defs/section_ref"},
                    "b": {"$ref": "#/$defs/section_ref"},
                },
            },
        },
        "pair_groups": {
            "type": "array",
            "items": {"type": "object"},
        },
        "pairs_total": {"type": "integer"},
        "read_next": {"type": "array"},
    },
    "$defs": {
        "section_ref": {
            "type": "object",
            "required": ["section_id", "relative_path", "heading_chain"],
            "properties": {
                "section_id": {"type": "string"},
                "file_id": {"type": "integer"},
                "relative_path": {"type": "string"},
                "start_line": {"type": "integer"},
                "heading_chain": {"type": "string"},
                "token_count": {"type": "integer"},
            },
        },
    },
}


REPEATED_CONCEPTS_SCHEMA: dict[str, Any] = {
    "$schema": SCHEMA_DIALECT,
    "$id": "md-navigator/repeated-concepts.json",
    "title": "md-navigator repeated-concepts output (--json)",
    "type": "object",
    "required": ["root", "threshold", "concepts"],
    "properties": {
        "root": {"type": "string"},
        "threshold": {"type": "number"},
        "min_files": {"type": "integer"},
        "min_sections": {"type": "integer"},
        "concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["unique_files", "section_count"],
                "properties": {
                    "label": {"type": "string"},
                    "representative": {
                        "type": "object",
                        "description": "Medoid section — highest summed similarity to other members.",
                        "properties": {
                            "section_id": {"type": "string"},
                            "relative_path": {"type": "string"},
                            "heading_chain": {"type": "string"},
                        },
                    },
                    "medoid": {
                        "type": "object",
                        "description": "Expanded-mode medoid section.",
                    },
                    "unique_files": {"type": "integer"},
                    "section_count": {"type": "integer"},
                    "cohesion": {
                        "type": "number",
                        "description": "Mean pairwise similarity inside the component. "
                                       "Higher = tighter; lower = transitive bridge.",
                    },
                    "files": {
                        "type": "array",
                        "description": "[(relative_path, section_count_in_concept), ...].",
                        "items": {
                            "type": "array",
                            "minItems": 2,
                            "maxItems": 2,
                        },
                    },
                    "mean_cohesion": {"type": "number"},
                    "top_handles": {"type": "array"},
                    "file_breakdown": {"type": "array"},
                    "members": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "section_id": {"type": "string"},
                                "relative_path": {"type": "string"},
                                "heading_chain": {"type": "string"},
                                "similarity_to_representative": {"type": "number"},
                            },
                        },
                    },
                },
            },
        },
        "expanded": {"type": "boolean"},
        "view": {"enum": ["map", "expanded"]},
        "read_next": {"type": "array"},
    },
}


CLUSTER_SCHEMA: dict[str, Any] = {
    "$schema": SCHEMA_DIALECT,
    "$id": "md-navigator/cluster.json",
    "title": "md-navigator cluster output (--json)",
    "type": "object",
    "required": ["k", "n_sections", "n_chunks", "clusters"],
    "properties": {
        "k": {"type": "integer", "minimum": 0},
        "n_sections": {"type": "integer"},
        "n_chunks": {"type": "integer"},
        "clusters": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "size", "cohesion", "centroid_section"],
                "properties": {
                    "id": {"type": "integer"},
                    "size": {"type": "integer"},
                    "cohesion": {
                        "type": "number",
                        "description": "Mean cosine of cluster members to centroid. Higher = tighter.",
                    },
                    "centroid_section": {"type": "string"},
                    "centroid_path": {"type": "string"},
                    "centroid_heading_chain": {"type": "string"},
                    "common_parent": {
                        "type": "string",
                        "description": "Longest directory prefix shared by all members. Mismatch vs centroid_path is an IA signal.",
                    },
                    "top_files": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "description": "[relative_path, section_count].",
                            "minItems": 2,
                            "maxItems": 2,
                        },
                    },
                    "section_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "expanded": {"type": "boolean"},
        "view": {"enum": ["map", "expanded"]},
        "read_next": {"type": "array"},
    },
}


AUDIT_SCHEMA: dict[str, Any] = {
    "$schema": SCHEMA_DIALECT,
    "$id": "md-navigator/audit.json",
    "title": "md-navigator audit output (--json)",
    "type": "object",
    "required": ["root", "health", "severity_counts", "findings", "stats", "engine"],
    "properties": {
        "root": {"type": "string"},
        "health": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Aggregate score: 100 minus 15·critical_count minus 5·warning_count, floored at 0.",
        },
        "severity_counts": {
            "type": "object",
            "required": ["critical", "warning", "info"],
            "properties": {
                "critical": {"type": "integer"},
                "warning": {"type": "integer"},
                "info": {"type": "integer"},
            },
        },
        "thresholds": {
            "type": "object",
            "description": "All thresholds actually applied during this audit run.",
        },
        "stats": {
            "type": "object",
            "properties": {
                "files_indexed": {"type": "integer"},
                "sections_indexed": {"type": "integer"},
                "embeddings_cached": {"type": "integer"},
                "embeddings_computed": {"type": "integer"},
            },
        },
        "engine": {
            "type": "object",
            "properties": {
                "embed_model": {"type": "string"},
                "embedding_api_url": {"type": "string"},
            },
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["class", "severity", "label", "next_step"],
                "properties": {
                    "class": {
                        "enum": [
                            "smeared_owner_truth",
                            "tight_duplicates",
                            "intra_file_drift",
                            "discovery_gaps",
                            "cluster_folder_mismatch",
                            "template_family",
                        ],
                    },
                    "severity": {"enum": ["critical", "warning", "info"]},
                    "label": {
                        "type": "string",
                        "description": "Short human-readable summary of the finding.",
                    },
                    "evidence": {
                        "type": "object",
                        "description": "Class-specific evidence payload (varies by class).",
                    },
                    "evidence_summary": {
                        "type": "object",
                        "description": "Normal-mode bounded evidence map.",
                    },
                    "next_step": {
                        "type": "string",
                        "description": "Recommended owner skill or action to remediate.",
                    },
                },
            },
        },
        "expanded": {"type": "boolean"},
        "view": {"enum": ["map", "expanded"]},
        "findings_total": {"type": "integer"},
        "findings_returned": {"type": "integer"},
        "read_next": {"type": "array"},
    },
}


ALL_SCHEMAS: dict[str, dict[str, Any]] = {
    "search": SEARCH_SCHEMA,
    "search-read": SEARCH_READ_SCHEMA,
    "map": MAP_SCHEMA,
    "headings": MAP_SCHEMA,  # same shape — headings is `map` with deeper detail
    "status": STATUS_SCHEMA,
    "overlaps": OVERLAPS_SCHEMA,
    "repeated-concepts": REPEATED_CONCEPTS_SCHEMA,
    "cluster": CLUSTER_SCHEMA,
    "audit": AUDIT_SCHEMA,
}
