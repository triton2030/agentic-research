# Phase 5 — Tier 2 capabilities

**Estimated cost**: ~2 дня
**Depends on**: P4 (section profile foundation)
**Unblocks**: Tier 2 ready

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md`.

## Цель

Реализовать **Tier 2 active capabilities** на foundation P4. Эти capabilities решают **корневую боль пользователя** — «у меня информация дублируется вместо того чтобы быть вики-ссылкой на блок-владелец». Tier 2 даёт:

1. **`md_originality`** (internal) — uniqueness score per section через cosine distance к ближайшим neighbors
2. **`md_owner_candidates`** (internal) — для секции найти best wikilink target через composite signal
3. **`md_refactor_candidates`** (composite primary) — actionable proposals для top-N suspicious sections
4. **`md_query_by_type`** (composite primary) — filter sections by `profile.type`

**Verification = editorial scenarios**, не accuracy labels. Real refactor session: user+agent действуют по top-10 proposals, ≥5 actionable.

## In scope

- New module `navigator/originality.py` — cosine-based uniqueness
- New module `navigator/owner_detector.py` — composite signal owner ranking
- New module `navigator/refactor_proposals.py` — orchestrator
- New composite MCP tools: `md_refactor_candidates`, `md_query_by_type`
- Internal helpers (NOT exposed in listTools): `md_originality`, `md_owner_candidates`
- Proposal output shape strict adherence: `{ proposal_type, affected_section, target_owner, evidence, confidence, why, no_automation: true }`
- Editorial session verification — real refactor work на `knowledge/`

## NOT in scope

- Automated edits (`md_auto_wikilink`, `md_auto_split`) — opasно, defer indefinitely
- Cross-corpus comparison — defer
- Workflow recipes / SKILL.md (P6)
- Cleanup (P7)

## Definition of done

- `originality.py` exports `compute_originality_score(corpus_root, section_id) → float` (0.0-1.0)
- `owner_detector.py` exports `find_owner_candidates(corpus_root, section_id_or_text) → list[candidate]`
- `refactor_proposals.py` exports `generate_proposals(corpus_root, top_n=10) → list[proposal]`
- Each proposal has shape:
  ```json
  {
    "proposal_type": "replace_with_wikilink" | "extract_to_owner" | "merge_with_X" | "orphan_quarantine",
    "affected_section": { "path", "heading_id", "line_range": [start, end] },
    "target_owner": { "path", "heading_id" } | null,
    "evidence": { "cosine_similarity", "section_profile", "in_degree_target", ... },
    "confidence": 0.0-1.0,
    "why": "human-readable rationale",
    "no_automation": true
  }
  ```
- CLI: `md_navigator.py originality <corpus> <section-id> --json` работает (для debug)
- CLI: `md_navigator.py refactor-candidates <corpus> --top 10 --json` работает
- CLI: `md_navigator.py query-by-type <corpus> --types definition,open-question --json` работает
- MCP composite `md_refactor_candidates({ corpus, top? })` зарегистрирован, returns proposals list
- MCP composite `md_query_by_type({ corpus, types[], filter? })` зарегистрирован
- **Editorial verification passed**: real session on `knowledge/`, top-10 proposals — user marks ≥5 as actionable (replace/merge/extract сделан ИЛИ explicitly rejected с обоснованием)

## Stop rules

- Editorial session shows < 50% actionable proposals (>5 noise out of 10) → STOP P5, reshape composite signal weights or rethink approach
- `md_refactor_candidates` latency > 30s on `knowledge/` (~300 sections) — performance issue, optimize before continuing
- Proposal noise visible in confidence distribution (all proposals confidence 0.5-0.6 = signal weak) → re-examine signal weights

## Подшаги

### P5.1 — originality.py (1 час)

**Файл**: `experiments/md-embedding-server/scripts/navigator/originality.py`

```python
"""Section uniqueness scoring via cosine distance to nearest neighbors.

Used by P5 owner_detector and refactor_proposals to identify
duplicate-likely sections (low uniqueness = good candidate for wikilink).
"""

from __future__ import annotations
from pathlib import Path
from typing import Any

import numpy as np

from .index_meta import open_or_create_index


