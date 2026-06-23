"""Facade module for the index layer.

The implementation lives in focused modules; this file re-exports their
public symbols so existing callers (`search.py`, `overlaps.py`,
`repeated_concepts.py`) keep working with no edits:

  - `index_meta`    - schema, meta, layout, open / probe / sticky model
  - `index_build`   - counters, delta apply, embed pipeline
  - `status_core`   - shared status state machine and corpus root discovery
  - `index_cluster` - K-means clustering primitives, `cluster_sections`

New code should prefer importing directly from the focused modules.
This shim exists only for backward compatibility."""

from __future__ import annotations

# --- Backwards-compat re-exports ----------------------------------------

from .index_meta import (  # noqa: F401
    GITIGNORE_BANNER,
    INDEX_DIRNAME,
    SCHEMA_VERSION,
    SEARCH_CACHE_ROOT,
    _acquire_index_write_lock,
    _cache_dir_for_root,
    _create_schema,
    _index_dir_for_corpus,
    _meta_get,
    _meta_set,
    _open_index,
    _open_index_metadata_readonly,
    _open_index_readonly,
    _release_index_write_lock,
    probe_embedding_dim,
    resolve_embed_model_for_corpus,
)
from .index_build import (  # noqa: F401
    DEFAULT_INDEX_BATCH,
    DEFAULT_INDEX_PAUSE_S,
    DEFAULT_MAX_AUTO_EMBED,
    _chunks_for_item,
    _clean_incomplete_sections,
    _ensure_index_unlocked,
    _index_delta_stats_readonly,
    _next_id,
    _set_counter,
    ensure_index,
)
from .index_store import delete_section_rowids as _delete_section_rowids  # noqa: F401
from .status_core import find_corpus_root_for  # noqa: F401
from .index_cluster import (  # noqa: F401
    _kmeans,
    _kmeans_pp_init,
    _longest_common_parent,
    cluster_sections,
)
