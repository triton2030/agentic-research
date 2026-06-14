from __future__ import annotations

import re
from dataclasses import dataclass

from navigator.lemmatize import lemmatize_token
from navigator.markdown_io import HEADING_RE

MIN_CLAIM_LEN = 25
MAX_CLAIM_LEN = 500
MAX_CLAIMS = 20
MODALITY_LEMMAS = {
    "должный", "обязанный", "нельзя", "запрещённый", "запрещенный",
    "требоваться", "необходимо", "только", "всегда", "никогда",
    "считаться", "являться", "означать", "недопустимый", "единственный",
    "правило", "принцип", "must", "should", "always", "never", "only",
}
PROCESS_LEMMAS = {
    "аннулироваться", "попадать", "разбираться", "уходить",
}
PROCESS_CONTEXT_RE = re.compile(
    r"\b(?:заявк|заказ|спор|реестр|строк|финанс|оплат|платн|студи|"
    r"клиент|покупател|событи|принять)\w*",
    re.IGNORECASE | re.UNICODE,
)
RULEISH_HEADINGS = {
    "правило", "принцип", "политика", "граница", "границы", "инвариант",
    "критерий", "критерии", "требование", "требования", "условие",
    "условия", "запрещённый", "запрещенные", "запрещённые",
}
ABBREVIATIONS = ("т.д.", "т.п.", "т.к.", "др.", "см.", "стр.", "напр.", "e.g.", "i.e.")
TOKEN_RE = re.compile(r"\w+", re.UNICODE)
LIST_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)(.+)$")
BLOCKQUOTE_PREFIX_RE = re.compile(r"^\s*(?:>\s?)+")
CALLOUT_MARKER_RE = re.compile(r"^\[!([A-Za-z][\w-]*)\][-+]?\s*(.*)$")


@dataclass(frozen=True)
class Claim:
    text: str
    line: int
    heading_chain: str
    score: int
    signals: tuple[str, ...]


@dataclass(frozen=True)
class ClaimExtraction:
    claims: list[Claim]
    truncated: bool


def _strip_frontmatter(lines: list[str]) -> tuple[int, list[str]]:
    if not lines or lines[0].strip() != "---":
        return 0, lines
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return idx + 1, lines[idx + 1 :]
    return 0, lines


def _mask_abbreviations(text: str) -> tuple[str, dict[str, str]]:
    masks: dict[str, str] = {}
    out = text
    for idx, abbr in enumerate(ABBREVIATIONS):
        token = f"__ABBR_{idx}__"
        if abbr in out:
            masks[token] = abbr
            out = out.replace(abbr, token)
    for idx, match in enumerate(re.findall(r"`[^`]+`", out)):
        token = f"__BT_{idx}__"
        masks[token] = match
        out = out.replace(match, token)
    return out, masks


def _unmask(text: str, masks: dict[str, str]) -> str:
    out = text
    for token, value in masks.items():
        out = out.replace(token, value)
    return out


def _split_sentences(text: str) -> list[str]:
    masked, masks = _mask_abbreviations(text)
    parts = re.split(r"(?<=[.!?…])\s+(?=[А-ЯЁA-Z«\"\[\d])", masked)
    return [_unmask(part, masks).strip() for part in parts if part.strip()]


def _score(text: str, heading_chain: str) -> tuple[int, tuple[str, ...]]:
    score = 0
    signals: list[str] = []
    has_process_context = PROCESS_CONTEXT_RE.search(text) is not None
    for raw in TOKEN_RE.findall(text.lower()):
        lemma = lemmatize_token(raw)
        if lemma in MODALITY_LEMMAS or raw in MODALITY_LEMMAS:
            score += 1
            signals.append(lemma)
        elif has_process_context and (lemma in PROCESS_LEMMAS or raw in PROCESS_LEMMAS):
            score += 1
            signals.append(f"process:{lemma}")
    heading_lc = heading_chain.lower()
    for marker in RULEISH_HEADINGS:
        if marker in heading_lc:
            score += 1
            signals.append(f"heading:{marker}")
            break
    return score, tuple(sorted(set(signals)))


def _claim(text: str, line: int, heading_chain: str) -> Claim | None:
    cleaned = " ".join(text.strip().split())
    if len(cleaned) < MIN_CLAIM_LEN or len(cleaned) > MAX_CLAIM_LEN:
        return None
    score, signals = _score(cleaned, heading_chain)
    if score < 1:
        return None
    return Claim(text=cleaned, line=line, heading_chain=heading_chain, score=score, signals=signals)


