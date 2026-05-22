"""Cross-encoder rerank layer.

Why reranking matters for business docs: RRF over BM25 + dense gives a
strong baseline but is still bag-of-features fusion. A cross-encoder
processes (query, document) pairs jointly through a transformer trained
for relevance — typically lifting top-1 accuracy by 10-15% on retrieval
benchmarks. Industry standard for production RAG.

Default backend: OpenRouter's `/api/v1/rerank` proxy to Cohere
`rerank-v3.5` (multilingual, $0.001/search). Same OPENROUTER_API_KEY
that the embeddings layer already uses — no second account or key file
required. Any Cohere-compatible endpoint works (Cohere direct, Jina,
self-hosted): point `--rerank-api-url` and `--rerank-model` at it.

The reranker is *optional*: search without `--rerank` works exactly as
before. With `--rerank` enabled, the top-N (default 30) RRF candidates
are sent for cross-encoder scoring; the final ordering is by rerank
score, with original RRF score retained for diagnostics.

Key lookup is delegated to the shared `_resolve_api_key` in the
embeddings module: same OPENROUTER_API_KEY for both layers.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .embeddings import _resolve_api_key


DEFAULT_RERANK_API_URL = os.environ.get(
    "MD_RERANK_API_URL", "https://openrouter.ai/api/v1/rerank"
)
DEFAULT_RERANK_MODEL = os.environ.get(
    "MD_RERANK_MODEL", "cohere/rerank-v3.5"
)
DEFAULT_RERANK_TIMEOUT = float(os.environ.get("MD_RERANK_TIMEOUT", "30"))
DEFAULT_RERANK_TOP_N = int(os.environ.get("MD_RERANK_TOP_N", "30"))
DEFAULT_RERANK_DOC_CHARS = int(os.environ.get("MD_RERANK_DOC_CHARS", "2000"))


def _resolve_rerank_key(api_url: str, corpus_root: Path | None = None) -> str | None:
    """Locate the rerank API bearer.

    For OpenRouter endpoints we share the `OPENROUTER_API_KEY` resolver
    with the embeddings layer (env vars and `.openrouter.key` walk).

    For non-OpenRouter rerank endpoints (Cohere direct, Jina, etc.) we
    fall back to the explicit `MD_RERANK_API_KEY` env var or
    `~/.rerank.key` file. Localhost endpoints skip auth.
    """
    if api_url.startswith("http://127.0.0.1") or api_url.startswith("http://localhost"):
        return None

    # Default path: OpenRouter rerank — reuse the embeddings key resolver
    # so users don't have to maintain a second key.
    if "openrouter.ai" in api_url:
        return _resolve_api_key(api_url, corpus_root=corpus_root)

    # Non-OpenRouter endpoint: explicit env var first, then a sibling
    # `.rerank.key` file alongside the openrouter one.
    env_key = (
        os.environ.get("MD_RERANK_API_KEY")
        or os.environ.get("COHERE_API_KEY")
    )
    if env_key:
        return env_key

    candidates: list[Path] = []
    if corpus_root is not None:
        cr = corpus_root.resolve()
        candidates.append(cr / ".rerank.key")
        for parent in cr.parents:
            candidates.append(parent / ".rerank.key")
    candidates.append(Path.cwd() / ".rerank.key")
    candidates.append(Path.home() / ".rerank.key")

    seen: set[Path] = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        if not path.exists():
            continue
        try:
            value = path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if value:
            return value
    return None


def _missing_key_error(api_url: str) -> str:
    if "openrouter.ai" in api_url:
        return (
            f"Rerank requested but no OPENROUTER_API_KEY found for {api_url}.\n"
            "  Set OPENROUTER_API_KEY env var, or place `.openrouter.key` in "
            "the corpus root, cwd, or ~/.\n"
            "  (The same key the embeddings layer uses — one credential covers both.)"
        )
    return (
        f"Rerank requested but no API key found for {api_url}.\n"
        "  Set MD_RERANK_API_KEY env var, or drop `.rerank.key` in the corpus "
        "root, cwd, or ~/.\n"
        "  Or omit `--rerank` to run without reranking."
    )


def rerank_documents(
    query: str,
    documents: list[str],
    model: str = DEFAULT_RERANK_MODEL,
    api_url: str = DEFAULT_RERANK_API_URL,
    timeout: float = DEFAULT_RERANK_TIMEOUT,
    corpus_root: Path | None = None,
) -> list[tuple[int, float]]:
    """POST query + documents to a Cohere-compatible rerank endpoint.

    Returns `[(original_index, relevance_score), ...]` sorted by score
    descending. The original_index is the position of each document in
    the input list — so the caller can reorder its own results array.

    Empty `documents` returns `[]` without making an HTTP call.
    """
    if not documents:
        return []

    from urllib import error, request

    needs_auth = not (
        api_url.startswith("http://127.0.0.1") or api_url.startswith("http://localhost")
    )
    api_key = _resolve_rerank_key(api_url, corpus_root=corpus_root)
    if needs_auth and not api_key:
        raise RuntimeError(_missing_key_error(api_url))

    headers = {"Content-Type": "application/json; charset=utf-8"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "query": query,
        "documents": documents,
        "top_n": len(documents),
        "return_documents": False,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = request.Request(api_url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Rerank API returned {exc.code}: {detail}") from exc
    except OSError as exc:
        raise RuntimeError(
            f"Rerank API unavailable at {api_url}: {exc}. Check key and network."
        ) from exc

    parsed = json.loads(raw)
    results: list[dict[str, Any]] = parsed.get("results") or []
    # Cohere returns `[{"index": int, "relevance_score": float}, ...]`,
    # already sorted descending by score.
    return [(int(r["index"]), float(r["relevance_score"])) for r in results]


def doc_text_for_rerank(
    relative_path: str,
    heading_chain: str,
    body: str,
    max_chars: int = DEFAULT_RERANK_DOC_CHARS,
) -> str:
    """Compose a compact document representation for the reranker.

    Cross-encoders work better with the structural prefix (heading chain
    + path hint) ahead of the body — same idea as contextual retrieval
    for embeddings. Truncate to `max_chars` because rerank latency
    scales linearly with document length and cross-encoder token
    budgets are tight (~512 typical)."""
    head = heading_chain or relative_path
    text = f"{head}\n\n{body}".strip()
    if len(text) > max_chars:
        text = text[:max_chars]
    return text
