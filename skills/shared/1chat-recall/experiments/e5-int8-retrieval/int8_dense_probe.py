"""One-shot dynamic-INT8 E5 acquisition probe for revealed development cases."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

DENSE_DEPTH = 8
LEXICAL_DEPTH = 48
SESSION_RADIUS = 2
UNCONDITIONAL_SESSION_SEEDS = 8
IDENTIFIER_MAXIMUM_FREQUENCY = 5
IDENTIFIER_SPECIAL_LIMIT = 4
SESSION_SPECIAL_LIMIT = 8
MAX_CANDIDATES = 48
MAX_PACKET_BYTES = 4000
PREVIEW_CHARACTERS = 36
RRF_CONSTANT = 60
MODEL_NAME = "intfloat/multilingual-e5-small"
MODEL_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
MODEL_FILE = "onnx/model.onnx"
EMBEDDING_DIMENSION = 384
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "
FOOTPRINT_LIMIT = 150_000_000
WARM_PROCESS_COUNT = 10
TOKEN_RE = re.compile(r"[\w./:-]+", re.UNICODE)
TRANSLITERATION = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "i",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def _finalize_packet(packet: dict[str, Any]) -> dict[str, Any]:
    result = dict(packet)
    result["packet_bytes"] = 0
    while True:
        actual = len(_json_bytes(result))
        if actual == result["packet_bytes"]:
            return result
        result["packet_bytes"] = actual


def _load_digest(path: Path) -> Any:
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("chat_digest_int8_source", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import parser: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_records(digest: Any, corpus: Path) -> tuple[list[dict[str, Any]], int]:
    records, diagnostics = digest.load(corpus)
    ids = [record["record_id"] for record in records]
    if len(ids) != len(set(ids)):
        raise RuntimeError("corpus contains duplicate immutable record IDs")
    return records, diagnostics


def _load_queries(paths: Iterable[Path]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in paths:
        payload = json.loads(path.read_text())
        if not isinstance(payload, list):
            raise TypeError(f"query file is not an array: {path}")
        for item in payload:
            case_id = item.get("case_id")
            variants = item.get("variants")
            if not isinstance(case_id, str) or not case_id or case_id in seen:
                raise RuntimeError(f"invalid or duplicate case_id: {case_id!r}")
            if not isinstance(item.get("query"), str) or not item["query"].strip():
                raise RuntimeError(f"invalid query: {case_id}")
            if (
                not isinstance(variants, list)
                or len(variants) > 3
                or any(not isinstance(value, str) or not value.strip() for value in variants)
            ):
                raise RuntimeError(f"invalid variants: {case_id}")
            seen.add(case_id)
            items.append(item)
    return items


def _dense_text(record: dict[str, Any]) -> str:
    note = record.get("context_note")
    return f"{record['text']}\n{note}" if note else record["text"]


def _corpus_manifest(records: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(record["record_id"].encode())
        digest.update(b"\0")
        digest.update(_dense_text(record).encode())
        digest.update(b"\0")
    return digest.hexdigest()


def _embedding_backend(model_dir: Path) -> Any:
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    from fastembed import TextEmbedding
    from fastembed.common.model_description import ModelSource, PoolingType
    from loguru import logger

    logger.disable("fastembed")
    known = {entry["model"].casefold() for entry in TextEmbedding.list_supported_models()}
    if MODEL_NAME.casefold() not in known:
        TextEmbedding.add_custom_model(
            model=MODEL_NAME,
            pooling=PoolingType.MEAN,
            normalization=True,
            sources=ModelSource(hf=MODEL_NAME),
            dim=EMBEDDING_DIMENSION,
            model_file=MODEL_FILE,
            description="One-shot dynamic-INT8 multilingual E5 small probe",
        )
    return TextEmbedding(
        model_name=MODEL_NAME,
        local_files_only=True,
        revision=MODEL_REVISION,
        specific_model_path=str(model_dir),
    )


def _embed(model: Any, texts: list[str]) -> np.ndarray:
    vectors = np.asarray(list(model.embed(texts, batch_size=64)), dtype=np.float32)
    if vectors.shape != (len(texts), EMBEDDING_DIMENSION):
        raise RuntimeError(
            f"unexpected embedding shape {vectors.shape}; "
            f"expected {(len(texts), EMBEDDING_DIMENSION)}"
        )
    return vectors


def _build_cache(
    digest_path: Path,
    corpus: Path,
    model_dir: Path,
    cache_path: Path,
) -> dict[str, Any]:
    if cache_path.exists():
        raise RuntimeError(f"isolated cache already exists: {cache_path}")
    digest = _load_digest(digest_path)
    records, diagnostics = _load_records(digest, corpus)
    started = perf_counter()
    model = _embedding_backend(model_dir)
    vectors = _embed(model, [PASSAGE_PREFIX + _dense_text(record) for record in records])
    ids = np.asarray([record["record_id"] for record in records])
    manifest = _corpus_manifest(records)
    np.savez(cache_path, record_ids=ids, vectors=vectors, corpus_manifest=manifest)
    return {
        "status": "built",
        "records": len(records),
        "diagnostics": diagnostics,
        "all_records_reembedded": True,
        "model_sha256": _sha256(model_dir / MODEL_FILE),
        "cache": str(cache_path),
        "cache_sha256": _sha256(cache_path),
        "cache_bytes": cache_path.stat().st_size,
        "corpus_manifest": manifest,
        "elapsed_s": round(perf_counter() - started, 6),
    }


def _load_cache(
    records: list[dict[str, Any]], cache_path: Path
) -> tuple[np.ndarray, dict[str, int]]:
    with np.load(cache_path, allow_pickle=False) as payload:
        record_ids = payload["record_ids"].tolist()
        vectors = np.asarray(payload["vectors"], dtype=np.float32)
        manifest = str(payload["corpus_manifest"].item())
    expected_ids = [record["record_id"] for record in records]
    if record_ids != expected_ids or manifest != _corpus_manifest(records):
        raise RuntimeError("isolated embedding cache does not match current corpus bytes")
    if vectors.shape != (len(records), EMBEDDING_DIMENSION):
        raise RuntimeError(f"invalid cache shape: {vectors.shape}")
    return vectors, {record_id: index for index, record_id in enumerate(record_ids)}


def _stem(token: str) -> str:
    token = token.casefold().strip("-_/.: ")
    if len(token) >= 7 and any("а" <= char <= "я" or char == "ё" for char in token):
        return token[:5]
    if len(token) >= 6:
        return token[:5]
    return token


def _anchor_variants(part: str) -> set[str]:
    raw = _stem(part)
    transliterated = _stem(part.casefold().translate(TRANSLITERATION))
    return {
        value
        for value in (raw, transliterated)
        if len(value) >= 4 or any(char.isdigit() for char in value)
    }


def _anchors(text: str) -> set[str]:
    result: set[str] = set()
    for raw in TOKEN_RE.findall(text):
        for part in re.split(r"[-_/.:]+", raw):
            result.update(_anchor_variants(part))
    return result


def _literal_identifier_anchors(text: str) -> set[str]:
    result: set[str] = set()
    for raw in TOKEN_RE.findall(text):
        for part in re.split(r"[-_/.:]+", raw):
            if re.search(r"[a-z\d]", part.casefold()):
                result.update(_anchor_variants(part))
    return result


def _record_search_text(record: dict[str, Any]) -> str:
    note = record.get("context_note")
    result = f"{record['type']} | {record['topic']} | {record['text']}"
    return f"{result} | {note}" if note else result


def _fused_lexical_order(
    digest: Any,
    records: list[dict[str, Any]],
    queries: list[str],
) -> list[str]:
    scores: dict[str, float] = defaultdict(float)
    best_rank: dict[str, int] = {}
    original_order = {
        record["record_id"]: index for index, record in enumerate(records)
    }
    for query in queries:
        for rank, record in enumerate(digest.search_bm25(records, query)[:LEXICAL_DEPTH], 1):
            record_id = record["record_id"]
            scores[record_id] += 1.0 / (RRF_CONSTANT + rank)
            best_rank[record_id] = min(best_rank.get(record_id, rank), rank)
    return sorted(
        scores,
        key=lambda record_id: (
            -scores[record_id],
            best_rank[record_id],
            original_order[record_id],
        ),
    )[:LEXICAL_DEPTH]


def _dense_order(
    records: list[dict[str, Any]],
    vectors: np.ndarray,
    query_vector: np.ndarray,
) -> list[str]:
    scores = vectors @ query_vector
    ranked = sorted(range(len(records)), key=lambda index: (-float(scores[index]), index))
    return [records[index]["record_id"] for index in ranked[:DENSE_DEPTH]]


def _interleave(left: list[str], right: list[str]) -> list[str]:
    result: list[str] = []
    for index in range(max(len(left), len(right))):
        for source in (left, right):
            if index < len(source) and source[index] not in result:
                result.append(source[index])
    return result


def _session_relations(
    records: list[dict[str, Any]],
    seed_ids: list[str],
    anchor_sets: dict[str, set[str]],
    frequency: Counter[str],
) -> dict[str, set[str]]:
    sessions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        sessions[record["session"]].append(record)
    positions: dict[str, int] = {}
    for session_records in sessions.values():
        session_records.sort(key=lambda item: (item["file"], item["line"]))
        for index, record in enumerate(session_records):
            positions[record["record_id"]] = index
    by_id = {record["record_id"]: record for record in records}
    result: dict[str, set[str]] = defaultdict(set)
    for seed_rank, record_id in enumerate(seed_ids, 1):
        record = by_id[record_id]
        session_records = sessions[record["session"]]
        index = positions[record_id]
        start = max(0, index - SESSION_RADIUS)
        stop = min(len(session_records), index + SESSION_RADIUS + 1)
        for adjacent in session_records[start:stop]:
            adjacent_id = adjacent["record_id"]
            offset = positions[adjacent_id] - index
            if not offset:
                continue
            shared = {
                anchor
                for anchor in anchor_sets[record_id] & anchor_sets[adjacent_id]
                if re.search(r"[a-z\d]", anchor) and frequency[anchor] <= 5
            }
            if seed_rank > UNCONDITIONAL_SESSION_SEEDS and not shared:
                continue
            suffix = ":" + min(shared) if shared else ""
            result[adjacent_id].add(f"S{seed_rank}{offset:+d}{suffix}")
    return result


def _identifier_relations(
    records: list[dict[str, Any]],
    query: str,
    seed_ids: list[str],
    anchor_sets: dict[str, set[str]],
    frequency: Counter[str],
) -> dict[str, set[str]]:
    by_id = {record["record_id"]: record for record in records}
    priorities = {anchor: 0 for anchor in _literal_identifier_anchors(query)}
    for seed_rank, record_id in enumerate(seed_ids, 1):
        for anchor in _literal_identifier_anchors(_record_search_text(by_id[record_id])):
            priorities.setdefault(anchor, seed_rank)
    priorities = {
        anchor: priority
        for anchor, priority in priorities.items()
        if 1 < frequency.get(anchor, 0) <= IDENTIFIER_MAXIMUM_FREQUENCY
    }
    result: dict[str, set[str]] = defaultdict(set)
    for record in records:
        for anchor in priorities.keys() & anchor_sets[record["record_id"]]:
            result[record["record_id"]].add(f"I{priorities[anchor]}:{anchor}")
    return result


def _preview(record: dict[str, Any]) -> str:
    return " ".join(record["text"].split())[:PREVIEW_CHARACTERS]


def _packet_for_case(
    digest: Any,
    records: list[dict[str, Any]],
    vectors: np.ndarray,
    model: Any,
    item: dict[str, Any],
) -> dict[str, Any]:
    started = perf_counter()
    query = item["query"]
    lexical = _fused_lexical_order(digest, records, [query, *item["variants"]])
    query_vector = _embed(model, [QUERY_PREFIX + query])[0]
    dense = _dense_order(records, vectors, query_vector)
    direct_order = _interleave(dense, lexical)
    direct_ids = set(direct_order)
    anchor_sets = {
        record["record_id"]: _anchors(_record_search_text(record)) for record in records
    }
    frequency = Counter(anchor for values in anchor_sets.values() for anchor in values)
    session = _session_relations(records, direct_order, anchor_sets, frequency)
    identifiers = _identifier_relations(
        records, query, direct_order, anchor_sets, frequency
    )
    origins: dict[str, set[str]] = defaultdict(set)
    for rank, record_id in enumerate(dense, 1):
        origins[record_id].add(f"D{rank}")
    for rank, record_id in enumerate(lexical, 1):
        origins[record_id].add(f"L{rank}")
    for record_id, routes in session.items():
        origins[record_id].update(routes)
    for record_id, routes in identifiers.items():
        origins[record_id].update(routes)

    def relation_rank(record_id: str, prefix: str) -> tuple[int, str, str]:
        ranks = [
            int(match.group(1))
            for route in origins[record_id]
            if (match := re.match(prefix + r"(\d+)", route))
        ]
        return (min(ranks, default=999), min(origins[record_id]), record_id)

    identifier_specials = sorted(
        set(identifiers) - direct_ids,
        key=lambda record_id: relation_rank(record_id, "I"),
    )[:IDENTIFIER_SPECIAL_LIMIT]
    session_specials = sorted(
        set(session) - direct_ids - set(identifier_specials),
        key=lambda record_id: relation_rank(record_id, "S"),
    )[:SESSION_SPECIAL_LIMIT]
    order = identifier_specials + session_specials + [
        record_id
        for record_id in direct_order
        if record_id not in identifier_specials and record_id not in session_specials
    ]
    by_id = {record["record_id"]: record for record in records}
    packet: dict[str, Any] = {
        "case_id": item["case_id"],
        "candidates": [],
        "returned": 0,
        "omitted": 0,
        "latency_s": 0.0,
    }
    considered = order[:MAX_CANDIDATES]
    for record_id in considered:
        candidate = {
            "id": record_id,
            "route": ",".join(sorted(origins[record_id])),
            "preview": _preview(by_id[record_id]),
        }
        trial = dict(packet)
        trial["candidates"] = packet["candidates"] + [candidate]
        trial["returned"] = len(trial["candidates"])
        trial["omitted"] = len(considered) - trial["returned"]
        if _finalize_packet(trial)["packet_bytes"] > MAX_PACKET_BYTES:
            break
        packet = trial
    packet["returned"] = len(packet["candidates"])
    packet["omitted"] = len(considered) - packet["returned"]
    packet["latency_s"] = round(perf_counter() - started, 6)
    packet = _finalize_packet(packet)
    while packet["packet_bytes"] > MAX_PACKET_BYTES and packet["candidates"]:
        packet["candidates"].pop()
        packet["returned"] = len(packet["candidates"])
        packet["omitted"] = len(considered) - packet["returned"]
        packet = _finalize_packet(packet)
    if packet["packet_bytes"] > MAX_PACKET_BYTES:
        raise RuntimeError("packet byte hard gate exceeded")
    return packet


def _runtime(
    digest_path: Path,
    corpus: Path,
    model_dir: Path,
    cache_path: Path,
) -> tuple[Any, list[dict[str, Any]], int, np.ndarray, Any]:
    digest = _load_digest(digest_path)
    records, diagnostics = _load_records(digest, corpus)
    vectors, _ = _load_cache(records, cache_path)
    model = _embedding_backend(model_dir)
    return digest, records, diagnostics, vectors, model


def _score_packets(
    packets: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    gold_path: Path,
) -> dict[str, Any]:
    gold = json.loads(gold_path.read_text())
    query_ids = [item["case_id"] for item in queries]
    packet_ids = [packet["case_id"] for packet in packets]
    groups = {
        "characterization": [item["case_id"] for item in queries[:7]],
        "blind_dev": [item["case_id"] for item in queries[7:]],
    }
    results: dict[str, Any] = {}
    packet_by_id = {packet["case_id"]: packet for packet in packets}
    for group, case_ids in groups.items():
        cases = []
        for case_id in case_ids:
            mandatory = gold[group][case_id]
            emitted = {candidate["id"] for candidate in packet_by_id[case_id]["candidates"]}
            missing = [record_id for record_id in mandatory if record_id not in emitted]
            cases.append(
                {
                    "case_id": case_id,
                    "mandatory": mandatory,
                    "missing": missing,
                    "pass": not missing,
                }
            )
        results[group] = {
            "passed": sum(case["pass"] for case in cases),
            "total": len(cases),
            "cases": cases,
        }
    return {
        "inputs_exactly_once": query_ids == packet_ids and len(packet_ids) == len(set(packet_ids)),
        "packet_count": len(packets),
        "maximum_packet_bytes": max(packet["packet_bytes"] for packet in packets),
        "maximum_candidates": max(packet["returned"] for packet in packets),
        "groups": results,
    }


def _run_all(args: argparse.Namespace) -> dict[str, Any]:
    queries = _load_queries(args.query_files)
    digest, records, diagnostics, vectors, model = _runtime(
        args.digest_script, args.corpus, args.model_dir, args.cache
    )
    packets = [
        _packet_for_case(digest, records, vectors, model, item) for item in queries
    ]
    return {
        "schema": 1,
        "method": {
            "model": MODEL_NAME,
            "revision": MODEL_REVISION,
            "quantization": "ORT quantize_dynamic QInt8/default",
            "dense_depth": DENSE_DEPTH,
            "lexical": "BM25 original+owner-independent variants, RRF",
            "relations": "session-radius-2+rare-transliterated-identifiers",
            "ordering": "relation-specials then dense/lexical interleave",
            "semantic_authority": False,
            "cross_encoder": False,
            "ann": False,
        },
        "records": len(records),
        "diagnostics": diagnostics,
        "score": _score_packets(packets, queries, args.gold),
        "packets": packets,
    }


def _run_one(args: argparse.Namespace) -> dict[str, Any]:
    queries = _load_queries(args.query_files)
    if args.case_index < 0 or args.case_index >= len(queries):
        raise RuntimeError(f"case index out of bounds: {args.case_index}")
    started = perf_counter()
    digest, records, diagnostics, vectors, model = _runtime(
        args.digest_script, args.corpus, args.model_dir, args.cache
    )
    packet = _packet_for_case(
        digest, records, vectors, model, queries[args.case_index]
    )
    return {
        "case_id": packet["case_id"],
        "process_elapsed_s": round(perf_counter() - started, 6),
        "records": len(records),
        "diagnostics": diagnostics,
        "packet": packet,
    }


def _benchmark(args: argparse.Namespace) -> dict[str, Any]:
    queries = _load_queries(args.query_files)
    base = [
        sys.executable,
        str(Path(__file__).resolve()),
        "run-one",
        "--digest-script",
        str(args.digest_script),
        "--corpus",
        str(args.corpus),
        "--model-dir",
        str(args.model_dir),
        "--cache",
        str(args.cache),
    ]
    for path in args.query_files:
        base.extend(("--query-file", str(path)))
    samples = []
    for index in range(WARM_PROCESS_COUNT + 1):
        case_index = index % len(queries)
        command = [*base, "--case-index", str(case_index)]
        started = perf_counter()
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        wall = perf_counter() - started
        child = json.loads(completed.stdout)
        samples.append(
            {
                "ordinal": index,
                "classification": "cold-first" if index == 0 else "warm",
                "case_id": child["case_id"],
                "wall_s": round(wall, 6),
                "child_elapsed_s": child["process_elapsed_s"],
                "packet_bytes": child["packet"]["packet_bytes"],
            }
        )
    warm = sorted(sample["wall_s"] for sample in samples[1:])
    rank = max(0, math.ceil(0.95 * len(warm)) - 1)
    return {
        "separate_process": True,
        "cold_first_wall_s": samples[0]["wall_s"],
        "warm_queries": len(warm),
        "warm_p95_wall_s": warm[rank],
        "warm_p95_method": "nearest-rank",
        "samples": samples,
        "command_prefix": base,
    }


def _footprint(model_dir: Path, cache_path: Path) -> dict[str, Any]:
    files = sorted(path for path in model_dir.rglob("*") if path.is_file()) + [cache_path]
    entries = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": _sha256(path)}
        for path in files
    ]
    total = sum(entry["bytes"] for entry in entries)
    return {
        "files": entries,
        "total_bytes": total,
        "limit_bytes": FOOTPRINT_LIMIT,
        "pass": total <= FOOTPRINT_LIMIT,
        "excludes": ["build-only onnx dependency", "source FP32 ONNX"],
    }


def _assess(run_path: Path, benchmark_path: Path, footprint_path: Path) -> dict[str, Any]:
    run = json.loads(run_path.read_text())
    benchmark = json.loads(benchmark_path.read_text())
    footprint = json.loads(footprint_path.read_text())
    score = run["score"]
    gates = {
        "characterization_7_of_7": score["groups"]["characterization"]["passed"] == 7,
        "blind_dev_10_of_10": score["groups"]["blind_dev"]["passed"] == 10,
        "dense_depth_exactly_8": run["method"]["dense_depth"] == 8,
        "inputs_exactly_once": score["inputs_exactly_once"],
        "packet_bytes_at_most_4000": score["maximum_packet_bytes"] <= MAX_PACKET_BYTES,
        "candidates_at_most_48": score["maximum_candidates"] <= MAX_CANDIDATES,
        "warm_p95_below_1_second": benchmark["warm_p95_wall_s"] < 1.0,
        "footprint_at_most_150000000": footprint["total_bytes"] <= FOOTPRINT_LIMIT,
    }
    passed = all(gates.values())
    return {
        "verdict": "PASS" if passed else "REJECT",
        "licenses": "one frozen fresh-holdout candidate; not acceptance" if passed else None,
        "gates": gates,
        "observed": {
            "characterization": score["groups"]["characterization"]["passed"],
            "blind_dev": score["groups"]["blind_dev"]["passed"],
            "maximum_packet_bytes": score["maximum_packet_bytes"],
            "maximum_candidates": score["maximum_candidates"],
            "warm_p95_wall_s": benchmark["warm_p95_wall_s"],
            "footprint_bytes": footprint["total_bytes"],
        },
    }


def _quantize(source_model: Path, source_assets: Path, model_dir: Path) -> dict[str, Any]:
    output = model_dir / MODEL_FILE
    if output.exists():
        raise RuntimeError(f"quantized output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=False)
    for name in (
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
    ):
        shutil.copyfile(source_assets / name, model_dir / name)
    from onnxruntime.quantization import QuantType, quantize_dynamic

    started = perf_counter()
    quantize_dynamic(str(source_model), str(output), weight_type=QuantType.QInt8)
    return {
        "status": "quantized-once",
        "configuration": "quantize_dynamic(weight_type=QuantType.QInt8); defaults otherwise",
        "source": str(source_model),
        "source_bytes": source_model.stat().st_size,
        "source_sha256": _sha256(source_model),
        "output": str(output),
        "output_bytes": output.stat().st_size,
        "output_sha256": _sha256(output),
        "elapsed_s": round(perf_counter() - started, 6),
    }


def _common_runtime(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--digest-script", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    quantize = commands.add_parser("quantize")
    quantize.add_argument("--source-model", type=Path, required=True)
    quantize.add_argument("--source-assets", type=Path, required=True)
    quantize.add_argument("--model-dir", type=Path, required=True)
    build_cache = commands.add_parser("build-cache")
    _common_runtime(build_cache)
    for name in ("run-all", "run-one", "benchmark"):
        subparser = commands.add_parser(name)
        _common_runtime(subparser)
        subparser.add_argument(
            "--query-file", dest="query_files", type=Path, action="append", required=True
        )
        if name == "run-all":
            subparser.add_argument("--gold", type=Path, required=True)
        if name == "run-one":
            subparser.add_argument("--case-index", type=int, required=True)
    footprint = commands.add_parser("footprint")
    footprint.add_argument("--model-dir", type=Path, required=True)
    footprint.add_argument("--cache", type=Path, required=True)
    assess = commands.add_parser("assess")
    assess.add_argument("--run", type=Path, required=True)
    assess.add_argument("--benchmark", type=Path, required=True)
    assess.add_argument("--footprint", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "quantize":
        result = _quantize(args.source_model, args.source_assets, args.model_dir)
    elif args.command == "build-cache":
        result = _build_cache(
            args.digest_script, args.corpus, args.model_dir, args.cache
        )
    elif args.command == "run-all":
        result = _run_all(args)
    elif args.command == "run-one":
        result = _run_one(args)
    elif args.command == "benchmark":
        result = _benchmark(args)
    elif args.command == "footprint":
        result = _footprint(args.model_dir, args.cache)
    elif args.command == "assess":
        result = _assess(args.run, args.benchmark, args.footprint)
    else:
        raise AssertionError(args.command)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