def compute_originality_score(
    corpus_root: Path,
    section_id: int,
    exclude_same_file: bool = True,
) -> float:
    """Uniqueness 0.0-1.0. Lower = duplicate-like, higher = unique.
    
    Score = 1 - max cosine similarity to any other section in corpus.
    """
    conn = open_or_create_index(corpus_root)
    cursor = conn.cursor()
    
    # Fetch target section embedding + path
    cursor.execute("""
        SELECT relative_path, embedding FROM sections
        WHERE rowid = ? AND scope = 'sections'
    """, (section_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return 1.0
    target_path, target_emb_blob = row
    target_emb = np.frombuffer(target_emb_blob, dtype=np.float32)
    
    # Fetch all other sections
    if exclude_same_file:
        cursor.execute("""
            SELECT embedding FROM sections
            WHERE scope = 'sections' AND rowid != ? AND relative_path != ?
        """, (section_id, target_path))
    else:
        cursor.execute("""
            SELECT embedding FROM sections
            WHERE scope = 'sections' AND rowid != ?
        """, (section_id,))
    others = cursor.fetchall()
    conn.close()
    
    if not others:
        return 1.0
    
    other_embs = np.vstack([np.frombuffer(o[0], dtype=np.float32) for o in others])
    
    # Cosine similarity
    target_norm = target_emb / (np.linalg.norm(target_emb) + 1e-9)
    other_norms = other_embs / (np.linalg.norm(other_embs, axis=1, keepdims=True) + 1e-9)
    similarities = other_norms @ target_norm
    
    max_sim = float(similarities.max())
    return float(max(0.0, 1.0 - max_sim))


def find_nearest_neighbors(
    corpus_root: Path,
    section_id: int,
    top_k: int = 5,
    exclude_same_file: bool = True,
) -> list[dict[str, Any]]:
    """Return top-K most similar sections (for use by owner detector)."""
    conn = open_or_create_index(corpus_root)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT relative_path, embedding FROM sections
        WHERE rowid = ? AND scope = 'sections'
    """, (section_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []
    target_path, target_emb_blob = row
    target_emb = np.frombuffer(target_emb_blob, dtype=np.float32)
    
    if exclude_same_file:
        cursor.execute("""
            SELECT rowid, relative_path, heading_chain, heading_text, embedding,
                   profile_type, profile_subject, profile_owns_terms, profile_confidence
            FROM sections
            WHERE scope = 'sections' AND rowid != ? AND relative_path != ?
        """, (section_id, target_path))
    else:
        cursor.execute("""
            SELECT rowid, relative_path, heading_chain, heading_text, embedding,
                   profile_type, profile_subject, profile_owns_terms, profile_confidence
            FROM sections
            WHERE scope = 'sections' AND rowid != ?
        """, (section_id,))
    candidates = cursor.fetchall()
    conn.close()
    
    if not candidates:
        return []
    
    target_norm = target_emb / (np.linalg.norm(target_emb) + 1e-9)
    results = []
    for cand in candidates:
        emb = np.frombuffer(cand[4], dtype=np.float32)
        emb_norm = emb / (np.linalg.norm(emb) + 1e-9)
        sim = float(emb_norm @ target_norm)
        results.append({
            "rowid": cand[0],
            "relative_path": cand[1],
            "heading_chain": cand[2],
            "heading_text": cand[3],
            "cosine_similarity": sim,
            "profile_type": cand[5],
            "profile_subject": cand[6],
            "profile_owns_terms": cand[7],  # JSON string
            "profile_confidence": cand[8],
        })
    
    results.sort(key=lambda x: -x["cosine_similarity"])
    return results[:top_k]
```

### P5.2 — owner_detector.py (1.5 часа)

**Файл**: `experiments/md-embedding-server/scripts/navigator/owner_detector.py`

**Composite signal** для owner ranking:

```python
"""Composite signal owner detection.

Adversarial review insight (2026-05-21): NetworkX centrality alone ≠ owner truth.
Owner = composite of graph_centrality + uniqueness + profile.type=="definition" + length.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from .originality import find_nearest_neighbors
from .link_graph import build_link_graph
from .importance import compute_importance


def find_owner_candidates(
    corpus_root: Path,
    section_id: int,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """Find best wikilink targets for section_id.
    
    Returns ranked candidates with composite confidence score.
    """
    # 1. Get semantic neighbors (P5.1)
    neighbors = find_nearest_neighbors(corpus_root, section_id, top_k=top_k * 3)
    
    if not neighbors:
        return []
    
    # 2. Get graph importance for files
    graph = build_link_graph(corpus_root)
    importance = {r["path"]: r for r in compute_importance(graph)}
    
    # 3. Score each neighbor
    scored = []
    for n in neighbors:
        path = n["relative_path"]
        imp = importance.get(path, {})
        
        # Component signals (each 0-1)
        cosine = n["cosine_similarity"]  # higher = more similar = more likely owner
        is_definition = 1.0 if n.get("profile_type") == "definition" else 0.3 if n.get("profile_type") == "decision" else 0.0
        pagerank = min(1.0, imp.get("pagerank", 0.0) * 50)  # scale; typical pagerank 0.02-0.05
        in_degree_norm = min(1.0, imp.get("in_degree", 0) / 10.0)
        confidence_prior = n.get("profile_confidence") or 0.5
        
        # Composite — weighted (tuning during editorial verification)
        composite = (
            0.35 * cosine +
            0.30 * is_definition +
            0.15 * pagerank +
            0.10 * in_degree_norm +
            0.10 * confidence_prior
        )
        
        scored.append({
            "path": path,
            "heading_chain": n["heading_chain"],
            "heading_text": n["heading_text"],
            "section_rowid": n["rowid"],
            "profile_type": n.get("profile_type"),
            "profile_subject": n.get("profile_subject"),
            "evidence": {
                "cosine_similarity": round(cosine, 3),
                "is_definition_boost": is_definition,
                "pagerank": round(imp.get("pagerank", 0.0), 4),
                "in_degree": imp.get("in_degree", 0),
                "profile_confidence": confidence_prior,
            },
            "composite_score": round(composite, 3),
        })
    
    scored.sort(key=lambda x: -x["composite_score"])
    return scored[:top_k]
```

### P5.3 — refactor_proposals.py (2 часа)

**Файл**: `experiments/md-embedding-server/scripts/navigator/refactor_proposals.py`

```python
"""Orchestrate refactor proposals: low-uniqueness + uses-type sections → owner.

Output shape strict (no_automation: true):
- proposal_type: replace_with_wikilink | extract_to_owner | merge_with_X | orphan_quarantine
- evidence and why fields populated for transparency
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from .originality import compute_originality_score
from .owner_detector import find_owner_candidates
from .section_profile import get_profile
from .index_meta import open_or_create_index


def generate_proposals(
    corpus_root: Path,
    top_n: int = 10,
    uniqueness_threshold: float = 0.30,  # below this = suspect dup
    owner_confidence_threshold: float = 0.55,
) -> list[dict[str, Any]]:
    """Generate top-N actionable refactor proposals.

    Strategy:
    1. Iterate sections with profile.type in {'uses', 'example'}
    2. Compute originality; if low (<threshold), candidate for owner detection
    3. Find owner candidates; if best > confidence_threshold, propose replace_with_wikilink
    4. If no clear owner but content unique within file, propose extract_to_owner
    5. If section is orphan (no in/out edges) with substantial body, propose orphan_quarantine
    """
    conn = open_or_create_index(corpus_root)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rowid, relative_path, heading_chain, heading_text,
               line_start, line_end, profile_type, profile_subject, profile_confidence
        FROM sections
        WHERE scope = 'sections' AND profile_type IS NOT NULL
        ORDER BY profile_confidence DESC
    """)
    sections = [
        dict(zip([d[0] for d in cursor.description], row))
        for row in cursor.fetchall()
    ]
    conn.close()
    
    candidates_by_score: list[dict[str, Any]] = []
    
    for s in sections:
        ptype = s.get("profile_type")
        if ptype not in {"uses", "example"}:
            continue
        
        uniqueness = compute_originality_score(corpus_root, s["rowid"])
        if uniqueness >= uniqueness_threshold:
            continue  # too unique, not a duplicate candidate
        
        owners = find_owner_candidates(corpus_root, s["rowid"], top_k=3)
        if not owners:
            continue
        
        best_owner = owners[0]
        if best_owner["composite_score"] < owner_confidence_threshold:
            # Could be extract_to_owner candidate (low signal for replace)
            continue
        
        proposal = {
            "proposal_type": "replace_with_wikilink",
            "affected_section": {
                "path": s["relative_path"],
                "heading_id": s.get("heading_chain") or s.get("heading_text"),
                "line_range": [s.get("line_start"), s.get("line_end")],
            },
            "target_owner": {
                "path": best_owner["path"],
                "heading_id": best_owner["heading_chain"] or best_owner["heading_text"],
            },
            "evidence": {
                "uniqueness": round(uniqueness, 3),
                "owner_composite_score": best_owner["composite_score"],
                "details": best_owner["evidence"],
                "section_profile": {
                    "type": s["profile_type"],
                    "subject": s.get("profile_subject"),
                    "confidence": s.get("profile_confidence"),
                },
            },
            "confidence": round(min(1.0, best_owner["composite_score"]), 3),
            "why": (
                f"Section is type={s['profile_type']}, low uniqueness ({uniqueness:.2f}) suggests "
                f"duplicate of existing content. Best owner candidate at {best_owner['path']} "
                f"({best_owner.get('profile_type')}) has composite score {best_owner['composite_score']:.2f}."
            ),
            "no_automation": True,
        }
        candidates_by_score.append(proposal)
    
    candidates_by_score.sort(key=lambda p: -p["confidence"])
    return candidates_by_score[:top_n]


def query_sections_by_type(
    corpus_root: Path,
    types: list[str],
    filter_text: str | None = None,
) -> list[dict[str, Any]]:
    """Filter sections by profile.type. Optional semantic filter."""
    conn = open_or_create_index(corpus_root)
    cursor = conn.cursor()
    
    placeholders = ",".join(["?"] * len(types))
    cursor.execute(f"""
        SELECT rowid, relative_path, heading_chain, heading_text,
               profile_type, profile_subject, profile_owns_terms, profile_confidence
        FROM sections
        WHERE scope = 'sections' AND profile_type IN ({placeholders})
        ORDER BY profile_confidence DESC
    """, types)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "rowid": row[0],
            "path": row[1],
            "heading_chain": row[2],
            "heading_text": row[3],
            "profile_type": row[4],
            "profile_subject": row[5],
            "profile_owns_terms": json.loads(row[6]) if row[6] else [],
            "profile_confidence": row[7],
        })
    
    # Optional semantic filter
    if filter_text:
        from .search import semantic_filter  # P5: may need to expose this
        # For now: simple substring match on subject + heading_text
        filter_lower = filter_text.lower()
        results = [
            r for r in results
            if filter_lower in (r["profile_subject"] or "").lower()
            or filter_lower in (r["heading_text"] or "").lower()
        ]
    
    return results
