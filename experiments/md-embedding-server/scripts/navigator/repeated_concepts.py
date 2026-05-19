"""Concept-level duplicate detection via connected components on the
section-similarity graph.

Vertices = sections (token_count >= min_tokens), edges = cosine
similarity >= threshold (max over chunk pairs). Connected components
are "concepts" — ideas that recur across the corpus. Sort by number of
unique files the concept touches, then by total section count.

Output is concept-centric: each concept lists the medoid section as its
label, the files it appears in (with section count per file), and the
top-K member sections by similarity to the medoid.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .folder_map import build_map
from .index import _index_dir_for_corpus, ensure_index
from .sections import build_sections_from_map


class _UnionFind:
    """Union-find with path compression and union-by-rank."""

    __slots__ = ("parent", "rank")

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1


def cmd_repeated_concepts(args) -> int:
    corpus_root = Path(args.path).expanduser().resolve()
    if not corpus_root.exists():
        print(f"Path does not exist: {corpus_root}", file=sys.stderr)
        return 2

    map_data = build_map(corpus_root, args.max_heading_level, with_tokens=False)
    if not map_data["files"]:
        print(f"No Markdown files under {corpus_root}", file=sys.stderr)
        return 1

    sections = build_sections_from_map(map_data)
    if not sections:
        print(f"No sections extracted from {corpus_root}", file=sys.stderr)
        return 1

    cache_root = Path(args.cache_dir).expanduser() if args.cache_dir else None
    if args.no_cache:
        target = _index_dir_for_corpus(corpus_root, cache_root=cache_root)
        for name in ("index.sqlite", "index.sqlite-wal", "index.sqlite-shm"):
            (target / name).unlink(missing_ok=True)

    max_auto_embed = (
        None if args.max_auto_embed == 0 else int(args.max_auto_embed)
    )

    try:
        conn, index_stats = ensure_index(
            corpus_root,
            "sections",
            sections,
            args.embed_model,
            embedding_api_url=args.embedding_api_url,
            embedding_timeout=args.embedding_timeout,
            cache_root=cache_root,
            max_auto_embed=max_auto_embed,
        )
    except ModuleNotFoundError as exc:
        print(
            f"Missing Python dependency: {exc}.\n"
            f"  This script needs uv to resolve its inline deps "
            f"(`numpy`, `sqlite-vec`, `pyyaml`).\n"
            f"  Run it via the uv shebang:\n"
            f"    chmod +x md_navigator.py && ./md_navigator.py repeated-concepts ...\n"
            f"  Or explicitly:\n"
            f"    uv run --script md_navigator.py repeated-concepts ...\n"
            f"  Install uv if missing: `brew install uv` (macOS) or "
            f"https://docs.astral.sh/uv.",
            file=sys.stderr,
        )
        return 3
    except RuntimeError as exc:
        print(
            f"Embedding API call failed: {exc}\n"
            f"  Check OPENROUTER_API_KEY env var or `.openrouter.key` file "
            f"(see SKILL.md → First-time setup).",
            file=sys.stderr,
        )
        return 3

    if index_stats.get("delta_too_large"):
        pending = index_stats["pending_chunks"]
        added = index_stats["added_sections"]
        print(
            f"Index needs warmup before repeated-concepts can run.\n"
            f"  {added} new sections / {pending} new chunks pending "
            f"(cap for auto-embed in `repeated-concepts` = {max_auto_embed}).\n"
            f"\n"
            f"  Next step:\n"
            f"    md_navigator.py index '{corpus_root}'\n"
            f"\n"
            f"  Then re-run repeated-concepts. One-time cost; subsequent runs "
            f"reuse the index on disk.",
            file=sys.stderr,
        )
        return 4

    embedded_count = index_stats["embedded"]
    cached_count = index_stats["reused"]

    import numpy as np  # type: ignore

    rows = conn.execute(
        "SELECT chunks.chunk_id, chunks.section_rowid, chunks.chunk_idx, "
        "s.section_id, s.file_id, s.relative_path, "
        "s.start_line, s.heading_text, s.heading_chain, "
        "s.token_count, vec.embedding "
        "FROM chunks "
        "JOIN sections_vec vec ON vec.rowid = chunks.chunk_id "
        "JOIN sections AS s ON s.rowid = chunks.section_rowid "
        "WHERE s.scope = 'sections' "
        "ORDER BY chunks.chunk_id"
    ).fetchall()

    m = len(rows)
    if m < 2:
        print("Need at least 2 chunks to compare.", file=sys.stderr)
        return 1

    threshold = float(args.threshold)
    min_tokens = int(args.min_tokens)
    min_files = int(args.min_files)
    min_sections = int(args.min_sections)
    top_n = int(args.top)
    top_members = int(args.top_members)

    chunk_section = np.array([r[1] for r in rows], dtype=np.int64)
    section_meta: dict[int, dict[str, Any]] = {}
    for r in rows:
        sec_rowid = r[1]
        if sec_rowid not in section_meta:
            section_meta[sec_rowid] = {
                "section_id": r[3],
                "file_id": r[4],
                "relative_path": r[5],
                "start_line": r[6],
                "heading_text": r[7],
                "heading_chain": r[8],
                "token_count": r[9],
            }

    # Section-level pair similarity = max cosine across chunk pairs of A x B.
    # Same aggregation as `overlaps`, but we'll use it to build an undirected
    # similarity graph and walk connected components.
    vecs = np.stack([np.frombuffer(r[10], dtype="float32") for r in rows])
    sim = vecs @ vecs.T
    sim_upper = np.triu(sim, k=1)
    high_pairs = np.argwhere(sim_upper >= threshold)

    section_pair_sim: dict[tuple[int, int], float] = {}
    for i, j in high_pairs:
        sa = int(chunk_section[i])
        sb = int(chunk_section[j])
        if sa == sb:
            continue
        a_meta = section_meta[sa]
        b_meta = section_meta[sb]
        if a_meta["token_count"] < min_tokens or b_meta["token_count"] < min_tokens:
            continue
        key = (sa, sb) if sa < sb else (sb, sa)
        s = float(sim[i, j])
        existing = section_pair_sim.get(key)
        if existing is None or s > existing:
            section_pair_sim[key] = s

    # Union-find on sections that participate in any above-threshold pair.
    # Sections with no edges = isolated noise, dropped silently — concepts
    # require at least one neighbour by definition.
    participating: set[int] = set()
    for a, b in section_pair_sim:
        participating.add(a)
        participating.add(b)

    section_to_idx: dict[int, int] = {sid: i for i, sid in enumerate(sorted(participating))}
    idx_to_section: list[int] = sorted(participating)
    uf = _UnionFind(len(section_to_idx))
    for a, b in section_pair_sim:
        uf.union(section_to_idx[a], section_to_idx[b])

    components: dict[int, list[int]] = {}
    for sid in idx_to_section:
        root = uf.find(section_to_idx[sid])
        components.setdefault(root, []).append(sid)

    items: list[dict[str, Any]] = []
    for member_ids in components.values():
        if len(member_ids) < min_sections:
            continue

        file_counts: dict[str, int] = {}
        for sid in member_ids:
            path = section_meta[sid]["relative_path"]
            file_counts[path] = file_counts.get(path, 0) + 1
        unique_files = len(file_counts)
        if unique_files < min_files:
            continue

        # Medoid = section with highest sum of similarities to other members.
        # Each pair (a, b) contributes once; both endpoints get credited.
        sum_sim: dict[int, float] = {sid: 0.0 for sid in member_ids}
        sorted_members = sorted(member_ids)
        for i, sa in enumerate(sorted_members):
            for sb in sorted_members[i + 1 :]:
                s = section_pair_sim.get((sa, sb), 0.0)
                if s == 0.0:
                    continue
                sum_sim[sa] += s
                sum_sim[sb] += s
        medoid_sid = max(sum_sim, key=lambda sid: sum_sim[sid])

        # Mean cohesion = average pairwise similarity (only above-threshold
        # edges contribute; pairs without an edge count as 0 — they exist in
        # the same component but transitively).
        n_pairs = len(member_ids) * (len(member_ids) - 1) // 2
        total = sum(sum_sim.values()) / 2.0  # each pair counted twice
        mean_cohesion = total / n_pairs if n_pairs > 0 else 0.0

        # Top members by similarity to medoid (medoid itself excluded).
        # Drop sections without a direct edge to the medoid — they belong to
        # the component transitively and would show as sim=0 noise.
        member_sim_to_medoid: list[tuple[int, float]] = []
        for sid in member_ids:
            if sid == medoid_sid:
                continue
            key = (sid, medoid_sid) if sid < medoid_sid else (medoid_sid, sid)
            s = section_pair_sim.get(key, 0.0)
            if s <= 0.0:
                continue
            member_sim_to_medoid.append((sid, s))
        member_sim_to_medoid.sort(key=lambda x: -x[1])
        top_member_records = [
            {
                "similarity": s,
                "section": section_meta[sid],
            }
            for sid, s in member_sim_to_medoid[:top_members]
        ]

        # All member sections grouped per file, for the file-list table.
        per_file: dict[str, list[dict[str, Any]]] = {}
        for sid in member_ids:
            path = section_meta[sid]["relative_path"]
            per_file.setdefault(path, []).append(section_meta[sid])
        file_breakdown = sorted(
            (
                {
                    "path": path,
                    "section_count": len(secs),
                    "sections": secs,
                }
                for path, secs in per_file.items()
            ),
            key=lambda x: (-x["section_count"], x["path"]),
        )

        items.append(
            {
                "label": _concept_label(section_meta[medoid_sid]),
                "medoid": section_meta[medoid_sid],
                "section_count": len(member_ids),
                "unique_files": unique_files,
                "mean_cohesion": mean_cohesion,
                "file_breakdown": file_breakdown,
                "top_members": top_member_records,
            }
        )

    items.sort(
        key=lambda x: (-x["unique_files"], -x["section_count"], -x["mean_cohesion"])
    )
    items = items[:top_n]

    eligible_section_count = sum(
        1 for meta in section_meta.values() if meta["token_count"] >= min_tokens
    )

    output = {
        "root": str(corpus_root),
        "threshold": threshold,
        "min_tokens": min_tokens,
        "min_files": min_files,
        "min_sections": min_sections,
        "engine": {
            "embed_model": args.embed_model,
            "embedding_api_url": args.embedding_api_url,
        },
        "stats": {
            "files_indexed": map_data["file_count"],
            "sections_indexed": len(section_meta),
            "sections_eligible": eligible_section_count,
            "chunks_compared": m,
            "embeddings_cached": cached_count,
            "embeddings_computed": embedded_count,
            "edges_above_threshold": len(section_pair_sim),
            "concepts_surfaced": len(items),
        },
        "concepts": items,
    }

    if args.output:
        out_path = Path(args.output).expanduser().resolve()
    else:
        index_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root)
        out_path = index_dir / "repeated-concepts.md"

    if args.json:
        payload = json.dumps(output, ensure_ascii=False, indent=2, default=str)
        if args.stdout:
            print(payload)
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(payload + "\n", encoding="utf-8")
            print(f"JSON report → {out_path}")
        return 0

    rendered = render_repeated_concepts(output)
    if args.stdout:
        print(rendered, end="")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    _print_summary(output, out_path)
    return 0


def _concept_label(medoid_meta: dict[str, Any]) -> str:
    chain = medoid_meta.get("heading_chain") or ""
    if chain:
        return chain
    heading = medoid_meta.get("heading_text") or ""
    if heading:
        return heading
    return f"(file) {medoid_meta['relative_path']}"


def _print_summary(out: dict[str, Any], out_path: Path) -> None:
    stats = out["stats"]
    print(f"# Repeated concepts: {out['root']}")
    print(
        f"Engine: dense similarity ({out['engine']['embed_model']})  "
        f"| Threshold: {out['threshold']}  | Min tokens: {out['min_tokens']}  "
        f"| Min files: {out['min_files']}  | Min sections: {out['min_sections']}"
    )
    print(
        f"Indexed: {stats['files_indexed']} files / {stats['sections_indexed']} sections "
        f"({stats['sections_eligible']} eligible) | edges above threshold: "
        f"{stats['edges_above_threshold']}"
    )
    print(f"Concepts surfaced: {stats['concepts_surfaced']}")
    print(f"Report → {out_path}")
    items = out["concepts"]
    if items:
        print()
        print("Top concepts (files × sections — label):")
        for i, c in enumerate(items[:8], start=1):
            label = c["label"] if len(c["label"]) <= 80 else c["label"][:77] + "..."
            print(
                f"  {i}. {c['unique_files']}f × {c['section_count']}s  "
                f"(cohesion {c['mean_cohesion']:.2f}) — {label}"
            )


def render_repeated_concepts(out: dict[str, Any]) -> str:
    stats = out["stats"]
    eng = out["engine"]
    lines = [
        f"# Repeated concepts: {out['root']}",
        "",
        f"Engine: dense similarity ({eng['embed_model']})",
        f"Indexed: {stats['files_indexed']} files / {stats['sections_indexed']} sections "
        f"({stats['sections_eligible']} eligible, {stats['chunks_compared']} chunks) "
        f"| cached: {stats['embeddings_cached']} | computed: {stats['embeddings_computed']}",
        f"Threshold: {out['threshold']} | min tokens: {out['min_tokens']} | "
        f"min files: {out['min_files']} | min sections: {out['min_sections']}",
        f"Edges above threshold: {stats['edges_above_threshold']} | "
        f"concepts surfaced: {stats['concepts_surfaced']}",
        "",
        "## How to read",
        "",
        "A **concept** is a connected component in the section-similarity "
        "graph: sections joined when their cosine similarity is at or above "
        "the threshold. Each concept represents one **idea that recurs** "
        "across the corpus. The medoid section (highest summed similarity to "
        "the rest of its component) is the representative.",
        "",
        "- **Unique files** — how many distinct files contribute a section. "
        "More files = stronger owner-truth question.",
        "- **Mean cohesion** — average pairwise similarity inside the "
        "component. Higher = tighter concept; lower = transitive bridge.",
        "- **Top members** — sections most similar to the representative.",
        "",
        "Concepts spanning many files are IA evidence for **owner truth** "
        "(`1ia-audit`): one home, others point at it. A concept inside one "
        "file is filtered out by `--min-files` — that's intra-file "
        "repetition, not duplication of idea across the repo.",
        "",
        "## Concepts (ranked by unique files, then section count)",
        "",
    ]
    if not out["concepts"]:
        lines.append(
            "(no repeated concepts above threshold — try lowering "
            "`--threshold` or `--min-files`)"
        )
        lines.append("")
    else:
        for i, c in enumerate(out["concepts"], start=1):
            medoid = c["medoid"]
            medoid_chain = medoid["heading_chain"] or "(file)"
            lines.append(
                f"### {i}. {c['label']}  "
                f"({c['unique_files']} files × {c['section_count']} sections, "
                f"cohesion {c['mean_cohesion']:.2f})"
            )
            lines.append("")
            lines.append(
                f"**Representative:** [{medoid['section_id']}] "
                f"`{medoid['relative_path']}:L{medoid['start_line']}` "
                f"## {medoid_chain} (~{medoid['token_count']}t)"
            )
            lines.append("")
            lines.append("**Files (section count):**")
            for fb in c["file_breakdown"]:
                lines.append(f"- `{fb['path']}`  ({fb['section_count']})")
            lines.append("")
            if c["top_members"]:
                lines.append("**Top member sections by similarity to representative:**")
                for mb in c["top_members"]:
                    sec = mb["section"]
                    chain = sec["heading_chain"] or "(file)"
                    lines.append(
                        f"- sim={mb['similarity']:.3f} — "
                        f"[{sec['section_id']}] `{sec['relative_path']}:L{sec['start_line']}` "
                        f"## {chain} (~{sec['token_count']}t)"
                    )
                lines.append("")

    lines.append("## Hand off")
    lines.append(
        "- Owner-truth candidate (concept spans many files) → "
        "`1ia-audit` (function split / smeared information)"
    )
    lines.append("- Before merge / move / rename → `1md-graph impact <file>`")
    lines.append(
        "- Inspect specific section → `pick --headings <id> --extract` "
        "after `headings` on the same root"
    )
    return "\n".join(lines).rstrip() + "\n"
