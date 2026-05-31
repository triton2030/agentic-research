"""K-means clustering over on-disk dense vectors (`cluster` command).

Read-only — never writes to the index. Uses `_open_index_readonly` from
`index_meta` to load `sections_vec` rows into NumPy. The clustering
itself is plain Lloyd's K-means with K-means++ seeding; vectors are
L2-normalised at index time, so Euclidean distance on the unit sphere
is monotone with cosine similarity.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .filters import (
    normalize_path_filter_patterns,
    sqlite_path_filter_sql,
)
from .index_meta import _open_index_readonly


def _kmeans_pp_init(X, k: int, rng) -> Any:
    """K-means++ seeding: first centroid random, each next sampled by
    distance² from the closest existing centroid. Better than uniform
    random init at avoiding empty / degenerate clusters."""
    import numpy as np  # type: ignore

    n = len(X)
    idxs = [int(rng.integers(n))]
    for _ in range(k - 1):
        # Min squared distance from each point to the existing centroid set.
        diff = X[:, None, :] - X[idxs][None, :, :]
        sq = np.sum(diff * diff, axis=2)
        min_sq = sq.min(axis=1)
        total = float(min_sq.sum())
        if total <= 1e-12:
            idxs.append(int(rng.integers(n)))
            continue
        probs = min_sq / total
        idxs.append(int(rng.choice(n, p=probs)))
    return X[idxs].copy()


def _kmeans(X, k: int, max_iter: int = 50, seed: int = 42):
    """Plain Lloyd's K-means in NumPy. Inputs are expected to be
    L2-normalized — Euclidean distance on the unit sphere is monotone
    with cosine similarity, so this is effectively spherical K-means."""
    import numpy as np  # type: ignore

    rng = np.random.default_rng(seed)
    centroids = _kmeans_pp_init(X, k, rng)
    assignments = np.zeros(len(X), dtype=np.int64)
    for _ in range(max_iter):
        # Vectorised distance: (N, K) matrix of squared L2 distances.
        diff = X[:, None, :] - centroids[None, :, :]
        sq = np.sum(diff * diff, axis=2)
        new_assignments = np.argmin(sq, axis=1)
        if np.array_equal(new_assignments, assignments):
            break
        assignments = new_assignments
        new_centroids = np.zeros_like(centroids)
        for j in range(k):
            mask = assignments == j
            if mask.any():
                new_centroids[j] = X[mask].mean(axis=0)
            else:
                # Empty cluster — reseed to a random point.
                new_centroids[j] = X[int(rng.integers(len(X)))]
        # Re-normalise centroids onto the unit sphere — keeps the
        # spherical-K-means invariant intact for cosine-style data.
        norms = np.linalg.norm(new_centroids, axis=1, keepdims=True)
        new_centroids = new_centroids / np.maximum(norms, 1e-12)
        if np.allclose(new_centroids, centroids, atol=1e-6):
            centroids = new_centroids
            break
        centroids = new_centroids
    return assignments, centroids


def _longest_common_parent(paths: list[str]) -> str:
    """Longest path prefix shared by all input paths, at directory
    granularity. '_ops/criteria/foo.md' + '_ops/criteria/bar.md' →
    '_ops/criteria'; mixed paths → ''."""
    if not paths:
        return ""
    parts = [p.split("/") for p in paths]
    out: list[str] = []
    for chunk in zip(*parts):
        if len(set(chunk)) == 1 and chunk[0]:
            out.append(chunk[0])
        else:
            break
    if out and out[-1].endswith(".md"):
        out.pop()
    return "/".join(out)


def cluster_sections(
    corpus_root: Path,
    k: int,
    cache_root: Path | None = None,
    seed: int = 42,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> dict[str, Any]:
    """Group all `sections`-scope chunks of the corpus into `k` semantic
    clusters using K-means on L2-normalised dense vectors. Aggregates
    chunks → sections by majority, then summarises each cluster: top
    files by section count, centroid section (nearest to cluster mean),
    internal cohesion (mean cosine within the cluster).

    Returns:
        {
            "k": int,
            "n_sections": int,
            "n_chunks": int,
            "clusters": [
                {
                    "id": int,
                    "size": int,
                    "cohesion": float,
                    "centroid_section": str,
                    "centroid_path": str,
                    "centroid_heading_chain": str,
                    "top_files": [(relative_path, section_count), ...],
                    "common_parent": str,  # longest shared path prefix
                    "section_ids": [str, ...],
                }
            ]
        }
    Raises FileNotFoundError if the corpus has no on-disk index."""
    import numpy as np  # type: ignore

    include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)
    path_clause, path_params = sqlite_path_filter_sql(
        "sections.relative_path",
        include_patterns,
        exclude_patterns,
    )

    conn = _open_index_readonly(corpus_root, cache_root=cache_root)
    try:
        rows = conn.execute(
            "SELECT chunks.chunk_id, chunks.section_rowid, "
            "sections.section_id, sections.relative_path, "
            "sections.heading_chain, sections.token_count, vec.embedding "
            "FROM chunks "
            "JOIN sections_vec vec ON vec.rowid = chunks.chunk_id "
            "JOIN sections ON sections.rowid = chunks.section_rowid "
            "WHERE sections.scope = 'sections' "
            f"{path_clause} "
            "ORDER BY chunks.chunk_id",
            path_params,
        ).fetchall()
        if not rows:
            return {"k": 0, "n_sections": 0, "n_chunks": 0, "clusters": []}

        vectors = np.stack([np.frombuffer(r[6], dtype="float32") for r in rows])
        chunk_section_rowid = np.array([r[1] for r in rows], dtype=np.int64)
        section_meta: dict[int, dict[str, Any]] = {}
        for r in rows:
            rowid = r[1]
            if rowid not in section_meta:
                section_meta[rowid] = {
                    "section_id": r[2],
                    "relative_path": r[3],
                    "heading_chain": r[4] or "",
                    "token_count": int(r[5]),
                }

        n_sections = len(section_meta)
        k_actual = max(1, min(int(k), n_sections))

        assignments, centroids = _kmeans(vectors, k_actual, seed=seed)

        # Aggregate chunk → section by majority vote.
        from collections import Counter

        section_to_chunks: dict[int, list[int]] = {}
        for i, sec_rowid in enumerate(chunk_section_rowid):
            section_to_chunks.setdefault(int(sec_rowid), []).append(i)
        section_cluster: dict[int, int] = {}
        for sec_rowid, chunk_idxs in section_to_chunks.items():
            votes = Counter(int(assignments[i]) for i in chunk_idxs)
            section_cluster[sec_rowid] = votes.most_common(1)[0][0]

        clusters: list[dict[str, Any]] = []
        for cid in range(k_actual):
            section_rowids = [s for s, c in section_cluster.items() if c == cid]
            if not section_rowids:
                continue
            chunk_idxs = [i for s in section_rowids for i in section_to_chunks[s]]
            cluster_vecs = vectors[chunk_idxs]
            mean_vec = cluster_vecs.mean(axis=0)
            mean_norm = float(np.linalg.norm(mean_vec))
            if mean_norm > 1e-12:
                mean_vec = mean_vec / mean_norm
            # Cohesion = mean cosine to cluster centroid.
            cohesion = float(np.mean(cluster_vecs @ mean_vec))
            # Centroid section: section whose mean vector is closest to mean_vec.
            section_mean_vecs: dict[int, Any] = {}
            for s in section_rowids:
                mv = vectors[section_to_chunks[s]].mean(axis=0)
                nrm = float(np.linalg.norm(mv))
                section_mean_vecs[s] = mv / nrm if nrm > 1e-12 else mv
            best = max(section_rowids, key=lambda s: float(section_mean_vecs[s] @ mean_vec))
            best_meta = section_meta[best]
            # Top files by section count.
            path_counts = Counter(section_meta[s]["relative_path"] for s in section_rowids)
            top_files = path_counts.most_common(5)
            # Common parent dir (longest shared path prefix segment).
            paths = [section_meta[s]["relative_path"] for s in section_rowids]
            common_parent = _longest_common_parent(paths)
            clusters.append(
                {
                    "id": cid,
                    "size": len(section_rowids),
                    "cohesion": cohesion,
                    "centroid_section": best_meta["section_id"],
                    "centroid_path": best_meta["relative_path"],
                    "centroid_heading_chain": best_meta["heading_chain"],
                    "top_files": top_files,
                    "common_parent": common_parent,
                    "section_ids": [section_meta[s]["section_id"] for s in section_rowids],
                }
            )

        clusters.sort(key=lambda c: -c["cohesion"])
        return {
            "k": k_actual,
            "n_sections": n_sections,
            "n_chunks": len(rows),
            "clusters": clusters,
        }
    finally:
        conn.close()
