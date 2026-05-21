# Phase 4 — Section profile foundation

**Estimated cost**: ~1.5-2 дня
**Depends on**: P1 (foundation refactor) — но **не** P2/P3 (parallel-safe)
**Unblocks**: P5

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md`.

## Цель

Создать **section profile** layer — для каждой section в corpus вычислять и кэшировать богатый metadata: `type`, `subject`, `owns_terms`, `mentions`, `evidence_sources`, `confidence`. Это **foundation для Tier 2 active suggestions** (P5): без profile невозможно различать «definition vs uses», «owner vs user of concept», «orphan definition vs missing owner».

Подход: **LLM-prompt classifier** через OpenRouter (тот же endpoint что embeddings, единый API key). Cache в существующей `sections` table в `<corpus>/.md-navigator/index.sqlite`. Invalidation rules: `mtime` change → re-profile; `model_id` change → re-profile; `prompt_version` bump → re-profile.

## In scope

- New module `navigator/section_profile.py` — classifier + cache management
- Schema extension `sections` table: additive nullable columns
- Integrate profile computation в `index_build.py` — batch при index run
- New CLI subcommand `profile-sections` для standalone re-profile
- Internal MCP tool `md_classify_section` — НЕ exposed через `listTools` (используется только composite в P5)
- Cost spike: один full corpus profile на `knowledge/` (~300 sections), measure cost + accuracy

## NOT in scope

- Tier 2 active capabilities (`md_originality`, `md_owner_candidates`, `md_refactor_candidates`) — P5
- Section profile derived metrics (uniqueness, owner detection) — P5
- Workflow recipes / SKILL.md updates — P6

## Definition of done

- `sections` table расширена columns: `profile_type`, `profile_subject`, `profile_owns_terms`, `profile_mentions`, `profile_evidence`, `profile_confidence`, `profile_version`, `profile_model`, `profile_classified_at`
- Schema migration: existing index opens без data loss, new columns NULL by default
- `navigator/section_profile.py` exports:
  - `PROFILE_VERSION = "1.0.0"` (bump when prompt or schema changes)
  - `classify_section(text: str, model: str, client) → profile_dict | None`
  - `profile_corpus(corpus_root, batch_size=50, force=False) → stats_dict`
  - `get_profile(corpus_root, section_id) → profile_dict | None`
- CLI: `md_navigator.py profile-sections <corpus> [--batch-size N] [--force]` работает
- При `md_navigator.py index <corpus>` новые sections **автоматически** профилятся (lazy, в существующем batch)
- Cache invalidation: mtime change → re-profile только дельты; model_id change → re-profile все; version bump → re-profile все
- Full run на `knowledge/` (~300 sections) показывает: cost < $0.50, latency reasonable (<5min)
- Manual review 20 random profiles: type assignment > 80% intuitively correct
- MCP `md_classify_section` зарегистрирован НО НЕ в `listTools` (internal — see implementation)

## Stop rules

- LLM profile cost > $0.50 для `knowledge/` corpus → stop, переоценить prompt size / model
- Manual review accuracy < 70% — prompt rework перед continuing к P5
- Schema migration ломает existing index — rollback, исследовать

## Подшаги

### P4.1 — Section profile schema design (30 минут)

**Profile shape** (JSON):

```python
{
    "type": "definition",            # one of: definition | decision | open-question | rule | example | uses | external-citation | heading-only
    "subject": "Anchor-aware extraction for Markdown wikilinks",  # ≤100 chars
    "owns_terms": ["anchor-aware extraction"],   # max 5 terms this section defines
    "mentions": ["wikilink", "section heading"],  # max 10 terms used but not defined
    "evidence_sources": [],                       # max 5 external/cited refs (URLs, file paths)
    "confidence": 0.85                            # 0.0-1.0 classifier confidence
}
```

**Type taxonomy** (8 values):

- `definition` — explicitly defines a term ("X is...", "X means...", "An X is...")
- `decision` — documents a choice ("We chose X because...", "Decision: X")
- `open-question` — poses unresolved question ("TODO:", "Open question:", "?")
- `rule` — actionable rule ("Always do X", "Never do Y", "Must X")
- `example` — usage of something defined elsewhere ("E.g.", "Example:")
- `uses` — references concepts without defining ("Following the X principle...")
- `external-citation` — cites external source primarily
- `heading-only` — section с no substantive body (just heading)

**Schema migration** (additive, nullable):

```sql
ALTER TABLE sections ADD COLUMN profile_type TEXT;
ALTER TABLE sections ADD COLUMN profile_subject TEXT;
ALTER TABLE sections ADD COLUMN profile_owns_terms TEXT;  -- JSON array
ALTER TABLE sections ADD COLUMN profile_mentions TEXT;     -- JSON array
ALTER TABLE sections ADD COLUMN profile_evidence TEXT;     -- JSON array
ALTER TABLE sections ADD COLUMN profile_confidence REAL;
ALTER TABLE sections ADD COLUMN profile_version TEXT;       -- "1.0.0"
ALTER TABLE sections ADD COLUMN profile_model TEXT;          -- e.g. "anthropic/claude-haiku-4.5"
ALTER TABLE sections ADD COLUMN profile_classified_at TEXT;  -- ISO timestamp
```

**Файл**: `experiments/md-embedding-server/scripts/navigator/index_meta.py`

```python
def migrate_to_profile_schema(conn):
    """Additive schema migration for section profile columns.
    Safe to call multiple times — uses IF NOT EXISTS via try/except."""
    cursor = conn.cursor()
    columns = [
        ("profile_type", "TEXT"),
        ("profile_subject", "TEXT"),
        ("profile_owns_terms", "TEXT"),
        ("profile_mentions", "TEXT"),
        ("profile_evidence", "TEXT"),
        ("profile_confidence", "REAL"),
        ("profile_version", "TEXT"),
        ("profile_model", "TEXT"),
        ("profile_classified_at", "TEXT"),
    ]
    for col_name, col_type in columns:
        try:
            cursor.execute(f"ALTER TABLE sections ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError as e:
            # Column already exists — fine
            if "duplicate column" not in str(e).lower():
                raise
    conn.commit()
```

Вызвать в `open_or_create_index()` после существующего schema setup.

### P4.2 — Create section_profile.py (3-4 часа)

**Файл**: `experiments/md-embedding-server/scripts/navigator/section_profile.py`

**Implementation**:

```python
"""Section profile classifier via LLM-prompt.

Each section gets a richer metadata than just embedding — type / subject /
owns_terms / mentions — used downstream by md_originality, md_owner_candidates,
md_refactor_candidates (P5).

Cache lives in sections table; invalidation by mtime, model, prompt version.
"""

from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .embeddings import OpenRouterClient  # re-use existing client

PROFILE_VERSION = "1.0.0"
DEFAULT_PROFILE_MODEL = "anthropic/claude-haiku-4.5"  # cheap + capable; configurable

VALID_TYPES = {
    "definition", "decision", "open-question", "rule",
    "example", "uses", "external-citation", "heading-only"
}

CLASSIFICATION_PROMPT = """You are a section profile classifier for a Markdown knowledge corpus.

Given the section text below, return a JSON object with:
- type: one of [definition, decision, open-question, rule, example, uses, external-citation, heading-only]
- subject: one-sentence topic (≤100 chars)
- owns_terms: array of terms this section *defines* (max 5; lowercase; deduplicated)
- mentions: array of terms used but not defined here (max 10; lowercase; deduplicated)
- evidence_sources: array of external citations or refs (max 5; URLs, file paths, or named sources)
- confidence: 0.0-1.0 your own confidence in this profile

Decision rules:
- definition: explicitly defines a term ("X is...", "X means...", "An X is...")
- decision: documents a choice or commitment ("We chose X because...", "Decision: X", "Stopped Y in favor of Z")
- open-question: poses unresolved question or TODO ("TODO:", "Open question:", "?", "Unresolved:")
- rule: actionable rule or prescription ("Always do X", "Never do Y", "Must X", "Should not Y")
- example: usage demonstration of concept defined elsewhere ("E.g.:", "Example:", "Sample:")
- uses: references concepts as input/given, doesn't define ("Following X principle...", "Per the X contract...")
- external-citation: primarily cites external source (URL, paper, library)
- heading-only: section with no substantive body (just heading text or 1-2 boilerplate lines)

Be conservative: when unsure between definition and uses, choose uses (definition requires explicit "is/means" statement).

Output JSON only, no surrounding text.

Section heading: "{heading}"
Section text:
{body}
"""


def classify_section(
    heading: str,
    body: str,
    client: OpenRouterClient,
    model: str = DEFAULT_PROFILE_MODEL,
) -> dict[str, Any] | None:
    """Classify one section via LLM. Returns profile dict or None on failure."""
    prompt = CLASSIFICATION_PROMPT.format(
        heading=heading[:200],
        body=body[:3000],  # cap input
    )
    try:
        response = client.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.0,
        )
        raw = response.strip()
        # Strip code fence if present
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:-1]) if raw.endswith("```") else raw.strip("`")
        profile = json.loads(raw)
        # Validate
        if profile.get("type") not in VALID_TYPES:
            return None
        # Normalize
        profile["owns_terms"] = [t.lower().strip() for t in (profile.get("owns_terms") or [])][:5]
        profile["mentions"] = [t.lower().strip() for t in (profile.get("mentions") or [])][:10]
        profile["evidence_sources"] = (profile.get("evidence_sources") or [])[:5]
        profile["subject"] = (profile.get("subject") or "")[:100]
        profile["confidence"] = max(0.0, min(1.0, float(profile.get("confidence", 0.5))))
        return profile
    except Exception as exc:
        # Return None — caller decides whether to retry
        return None