```

### P5.4 — CLI subcommands (30 минут)

**Файл**: `experiments/md-embedding-server/scripts/navigator/cli.py`

```python
# originality
orig = sub.add_parser("originality", help="Uniqueness score for one section (debug).")
orig.add_argument("path", help="Corpus root.")
orig.add_argument("section_id", type=int, help="Section rowid (from index).")
orig.add_argument("--json", action="store_true")

# refactor-candidates
rc = sub.add_parser("refactor-candidates", help="Generate actionable refactor proposals.")
rc.add_argument("path", help="Corpus root.")
rc.add_argument("--top", type=int, default=10)
rc.add_argument("--uniqueness-threshold", type=float, default=0.30)
rc.add_argument("--owner-confidence-threshold", type=float, default=0.55)
rc.add_argument("--json", action="store_true")

# query-by-type
qbt = sub.add_parser("query-by-type", help="Filter sections by profile.type.")
qbt.add_argument("path", help="Corpus root.")
qbt.add_argument("--types", required=True, help="Comma-separated types (e.g. 'definition,open-question').")
qbt.add_argument("--filter", default=None, help="Optional text filter (matches subject/heading).")
qbt.add_argument("--json", action="store_true")
```

Dispatch each with import from new modules.

### P5.5 — MCP composite tools (30 минут)

**Файл**: `experiments/md-embedding-server/mcp/src/tools/composite-tools.js`

```js
registerTool(
  "md_refactor_candidates",
  "**PRIMARY for W7 refactor opportunities workflow.** Generate actionable refactor proposals for a Markdown corpus. Top-N suspicious sections (low uniqueness + type=uses) with target owner candidates. Output is **proposal shape with evidence/confidence/why** — never auto-edits. Use for editorial refactor sessions.",
  {
    corpus: z.string().min(1).describe("Corpus root path"),
    top: z.number().int().positive().max(50).optional().describe("Top N proposals (default 10)"),
    uniqueness_threshold: z.number().min(0).max(1).optional(),
    owner_confidence_threshold: z.number().min(0).max(1).optional()
  },
  async ({ corpus, top, uniqueness_threshold, owner_confidence_threshold }) => {
    const args = ["refactor-candidates", corpus, "--json"];
    if (top) args.push("--top", String(top));
    if (uniqueness_threshold !== undefined) args.push("--uniqueness-threshold", String(uniqueness_threshold));
    if (owner_confidence_threshold !== undefined) args.push("--owner-confidence-threshold", String(owner_confidence_threshold));
    return await runNavigator(args, { timeoutMs: 180_000 });
  }
);

