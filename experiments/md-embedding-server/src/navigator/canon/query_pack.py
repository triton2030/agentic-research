from __future__ import annotations

import re

from navigator.lemmatize import available as _lemmatizer_available
from navigator.lemmatize import lemmatize_token

RU_STOPWORDS = {
    "а", "без", "бы", "был", "была", "были", "было", "в", "во", "вот",
    "все", "для", "до", "его", "ее", "если", "есть", "ещё", "же", "за",
    "и", "или", "из", "к", "как", "ко", "когда", "ли", "на", "над", "не",
    "нет", "но", "о", "об", "от", "по", "под", "при", "про", "с", "со",
    "так", "также", "то", "только", "у", "уже", "что", "это", "этот",
    "эта", "эти", "the", "a", "an", "and", "or", "to", "of", "in", "for",
}
CONTENT_POS = {"NOUN", "ADJF", "VERB", "INFN"}
TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9_-]{2,}", re.UNICODE)
_MORPH = None
_MORPH_READY = False


def _normalize_query(text: str) -> str:
    return " ".join(text.lower().split())


def morphology_available() -> bool:
    return _lemmatizer_available()


def _morph_parse(token: str):
    global _MORPH, _MORPH_READY
    if not _MORPH_READY:
        try:
            import pymorphy3  # type: ignore
        except Exception:
            _MORPH = None
        else:
            _MORPH = pymorphy3.MorphAnalyzer()
        _MORPH_READY = True
    if _MORPH is None:
        return None
    try:
        parsed = _MORPH.parse(token)
    except Exception:
        return None
    return parsed[0] if parsed else None


def content_words(text: str) -> str:
    words: list[str] = []
    for raw in TOKEN_RE.findall(text):
        token = raw.lower()
        if token in RU_STOPWORDS:
            continue
        parsed = _morph_parse(token) if re.search(r"[а-яё]", token) else None
        if parsed is not None:
            if parsed.tag.POS not in CONTENT_POS:
                continue
            token = parsed.normal_form
        else:
            token = lemmatize_token(token)
        if token and token not in RU_STOPWORDS:
            words.append(token)
    return " ".join(words)


def extract_terms(text: str, heading_chain: str = "") -> str:
    backticked = re.findall(r"`([^`]{2,80})`", text)
    latin_caps = re.findall(r"\b[A-Z][A-Za-z0-9_-]{2,}\b", text)
    cyrillic_phrases = re.findall(r"\b[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁа-яё][а-яё]+){0,2}\b", text)
    heading_terms = [part.strip() for part in re.split(r"[>#/|]", heading_chain or "") if part.strip()]
    seen: set[str] = set()
    out: list[str] = []
    for raw in [*backticked, *latin_caps, *cyrillic_phrases, *heading_terms]:
        term = raw.strip()
        key = term.lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(term)
    return " ".join(out)


def build_query_pack(claim_text: str, heading_chain: str = "") -> list[str]:
    raw = " ".join((claim_text or "").split())
    p2 = content_words(raw)
    p3 = extract_terms(raw, heading_chain)
    projections = [
        raw,
        p2,
        p3,
        f"правило: {p2}" if p2 else "",
    ]
    seen: set[str] = set()
    out: list[str] = []
    for query in projections:
        cleaned = " ".join(query.split())
        key = _normalize_query(cleaned)
        if not cleaned or key in seen:
            continue
        seen.add(key)
        out.append(cleaned)
    return out