def needs_reclassification(
    row: dict[str, Any],
    file_mtime: float,
    current_model: str,
    current_version: str = PROFILE_VERSION,
    force: bool = False,
) -> bool:
    """Check if a section row needs re-profiling.

    Invalidation triggers:
    - force flag set
    - no existing profile
    - profile_version mismatch
    - profile_model mismatch
    - file mtime > profile_classified_at
    """
    if force:
        return True
    if not row.get("profile_type"):
        return True
    if row.get("profile_version") != current_version:
        return True
    if row.get("profile_model") != current_model:
        return True
    classified_at_str = row.get("profile_classified_at")
    if not classified_at_str:
        return True
    try:
        classified_dt = datetime.fromisoformat(classified_at_str.replace("Z", "+00:00"))
        classified_ts = classified_dt.timestamp()
        return file_mtime > classified_ts
    except (ValueError, AttributeError):
        return True


def profile_corpus(
    corpus_root: Path,
    batch_size: int = 50,
    force: bool = False,
    model: str = DEFAULT_PROFILE_MODEL,
    verbose: bool = True,
) -> dict[str, Any]:
    """Profile sections in corpus, respecting cache.

    Returns stats dict: { profiled: int, skipped_cached: int, failed: int, cost_estimate_usd: float }
    """
    from .index_meta import open_or_create_index
    conn = open_or_create_index(corpus_root)
    cursor = conn.cursor()

    # Fetch sections with current profile state
    cursor.execute("""
        SELECT s.rowid, s.relative_path, s.heading_chain, s.heading_text, s.body_text,
               s.profile_type, s.profile_version, s.profile_model, s.profile_classified_at
        FROM sections s
        WHERE s.scope = 'sections'
    """)
    rows = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    client = OpenRouterClient()
    profiled = 0
    skipped = 0
    failed = 0
    cost_estimate = 0.0
    now_iso = datetime.now(timezone.utc).isoformat()

    for i, row in enumerate(rows):
        file_path = corpus_root / row["relative_path"]
        try:
            file_mtime = file_path.stat().st_mtime
        except OSError:
            file_mtime = 0

        if not needs_reclassification(row, file_mtime, model, PROFILE_VERSION, force):
            skipped += 1
            continue

        heading = row.get("heading_text") or row.get("heading_chain") or ""
        body = row.get("body_text") or ""
        profile = classify_section(heading, body, client, model=model)
        if profile is None:
            failed += 1
            continue

        cursor.execute("""
            UPDATE sections
            SET profile_type = ?,
                profile_subject = ?,
                profile_owns_terms = ?,
                profile_mentions = ?,
                profile_evidence = ?,
                profile_confidence = ?,
                profile_version = ?,
                profile_model = ?,
                profile_classified_at = ?
            WHERE rowid = ?
        """, (
            profile["type"],
            profile["subject"],
            json.dumps(profile["owns_terms"], ensure_ascii=False),
            json.dumps(profile["mentions"], ensure_ascii=False),
            json.dumps(profile["evidence_sources"], ensure_ascii=False),
            profile["confidence"],
            PROFILE_VERSION,
            model,
            now_iso,
            row["rowid"],
        ))
        profiled += 1
        # Rough cost estimate: ~500 input tokens + 256 output tokens via Haiku 4.5 ≈ $0.001
        cost_estimate += 0.001

        if verbose and (i + 1) % batch_size == 0:
            print(f"  [{i+1}/{len(rows)}] profiled={profiled} skipped={skipped} failed={failed}")

    conn.commit()
    conn.close()

    return {
        "total_sections": len(rows),
        "profiled": profiled,
        "skipped_cached": skipped,
        "failed": failed,
        "cost_estimate_usd": round(cost_estimate, 4),
        "model": model,
        "version": PROFILE_VERSION,
    }