def extract_claims(text: str, *, max_claims: int | None = None) -> ClaimExtraction:
    limit = int(max_claims or MAX_CLAIMS)
    lines = text.splitlines()
    offset, body_lines = _strip_frontmatter(lines)
    claims: list[Claim] = []
    heading_stack: list[tuple[int, str]] = []
    paragraph: list[str] = []
    paragraph_line = 0
    in_fence = False
    callout_heading = ""
    callout_prose: list[str] = []
    callout_prose_line = 0
    callout_fence = False

    def heading_chain() -> str:
        return " > ".join(title for _level, title in heading_stack)

    def callout_chain() -> str:
        base = heading_chain()
        if callout_heading:
            return f"{base} > {callout_heading}" if base else callout_heading
        return base

    def flush_paragraph() -> None:
        nonlocal paragraph, paragraph_line
        if not paragraph:
            return
        body = " ".join(paragraph)
        for sentence in _split_sentences(body):
            item = _claim(sentence, paragraph_line, heading_chain())
            if item is not None:
                claims.append(item)
        paragraph = []
        paragraph_line = 0

    def flush_callout_prose() -> None:
        nonlocal callout_prose, callout_prose_line
        if not callout_prose:
            return
        body = " ".join(callout_prose)
        for sentence in _split_sentences(body):
            item = _claim(sentence, callout_prose_line, callout_chain())
            if item is not None:
                claims.append(item)
        callout_prose = []
        callout_prose_line = 0

    for idx, raw in enumerate(body_lines, start=offset + 1):
        line = raw.rstrip()
        is_blockquote = bool(BLOCKQUOTE_PREFIX_RE.match(line))
        if not is_blockquote:
            flush_callout_prose()
            callout_heading = ""
            callout_fence = False
        if line.strip().startswith("```"):
            flush_paragraph()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not line.strip():
            flush_paragraph()
            continue
        heading = HEADING_RE.match(line)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            heading_stack = [(lvl, txt) for lvl, txt in heading_stack if lvl < level]
            heading_stack.append((level, title))
            continue
        if line.lstrip().startswith("|"):
            flush_paragraph()
            continue
        if is_blockquote:
            # Obsidian-callout / blockquote: strip the `>` prefixes, then
            # classify the inner line exactly as the main loop does (fence,
            # table, heading, list, prose). Without this the `>` lines fall into
            # `paragraph`, blob past MAX_CLAIM_LEN and get dropped. Inner prose
            # accumulates in `callout_prose` so a sentence wrapped across several
            # `>` lines stays one claim (mirrors the main loop's paragraph join).
            # An inner heading scopes following inner claims via `callout_heading`
            # without touching heading_stack. The `[!type] Title` marker line is
            # its own unit, like a heading label.
            # NOTE: like the main loop, a list item whose text wraps onto a
            # continuation line is not merged with that continuation; that is a
            # segmenter-wide limitation, not callout-specific.
            flush_paragraph()
            inner = BLOCKQUOTE_PREFIX_RE.sub("", line, count=1).strip()
            marker = CALLOUT_MARKER_RE.match(inner)
            if marker:
                flush_callout_prose()
                title = marker.group(2).strip()
                if title:
                    for sentence in _split_sentences(title):
                        item = _claim(sentence, idx, callout_chain())
                        if item is not None:
                            claims.append(item)
                continue
            if inner.startswith("```"):
                flush_callout_prose()
                callout_fence = not callout_fence
                continue
            if callout_fence:
                continue
            if not inner or inner.startswith("|"):
                flush_callout_prose()
                continue
            inner_heading = HEADING_RE.match(inner)
            if inner_heading:
                flush_callout_prose()
                callout_heading = inner_heading.group(2).strip()
                continue
            inner_listed = LIST_RE.match(inner)
            if inner_listed:
                flush_callout_prose()
                item = _claim(inner_listed.group(1), idx, callout_chain())
                if item is not None:
                    claims.append(item)
                continue
            if not callout_prose:
                callout_prose_line = idx
            callout_prose.append(inner)
            continue
        listed = LIST_RE.match(line)
        if listed:
            flush_paragraph()
            item = _claim(listed.group(1), idx, heading_chain())
            if item is not None:
                claims.append(item)
            continue
        if not paragraph:
            paragraph_line = idx
        paragraph.append(line)
    flush_paragraph()
    flush_callout_prose()
    truncated = len(claims) > limit
    return ClaimExtraction(claims=claims[:limit], truncated=truncated)


def split_into_claims(text: str) -> list[Claim]:
    return extract_claims(text).claims
