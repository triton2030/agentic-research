#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = [
#   "fastembed==0.8.0",
# ]
# ///
"""Lossless inventory and bounded retrieval for `_ops/chat-recall`.

Every Markdown star block is a record. Broken metadata becomes diagnostics and
sentinels; it never makes the block disappear.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import sqlite3
import struct
import sys
from collections import Counter, defaultdict
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import Any

from recall_metadata import REPAIR_TOPIC, REPAIR_TYPE, TOPICS, TYPES

KINDS = {"quote", "selection", "note", "raw"}
PRECISIONS = {"exact", "minute", "date", "unknown"}
META_KEY = r"kind|type|topic|source|precision|source-ref|context-note"
ENTRY_RE = re.compile(
    r"^\*\s+(?P<timestamp>.+?)\s+—\s+"
    r'(?P<text>".*?"|.*?)\s+—\s+(?P<meta>(?:' + META_KEY + r'):.*)$',
    re.DOTALL,
)
META_RE = re.compile(
    r"(?:^|\s*\|\s*)(" + META_KEY + r"):\s*"
    r"([^|\n]*?)(?=\s*\|\s*(?:" + META_KEY + r"):|$)",
    re.MULTILINE,
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?$")
QUERY_TOKEN_RE = re.compile(r"[\w-]+\*?", re.UNICODE)

FASTEMBED_VERSION = "0.8.0"
EMBEDDING_MODEL = "Xenova/multilingual-e5-large"
EMBEDDING_REVISION = "00fc3aeb3dbb95842de2ac1961d33c6319acf57b"
EMBEDDING_DIMENSION = 1024
EMBEDDING_MODEL_FILE = "onnx/model_quantized.onnx"
EMBEDDING_BATCH_SIZE = 32
# Калибровка порогов поддержки: 20 закреплённых кейсов против 15 запросов вне
# корпуса, 940 записей, Xenova/multilingual-e5-large int8, 2026-08-20.
# >= 0.82 — 18/20 по делу и 0/15 вне корпуса; < 0.805 — 0/20 по делу и 13/15
# вне корпуса. Пороги привязаны к EMBEDDING_PROFILE: смена модели требует
# повторной калибровки (tests/evaluate_support.py).
SUPPORT_STRONG = 0.82
SUPPORT_WEAK = 0.805
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "
HYBRID_DEPTH = 40
RRF_CONSTANT = 60
SESSION_ROUTE_LIMIT = 5
CONTEXT_RESCUE_LIMIT = 2
FILE_SUPPORT_WEIGHT = 0.1
DEFAULT_MAX_CHARS = 8000
EMBEDDING_PROFILE = (
    "chat-recall-v1|fastembed=" + FASTEMBED_VERSION
    + "|model=" + EMBEDDING_MODEL
    + "|revision=" + EMBEDDING_REVISION
    + "|pooling=mean|normalization=true|query-prefix=query:|passage-prefix=passage:"
)
_EMBEDDING_BACKENDS: dict[tuple[bool, str], Any] = {}


class CliError(RuntimeError):
    """Short, expected command-line failure."""


def _frontmatter(lines: list[str]) -> dict[str, str]:
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ": " in line and not line.startswith((" ", "\t")):
            key, value = line.split(": ", 1)
            scalar = value.strip()
            if scalar.startswith('"'):
                try:
                    decoded = json.loads(scalar)
                except json.JSONDecodeError:
                    decoded = scalar.strip('"')
                scalar = decoded if isinstance(decoded, str) else scalar
            result[key.strip()] = scalar
    return result


def _star_blocks(lines: list[str]) -> list[tuple[int, str]]:
    starts = [index for index, line in enumerate(lines) if line.startswith("* ")]
    blocks: list[tuple[int, str]] = []
    for number, start in enumerate(starts):
        end = starts[number + 1] if number + 1 < len(starts) else len(lines)
        raw_lines = lines[start:end]
        while raw_lines and not raw_lines[-1].strip():
            raw_lines.pop()
        while raw_lines and raw_lines[-1].startswith("#"):
            raw_lines.pop()
        blocks.append((start + 1, "\n".join(raw_lines).strip()))
    return blocks


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _record_id(session: str, kind: str, text: str) -> str:
    payload = "\0".join((session, kind, _normalized_text(text))).encode("utf-8")
    return "cr-" + hashlib.sha256(payload).hexdigest()[:16]


def _timestamp(
    raw: str, file_date: str, explicit_precision: str | None
) -> tuple[str | None, str, str, list[str]]:
    diagnostics: list[str] = []
    value = raw.strip()
    inferred = "unknown"
    sortable: str | None = None
    if value.casefold() == "unknown":
        inferred = "unknown"
    elif DATE_RE.fullmatch(value):
        try:
            date.fromisoformat(value)
            inferred, sortable = "date", value
        except ValueError:
            diagnostics.append("invalid-date")
    elif TIME_RE.fullmatch(value):
        try:
            datetime.strptime(value, "%H:%M:%S" if value.count(":") == 2 else "%H:%M")
            inferred = "minute"
            sortable = f"{file_date}T{value}" if DATE_RE.fullmatch(file_date) else None
            if explicit_precision is None:
                diagnostics.append("legacy-time")
        except ValueError:
            diagnostics.append("invalid-time")
    else:
        normalized = value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
        try:
            parsed = datetime.fromisoformat(normalized)
            sortable = parsed.isoformat()
            if parsed.tzinfo is not None and parsed.utcoffset() is not None:
                inferred = "exact"
            else:
                inferred = "minute"
                diagnostics.append("timezone-missing")
        except ValueError:
            diagnostics.append("invalid-timestamp")
    precision = explicit_precision or inferred
    if precision not in PRECISIONS:
        diagnostics.append("invalid-precision")
        precision = inferred
    if precision == "exact" and inferred != "exact":
        diagnostics.append("unsupported-exact-precision")
        precision = inferred
    return sortable, precision, value, diagnostics


def _parse_block(
    path: Path,
    lineno: int,
    block: str,
    header: dict[str, str],
) -> dict[str, Any]:
    diagnostics: list[str] = []
    match = ENTRY_RE.match(block)
    metadata: dict[str, str] = {}
    timestamp_raw = "unknown"
    text = block[2:].strip()
    kind = "raw"
    if match:
        timestamp_raw = match.group("timestamp").strip()
        metadata = {
            key: " ".join(value.split())
            for key, value in META_RE.findall(match.group("meta"))
        }
        raw_text = match.group("text").strip()
        quoted = len(raw_text) >= 2 and raw_text[0] == raw_text[-1] == '"'
        text = raw_text[1:-1] if quoted else raw_text
        kind = metadata.get("kind", "quote" if quoted else "note")
        if kind not in KINDS - {"raw"}:
            diagnostics.append("invalid-kind")
            kind = "note"
    else:
        diagnostics.append("unrecognized-format")

    type_raw = metadata.get("type", "")
    type_value = type_raw if type_raw in TYPES else REPAIR_TYPE
    if type_raw not in TYPES:
        diagnostics.append("missing-type" if not type_raw else "invalid-type")
    topic_raw = metadata.get("topic", "").strip()
    topic = topic_raw if topic_raw in TOPICS else REPAIR_TOPIC
    if topic_raw not in TOPICS:
        diagnostics.append("missing-topic" if not topic_raw else "invalid-topic")

    sortable, precision, timestamp_raw, timestamp_diagnostics = _timestamp(
        timestamp_raw,
        header.get("date", ""),
        metadata.get("precision"),
    )
    diagnostics.extend(timestamp_diagnostics)
    source = metadata.get("source")
    if not source:
        source = "transcript" if precision == "exact" else "legacy"
    if precision != "exact" and "precision" not in metadata:
        diagnostics.append("unmarked-approximate")

    context_note = metadata.get("context-note")
    if context_note == "":
        diagnostics.append("empty-context-note")
    if context_note is not None and kind == "note":
        diagnostics.append("context-note-on-note")
    session_context = header.get("session-context")

    session = header.get("session", "unknown")
    record = {
        "record_id": _record_id(session, kind, text),
        "kind": kind,
        "text": text,
        "quote": text,
        "timestamp": timestamp_raw,
        "sort_timestamp": sortable,
        "date": sortable[:10] if sortable else None,
        "source": source,
        "precision": precision,
        "source_ref": metadata.get("source-ref"),
        "type": type_value,
        "type_raw": type_raw or None,
        "topic": topic,
        "topic_raw": topic_raw if topic_raw != topic else None,
        "session": session,
        "agent": header.get("agent", "unknown"),
        "model": header.get("model"),
        "project": header.get("project"),
        "file": path.name,
        "line": lineno,
        "address": f"{path.name}:{lineno}",
        "raw": block,
        "diagnostics": sorted(set(diagnostics)),
    }
    if context_note is not None:
        record["context_note"] = context_note
    if session_context:
        record["session_context"] = session_context
    return record


def load(records_dir: Path) -> tuple[list[dict[str, Any]], int]:
    """Return one record per Markdown star block; second value is diagnostic count."""
    records: list[dict[str, Any]] = []
    for path in sorted(records_dir.glob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except OSError as error:
            raise CliError(f"не удалось прочитать {path}: {error}") from error
        header = _frontmatter(lines)
        for lineno, block in _star_blocks(lines):
            records.append(_parse_block(path, lineno, block, header))
    session_holders: dict[str, set[str]] = defaultdict(set)
    id_counts: Counter[str] = Counter()
    for record in records:
        if record["session"] != "unknown":
            session_holders[record["session"]].add(record["file"])
        id_counts[record["record_id"]] += 1
    for record in records:
        diagnostics = set(record["diagnostics"])
        if len(session_holders[record["session"]]) > 1:
            diagnostics.add("duplicate-session-holder")
        if id_counts[record["record_id"]] > 1:
            diagnostics.add("duplicate-record-id")
        record["diagnostics"] = sorted(diagnostics)
    return records, sum(bool(record["diagnostics"]) for record in records)


def inventory(records: list[dict[str, Any]], diagnostic_count: int) -> str:
    topics: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"n": 0, "types": Counter(), "dates": []}
    )
    type_totals: Counter[str] = Counter()
    for record in records:
        entry = topics[record["topic"]]
        entry["n"] += 1
        entry["types"][record["type"]] += 1
        if record["date"]:
            entry["dates"].append(record["date"])
        type_totals[record["type"]] += 1
    lines: list[str] = []
    for name, entry in sorted(topics.items(), key=lambda item: (-item[1]["n"], item[0])):
        dates = entry["dates"]
        period = f"{min(dates)}…{max(dates)}" if dates else "дата неизвестна"
        mix = " ".join(f"{key}:{count}" for key, count in entry["types"].most_common())
        lines.append(f'{entry["n"]:4d}  {name:22s} {period}  {mix}')
    totals = " ".join(f"{key}:{count}" for key, count in type_totals.most_common())
    lines.append(f"---- всего {len(records)} записей / {len(topics)} topics; {totals}")
    if diagnostic_count:
        lines.append(
            f"---- REPAIR: {diagnostic_count} записей имеют diagnostics; "
            "запустите --check"
        )
    return "\n".join(lines)


def _fts_query(query: str) -> str:
    tokens = QUERY_TOKEN_RE.findall(query.casefold())
    if not tokens:
        raise CliError("query не содержит поисковых терминов")
    return " OR ".join(f'"{token[:-1]}"*' if token.endswith("*") else f'"{token}"' for token in tokens)


def search_bm25(records: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE recall USING fts5("
            "text, topic, context, tokenize='unicode61')"
        )
        connection.executemany(
            "INSERT INTO recall(rowid, text, topic, context) VALUES (?, ?, ?, ?)",
            (
                (
                    index,
                    record["text"],
                    " ".join(
                        value
                        for value in (record["topic"], record["topic_raw"])
                        if value
                    ),
                    "\n".join(
                        value
                        for value in (
                            record.get("context_note"),
                        )
                        if value
                    ),
                )
                for index, record in enumerate(records, 1)
            ),
        )
        rows = connection.execute(
            "SELECT rowid, bm25(recall, 1.0, 0.25, 0.5) AS score "
            "FROM recall WHERE recall MATCH ? ORDER BY score, rowid",
            (_fts_query(query),),
        ).fetchall()
    except sqlite3.Error as error:
        raise CliError(f"BM25 query недопустим: {error}") from error
    finally:
        connection.close()
    result: list[dict[str, Any]] = []
    for rowid, score in rows:
        record = dict(records[rowid - 1])
        record["score"] = score
        result.append(record)
    return result


def search_session_context_bm25(
    records: list[dict[str, Any]], query: str
) -> list[dict[str, Any]]:
    representatives: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        if record["file"] in seen or not record.get("session_context"):
            continue
        seen.add(record["file"])
        representatives.append(record)
    if not representatives:
        return []

    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE session_cards USING fts5("
            "context, tokenize='unicode61')"
        )
        connection.executemany(
            "INSERT INTO session_cards(rowid, context) VALUES (?, ?)",
            (
                (index, record["session_context"])
                for index, record in enumerate(representatives, 1)
            ),
        )
        rows = connection.execute(
            "SELECT rowid, bm25(session_cards) AS score "
            "FROM session_cards WHERE session_cards MATCH ? ORDER BY score, rowid",
            (_fts_query(query),),
        ).fetchall()
    except sqlite3.Error as error:
        raise CliError(f"BM25 query недопустим: {error}") from error
    finally:
        connection.close()

    result: list[dict[str, Any]] = []
    for rowid, score in rows:
        record = dict(representatives[rowid - 1])
        record["score"] = score
        result.append(record)
    return result


def search_session_routes(
    records: list[dict[str, Any]], query: str, *, hybrid: bool
) -> tuple[list[dict[str, Any]], str]:
    tokens = list(dict.fromkeys(QUERY_TOKEN_RE.findall(query.casefold())))
    wildcard_tokens = {token for token in tokens if token.endswith("*")}
    novel_tokens = {token for token in tokens if not search_bm25(records, token)}
    card_matches: dict[str, set[str]] = defaultdict(set)
    for token in tokens:
        for record in search_session_context_bm25(records, token):
            card_matches[record["file"]].add(token)

    ranked_cards = search_session_context_bm25(records, query)
    admitted: list[tuple[int, int, dict[str, Any]]] = []
    for bm25_rank, record in enumerate(ranked_cards):
        matched_tokens = card_matches[record["file"]]
        novel_match = bool(matched_tokens & novel_tokens)
        ordinary_match = (
            len(wildcard_tokens) >= 2 and len(matched_tokens) >= 2
        )
        if novel_match or ordinary_match:
            admitted.append((len(matched_tokens), bm25_rank, record))

    admitted.sort(key=lambda item: (-item[0], item[1]))
    lexical_files = [item[2]["file"] for item in admitted]

    consensus: list[dict[str, Any]] = []
    if hybrid and ranked_cards:
        dense_cards = search_session_context_dense(records, query)
        lexical_ranks = {
            record["file"]: rank
            for rank, record in enumerate(ranked_cards[:SESSION_ROUTE_LIMIT], 1)
        }
        dense_ranks = {
            record["file"]: rank
            for rank, record in enumerate(dense_cards[:SESSION_ROUTE_LIMIT], 1)
        }
        representatives = {record["file"]: record for record in ranked_cards}
        representatives.update(
            {
                record["file"]: record
                for record in dense_cards
                if record["file"] not in representatives
            }
        )
        consensus_files = lexical_ranks.keys() & dense_ranks.keys()
        for filename in sorted(
            consensus_files,
            key=lambda value: (
                lexical_ranks[value] + dense_ranks[value],
                max(lexical_ranks[value], dense_ranks[value]),
                value,
            ),
        ):
            candidate = dict(representatives[filename])
            candidate["card_evidence"] = ["bm25", "dense"]
            consensus.append(candidate)

    ordered: list[dict[str, Any]] = []
    seen_files: set[str] = set()
    for record in consensus:
        ordered.append(record)
        seen_files.add(record["file"])
    for _, _, record in admitted:
        if record["file"] in seen_files:
            for candidate in ordered:
                if candidate["file"] == record["file"]:
                    candidate.setdefault("card_evidence", []).append("lexical-gate")
                    break
            continue
        candidate = dict(record)
        candidate["card_evidence"] = ["lexical-gate"]
        ordered.append(candidate)
        seen_files.add(record["file"])

    if ordered:
        for rank, record in enumerate(ordered[:SESSION_ROUTE_LIMIT], 1):
            record["card_rank"] = rank
        routes = "+".join(
            name
            for name, present in (
                ("consensus", bool(consensus)),
                ("lexical", bool(lexical_files)),
            )
            if present
        )
        return ordered[:SESSION_ROUTE_LIMIT], f"open: {routes}"
    if len(wildcard_tokens) < 2:
        return [], "closed: no context consensus or lexical novelty"
    return [], "no context consensus or lexical admission"


def _cache_root() -> Path:
    explicit = os.environ.get("CHAT_RECALL_CACHE_DIR")
    if explicit:
        return Path(explicit).expanduser()
    xdg_root = os.environ.get("XDG_CACHE_HOME")
    if xdg_root:
        return Path(xdg_root).expanduser() / "chat-recall"
    return Path.home() / ".cache" / "chat-recall"


def _embedding_cache_path() -> Path:
    return _cache_root() / "embeddings.sqlite3"


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _pack_vector(vector: list[float]) -> bytes:
    return struct.pack(f"<{len(vector)}f", *vector)


def _unpack_vector(payload: bytes, dimension: int) -> list[float]:
    expected = dimension * 4
    if len(payload) != expected:
        raise CliError(
            "embedding cache повреждён: "
            f"ожидалось {expected} bytes, получено {len(payload)}"
        )
    return list(struct.unpack(f"<{dimension}f", payload))


def _open_embedding_cache(path: Path) -> sqlite3.Connection:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path, timeout=30)
        connection.execute("PRAGMA busy_timeout = 30000")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS embeddings ("
            "profile TEXT NOT NULL, "
            "content_hash TEXT NOT NULL, "
            "dimension INTEGER NOT NULL, "
            "vector BLOB NOT NULL, "
            "PRIMARY KEY (profile, content_hash)"
            ")"
        )
        return connection
    except (OSError, sqlite3.Error) as error:
        raise CliError(f"не удалось открыть embedding cache {path}: {error}") from error


def _cached_vectors(
    path: Path,
    content_hashes: list[str],
) -> dict[str, list[float]]:
    try:
        connection = _open_embedding_cache(path)
        try:
            result: dict[str, list[float]] = {}
            for content_hash in dict.fromkeys(content_hashes):
                row = connection.execute(
                    "SELECT dimension, vector FROM embeddings "
                    "WHERE profile = ? AND content_hash = ?",
                    (EMBEDDING_PROFILE, content_hash),
                ).fetchone()
                if row is None:
                    continue
                dimension, payload = row
                if dimension != EMBEDDING_DIMENSION:
                    raise CliError(
                        "embedding cache повреждён: неверная размерность "
                        f"для {content_hash[:12]}"
                    )
                result[content_hash] = _unpack_vector(payload, dimension)
            return result
        finally:
            connection.close()
    except sqlite3.Error as error:
        raise CliError(f"не удалось прочитать embedding cache {path}: {error}") from error


def _store_vectors(path: Path, vectors: dict[str, list[float]]) -> None:
    if not vectors:
        return
    for content_hash, vector in vectors.items():
        if len(vector) != EMBEDDING_DIMENSION:
            raise CliError(
                "embedding backend вернул неверную размерность "
                f"для {content_hash[:12]}: {len(vector)}"
            )
    try:
        connection = _open_embedding_cache(path)
        try:
            with connection:
                connection.executemany(
                    "INSERT OR REPLACE INTO embeddings "
                    "(profile, content_hash, dimension, vector) VALUES (?, ?, ?, ?)",
                    (
                        (
                            EMBEDDING_PROFILE,
                            content_hash,
                            EMBEDDING_DIMENSION,
                            _pack_vector(vector),
                        )
                        for content_hash, vector in vectors.items()
                    ),
                )
        finally:
            connection.close()
    except sqlite3.Error as error:
        raise CliError(f"не удалось записать embedding cache {path}: {error}") from error


def _embedding_backend(*, offline: bool) -> Any:
    backend_key = (offline, str(_cache_root() / "models"))
    if backend_key in _EMBEDDING_BACKENDS:
        return _EMBEDDING_BACKENDS[backend_key]
    try:
        installed = importlib.metadata.version("fastembed")
    except importlib.metadata.PackageNotFoundError as error:
        raise CliError(
            "hybrid runtime не подготовлен; выполните `uv run --locked --script "
            "chat_digest.py --prepare` или используйте --lexical"
        ) from error
    if installed != FASTEMBED_VERSION:
        raise CliError(
            f"нужен fastembed=={FASTEMBED_VERSION}, найден {installed}; "
            "выполните `uv run --locked --script chat_digest.py --prepare`"
        )

    try:
        from fastembed import TextEmbedding
        from fastembed.common.model_description import ModelSource, PoolingType
        from loguru import logger

        logger.disable("fastembed")
        known = {entry["model"].casefold() for entry in TextEmbedding.list_supported_models()}
        if EMBEDDING_MODEL.casefold() not in known:
            TextEmbedding.add_custom_model(
                model=EMBEDDING_MODEL,
                pooling=PoolingType.MEAN,
                normalization=True,
                sources=ModelSource(hf=EMBEDDING_MODEL),
                dim=EMBEDDING_DIMENSION,
                model_file=EMBEDDING_MODEL_FILE,
                description="Multilingual E5 small for local chat recall",
            )
        os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
        if offline:
            os.environ["HF_HUB_OFFLINE"] = "1"
        backend = TextEmbedding(
            model_name=EMBEDDING_MODEL,
            cache_dir=str(_cache_root() / "models"),
            local_files_only=offline,
            revision=EMBEDDING_REVISION,
        )
        _EMBEDDING_BACKENDS[backend_key] = backend
        return backend
    except CliError:
        raise
    except Exception as error:
        action = (
            "выполните `uv run --locked --script chat_digest.py --prepare` "
            "при доступной сети"
            if offline
            else "проверьте сеть и доступ к Hugging Face"
        )
        raise CliError(
            f"не удалось открыть локальную embedding model: {error}; {action}; "
            "для BM25 используйте --lexical"
        ) from error


def _embed(model: Any, texts: list[str]) -> list[list[float]]:
    try:
        vectors = [
            list(map(float, vector))
            for vector in model.embed(texts, batch_size=EMBEDDING_BATCH_SIZE)
        ]
    except Exception as error:
        raise CliError(f"embedding inference завершился ошибкой: {error}") from error
    if len(vectors) != len(texts):
        raise CliError(
            "embedding backend вернул неожиданное число векторов: "
            f"{len(vectors)} вместо {len(texts)}"
        )
    if any(len(vector) != EMBEDDING_DIMENSION for vector in vectors):
        raise CliError("embedding backend вернул неверную размерность вектора")
    return vectors


def _prepare_hybrid() -> str:
    model = _embedding_backend(offline=False)
    _embed(model, [PASSAGE_PREFIX + "local chat recall readiness check"])
    return (
        f"READY: {EMBEDDING_MODEL}@{EMBEDDING_REVISION[:12]} · "
        f"cache={_cache_root()}"
    )


def _dense_text(record: dict[str, Any]) -> str:
    return "\n".join(
        value
        for value in (
            record["text"],
            record.get("context_note"),
        )
        if value
    )


def _search_dense_texts(
    records: list[dict[str, Any]],
    query: str,
    text_for: Callable[[dict[str, Any]], str],
) -> list[dict[str, Any]]:
    if not records:
        return []
    model = _embedding_backend(offline=True)
    cache_path = _embedding_cache_path()
    texts = [text_for(record) for record in records]
    hashes = [_content_hash(text) for text in texts]
    vectors = _cached_vectors(cache_path, hashes)
    missing = [content_hash for content_hash in dict.fromkeys(hashes) if content_hash not in vectors]
    if missing:
        text_by_hash = {
            _content_hash(text): text
            for text in texts
        }
        embedded = _embed(
            model,
            [PASSAGE_PREFIX + text_by_hash[content_hash] for content_hash in missing],
        )
        additions = dict(zip(missing, embedded, strict=True))
        _store_vectors(cache_path, additions)
        vectors.update(additions)

    dense_query = query.replace("*", "")
    query_vector = _embed(model, [QUERY_PREFIX + dense_query])[0]
    ranked: list[tuple[float, int, dict[str, Any]]] = []
    for index, (record, content_hash) in enumerate(zip(records, hashes, strict=True)):
        score = sum(
            left * right for left, right in zip(vectors[content_hash], query_vector, strict=True)
        )
        ranked.append((score, index, record))
    result: list[dict[str, Any]] = []
    for score, _, record in sorted(ranked, key=lambda item: (-item[0], item[1])):
        candidate = dict(record)
        candidate["score"] = score
        result.append(candidate)
    return result


_DENSE_TOP1: float | None = None


def search_dense(records: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    global _DENSE_TOP1
    ranked = _search_dense_texts(records, query, _dense_text)
    _DENSE_TOP1 = ranked[0]["score"] if ranked else None
    return ranked


def _support_verdict(top1: float | None) -> str | None:
    """Ближайшая запись корпуса как сырой косинус, а не как позиция в ранге.

    RRF стирает абсолютный смысл скора, поэтому вердикт считается до слияния
    каналов. Он описывает наличие материала в корпусе, а не правоту выдачи.
    """
    if top1 is None:
        return None
    if top1 >= SUPPORT_STRONG:
        return "supported"
    if top1 >= SUPPORT_WEAK:
        return "weak"
    return "unsupported"


def search_session_context_dense(
    records: list[dict[str, Any]], query: str
) -> list[dict[str, Any]]:
    representatives: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        if record["file"] in seen or not record.get("session_context"):
            continue
        seen.add(record["file"])
        representatives.append(record)
    return _search_dense_texts(
        representatives,
        query,
        lambda record: record["session_context"],
    )


def _first_per_file(ranking: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in ranking:
        if record["file"] in seen:
            continue
        seen.add(record["file"])
        result.append(record)
    return result


def _merge_file_rankings(
    records: list[dict[str, Any]],
    rankings: tuple[list[dict[str, Any]], ...],
) -> list[dict[str, Any]]:
    file_rankings = tuple(
        _first_per_file(ranking)[:HYBRID_DEPTH]
        for ranking in rankings
        if ranking
    )
    rank_by_address = tuple(
        {
            record["address"]: rank
            for rank, record in enumerate(ranking[:HYBRID_DEPTH], 1)
        }
        for ranking in rankings
    )
    rank_by_file = tuple(
        {
            record["file"]: (rank, record)
            for rank, record in enumerate(ranking, 1)
        }
        for ranking in file_rankings
    )
    filenames = {
        filename
        for ranking in rank_by_file
        for filename in ranking
    }
    records_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        records_by_file[record["file"]].append(record)
    scores: dict[str, float] = {}
    representatives: dict[str, dict[str, Any]] = {}
    evidence: dict[str, list[dict[str, Any]]] = {}
    for filename in filenames:
        channel_hits = [
            ranking[filename]
            for ranking in rank_by_file
            if filename in ranking
        ]
        file_support = sum(
            1.0 / (RRF_CONSTANT + rank)
            for rank, _ in channel_hits
        )
        passage_scores = [
            (
                sum(
                    1.0 / (RRF_CONSTANT + ranking[record["address"]])
                    for ranking in rank_by_address
                    if record["address"] in ranking
                ),
                record,
            )
            for record in records_by_file[filename]
            if any(record["address"] in ranking for ranking in rank_by_address)
        ]
        ranked_evidence = sorted(channel_hits, key=lambda item: item[0])
        if passage_scores:
            primary_score, primary_record = max(
                passage_scores,
                key=lambda item: item[0],
            )
        else:
            primary_score, primary_record = 0.0, ranked_evidence[0][1]
        scores[filename] = primary_score + FILE_SUPPORT_WEIGHT * file_support
        representatives[filename] = primary_record
        evidence[filename] = []
        seen_addresses: set[str] = set()
        for record in (primary_record, *(record for _, record in ranked_evidence)):
            if record["address"] in seen_addresses:
                continue
            seen_addresses.add(record["address"])
            evidence[filename].append(record)
            if len(evidence[filename]) == 3:
                break

    original_order: dict[str, int] = {}
    for index, record in enumerate(records):
        original_order.setdefault(record["file"], index)
    ordered = sorted(
        scores,
        key=lambda filename: (-scores[filename], original_order[filename]),
    )
    return [
        {
            **representatives[filename],
            "score": scores[filename],
            "quote_channels": len(
                [ranking for ranking in rank_by_file if filename in ranking]
            ),
            "quote_evidence": evidence[filename],
        }
        for filename in ordered
    ]


def search_hybrid(
    records: list[dict[str, Any]],
    query: str,
    *,
    collapse_files: bool = False,
) -> list[dict[str, Any]]:
    lexical = search_bm25(records, query)
    if not lexical:
        return []
    dense = search_dense(records, query)
    rankings = (lexical, dense)
    if not collapse_files:
        scores: dict[str, float] = defaultdict(float)
        representatives: dict[str, dict[str, Any]] = {}
        for ranking in rankings:
            for rank, record in enumerate(ranking[:HYBRID_DEPTH], 1):
                scores[record["address"]] += 1.0 / (RRF_CONSTANT + rank)
                representatives.setdefault(record["address"], record)
        original_order = {
            record["address"]: index for index, record in enumerate(records)
        }
        ordered = sorted(
            scores,
            key=lambda address: (-scores[address], original_order[address]),
        )
        return [
            {**representatives[address], "score": scores[address]}
            for address in ordered
        ]

    return _merge_file_rankings(records, rankings)


def _validate_date(value: str, name: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise CliError(f"{name}: ожидается YYYY-MM-DD") from error


def _filter(records: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    result = records
    if args.types:
        wanted = {value.strip() for value in args.types.split(",") if value.strip()}
        result = [record for record in result if record["type"] in wanted]
    if args.topics:
        wanted = {value.strip() for value in args.topics.split(",") if value.strip()}
        result = [record for record in result if record["topic"] in wanted]
    if args.agent:
        result = [record for record in result if record["agent"] == args.agent]
    if args.session:
        result = [record for record in result if record["session"] == args.session]
    if args.grep:
        try:
            pattern = re.compile(args.grep, re.IGNORECASE)
        except re.error as error:
            raise CliError(f"grep regex недопустим: {error}") from error
        result = [record for record in result if pattern.search(record["text"])]
    if args.since:
        since = _validate_date(args.since, "--since")
        result = [record for record in result if record["date"] and record["date"] >= since]
    if args.until:
        until = _validate_date(args.until, "--until")
        result = [record for record in result if record["date"] and record["date"] <= until]
    return result


def _retrieve(
    records: list[dict[str, Any]], args: argparse.Namespace
) -> tuple[list[dict[str, Any]], str | None, list[dict[str, Any]], str | None]:
    filtered = _filter(records, args)
    if not args.query:
        return filtered, None, [], None
    session_routes, card_route = search_session_routes(
        filtered,
        args.query,
        hybrid=not args.lexical,
    )
    if args.lexical:
        lexical = search_bm25(filtered, args.query)
        return (
            _merge_file_rankings(filtered, (lexical,)),
            "lexical",
            session_routes,
            card_route,
        )
    hybrid = search_hybrid(
        filtered,
        args.query,
        collapse_files=True,
    )
    return hybrid, "hybrid", session_routes, card_route


def _select_holders(
    quote_ranking: list[dict[str, Any]],
    card_ranking: list[dict[str, Any]],
    limit: int,
) -> tuple[list[dict[str, Any]], int]:
    by_card_file = {record["file"]: record for record in card_ranking}
    selected: list[dict[str, Any]] = []
    for record in quote_ranking[:limit]:
        candidate = dict(record)
        card = by_card_file.get(record["file"])
        candidate["admitted_by"] = "both" if card else "quote"
        if card:
            candidate["card_evidence"] = card.get("card_evidence", [])
            candidate["card_rank"] = card.get("card_rank")
        selected.append(candidate)

    selected_files = {record["file"] for record in selected}
    rescues = 0
    for card in card_ranking:
        if card["file"] in selected_files:
            continue
        candidate = dict(card)
        candidate["admitted_by"] = "card"
        candidate["quote_channels"] = 0
        candidate["quote_evidence"] = []
        if len(selected) < limit:
            selected.append(candidate)
            selected_files.add(candidate["file"])
            continue
        if rescues >= CONTEXT_RESCUE_LIMIT:
            break
        replacement = next(
            (
                index
                for index in range(len(selected) - 1, -1, -1)
                if selected[index].get("admitted_by") == "quote"
                and selected[index].get("quote_channels", 1) < 2
            ),
            None,
        )
        if replacement is None:
            break
        selected_files.remove(selected[replacement]["file"])
        selected[replacement] = candidate
        selected_files.add(candidate["file"])
        rescues += 1

    for rank, record in enumerate(selected, 1):
        record["semantic_rank"] = rank
    candidate_count = len(
        {record["file"] for record in (*quote_ranking, *card_ranking)}
    )
    return selected, candidate_count


def _parse_sort_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return parsed


def _latest_holder_datetime(records: list[dict[str, Any]]) -> datetime | None:
    values = [
        parsed
        for record in records
        if (parsed := _parse_sort_datetime(record.get("sort_timestamp")))
        is not None
    ]
    return max(values) if values else None


def _russian_count(value: int, forms: tuple[str, str, str]) -> str:
    tail = value % 100
    if 11 <= tail <= 14:
        form = forms[2]
    elif value % 10 == 1:
        form = forms[0]
    elif 2 <= value % 10 <= 4:
        form = forms[1]
    else:
        form = forms[2]
    return f"{value} {form} назад"


def _relative_age(value: datetime | None, now: datetime) -> str:
    if value is None:
        return "время неизвестно"
    localized = value.astimezone(now.tzinfo)
    seconds = max(0, int((now - localized).total_seconds()))
    if seconds < 60:
        return "только что"
    minutes = seconds // 60
    if minutes < 60:
        return _russian_count(minutes, ("минуту", "минуты", "минут"))
    hours = minutes // 60
    if hours < 24:
        return _russian_count(hours, ("час", "часа", "часов"))
    days = hours // 24
    if days < 30:
        return _russian_count(days, ("день", "дня", "дней"))
    months = days // 30
    if months < 12:
        return _russian_count(months, ("месяц", "месяца", "месяцев"))
    years = days // 365
    return _russian_count(years, ("год", "года", "лет"))


def _holder_cards(
    selected: list[dict[str, Any]],
    all_records: list[dict[str, Any]],
    head: int,
) -> list[dict[str, Any]]:
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in all_records:
        by_file[record["file"]].append(record)
    now = datetime.now().astimezone()
    cards: list[dict[str, Any]] = []
    for candidate in selected:
        holder_records = by_file[candidate["file"]]
        latest = _latest_holder_datetime(holder_records)
        evidence = candidate.get("quote_evidence", [])
        strongest_quote = None
        if evidence:
            text = evidence[0]["text"]
            strongest_quote = {
                "text": text[:head].rstrip() + ("…" if len(text) > head else ""),
                "address": evidence[0]["address"],
            }
        types = Counter(record["type"] for record in holder_records)
        topics = Counter(record["topic"] for record in holder_records)
        session_context = candidate.get("session_context")
        if session_context is None and holder_records:
            session_context = holder_records[0].get("session_context")
        cards.append(
            {
                "file": candidate["file"],
                "age": _relative_age(latest, now),
                "semantic_rank": candidate["semantic_rank"],
                "session_context": session_context,
                "strongest_quote": strongest_quote,
                "supporting_quote_count": min(max(len(evidence) - 1, 0), 2),
                "types": dict(types.most_common()),
                "topics": dict(topics.most_common()),
                "admitted_by": candidate["admitted_by"],
                "card_evidence": candidate.get("card_evidence", []),
                "_latest": latest,
            }
        )
    cards.sort(
        key=lambda card: (
            card["_latest"] is not None,
            card["_latest"] or datetime.min.replace(tzinfo=now.tzinfo),
            -card["semantic_rank"],
        ),
        reverse=True,
    )
    for card in cards:
        del card["_latest"]
    return cards


def _quality(records: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "exact": sum(record["precision"] == "exact" for record in records),
        "approximate": sum(record["precision"] in {"minute", "date"} for record in records),
        "unknown": sum(record["precision"] == "unknown" for record in records),
        "with_diagnostics": sum(bool(record["diagnostics"]) for record in records),
        "raw": sum(record["kind"] == "raw" for record in records),
    }


def _summary(record: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "record_id",
        "kind",
        "text",
        "timestamp",
        "source",
        "precision",
        "source_ref",
        "type",
        "topic",
        "topic_raw",
        "session_context",
        "session",
        "agent",
        "address",
        "diagnostics",
        "score",
    )
    return {field: record[field] for field in fields if field in record}


def _snippet_summary(record: dict[str, Any], head: int) -> dict[str, Any]:
    summary = _summary(record)
    text = summary.get("text")
    if isinstance(text, str) and len(text) > head:
        summary["text"] = text[:head].rstrip() + "…"
    return summary


def _validate_bounds(limit: int, max_chars: int) -> None:
    if limit < 1:
        raise CliError("--limit должен быть положительным")
    if max_chars < 512:
        raise CliError("--max-chars должен быть не меньше 512")


def _bounded(
    records: list[dict[str, Any]], limit: int, max_chars: int
) -> tuple[list[dict[str, Any]], str | None]:
    _validate_bounds(limit, max_chars)
    result: list[dict[str, Any]] = []
    used = 0
    truncated_by: str | None = None
    for record in records[:limit]:
        estimate = len(json.dumps(_summary(record), ensure_ascii=False))
        if result and used + estimate > max_chars:
            truncated_by = "max_chars"
            break
        if not result and estimate > max_chars:
            clipped = dict(record)
            clipped["text"] = clipped["text"][: max(40, max_chars // 2)] + "…"
            clipped["quote"] = clipped["text"]
            clipped["raw"] = clipped["raw"][: max(40, max_chars // 3)] + "…"
            result.append(clipped)
            truncated_by = "max_chars"
            break
        result.append(record)
        used += estimate
    if truncated_by is None and len(result) < len(records):
        truncated_by = "limit"
    return result, truncated_by


def _digest(records: list[dict[str, Any]], head: int, *, verbose: bool) -> str:
    if head < 1:
        raise CliError("--head должен быть положительным")
    lines: list[str] = []
    for record in records:
        clipped = record["text"][:head] + ("…" if len(record["text"]) > head else "")
        score = f" score={record['score']:.4f}" if verbose and "score" in record else ""
        diagnostics = " !diagnostics" if record["diagnostics"] else ""
        lines.append(
            f"{record['record_id']} {record['date'] or 'unknown'} "
            f"{record['precision']} {record['kind']} "
            f"{record['type']}/{record['topic']}{diagnostics}{score} · {clipped}"
        )
    return "\n".join(lines)


def _show(record: dict[str, Any]) -> str:
    source = (
        f"timestamp={record['timestamp']} · precision={record['precision']} · "
        f"source={record['source']}"
    )
    if record["source_ref"]:
        source += f" · source_ref={record['source_ref']}"
    owner = (
        f"address={record['address']} · session={record['session']} · "
        f"agent={record['agent']}"
    )
    if record["project"]:
        owner += f" · project={record['project']}"
    if record["model"]:
        owner += f" · model={record['model']}"
    classification = (
        f"record={record['record_id']} · kind={record['kind']} · "
        f"type={record['type']} · topic={record['topic']}"
    )
    if record["type_raw"] and record["type_raw"] != record["type"]:
        classification += f" · type_raw={record['type_raw']}"
    if record["topic_raw"] and record["topic_raw"] != record["topic"]:
        classification += f" · topic_raw={record['topic_raw']}"
    diagnostics = ",".join(record["diagnostics"]) or "none"
    lines = [record["text"]]
    if record.get("context_note"):
        lines.append(f"context-note: {record['context_note']}")
    if record.get("session_context"):
        lines.append(f"session-context: {record['session_context']}")
    lines.extend((classification, source, owner, f"diagnostics={diagnostics}"))
    return "\n".join(lines)


def _check_report(records: list[dict[str, Any]], total: int, max_chars: int) -> str:
    issues = [record for record in records if record["diagnostics"]]
    if not issues:
        return f"OK: {total} записей без diagnostics"

    issue_lines = [
        f"{record['address']} {record['record_id']}: {','.join(record['diagnostics'])}"
        for record in issues
    ]
    visible: list[str] = []
    for line in issue_lines:
        candidate_count = len(visible) + 1
        candidate_summary = (
            f"{candidate_count}/{len(issues)} records with diagnostics shown · "
            f"{total} records · truncated"
        )
        candidate = "\n".join((candidate_summary, *visible, line))
        if len(candidate) > max_chars:
            break
        visible.append(line)

    truncated = len(visible) < len(issue_lines)
    summary = (
        f"{len(visible)}/{len(issues)} records with diagnostics shown · "
        f"{total} records · truncated"
        if truncated
        else f"{len(issues)} records with diagnostics · {total} records"
    )
    return "\n".join((summary, *visible))


def _result_status(
    returned: int,
    matched: int,
    total: int,
    truncated_by: str | None,
    retrieval: str | None,
) -> str:
    noun = "candidates" if retrieval else "records"
    status = f"{returned}/{matched} {noun} shown · {total} records"
    if retrieval:
        status += f" · retrieval={retrieval}"
    if truncated_by == "limit":
        return f"{status} · truncated by --limit"
    if truncated_by == "max_chars":
        return f"{status} · truncated by --max-chars"
    return status


def _render_digest(
    records: list[dict[str, Any]],
    *,
    head: int,
    verbose: bool,
    matched: int,
    total: int,
    truncated_by: str | None,
    retrieval: str | None,
) -> str:
    digest = _digest(records, head, verbose=verbose)
    lines = [
        _result_status(len(records), matched, total, truncated_by, retrieval)
    ]
    lines.append(digest or "selection=none")
    return "\n".join(lines)


def _render_holders(
    cards: list[dict[str, Any]],
    *,
    matched: int,
    total: int,
    truncated_by: str | None,
    retrieval: str,
) -> str:
    status = (
        f"{len(cards)}/{matched} holders shown · {total} records · "
        f"retrieval={retrieval} · order=newest-first"
    )
    if truncated_by:
        status += f" · truncated by --{truncated_by.replace('_', '-')}"
    lines = [status]
    support = _support_verdict(_DENSE_TOP1)
    if support is not None:
        lines.append(f"corpus-support={support} · dense_top1={_DENSE_TOP1:.3f}")
    for card in cards:
        lines.append(
            f"holder={card['file']} · {card['age']} · "
            f"semantic_rank={card['semantic_rank']} · "
            f"admitted_by={card['admitted_by']}"
        )
        lines.append(
            "session-context: "
            + (card["session_context"] or "[нет session-context]")
        )
        strongest = card["strongest_quote"]
        if strongest:
            text = " ".join(strongest["text"].split())
            lines.append(
                f"strongest-quote: {text} · {strongest['address']} · "
                f"supporting={card['supporting_quote_count']}"
            )
        else:
            lines.append("strongest-quote: [нет quote-hit] · supporting=0")
        type_counts = " ".join(
            f"{name}:{count}" for name, count in card["types"].items()
        )
        topic_counts = " ".join(
            f"{name}:{count}" for name, count in card["topics"].items()
        )
        lines.append(f"types: {type_counts or '[нет]'}")
        lines.append(f"topics: {topic_counts or '[нет]'}")
    return "\n".join(lines)


def _bounded_holder_cards(
    cards: list[dict[str, Any]],
    *,
    matched: int,
    total: int,
    max_chars: int,
    retrieval: str,
) -> tuple[list[dict[str, Any]], str | None]:
    selected: list[dict[str, Any]] = []
    truncated_by: str | None = None
    for card in cards:
        candidate = [*selected, card]
        rendered = _render_holders(
            candidate,
            matched=matched,
            total=total,
            truncated_by=("max_chars" if len(candidate) < len(cards) else None),
            retrieval=retrieval,
        )
        if len(rendered) > max_chars:
            truncated_by = "max_chars"
            break
        selected = candidate
    if cards and not selected:
        raise CliError(
            "первая holder-card не помещается в --max-chars; "
            "уменьшите --head или увеличьте лимит"
        )
    return selected, truncated_by


def _bounded_digest(
    records: list[dict[str, Any]],
    *,
    limit: int,
    max_chars: int,
    head: int,
    verbose: bool,
    total: int,
    retrieval: str | None,
) -> tuple[list[dict[str, Any]], str | None]:
    _validate_bounds(limit, max_chars)
    _digest([], head, verbose=verbose)
    selected: list[dict[str, Any]] = []
    truncated_by: str | None = None
    for record in records[:limit]:
        candidate = [*selected, record]
        rendered = _render_digest(
            candidate,
            head=head,
            verbose=verbose,
            matched=len(records),
            total=total,
            truncated_by=("max_chars" if len(candidate) < len(records) else None),
            retrieval=retrieval,
        )
        if len(rendered) > max_chars:
            truncated_by = "max_chars"
            break
        selected = candidate
    if records and not selected:
        raise CliError(
            "первая запись не помещается в --max-chars; "
            "уменьшите --head или увеличьте --max-chars"
        )
    if truncated_by is None and len(selected) < len(records):
        truncated_by = "limit"
    return selected, truncated_by


def _timeline(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dated = sorted(
        (
            record
            for record in records
            if record["sort_timestamp"] and record["precision"] != "unknown"
        ),
        key=lambda record: (
            record["sort_timestamp"],
            record["file"],
            record["line"],
        ),
        reverse=True,
    )
    uncertain = [
        record for record in records
        if not record["sort_timestamp"] or record["precision"] == "unknown"
    ]
    return dated + sorted(
        uncertain,
        key=lambda record: (record["file"], record["line"]),
        reverse=True,
    )


def _warnings(records: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    if any(record["diagnostics"] for record in records):
        warnings.append("repair-backlog-present")
    if any(record["precision"] != "exact" for record in records):
        warnings.append("approximate-or-unknown-time-present")
    return warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records_dir", type=Path, nargs="?")
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="download and verify the pinned local embedding model",
    )
    parser.add_argument("--digest", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--query")
    parser.add_argument(
        "--lexical",
        action="store_true",
        help="use BM25 only instead of the default local hybrid retrieval",
    )
    parser.add_argument(
        "--show",
        help="show complete record, provenance, and context-note when present",
    )
    parser.add_argument("--timeline", action="store_true")
    parser.add_argument("--type", dest="types")
    parser.add_argument("--topic", dest="topics")
    parser.add_argument("--grep")
    parser.add_argument("--since")
    parser.add_argument("--until")
    parser.add_argument("--agent")
    parser.add_argument("--session")
    parser.add_argument(
        "--head",
        type=int,
        default=110,
        help="excerpt length for human digest and strongest quote text",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="maximum holders for a query, records for other modes",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=None,
        help=(
            "hard output cap; default: full query holder cards, "
            "8000 characters in other modes"
        ),
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        if args.prepare:
            incompatible = any(
                (
                    args.records_dir,
                    args.digest,
                    args.check,
                    args.strict,
                    args.query,
                    args.lexical,
                    args.show,
                    args.timeline,
                    args.types,
                    args.topics,
                    args.grep,
                    args.since,
                    args.until,
                    args.agent,
                    args.session,
                    args.json,
                    args.verbose,
                    args.head != 110,
                    args.limit != 10,
                    args.max_chars is not None,
                )
            )
            if incompatible:
                raise CliError(
                    "--prepare запускается отдельно, без records_dir и retrieval flags"
                )
            print(_prepare_hybrid())
            return 0
        if args.strict and not args.check:
            raise CliError("--strict используется только вместе с --check")
        if args.lexical and not args.query:
            raise CliError("--lexical используется только вместе с --query")
        if args.records_dir is None:
            raise CliError("укажите папку `_ops/chat-recall` или используйте --prepare")
        if not args.records_dir.is_dir():
            raise CliError(f"нет папки: {args.records_dir}")
        holder_mode = bool(args.query and not args.timeline and not args.show)
        if args.max_chars is None:
            args.max_chars = sys.maxsize if holder_mode else DEFAULT_MAX_CHARS
        if not args.show:
            _validate_bounds(args.limit, args.max_chars)
        records, diagnostic_count = load(args.records_dir)
        total = len(records)
        session_routes: list[dict[str, Any]] = []
        card_route: str | None = None
        holder_cards: list[dict[str, Any]] = []
        candidate_count = 0
        inventory_mode = not any(
            (
                args.digest,
                args.query,
                args.timeline,
                args.types,
                args.topics,
                args.grep,
                args.since,
                args.until,
                args.agent,
                args.session,
            )
        )

        if args.show:
            matches = [record for record in records if record["record_id"] == args.show]
            if not matches:
                raise CliError(f"record_id не найден: {args.show}")
            if len(matches) > 1:
                addresses = ", ".join(record["address"] for record in matches)
                raise CliError(
                    f"record_id неоднозначен ({addresses}); сначала почините duplicate"
                )
            selected, truncated_by = matches, None
            matched = len(selected)
            retrieval = None
        elif holder_mode:
            quote_ranking, retrieval, session_routes, card_route = _retrieve(
                records,
                args,
            )
            selected_holders, candidate_count = _select_holders(
                quote_ranking,
                session_routes,
                args.limit,
            )
            holder_cards = _holder_cards(selected_holders, records, args.head)
            matched = candidate_count
            truncated_by = (
                "limit" if len(selected_holders) < candidate_count else None
            )
            if not args.json:
                holder_cards, character_truncation = _bounded_holder_cards(
                    holder_cards,
                    matched=matched,
                    total=total,
                    max_chars=args.max_chars,
                    retrieval=retrieval or "lexical",
                )
                if character_truncation:
                    truncated_by = character_truncation
            selected = []
        else:
            candidates, retrieval, session_routes, card_route = _retrieve(
                records,
                args,
            )
            if args.query and args.timeline:
                selected_holders, candidate_count = _select_holders(
                    candidates,
                    session_routes,
                    min(args.limit, 10),
                )
                holder_files = {
                    record["file"] for record in selected_holders
                }
                candidates = [
                    record
                    for record in _filter(records, args)
                    if record["file"] in holder_files
                ]
            if args.timeline:
                candidates = _timeline(candidates)
            matched = len(candidates)
            if args.json:
                selected, truncated_by = _bounded(
                    candidates, args.limit, args.max_chars
                )
            elif args.check or inventory_mode:
                selected, truncated_by = candidates, None
            else:
                selected, truncated_by = _bounded_digest(
                    candidates,
                    limit=args.limit,
                    max_chars=args.max_chars,
                    head=args.head,
                    verbose=args.verbose,
                    total=total,
                    retrieval=retrieval,
                )
        if holder_mode:
            rendered_records: list[dict[str, Any]] = []
        elif args.show:
            rendered_records = selected
        else:
            rendered_records = [_summary(record) for record in selected]
        envelope: dict[str, Any] = {
            "total": total,
            "matched": matched,
            "returned": len(holder_cards) if holder_mode else len(selected),
            "truncated": truncated_by is not None,
            "truncated_by": truncated_by,
            "selection": (
                "holders"
                if holder_mode and holder_cards
                else "records"
                if not holder_mode and matched
                else "none"
            ),
            "quality": _quality(records),
            "warnings": _warnings(records),
        }
        if holder_mode:
            envelope["holders"] = holder_cards
            envelope["order"] = "newest-first"
            envelope["semantic_order"] = "semantic_rank"
        else:
            envelope["records"] = rendered_records
        if args.query:
            envelope["card_route"] = card_route
            envelope["retrieval"] = retrieval
            envelope["retrieval_complete"] = True
            envelope["candidate_count"] = (
                candidate_count if candidate_count else matched
            )
            support = _support_verdict(_DENSE_TOP1)
            if support is not None:
                envelope["dense_top1"] = round(_DENSE_TOP1, 4)
                envelope["support"] = support
                if support != "supported":
                    envelope["warnings"] = [
                        *envelope["warnings"],
                        f"corpus-support-{support}",
                    ]
            if retrieval == "hybrid":
                envelope["candidate_depth"] = HYBRID_DEPTH
        if args.timeline:
            envelope["order"] = "newest-first"

        if args.json:
            rendered = json.dumps(
                envelope, ensure_ascii=False, separators=(",", ":")
            )
            if args.show and len(rendered) > args.max_chars:
                raise CliError(
                    "полная запись превышает --max-chars; увеличьте лимит для --show"
                )
            output_key = "holders" if holder_mode else "records"
            while (
                not args.show
                and len(rendered) > args.max_chars
                and envelope[output_key]
            ):
                envelope[output_key].pop()
                envelope["returned"] = len(envelope[output_key])
                envelope["truncated"] = True
                envelope["truncated_by"] = "max_chars"
                rendered = json.dumps(
                    envelope, ensure_ascii=False, separators=(",", ":")
                )
            if len(rendered) > args.max_chars:
                raise CliError(
                    "--max-chars слишком мал для обязательного JSON envelope"
                )
            print(rendered)
        elif args.check:
            print(_check_report(records, total, args.max_chars))
        elif args.show:
            rendered = (
                json.dumps(selected[0], ensure_ascii=False, indent=2)
                if args.verbose
                else _show(selected[0])
            )
            if len(rendered) > args.max_chars:
                raise CliError(
                    "полная запись превышает --max-chars; увеличьте лимит для --show"
                )
            print(rendered)
        elif inventory_mode:
            print(inventory(records, diagnostic_count))
        elif holder_mode:
            print(
                _render_holders(
                    holder_cards,
                    matched=matched,
                    total=total,
                    truncated_by=truncated_by,
                    retrieval=retrieval or "lexical",
                )
            )
        else:
            print(
                _render_digest(
                    selected,
                    head=args.head,
                    verbose=args.verbose,
                    matched=matched,
                    total=total,
                    truncated_by=truncated_by,
                    retrieval=retrieval,
                )
            )
        if args.check and args.strict and diagnostic_count:
            return 1
        return 0
    except CliError as error:
        print(f"chat-digest: error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