def get_profile(corpus_root: Path, section_id: int) -> dict[str, Any] | None:
    """Read one section profile from cache."""
    from .index_meta import open_or_create_index
    conn = open_or_create_index(corpus_root)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT profile_type, profile_subject, profile_owns_terms, profile_mentions,
               profile_evidence, profile_confidence, profile_version, profile_model,
               profile_classified_at
        FROM sections WHERE rowid = ?
    """, (section_id,))
    row = cursor.fetchone()
    conn.close()
    if not row or row[0] is None:
        return None
    return {
        "type": row[0],
        "subject": row[1],
        "owns_terms": json.loads(row[2]) if row[2] else [],
        "mentions": json.loads(row[3]) if row[3] else [],
        "evidence_sources": json.loads(row[4]) if row[4] else [],
        "confidence": row[5],
        "version": row[6],
        "model": row[7],
        "classified_at": row[8],
    }
```

**Зависимости**:

- `OpenRouterClient.completion()` — может потребовать добавить в `embeddings.py` если ещё не существует. Если только embeddings sup, добавить:
  ```python
  def completion(self, model, messages, max_tokens=512, temperature=0.0) -> str:
      """Chat completion call via OpenRouter."""
      # ... POST to /chat/completions, return response["choices"][0]["message"]["content"]
  ```

### P4.3 — CLI subcommand profile-sections (30 минут)

**Файл**: `experiments/md-embedding-server/scripts/navigator/cli.py`

```python
ps = sub.add_parser(
    "profile-sections",
    help="Classify sections by type / subject / owns_terms via LLM. Cached in sections table.",
)
ps.add_argument("path", help="Corpus root.")
ps.add_argument("--batch-size", type=int, default=50, help="Progress reporting interval.")
ps.add_argument("--force", action="store_true", help="Re-profile all sections even if cached.")
ps.add_argument("--model", default=None, help=f"Classifier model (default: {DEFAULT_PROFILE_MODEL}).")
ps.add_argument("--json", action="store_true", help="Print JSON stats.")
```

Dispatch:
```python
if args.command == "profile-sections":
    from .section_profile import profile_corpus, DEFAULT_PROFILE_MODEL
    stats = profile_corpus(
        Path(args.path),
        batch_size=args.batch_size,
        force=args.force,
        model=args.model or DEFAULT_PROFILE_MODEL,
        verbose=not args.json,
    )
    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print(f"\nProfiled: {stats['profiled']}, skipped (cache): {stats['skipped_cached']}, failed: {stats['failed']}")
        print(f"Cost estimate: ${stats['cost_estimate_usd']}")
    return 0
```

### P4.4 — Integrate в index_build (1 час)

**Файл**: `experiments/md-embedding-server/scripts/navigator/index_build.py`

При `index` command, после indexing новых sections, **lazy** профилить их:

```python
# В функции build_index или подобной, после section indexing complete:
if getattr(args, "with_profile", True):  # default ON, opt-out с --no-profile
    from .section_profile import profile_corpus
    stats = profile_corpus(corpus_root, batch_size=50, force=False, verbose=verbose)
    if verbose:
        print(f"[profile] +{stats['profiled']} sections (cached {stats['skipped_cached']})")
```

CLI flag в register_index:
```python
p.add_argument(
    "--no-profile",
    action="store_true",
    help="Skip section profile classification during indexing (cheaper).",
)
```

### P4.5 — MCP internal tool md_classify_section (30 минут)

**Файл**: `experiments/md-embedding-server/mcp/src/tools/navigator-tools.js`

```js
// INTERNAL — registered in MCP but NOT listed in listTools.
// Used by composite md_refactor_candidates and md_query_by_type in P5.
// To hide from listTools, we can either:
//   (a) register normally and hope agent doesn't see it (still visible — not real hiding)
//   (b) skip registration entirely; expose only via internal Node-side helpers
//
// Recommended: (b) — define as exported helper function, NOT registered as MCP tool.

export async function classifySection(path, headingId) {
  // Wrap CLI: navigator.py classify-section <path> <heading-id> ... 
  // OR: read profile from cache directly (db query)
  // Implementation: query sections table by (relative_path, heading_id), return profile_*
  // TODO during P4 implementation: decide query vs subprocess
}
```

For now: keep classify-section **CLI-only** (`md_navigator.py classify-section <corpus> <section-id>` returns JSON profile). Compose tools in P5 will subprocess this.

### P4.6 — Spike: full corpus profile run (1-2 часа)

```bash
# Index знание (ensure index up-to-date)
md_navigator.py index /Users/triton/Documents/GitHub/agentic-research/knowledge

# Then profile
md_navigator.py profile-sections /Users/triton/Documents/GitHub/agentic-research/knowledge --json > /tmp/profile-stats.json
cat /tmp/profile-stats.json
```

**Expected output**:
```json
{
  "total_sections": 300,
  "profiled": 300,
  "skipped_cached": 0,
  "failed": 0-5,
  "cost_estimate_usd": 0.30,
  "model": "anthropic/claude-haiku-4.5",
  "version": "1.0.0"
}
```

**If cost > $0.50**: STOP, переоценить prompt size или сменить model на cheaper (e.g. `meta-llama/llama-3.1-8b-instruct`).

**Manual accuracy review**: 20 random sections — check type assignment intuitively:
```bash
# Fetch 20 random profiles
sqlite3 /Users/triton/Documents/GitHub/agentic-research/knowledge/.md-navigator/index.sqlite \
  "SELECT relative_path, heading_text, profile_type, profile_subject FROM sections WHERE profile_type IS NOT NULL ORDER BY RANDOM() LIMIT 20"
```

Каждую review manually: is type assignment intuitive? Threshold: >80% correct.

**Cache invalidation test**:
```bash
# Re-run profile-sections — should skip all (0 LLM calls)
md_navigator.py profile-sections /path/to/knowledge --json | jq '.skipped_cached'
# Expected: 300 (all)

# Touch one file's mtime
touch /path/to/knowledge/agents/evaluation.md
md_navigator.py profile-sections /path/to/knowledge --json | jq '{profiled, skipped_cached}'
# Expected: profiled=N (sections in evaluation.md), skipped_cached=remainder
```

## Verification (общая для P4)

- [ ] Schema migration ran на existing index без errors
- [ ] `section_profile.py` exists с public API
- [ ] CLI `md_navigator.py profile-sections <corpus> --json` работает
- [ ] CLI `md_navigator.py index <corpus>` теперь auto-profiles новые sections
- [ ] Full corpus profile run на `knowledge/`: cost < $0.50, < 5 min
- [ ] Manual 20-sample review: type accuracy > 80%
- [ ] Cache invalidation test: re-run без changes → 0 LLM calls; touch one file → only those sections re-profile
- [ ] `get_profile(corpus, section_id)` returns valid profile

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| OpenRouter completion API не работает identically embeddings endpoint | Test client.completion() сначала на 1 call, потом батч |
| LLM возвращает invalid JSON (trailing commas, code fences) | `classify_section` strips fences, json.loads с try/except → return None on fail |
| Cost эскалирует на больших корпусах | Cap input body to 3000 chars, output max_tokens 512. Could swap model |
| Manual accuracy < 80% | Iterate prompt: add more decision rules, examples, edge cases |
| Cache invalidation has race condition (concurrent index runs) | sqlite WAL mode (existing); sequential profile run (no parallelism) |
| Profile column data not preserved при reindex | Reindex preserves sections table — verify in code |

## Hand-off to P5

После P4 готов:
- Every section in corpus имеет `{ type, subject, owns_terms, mentions, evidence, confidence }` cached
- Cache invalidation работает (mtime / model / version)
- LLM cost manageable ($0.30-$0.50 per full corpus)
- Profile data доступна через SQL queries для P5

P5 теперь может: implement `md_originality` (cosine distance via existing embeddings), `md_owner_candidates` (composite signal incl. profile.type=="definition"), `md_refactor_candidates` composite (uses originality + owner_candidates).

## Anchors / Evidence

- High-level контракт: `task-001-md-tools-unified-backend.md`
- Adversarial review insight: `section_profile` > flat `section_classifier` — richer foundation, integrated 2026-05-21
- Existing OpenRouter client: `experiments/md-embedding-server/scripts/navigator/embeddings.py`
- Existing sections table schema: `experiments/md-embedding-server/scripts/navigator/index_meta.py`
- 2026 NLP research: structured prompting with decision rules outperforms embedding-based and rule-based для open-domain classification
