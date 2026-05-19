from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


SEARCH_DEFAULT_EMBED_MODEL = os.environ.get(
    "MD_EMBEDDING_MODEL_ID", "openai/text-embedding-3-small"
)
SEARCH_DEFAULT_EMBEDDING_API_URL = os.environ.get(
    "MD_EMBEDDING_API_URL", "https://openrouter.ai/api/v1"
)
SEARCH_DEFAULT_EMBEDDING_TIMEOUT = float(os.environ.get("MD_EMBEDDING_TIMEOUT", "60"))
# Cloud APIs accept much larger batches than a local Metal allocator. OpenAI's
# embedding endpoint takes up to 2048 inputs per request; 32 is a comfortable
# middle for throughput vs HTTP latency.
SEARCH_EMBED_BATCH = int(os.environ.get("MD_EMBEDDING_BATCH", "32"))
# Transient-error retry. 5xx, connection-reset, and DNS hiccups recover with a
# short wait — without retry, every second large cold-index trips on the
# first network glitch and forces a manual restart.
SEARCH_RETRY_ATTEMPTS = int(os.environ.get("MD_EMBEDDING_RETRY", "3"))
SEARCH_RETRY_BACKOFF_S = float(os.environ.get("MD_EMBEDDING_RETRY_BACKOFF", "1.0"))


# --- Key resolution ------------------------------------------------------


def _read_key_file(path: Path) -> str | None:
    """Read a single-line key file. Whitespace-stripped. Empty → None."""
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return value or None


def _key_lookup_paths(corpus_root: Path | None = None) -> list[Path]:
    """All filesystem locations the key lookup walks, in priority order.

    Used both by `_resolve_api_key` for the actual lookup and by the
    missing-key error message so the user / agent sees exactly where we
    searched."""
    paths: list[Path] = []
    if corpus_root is not None:
        cr = corpus_root.resolve()
        # 1) corpus root itself (per-project key co-located with the docs).
        paths.append(cr / ".openrouter.key")
        # 2) walk upward from corpus root toward `/` so a parent repo can
        #    hold one shared key for all its sub-projects.
        for parent in cr.parents:
            paths.append(parent / ".openrouter.key")
    # 3) current working directory (compat path for shells where the corpus
    #    is invoked relatively).
    cwd = Path.cwd().resolve()
    cwd_path = cwd / ".openrouter.key"
    if cwd_path not in paths:
        paths.append(cwd_path)
    # 4) home directory — recommended default for cross-project use.
    paths.append(Path.home() / ".openrouter.key")
    # 5) XDG-style config dir (an alternate global location).
    xdg_root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    paths.append(xdg_root / "md-navigator" / "openrouter.key")
    # Deduplicate while preserving order.
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def _resolve_api_key(api_url: str, corpus_root: Path | None = None) -> str | None:
    """Resolve the bearer token. Order:

    1. `OPENROUTER_API_KEY` or `MD_EMBEDDING_API_KEY` env vars (highest
       priority — explicit, typical for shell-driven invocations).
    2. `<corpus_root>/.openrouter.key` and every parent directory upward.
    3. `<cwd>/.openrouter.key` (compat).
    4. `~/.openrouter.key` (cross-project default).
    5. `$XDG_CONFIG_HOME/md-navigator/openrouter.key`.

    Localhost URLs don't need auth — return None and skip the header."""
    if api_url.startswith("http://127.0.0.1") or api_url.startswith("http://localhost"):
        return None
    env_key = (
        os.environ.get("OPENROUTER_API_KEY")
        or os.environ.get("MD_EMBEDDING_API_KEY")
    )
    if env_key:
        return env_key
    for path in _key_lookup_paths(corpus_root):
        value = _read_key_file(path)
        if value:
            return value
    return None


def _format_missing_key_error(api_url: str, corpus_root: Path | None = None) -> str:
    """Diagnostic text printed when no key is found. Lists every location
    that was checked, plus a one-liner setup recipe."""
    lines = [
        f"No OpenRouter API key found for {api_url}.",
        "Checked, in order:",
        "  - $OPENROUTER_API_KEY env var: "
        + ("set" if os.environ.get("OPENROUTER_API_KEY") else "unset"),
        "  - $MD_EMBEDDING_API_KEY env var: "
        + ("set" if os.environ.get("MD_EMBEDDING_API_KEY") else "unset"),
    ]
    for path in _key_lookup_paths(corpus_root):
        marker = "found-but-empty" if path.exists() else "missing"
        lines.append(f"  - {path}: {marker}")
    lines.extend(
        [
            "",
            "Recommended fix (one-time, works across every project):",
            '  echo "sk-or-v1-..." > ~/.openrouter.key && chmod 600 ~/.openrouter.key',
            "",
            "Get a key at https://openrouter.ai/keys (free tier exists).",
        ]
    )
    return "\n".join(lines)


# --- Vector helpers ------------------------------------------------------


