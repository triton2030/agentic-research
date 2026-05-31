"""Diagnosis-shaped output over a Markdown corpus.

The retrieval-shaped commands (`search`, `overlaps`, `repeated-concepts`,
`cluster`, `map`) answer the question "where is X?". This command answers
"is this corpus healthy?" — orchestrates the existing primitives, adds
two new ones (intra-file topical drift, heading-skeleton template
detection), classifies findings into five IA-meaningful classes,
attaches severity (🔴 critical / 🟡 warning / ℹ️ info), and renders a
single coherent doctor's-report-style output.

Design adopted from Obsidian's **Vault Physician** plugin (severity
tags + health gauge + module-based detection + per-finding next-step
recommendation). Two new primitive classes — intra-file drift and
template-effect — are this corpus's contribution beyond Vault Physician's
orphan/decay/frontmatter/tag focus.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


from .audit_severity import (
    SEVERITY_BADGE,
    SEVERITY_CRITICAL,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    compute_health,
    severity_counts,
    severity_for_classified_pair,
    severity_for_cluster_mismatch,
    severity_for_discovery_gap,
    severity_for_heading_family,
    severity_for_heading_lex_drift,
    severity_for_intra_file_drift,
    severity_for_smeared_concept,
)


# --- New primitive: heading-skeleton classification ----------------------


_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_heading(text: str) -> str:
    """Case-fold + strip + collapse whitespace. Used to compute heading
    Jaccard between files: two files with `## Опоры` and `##  ОПОРЫ  `
    should match."""
    if not text:
        return ""
    return _WHITESPACE_RE.sub(" ", text.strip().lower())


def _heading_set_for_file(file_entry: dict[str, Any]) -> set[str]:
    """Extract the set of normalised heading texts for one file's `headings`
    list (as returned by `folder_map.build_map`)."""
    return {
        _normalize_heading(h.get("text", ""))
        for h in (file_entry.get("headings") or [])
        if h.get("text")
    }


def _h2_plus_heading_set(file_entry: dict[str, Any]) -> set[str]:
    """Like `_heading_set_for_file` but skips H1 (file title). H1 headings
    naturally encode the file's unique identity (`# Wisdom — Claude Code`
    vs `# Wisdom — Claude Opus 4.7`), so they never match across files
    and would dilute family signals. H2+ headings encode structural
    template (`## Опоры`, `## Проверено`)."""
    return {
        _normalize_heading(h.get("text", ""))
        for h in (file_entry.get("headings") or [])
        if h.get("text") and (h.get("level") or 1) >= 2
    }


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _heading_token_set(text: str) -> set[str]:
    """Token set of a single heading text, normalised. Used for
    intra-file heading-lex-diversity (token overlap between sibling
    headings inside one file)."""
    return set(_WORD_RE.findall(_normalize_heading(text)))


def heading_lex_diversity(file_entry: dict[str, Any]) -> float:
    """Mean pairwise (1 − Jaccard) over H2+ heading token sets inside one
    file. 1.0 = every heading shares no tokens with any sibling
    (lexically distant topics under one roof). 0.0 = headings reuse
    the same vocabulary.

    Embedding-based intra-file drift is blind when all sections tug
    toward the file's H1 title vector. Heading-lex-diversity is the
    cheap independent co-signal: «Hooks / Agent tool / Deferred Tools»
    share no tokens — even when section bodies all read as «про
    Claude Code»."""
    raw_headings = [
        h.get("text", "")
        for h in (file_entry.get("headings") or [])
        if h.get("text") and (h.get("level") or 1) >= 2
    ]
    token_sets = [s for s in (_heading_token_set(h) for h in raw_headings) if s]
    if len(token_sets) < 2:
        return 0.0
    distances: list[float] = []
    for i in range(len(token_sets)):
        for j in range(i + 1, len(token_sets)):
            distances.append(1.0 - _jaccard(token_sets[i], token_sets[j]))
    return sum(distances) / len(distances)


def detect_heading_families(
    map_data: dict[str, Any],
    *,
    min_files: int = 3,
) -> list[dict[str, Any]]:
    """Find H2+ heading texts that appear in ≥ `min_files` files across
    the corpus. One entry per shared heading. No embeddings — pure
    inverted index over normalised heading text.

    This is the family-wise complement to `classify_pairs_by_template`'s
    pair-wise heading-Jaccard: catches «N files all have section X»
    even when no pair crosses the smear-similarity threshold (classic
    template-family with divergent bodies, e.g. parallel-structure
    `wisdom-*` files whose `## Опоры` sections look superficially
    distinct but share the structural slot)."""
    heading_to_files: dict[str, list[str]] = {}
    for f in map_data.get("files", []):
        rel = f["relative_path"]
        seen_in_file: set[str] = set()
        for h in (f.get("headings") or []):
            if (h.get("level") or 1) < 2:
                continue
            norm = _normalize_heading(h.get("text", ""))
            if not norm or norm in seen_in_file:
                continue
            seen_in_file.add(norm)
            heading_to_files.setdefault(norm, []).append(rel)

    families: list[dict[str, Any]] = []
    for heading, files in heading_to_files.items():
        if len(files) < min_files:
            continue
        families.append(
            {
                "shared_heading": heading,
                "file_count": len(files),
                "files": sorted(files),
            }
        )
    families.sort(key=lambda x: -x["file_count"])
    return families


def classify_pairs_by_template(
    pairs: list[dict[str, Any]],
    map_data: dict[str, Any],
    *,
    heading_jaccard_threshold: float = 0.7,
    full_dup_body_threshold: float = 0.92,
    smear_body_threshold: float = 0.85,
) -> list[dict[str, Any]]:
    """Classify each overlap pair into TEMPLATE_EFFECT / SEMANTIC_SMEAR /
    FULL_DUPLICATE / UNCLASSIFIED based on the relationship between
    heading-skeleton similarity (Jaccard over each file's heading set)
    and body cosine similarity (already in `pairs[i]["similarity"]`).

    Validated by academic literature on template-aware near-duplicate
    detection: separating structural template-effect from semantic smear
    sharpens the IA verdict.

    Returns pairs enriched with `heading_jaccard` and `classification`
    fields. Original pair dict keys (`similarity`, `a`, `b`) untouched."""
    headings_by_path: dict[str, set[str]] = {
        f["relative_path"]: _heading_set_for_file(f)
        for f in map_data.get("files", [])
    }

    enriched: list[dict[str, Any]] = []
    for p in pairs:
        rel_a = p["a"]["relative_path"]
        rel_b = p["b"]["relative_path"]
        set_a = headings_by_path.get(rel_a, set())
        set_b = headings_by_path.get(rel_b, set())
        j = _jaccard(set_a, set_b)
        body_sim = float(p.get("similarity", 0.0))

        if j >= heading_jaccard_threshold and body_sim >= full_dup_body_threshold:
            cls = "FULL_DUPLICATE"
        elif j >= heading_jaccard_threshold:
            cls = "TEMPLATE_EFFECT"
        elif body_sim >= smear_body_threshold:
            cls = "SEMANTIC_SMEAR"
        else:
            cls = "UNCLASSIFIED"

        out_pair = dict(p)
        out_pair["heading_jaccard"] = j
        out_pair["classification"] = cls
        enriched.append(out_pair)
    return enriched


# --- New primitive: intra-file topical drift -----------------------------


def detect_intra_file_drift(
    conn,
    *,
    min_sections: int = 5,
    tight_cohesion: float = 0.65,
    min_tight_clusters: int = 2,
    inter_cluster_max: float = 0.40,
    min_cluster_size: int = 2,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """For each file with ≥ `min_sections` sections, cluster its OWN
    section embeddings into k = min(3, n // 2) clusters and flag the
    file when **two or more internally-tight clusters are topically
    distinct** — i.e. the owner file is splitting itself across multiple
    real topics.

    Flag condition:
      `count(clusters where cohesion ≥ tight_cohesion AND size ≥ min_cluster_size) ≥ min_tight_clusters`
      AND `mean inter-cluster centroid similarity < inter_cluster_max`

    Both halves matter: requiring "tight clusters" filters out files
    that are just generally noisy (no real structure to compare against),
    and requiring low inter-cluster similarity filters out files where
    K-means split a single coherent topic into arbitrary halves.

    Returns one entry per drifting file with cohesion / inter_sim stats
    and the representative heading of each topic group, sorted by
    severity (most distinct topics first)."""
    import numpy as np  # type: ignore

    from .index_cluster import _kmeans

    # Aggregate chunk vectors → one mean vector per (section_rowid).
    rows = conn.execute(
        "SELECT chunks.section_rowid, sections.relative_path, "
        "sections.section_id, sections.heading_chain, sections.token_count, "
        "vec.embedding "
        "FROM chunks "
        "JOIN sections_vec vec ON vec.rowid = chunks.chunk_id "
        "JOIN sections ON sections.rowid = chunks.section_rowid "
        "WHERE sections.scope = 'sections' "
        "ORDER BY sections.relative_path, sections.start_line, chunks.chunk_idx"
    ).fetchall()
    if not rows:
        return []

    # Group: section_rowid → (relative_path, section_id, heading_chain, mean_vec)
    section_data: dict[int, dict[str, Any]] = {}
    section_vec_accum: dict[int, list[Any]] = {}
    for sec_rowid, rel_path, section_id, heading_chain, token_count, blob in rows:
        vec = np.frombuffer(blob, dtype="float32")
        if sec_rowid not in section_data:
            section_data[sec_rowid] = {
                "relative_path": rel_path,
                "section_id": section_id,
                "heading_chain": heading_chain or "",
                "token_count": int(token_count),
            }
            section_vec_accum[sec_rowid] = []
        section_vec_accum[sec_rowid].append(vec)

    # Build per-file lists.
    per_file: dict[str, list[tuple[int, Any, dict[str, Any]]]] = {}
    for sec_rowid, vecs in section_vec_accum.items():
        meta = section_data[sec_rowid]
        mean_vec = np.mean(np.stack(vecs), axis=0)
        # Re-normalise so dot product == cosine; chunks are L2-normalised
        # but the mean is not.
        norm = float(np.linalg.norm(mean_vec))
        if norm > 1e-12:
            mean_vec = mean_vec / norm
        per_file.setdefault(meta["relative_path"], []).append(
            (sec_rowid, mean_vec, meta)
        )

    drifting: list[dict[str, Any]] = []
    for rel_path, sec_list in per_file.items():
        n = len(sec_list)
        if n < min_sections:
            continue
        section_vecs = np.stack([v for _, v, _ in sec_list])
        # Pick k so even tiny files (5-6 sections) get a meaningful split.
        k = min(3, n // 2)
        if k < 2:
            continue
        assignments, centroids = _kmeans(section_vecs, k, seed=seed)

        # Per-cluster cohesion: mean cosine of cluster members to cluster mean.
        cluster_cohesions: list[float] = []
        cluster_sizes: list[int] = []
        cluster_centroids: list[Any] = []
        cluster_repr_headings: list[str] = []
        for cid in range(k):
            mask = assignments == cid
            size = int(mask.sum())
            if size == 0:
                continue
            members = section_vecs[mask]
            cluster_mean = members.mean(axis=0)
            cluster_norm = float(np.linalg.norm(cluster_mean))
            if cluster_norm > 1e-12:
                cluster_mean = cluster_mean / cluster_norm
            cohesion = float(np.mean(members @ cluster_mean))
            cluster_cohesions.append(cohesion)
            cluster_sizes.append(size)
            cluster_centroids.append(cluster_mean)
            # Representative heading: section in this cluster with highest
            # similarity to the cluster mean.
            local_sims = members @ cluster_mean
            local_best = int(np.argmax(local_sims))
            global_idx = int(np.flatnonzero(mask)[local_best])
            cluster_repr_headings.append(sec_list[global_idx][2]["heading_chain"])

        if len(cluster_cohesions) < 2:
            continue

        max_cohesion = max(cluster_cohesions)
        tight_cluster_count = sum(
            1
            for c, s in zip(cluster_cohesions, cluster_sizes)
            if c >= tight_cohesion and s >= min_cluster_size
        )
        # Inter-cluster centroid similarity (cosine between cluster means).
        n_pairs = 0
        inter_sum = 0.0
        for i in range(len(cluster_centroids)):
            for j in range(i + 1, len(cluster_centroids)):
                inter_sum += float(cluster_centroids[i] @ cluster_centroids[j])
                n_pairs += 1
        inter_sim = inter_sum / n_pairs if n_pairs else 1.0

        if (
            tight_cluster_count >= min_tight_clusters
            and inter_sim < inter_cluster_max
        ):
            drifting.append(
                {
                    "relative_path": rel_path,
                    "section_count": n,
                    "k": k,
                    "tight_cluster_count": tight_cluster_count,
                    "max_cohesion": max_cohesion,
                    "inter_cluster_sim": inter_sim,
                    "topic_groups": [
                        {
                            "size": cluster_sizes[i],
                            "cohesion": cluster_cohesions[i],
                            "representative_heading_chain": cluster_repr_headings[i],
                        }
                        for i in range(len(cluster_cohesions))
                    ],
                }
            )

    # Sort by severity proxy: more distinct topic groups + lower inter_sim
    # = more obvious drift.
    drifting.sort(key=lambda d: (-d["tight_cluster_count"], d["inter_cluster_sim"]))
    return drifting


def detect_heading_lex_drift(
    map_data: dict[str, Any],
    *,
    min_sections: int = 5,
    heading_diversity_threshold: float = 0.85,
) -> list[dict[str, Any]]:
    """Heading-side co-signal for intra-file drift. Independent of
    embeddings: looks at whether H2+ heading texts inside one file
    share any vocabulary. Catches files where `_kmeans` on section
    embeddings reports artificial cohesion (because every section's
    embedding leans on the H1 title), but the headings themselves
    spell out distinct topics — `## Hooks`, `## Agent tool`,
    `## Deferred Tools` share no tokens, even when all sections
    embed as «про Claude Code»."""
    drifting: list[dict[str, Any]] = []
    for f in map_data.get("files", []):
        h2_plus = [
            h
            for h in (f.get("headings") or [])
            if h.get("text") and (h.get("level") or 1) >= 2
        ]
        if len(h2_plus) < min_sections:
            continue
        diversity = heading_lex_diversity(f)
        if diversity < heading_diversity_threshold:
            continue
        drifting.append(
            {
                "relative_path": f["relative_path"],
                "section_count": len(h2_plus),
                "heading_diversity": diversity,
                "headings_sample": [
                    _normalize_heading(h.get("text", "")) for h in h2_plus[:6]
                ],
            }
        )
    drifting.sort(key=lambda d: -d["heading_diversity"])
    return drifting


# --- Orchestrators per detection class -----------------------------------


def _check_smeared_owner_truth(
    corpus_root: Path, conn, map_data: dict[str, Any], index_stats: dict[str, Any], args
) -> list[dict[str, Any]]:
    """Cross-file concepts surfaced by repeated_concepts, classified by
    severity from `unique_files × cohesion`. Concepts whose participating
    files share a heading skeleton (mean pairwise heading-Jaccard ≥
    `threshold_template`) are demoted as **template repetition** and surface
    once in `tight_duplicates` instead — keeps the smeared-owner class
    focused on real owner-truth issues, not intentional templates."""
    from types import SimpleNamespace

    from .repeated_concepts import compute_repeated_concepts

    rc_args = SimpleNamespace(
        threshold=args.threshold_smear,
        min_tokens=30,
        min_files=2,
        min_sections=2,
        top=args.max_concepts,
        top_members=5,
        embed_model=args.embed_model,
        embedding_api_url=args.embedding_api_url,
        path_include=getattr(args, "path_include", []) or [],
        path_exclude=getattr(args, "path_exclude", []) or [],
    )
    rc_output = compute_repeated_concepts(
        corpus_root, conn, map_data, index_stats, rc_args
    )
    if rc_output is None:
        return []

    # Build a heading-set map ONCE for the template filter.
    headings_by_path: dict[str, set[str]] = {
        f["relative_path"]: _heading_set_for_file(f)
        for f in map_data.get("files", [])
    }

    findings: list[dict[str, Any]] = []
    for concept in rc_output["concepts"]:
        # Filter: if files in this concept share heading skeleton, the
        # "concept" is actually a template-row repetition. Skip — the
        # tight_duplicates check will surface it as TEMPLATE_EFFECT (info).
        files_in_concept = [f["path"] for f in concept["file_breakdown"]]
        if len(files_in_concept) >= 2:
            heading_sets = [
                headings_by_path.get(p, set()) for p in files_in_concept
            ]
            heading_sets = [s for s in heading_sets if s]
            if len(heading_sets) >= 2:
                n_pairs = 0
                jaccard_sum = 0.0
                for i in range(len(heading_sets)):
                    for j in range(i + 1, len(heading_sets)):
                        jaccard_sum += _jaccard(heading_sets[i], heading_sets[j])
                        n_pairs += 1
                mean_jaccard = jaccard_sum / n_pairs if n_pairs else 0.0
                if mean_jaccard >= args.threshold_template:
                    continue  # Template, not smear.

        sev = severity_for_smeared_concept(
            concept["unique_files"], concept["mean_cohesion"]
        )
        if sev is None:
            continue
        findings.append(
            {
                "class": "smeared_owner_truth",
                "severity": sev,
                "label": concept.get("label") or concept["medoid"]["section_id"],
                "evidence": {
                    "unique_files": concept["unique_files"],
                    "section_count": concept["section_count"],
                    "cohesion": round(concept["mean_cohesion"], 3),
                    "representative": {
                        "section_id": concept["medoid"]["section_id"],
                        "relative_path": concept["medoid"]["relative_path"],
                        "heading_chain": concept["medoid"]["heading_chain"],
                    },
                    "files": [
                        f["path"] for f in concept["file_breakdown"][:5]
                    ],
                },
                "next_step": "`1ia-audit` — pick owner file, deprecate others",
            }
        )
    return findings


def _check_tight_duplicates(
    corpus_root: Path, conn, map_data: dict[str, Any], index_stats: dict[str, Any], args
) -> list[dict[str, Any]]:
    """Overlap pairs classified by heading-Jaccard into FULL_DUPLICATE /
    SEMANTIC_SMEAR / TEMPLATE_EFFECT, with one finding per non-UNCLASSIFIED
    classification."""
    from types import SimpleNamespace

    from .overlaps import compute_overlaps

    ov_args = SimpleNamespace(
        threshold=args.threshold_smear,
        top=200,  # broad pool for classifier; severity gates which surface
        min_tokens=30,
        include_same_file=False,
        embed_model=args.embed_model,
        embedding_api_url=args.embedding_api_url,
        path_include=getattr(args, "path_include", []) or [],
        path_exclude=getattr(args, "path_exclude", []) or [],
    )
    ov_output = compute_overlaps(
        corpus_root, conn, map_data, index_stats, ov_args
    )
    if ov_output is None:
        return []

    classified = classify_pairs_by_template(
        ov_output["pairs"],
        map_data,
        heading_jaccard_threshold=args.threshold_template,
    )

    # Group by classification, emit one finding per non-UNCLASSIFIED class.
    grouped: dict[str, list[dict[str, Any]]] = {}
    for p in classified:
        cls = p["classification"]
        if cls == "UNCLASSIFIED":
            continue
        grouped.setdefault(cls, []).append(p)

    findings: list[dict[str, Any]] = []
    for cls, pairs in grouped.items():
        sev = severity_for_classified_pair(cls)
        if sev is None:
            continue
        # FULL_DUPLICATE with many instances escalates from per-pair to
        # one critical group finding.
        if cls == "FULL_DUPLICATE" and len(pairs) >= 3:
            sev = SEVERITY_CRITICAL
        findings.append(
            {
                "class": "tight_duplicates",
                "severity": sev,
                "label": cls.lower().replace("_", " "),
                "evidence": {
                    "classification": cls,
                    "pair_count": len(pairs),
                    "top_pairs": [
                        {
                            "similarity": round(p["similarity"], 3),
                            "heading_jaccard": round(p["heading_jaccard"], 3),
                            "a": {
                                "section_id": p["a"]["section_id"],
                                "relative_path": p["a"]["relative_path"],
                                "heading_chain": p["a"]["heading_chain"],
                            },
                            "b": {
                                "section_id": p["b"]["section_id"],
                                "relative_path": p["b"]["relative_path"],
                                "heading_chain": p["b"]["heading_chain"],
                            },
                        }
                        for p in pairs[:5]
                    ],
                },
                "next_step": {
                    "FULL_DUPLICATE": "`1ia-audit` — merge or deprecate duplicates",
                    "SEMANTIC_SMEAR": "`1ia-audit` — owner truth question",
                    "TEMPLATE_EFFECT": "None — expected shared template; safe to ignore",
                }.get(cls, ""),
            }
        )
    return findings


def _check_intra_file_drift(conn, map_data, args) -> list[dict[str, Any]]:
    """Union of two independent drift detectors, with agreement-based
    severity:

    - Embedding k-means inside the file: catches drift when section
      bodies cluster into ≥ 2 tight, dissimilar groups.
    - Heading-lex diversity: catches drift when H2+ headings share no
      vocabulary — works even when section embeddings all lean on the
      file's H1 title vector.

    Severity per file (NOT per finding):
    - both sources fire   → 🔴 critical (semantic + lexical agreement)
    - embedding only      → 🟡 warning  (bodies diverge but headings don't)
    - heading-lex only    → ℹ️ info     (weak signal; could be designed
                                         structure — guide / inventory)

    One finding emitted per non-empty severity tier so the report shows
    high-confidence drift separately from candidates worth a look. The
    heading-lex path uses `min_sections - 1` so files with 4 H2+ headings
    (too few for meaningful k-means) still get a heading-side check.
    """
    embed_drift = detect_intra_file_drift(
        conn,
        min_sections=args.min_sections_per_file,
        tight_cohesion=args.threshold_drift,
        inter_cluster_max=args.threshold_inter,
    )
    heading_drift = detect_heading_lex_drift(
        map_data,
        min_sections=max(2, args.min_sections_per_file - 1),
        heading_diversity_threshold=getattr(
            args, "threshold_heading_diversity", 0.85
        ),
    )

    by_path: dict[str, dict[str, Any]] = {}
    for d in embed_drift:
        entry = by_path.setdefault(
            d["relative_path"],
            {
                "relative_path": d["relative_path"],
                "section_count": d["section_count"],
                "sources": [],
            },
        )
        entry["sources"].append("embedding_kmeans")
        entry["tight_clusters"] = d["tight_cluster_count"]
        entry["inter_cluster_sim"] = round(d["inter_cluster_sim"], 3)
        entry["topic_groups"] = [
            {
                "size": g["size"],
                "cohesion": round(g["cohesion"], 3),
                "heading_chain": g["representative_heading_chain"],
            }
            for g in d["topic_groups"]
        ]
    for d in heading_drift:
        entry = by_path.setdefault(
            d["relative_path"],
            {
                "relative_path": d["relative_path"],
                "section_count": d["section_count"],
                "sources": [],
            },
        )
        entry["sources"].append("heading_lex")
        entry["heading_diversity"] = round(d["heading_diversity"], 3)
        entry["headings_sample"] = d["headings_sample"]

    if not by_path:
        return []

    # Per-file severity based on source agreement.
    by_severity: dict[str, list[dict[str, Any]]] = {
        SEVERITY_CRITICAL: [],
        SEVERITY_WARNING: [],
        SEVERITY_INFO: [],
    }
    for entry in by_path.values():
        srcs = set(entry["sources"])
        if len(srcs) >= 2:
            sev = SEVERITY_CRITICAL
        elif "embedding_kmeans" in srcs:
            sev = SEVERITY_WARNING
        else:
            sev = SEVERITY_INFO
        by_severity[sev].append(entry)

    findings: list[dict[str, Any]] = []
    sev_label = {
        SEVERITY_CRITICAL: "high-confidence (embedding + heading-lex agree)",
        SEVERITY_WARNING: "embedding clusters diverge",
        SEVERITY_INFO: "headings lexically distant (could be designed structure)",
    }
    for sev, entries in by_severity.items():
        if not entries:
            continue
        entries.sort(
            key=lambda e: (
                -len(e["sources"]),
                -e.get("heading_diversity", 0.0),
                -e.get("tight_clusters", 0),
            )
        )
        findings.append(
            {
                "class": "intra_file_drift",
                "severity": sev,
                "label": (
                    f"{len(entries)} file(s) — {sev_label[sev]}"
                ),
                "evidence": {
                    "drift_count": len(entries),
                    "files": entries[:10],
                },
                "next_step": (
                    "`1ia-audit` — split file along topic groups, or "
                    "confirm template-by-design"
                ),
            }
        )
    return findings


def _check_template_family(map_data: dict[str, Any], args) -> list[dict[str, Any]]:
    """Heading-skeleton families across the corpus. Surfaces «same H2+
    heading appears in N files» as a single finding per shared heading.
    Independent of similarity thresholds — catches `wisdom-*` style
    families even when bodies diverge below the smear cutoff."""
    families = detect_heading_families(
        map_data, min_files=getattr(args, "min_files_in_family", 3)
    )
    findings: list[dict[str, Any]] = []
    for fam in families:
        sev = severity_for_heading_family(fam["file_count"])
        if sev is None:
            continue
        findings.append(
            {
                "class": "template_family",
                "severity": sev,
                "label": (
                    f"'{fam['shared_heading']}' heading shared by "
                    f"{fam['file_count']} files"
                ),
                "evidence": {
                    "shared_heading": fam["shared_heading"],
                    "file_count": fam["file_count"],
                    "files": fam["files"][:8],
                },
                "next_step": (
                    "`1ia-audit` — confirm template-by-design or split into "
                    "function-specific owners"
                ),
            }
        )
    return findings


def _check_discovery_gaps(map_data: dict[str, Any], args) -> list[dict[str, Any]]:
    """Frontmatter description coverage. Counts only files that pass
    --path-include / --path-exclude, so the ratio is meaningful."""
    from .filters import path_matches_any

    include = getattr(args, "path_include", []) or []
    exclude = getattr(args, "path_exclude", []) or []

    def _ok(rel: str) -> bool:
        if include and not path_matches_any(rel, include):
            return False
        if exclude and path_matches_any(rel, exclude):
            return False
        return True

    files = [f for f in map_data.get("files", []) if _ok(f["relative_path"])]
    if not files:
        return []
    gaps = [f for f in files if not f.get("description")]
    ratio = len(gaps) / len(files)
    sev = severity_for_discovery_gap(ratio)
    if sev is None:
        return []
    return [
        {
            "class": "discovery_gaps",
            "severity": sev,
            "label": f"{len(gaps)}/{len(files)} files lack frontmatter description",
            "evidence": {
                "gap_ratio": round(ratio, 3),
                "files_total": len(files),
                "files_without_description": len(gaps),
                "examples": [f["relative_path"] for f in gaps[:5]],
            },
            "next_step": "`1instruction-layer` — add frontmatter `description` to high-traffic files",
        }
    ]


def _check_cluster_folder_mismatch(corpus_root: Path, args) -> list[dict[str, Any]]:
    from .index_cluster import cluster_sections

    try:
        result = cluster_sections(
            corpus_root,
            k=args.cluster_k,
            cache_root=Path(args.cache_dir).expanduser() if args.cache_dir else None,
            seed=42,
            path_include=getattr(args, "path_include", None),
            path_exclude=getattr(args, "path_exclude", None),
        )
    except (FileNotFoundError, ModuleNotFoundError):
        return []

    if not result.get("clusters"):
        return []

    findings: list[dict[str, Any]] = []
    for c in result["clusters"]:
        sev = severity_for_cluster_mismatch(c.get("common_parent", ""), c["size"])
        if sev != SEVERITY_WARNING:
            continue  # info-level clusters don't surface as separate findings
        findings.append(
            {
                "class": "cluster_folder_mismatch",
                "severity": sev,
                "label": f"Cluster {c['id'] + 1}: {c['size']} sections, no shared folder",
                "evidence": {
                    "cluster_size": c["size"],
                    "cohesion": round(c["cohesion"], 3),
                    "centroid_path": c["centroid_path"],
                    "centroid_heading_chain": c.get("centroid_heading_chain", ""),
                    "top_files": [
                        {"path": p, "section_count": n}
                        for p, n in c["top_files"][:5]
                    ],
                },
                "next_step": "`1ia-audit` — sections topic-related but folder-scattered",
            }
        )
    return findings


def audit_payload(
    *,
    corpus_root: Path,
    conn: Any,
    map_data: dict[str, Any],
    sections: list[dict[str, Any]],
    index_stats: dict[str, Any],
    args: Any,
) -> dict[str, Any]:
    """Build the canonical audit JSON payload used by CLI and public API."""
    findings: list[dict[str, Any]] = []
    findings.extend(_check_discovery_gaps(map_data, args))
    findings.extend(_check_smeared_owner_truth(corpus_root, conn, map_data, index_stats, args))
    findings.extend(_check_tight_duplicates(corpus_root, conn, map_data, index_stats, args))
    findings.extend(_check_template_family(map_data, args))
    findings.extend(_check_intra_file_drift(conn, map_data, args))
    findings.extend(_check_cluster_folder_mismatch(corpus_root, args))

    severity_order = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 1, SEVERITY_INFO: 2}
    findings.sort(key=lambda f: (severity_order.get(f["severity"], 3), f["class"]))

    return {
        "root": str(corpus_root),
        "health": compute_health(findings),
        "severity_counts": severity_counts(findings),
        "thresholds": {
            "smear": args.threshold_smear,
            "drift_cohesion": args.threshold_drift,
            "drift_inter": args.threshold_inter,
            "template_jaccard": args.threshold_template,
            "heading_diversity": getattr(args, "threshold_heading_diversity", 0.85),
            "min_files_in_family": getattr(args, "min_files_in_family", 3),
            "discovery_gap_warn": args.discovery_gap_warn,
            "discovery_gap_crit": args.discovery_gap_crit,
            "min_sections_per_file": args.min_sections_per_file,
            "cluster_k": args.cluster_k,
        },
        "stats": {
            "files_indexed": map_data["file_count"],
            "sections_indexed": len(sections),
            "embeddings_cached": index_stats["reused"],
            "embeddings_computed": index_stats["embedded"],
        },
        "engine": {
            "embed_model": args.embed_model,
            "embedding_api_url": args.embedding_api_url,
        },
        "findings": findings,
    }
