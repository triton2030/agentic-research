#!/usr/bin/env python3
"""Run the pinned Russian paraphrase regression against a recall corpus."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_digest.py"
CASES = Path(__file__).with_name("retrieval_cases.json")
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))


def _load_digest(path: Path, module_name: str = "chat_digest_eval") -> Any:
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    digest = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(digest)
    return digest


DIGEST = _load_digest(SCRIPT)

FIXTURE_SCHEMA = 1


def _load_fixture(path: Path) -> tuple[str, list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("top level must be an object")
    if payload.get("schema") != FIXTURE_SCHEMA:
        raise ValueError(f"schema must equal {FIXTURE_SCHEMA}")
    corpus = payload.get("corpus")
    if not isinstance(corpus, dict) or not isinstance(corpus.get("project"), str):
        raise ValueError("corpus.project must be a string")
    project = corpus["project"].strip()
    if not project:
        raise ValueError("corpus.project must not be empty")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"cases[{index}] must be an object")
        if not isinstance(case.get("id"), str) or not case["id"].strip():
            raise ValueError(f"cases[{index}].id must be a non-empty string")
        if not isinstance(case.get("query"), str) or not case["query"].strip():
            raise ValueError(f"cases[{index}].query must be a non-empty string")
        relevant = case.get("relevant")
        relevant_files = case.get("relevant_files")
        record_targets_valid = (
            isinstance(relevant, list)
            and bool(relevant)
            and all(isinstance(record_id, str) and record_id for record_id in relevant)
        )
        file_targets_valid = (
            isinstance(relevant_files, list)
            and bool(relevant_files)
            and all(
                isinstance(filename, str) and filename
                for filename in relevant_files
            )
        )
        if record_targets_valid == file_targets_valid:
            raise ValueError(
                f"cases[{index}] must define exactly one non-empty string list: "
                "relevant or relevant_files"
            )
    return project, cases


def _fixture_corpus_error(
    records: list[dict[str, Any]],
    project: str,
    cases: list[dict[str, Any]],
) -> dict[str, Any] | None:
    projects = sorted(
        {
            record["project"]
            for record in records
            if isinstance(record.get("project"), str) and record["project"]
        }
    )
    if project not in projects:
        return {
            "error": "corpus-mismatch",
            "expected": {"project": project},
            "found": {"projects": projects},
        }

    targets = {
        record_id for case in cases for record_id in case.get("relevant", [])
    }
    by_id: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_id.setdefault(record["record_id"], []).append(record)
    missing = sorted(targets - set(by_id))
    if missing:
        return {"error": "missing-targets", "record_ids": missing}

    wrong_project: dict[str, list[str]] = {}
    for record_id in targets:
        target_projects = {record.get("project") for record in by_id[record_id]}
        if target_projects != {project}:
            wrong_project[record_id] = sorted(
                value if isinstance(value, str) and value else "<missing>"
                for value in target_projects
            )
    if wrong_project:
        return {
            "error": "target-project-mismatch",
            "expected": {"project": project},
            "record_projects": wrong_project,
        }
    return None


def _ranking(
    corpus: Path,
    query: str,
    *,
    lexical: bool,
    script: Path = SCRIPT,
) -> list[str]:
    if lexical:
        command = [sys.executable, str(script)]
    else:
        command = [
            "uv",
            "run",
            "--offline",
            "--locked",
            "--script",
            str(script),
        ]
    command.extend(
        (
            str(corpus),
            "--query",
            query,
            "--json",
            "--limit",
            "10",
            "--max-chars",
            "200000",
        )
    )
    if lexical:
        command.append("--lexical")
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise RuntimeError(f"cannot start retrieval command: {error}") from error
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"retrieval command failed: {detail}")
    payload = json.loads(completed.stdout)
    holders = sorted(
        payload["holders"],
        key=lambda holder: holder["semantic_rank"],
    )
    return [holder["file"] for holder in holders]


def _file_relevance(
    records: list[dict[str, Any]], cases: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    files_by_record_id: dict[str, list[str]] = {}
    for record in records:
        files_by_record_id.setdefault(record["record_id"], []).append(record["file"])
    result: list[dict[str, Any]] = []
    for case in cases:
        if "relevant_files" in case:
            result.append({**case, "relevant": case["relevant_files"]})
            continue
        files = list(
            dict.fromkeys(
                filename
                for record_id in case["relevant"]
                for filename in files_by_record_id[record_id]
            )
        )
        result.append({**case, "relevant": files})
    return result


def _metrics(
    cases: list[dict[str, Any]], rankings: list[list[str]]
) -> tuple[dict[str, float], list[str]]:
    positions: list[float] = []
    coverage_at_ten: list[float] = []
    failed_at_five: list[str] = []
    for case, ranking in zip(cases, rankings, strict=True):
        found = [
            ranking.index(record_id) + 1
            for record_id in case["relevant"]
            if record_id in ranking
        ]
        position = min(found) if found else math.inf
        positions.append(position)
        coverage_at_ten.append(
            sum(filename in ranking[:10] for filename in case["relevant"])
            / len(case["relevant"])
        )
        if position > 5:
            failed_at_five.append(case["id"])
    count = len(cases)
    return (
        {
            "hit@1": round(sum(position <= 1 for position in positions) / count, 3),
            "hit@5": round(sum(position <= 5 for position in positions) / count, 3),
            "hit@10": round(sum(position <= 10 for position in positions) / count, 3),
            "coverage@10": round(sum(coverage_at_ten) / count, 3),
            "mrr@10": round(
                sum(0.0 if position > 10 else 1.0 / position for position in positions)
                / count,
                3,
            ),
        },
        failed_at_five,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--cases", type=Path, default=CASES)
    parser.add_argument("--digest-script", type=Path, default=SCRIPT)
    parser.add_argument("--min-hit-at-five", type=float, default=0.90)
    args = parser.parse_args()

    digest = (
        DIGEST
        if args.digest_script.resolve() == SCRIPT.resolve()
        else _load_digest(args.digest_script.resolve(), "chat_digest_eval_candidate")
    )
    records, _ = digest.load(args.corpus)
    try:
        project, cases = _load_fixture(args.cases)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(
            json.dumps(
                {
                    "error": "cases-schema",
                    "fixture": str(args.cases),
                    "detail": str(error),
                },
                ensure_ascii=False,
            )
        )
        return 2
    corpus_error = _fixture_corpus_error(records, project, cases)
    if corpus_error:
        print(json.dumps(corpus_error, ensure_ascii=False))
        return 2
    evaluation_cases = _file_relevance(records, cases)

    lexical_rankings: list[list[str]] = []
    hybrid_rankings: list[list[str]] = []
    for case in evaluation_cases:
        lexical_rankings.append(
            _ranking(
                args.corpus,
                case["query"],
                lexical=True,
                script=args.digest_script,
            )
        )
        hybrid_rankings.append(
            _ranking(
                args.corpus,
                case["query"],
                lexical=False,
                script=args.digest_script,
            )
        )

    lexical, lexical_failed = _metrics(evaluation_cases, lexical_rankings)
    hybrid, hybrid_failed = _metrics(evaluation_cases, hybrid_rankings)
    passed = (
        hybrid["hit@5"] >= args.min_hit_at_five
        and hybrid["hit@5"] > lexical["hit@5"]
    )
    print(
        json.dumps(
            {
                "corpus": {
                    "fixture_project": project,
                    "observed_projects": sorted(
                        {
                            record["project"]
                            for record in records
                            if isinstance(record.get("project"), str)
                            and record["project"]
                        }
                    ),
                },
                "records": len(records),
                "cases": len(cases),
                "relevance_unit": "file",
                "digest_script": str(args.digest_script),
                "model": digest.EMBEDDING_MODEL,
                "revision": digest.EMBEDDING_REVISION,
                "hybrid_depth": digest.HYBRID_DEPTH,
                "lexical": lexical,
                "hybrid": hybrid,
                "delta_hit@5": round(hybrid["hit@5"] - lexical["hit@5"], 3),
                "failed_at_five": {
                    "lexical": lexical_failed,
                    "hybrid": hybrid_failed,
                },
                "threshold": {"min_hybrid_hit@5": args.min_hit_at_five},
                "passed": passed,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