def _normalize_vectors(vectors: list[Any]) -> list[Any]:
    import numpy as np  # type: ignore

    normed = []
    for v in vectors:
        arr = np.asarray(v, dtype="float32")
        norm = float(np.linalg.norm(arr))
        if norm > 1e-12:
            arr = arr / norm
        normed.append(arr)
    return normed


def _vec_to_blob(vec) -> bytes:
    import numpy as np  # type: ignore

    return np.asarray(vec, dtype="float32").tobytes()


def _blob_to_vec(blob: bytes, dim: int):
    import numpy as np  # type: ignore

    return np.frombuffer(blob, dtype="float32").reshape(dim)


# --- HTTP client ---------------------------------------------------------


def _embeddings_url(api_url: str) -> str:
    base = api_url.rstrip("/")
    if base.endswith("/embeddings"):
        return base
    return f"{base}/embeddings"


def _embed_texts_http(
    model_name: str,
    texts: list[str],
    api_url: str,
    timeout: float,
    batch_size: int = SEARCH_EMBED_BATCH,
    corpus_root: Path | None = None,
) -> list[Any]:
    """POST /v1/embeddings (OpenAI-compatible) and return L2-normalized vectors.

    Splits the input list into chunks of `batch_size` per HTTP call. Default
    target is OpenRouter (`https://openrouter.ai/api/v1`) talking to
    `openai/text-embedding-3-small`; override with env vars or CLI flags
    for any other OpenAI-compatible endpoint.

    `corpus_root` (optional) extends the API key lookup to include
    `<corpus_root>/.openrouter.key` and parent directories — useful when
    one repo holds a shared key for all its sub-projects."""
    if not texts:
        return []

    from urllib import error, request

    url = _embeddings_url(api_url)
    headers = {"Content-Type": "application/json; charset=utf-8"}
    needs_auth = not (
        api_url.startswith("http://127.0.0.1") or api_url.startswith("http://localhost")
    )
    api_key = _resolve_api_key(api_url, corpus_root=corpus_root)
    if needs_auth and not api_key:
        raise RuntimeError(_format_missing_key_error(api_url, corpus_root=corpus_root))
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    # OpenRouter asks (politely) for these so usage shows up under a
    # recognisable referrer rather than "Unknown".
    if "openrouter.ai" in api_url:
        headers.setdefault("HTTP-Referer", "https://github.com/anthropics/claude-code")
        headers.setdefault("X-Title", "md-navigator")

    import sys
    import time

    all_vectors: list[Any] = []
    for start in range(0, len(texts), max(1, batch_size)):
        chunk = texts[start : start + max(1, batch_size)]
        payload = {"model": model_name, "input": chunk, "encoding_format": "float"}
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        # Retry loop: 5xx, connection reset, DNS / TLS hiccup get up to
        # SEARCH_RETRY_ATTEMPTS attempts with exponential backoff. 4xx
        # surfaces immediately — auth and bad-request errors don't get
        # better by retrying.
        last_exc: Exception | None = None
        raw: str | None = None
        for attempt in range(SEARCH_RETRY_ATTEMPTS):
            req = request.Request(url, data=body, headers=headers, method="POST")
            try:
                with request.urlopen(req, timeout=timeout) as response:
                    raw = response.read().decode("utf-8")
                break
            except error.HTTPError as exc:
                if exc.code < 500 or attempt == SEARCH_RETRY_ATTEMPTS - 1:
                    detail = exc.read().decode("utf-8", errors="replace")
                    raise RuntimeError(
                        f"Embedding API returned {exc.code}: {detail}"
                    ) from exc
                last_exc = exc
                wait = SEARCH_RETRY_BACKOFF_S * (2**attempt)
                print(
                    f"  embedding API {exc.code}, retry "
                    f"{attempt + 1}/{SEARCH_RETRY_ATTEMPTS} in {wait:.1f}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)
            except OSError as exc:
                if attempt == SEARCH_RETRY_ATTEMPTS - 1:
                    raise RuntimeError(
                        f"Embedding API unavailable at {url}: {exc}. "
                        f"Check OPENROUTER_API_KEY env var or `.openrouter.key` file."
                    ) from exc
                last_exc = exc
                wait = SEARCH_RETRY_BACKOFF_S * (2**attempt)
                print(
                    f"  network error ({exc}), retry "
                    f"{attempt + 1}/{SEARCH_RETRY_ATTEMPTS} in {wait:.1f}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)

        if raw is None:
            # Should not be reachable — retry loop raises on the final attempt.
            raise RuntimeError(
                f"Embedding API call exhausted retries: {last_exc}"
            )

        parsed = json.loads(raw)
        data = parsed.get("data")
        if not isinstance(data, list):
            raise RuntimeError("Embedding API response missing data list")
        ordered = sorted(data, key=lambda item: int(item.get("index", 0)))
        vectors = [item.get("embedding") for item in ordered]
        if len(vectors) != len(chunk) or any(v is None for v in vectors):
            raise RuntimeError("Embedding API returned incomplete embeddings")
        all_vectors.extend(vectors)
    return _normalize_vectors(all_vectors)
