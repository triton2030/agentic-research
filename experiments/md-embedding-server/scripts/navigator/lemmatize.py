"""Russian morphology lemmatization for BM25 channel.

Default FTS5 tokenizer `unicode61` normalizes case and diacritics but does
not stem. On Russian queries this means `критериев` does not match
`критерии` (the stem is the same; only suffix differs). We pre-lemmatize
both stored text and query tokens so BM25 finds them via the same
normal form.

English / numeric / non-Cyrillic tokens pass through unchanged.

`pymorphy3` is the recommended dependency. If it fails to import, we
fall back to identity — the index is still usable, just unstemmed.
"""

from __future__ import annotations

import re
import sys
import threading
from typing import Any

_LOCK = threading.Lock()
_MORPH: Any = None
_INITIALIZED = False
_AVAILABLE = False
_CYRILLIC = re.compile(r"[а-яёА-ЯЁ]")
_WORD = re.compile(r"\w+", re.UNICODE)


def _morph() -> Any:
    """Lazy-init the pymorphy3 analyzer. Threadsafe. Idempotent on import
    failure (records unavailable, never re-tries)."""
    global _MORPH, _INITIALIZED, _AVAILABLE
    if _INITIALIZED:
        return _MORPH
    with _LOCK:
        if _INITIALIZED:
            return _MORPH
        try:
            import pymorphy3  # type: ignore

            _MORPH = pymorphy3.MorphAnalyzer()
            _AVAILABLE = True
        except Exception as exc:
            print(
                f"md_navigator: pymorphy3 unavailable ({exc}); BM25 stays "
                "unstemmed. Russian queries will rely on dense channel only.",
                file=sys.stderr,
            )
            _MORPH = None
            _AVAILABLE = False
        _INITIALIZED = True
    return _MORPH


def available() -> bool:
    _morph()
    return _AVAILABLE


def lemmatize_token(token: str) -> str:
    """Return the normal form of one token. Pass through if non-Russian or
    pymorphy3 unavailable."""
    if not token or not _CYRILLIC.search(token):
        return token
    morph = _morph()
    if morph is None:
        return token
    parsed = morph.parse(token)
    if parsed:
        return parsed[0].normal_form
    return token


def lemmatize_text(text: str) -> str:
    """Walk word-tokens in `text`; lemmatize Russian ones, keep everything
    else (English, numbers, punctuation, separators) intact."""
    if not text:
        return text
    morph = _morph()
    if morph is None:
        return text
    out: list[str] = []
    pos = 0
    for m in _WORD.finditer(text):
        if m.start() > pos:
            out.append(text[pos : m.start()])
        token = m.group(0)
        if _CYRILLIC.search(token):
            parsed = morph.parse(token)
            out.append(parsed[0].normal_form if parsed else token)
        else:
            out.append(token)
        pos = m.end()
    if pos < len(text):
        out.append(text[pos:])
    return "".join(out)