registerTool(
  "md_query_by_type",
  "**PRIMARY for W8 semantic-shape query workflow.** Filter sections by profile.type — find all open-questions, decisions, definitions across corpus. Use when looking for «найди все TODO в knowledge» or «список всех decisions about X».",
  {
    corpus: z.string().min(1),
    types: z.array(z.enum([
      "definition", "decision", "open-question", "rule",
      "example", "uses", "external-citation", "heading-only"
    ])).min(1),
    filter: z.string().optional().describe("Optional text filter on subject/heading")
  },
  async ({ corpus, types, filter }) => {
    const args = ["query-by-type", corpus, "--types", types.join(","), "--json"];
    if (filter) args.push("--filter", filter);
    return await runNavigator(args, { timeoutMs: 60_000 });
  }
);
```

### P5.6 — Editorial verification session (2-3 часа)

**Procedure**:

1. Ensure `knowledge/` profiled (P4 completed): `md_navigator.py profile-sections /path/to/knowledge`
2. Run refactor candidates: `md_navigator.py refactor-candidates /path/to/knowledge --top 10 --json > /tmp/proposals.json`
3. For each proposal:
   - Read affected_section + target_owner
   - Decide: actionable / not-actionable / partial
   - If actionable: actually replace by wikilink OR explicitly reject с обоснованием

**Acceptance**: ≥5 of 10 proposals user marks as actionable. If <5 → STOP, reshape signal weights в `owner_detector.py` (P5.2 composite).

**Output**: editorial session log written в `_ops/findings/2026-MM-DD-md-refactor-editorial-verification.md` или подобное.

## Verification (общая для P5)

- [ ] `originality.py`, `owner_detector.py`, `refactor_proposals.py` exist
- [ ] CLI `originality`, `refactor-candidates`, `query-by-type` working
- [ ] MCP `md_refactor_candidates`, `md_query_by_type` registered
- [ ] Smoke adds 2 new assertions (smoke 22+/22+)
- [ ] **Editorial session passed**: ≥5/10 proposals actionable on `knowledge/`
- [ ] Latency `md_refactor_candidates` on `knowledge/` < 30s
- [ ] Proposal output shape strict: all required keys present, `no_automation: true`

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Signal weights wrong, top-10 dominated by false positives | Editorial session — if <5 actionable, tune weights в owner_detector composite |
| Cosine threshold tuning takes iterations | Start with 0.30/0.55 defaults, adjust based on editorial feedback |
| `compute_originality_score` slow на каждый section | Batch precompute upfront: one matrix multiply for whole corpus, store as additional column in sections table (optional optimization) |
| Editorial session takes 3+ hours user time | Cap at top-5 first; if signal good, expand to top-10 |
| owner_detector finds same file as both candidate and source | Filter в find_nearest_neighbors (exclude_same_file already True by default) |

## Hand-off to P6

После P5 готов:
- All Tier 2 capabilities working
- Editorial verification proved signal > noise
- User can run real refactor sessions через MCP composite tools

P6 теперь может: write workflow recipes в SKILL.md, теперь когда capabilities проверены работающими.

## Anchors / Evidence

- High-level контракт: `task-001-md-tools-unified-backend.md`
- Adversarial review: proposal output shape strict (evidence/confidence/why), no automation
- P4 deliverable: section profile cache в sections table
- Existing embeddings: `experiments/md-embedding-server/scripts/navigator/embeddings.py` + sqlite-vec
- User's core pain: «информация дублируется вместо того чтобы быть вики-ссылкой на блок-владелец» — этот phase это решает
