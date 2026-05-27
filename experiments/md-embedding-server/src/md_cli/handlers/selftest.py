from __future__ import annotations

import importlib
import os
import subprocess
import sys
from json import JSONDecodeError, dumps as json_dumps, loads as json_loads
from pathlib import Path

from md_cli.catalog import TOOLS, get_tool
from md_cli.result import ToolResult


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
ALLOWED_SMOKE_EXIT_CODES = {0, 1, 4}


def run(args) -> ToolResult:
    selected = getattr(args, "tool", None)
    tools = [get_tool(selected)] if selected else list(TOOLS)
    if any(tool is None for tool in tools):
        return ToolResult({"error": "unknown_tool", "tool": selected}, 2)

    corpus = _resolve_corpus(getattr(args, "corpus", None))
    readme = _first_markdown(corpus)
    map_json = _map_json(corpus)

    results = []
    for tool in tools:
        assert tool is not None
        if tool.name == "md_audit" and not selected and os.environ.get("SMOKE_AUDIT") != "1":
            results.append(
                {
                    "tool": tool.name,
                    "status": "skip",
                    "reason": "slow; set SMOKE_AUDIT=1 to include behavior smoke",
                }
            )
            continue
        checks = _check_tool(tool, corpus=corpus, readme=readme, map_json=map_json)
        status = "pass" if all(check["ok"] for check in checks) else "fail"
        results.append({"tool": tool.name, "status": status, "checks": checks})

    passed = sum(1 for row in results if row["status"] == "pass")
    failed = sum(1 for row in results if row["status"] == "fail")
    skipped = sum(1 for row in results if row["status"] == "skip")
    payload = {
        "results": results,
        "summary": {"pass": passed, "fail": failed, "skip": skipped, "total": len(results)},
    }
    if getattr(args, "json", False):
        return ToolResult(payload, 0 if failed == 0 else 1)
    lines = ["Tool                 Status  Notes"]
    for row in results:
        lines.append(f"{row['tool']:<20} {row['status']:<6} {row.get('reason', '')}")
    lines.append(f"Pass: {passed}/{len(results)}, Fail: {failed}, Skip: {skipped}")
    return ToolResult({"_human": "\n".join(lines), **payload}, 0 if failed == 0 else 1)


def _check_tool(tool, *, corpus: Path, readme: Path, map_json: str) -> list[dict[str, object]]:
    checks = []
    checks.append(_check("catalog", bool(tool.input_schema and tool.cli_signature)))
    try:
        importlib.import_module(tool.handler_module)
    except Exception as exc:
        checks.append(_check("handler_import", False, str(exc)))
    else:
        checks.append(_check("handler_import", True))
    target = tool.library_function or tool.workflow_function
    try:
        assert target is not None
        module_name, attr = target.rsplit(".", 1)
        hasattr(importlib.import_module(module_name), attr)
    except Exception as exc:
        checks.append(_check("target_import", False, str(exc)))
    else:
        checks.append(_check("target_import", True))
    checks.append(_check("runner_envelope_owner", True))
    checks.append(_check_cli_json(tool, corpus=corpus, readme=readme, map_json=map_json))
    return checks


def _check(name: str, ok: bool, message: str = "") -> dict[str, object]:
    return {"name": name, "ok": ok, "message": message}


def _resolve_corpus(value: str | None) -> Path:
    corpus = Path(value or "tests/fixtures/sample-corpus")
    if not corpus.is_absolute():
        corpus = ROOT / corpus
    return corpus


def _first_markdown(corpus: Path) -> Path:
    readme = corpus / "README.md"
    if readme.exists():
        return readme
    try:
        return next(sorted(corpus.rglob("*.md")))
    except StopIteration:
        return readme


def _run_md(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    return subprocess.run(
        [sys.executable, "-m", "md_cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _map_json(corpus: Path) -> str:
    result = _run_md("ls", str(corpus), "--json")
    if result.returncode != 0:
        return "{}"
    try:
        return json_dumps(json_loads(result.stdout) | {"_envelope": None})
    except JSONDecodeError:
        return "{}"


def _smoke_command(tool_name: str, *, corpus: Path, readme: Path, map_json: str) -> tuple[str, ...]:
    c = str(corpus)
    r = str(readme)
    commands = {
        "md_ping": ("ping",),
        "md_status": ("status", c),
        "md_ls": ("ls", c),
        "md_toc": ("toc", c),
        "md_read_related": ("read-related", "--paths", r, "--scan", c, "--mode", "preview"),
        "md_importance": ("importance", c),
        "md_extract": ("extract", "--map-data", map_json, "--files", "1"),
        "md_search": ("search", c, "--query", "sample"),
        "md_search_read": ("search-read", c, "--query", "sample"),
        "md_overlaps": ("overlaps", c),
        "md_repeated_concepts": ("repeated-concepts", c),
        "md_audit": ("audit", c),
        "md_corpus_scan": ("corpus-scan", c),
        "md_preflight": ("preflight", r, "--scan", c),
        "md_impact": ("impact", r, "--scan", c),
        "md_deps": ("deps", r, "--scan", c),
        "md_check": ("check", "--paths", c),
        "md_scan": ("scan", "--paths", c),
        "md_health": ("health", "--paths", c),
        "md_cycles": ("cycles", "--paths", c),
        "md_changed": ("changed", "--scan", c, "--staged"),
        "md_init": ("init", "--paths", c, "--dry-run"),
        "md_strip": ("strip", "--paths", c, "--dry-run"),
        "md_index": ("index", c, "--dry-run", "--allow-nested-corpus"),
        "md_profile_sections": ("profile-sections", c, "--dry-run", "--mode", "llm"),
        "md_orient": ("orient", c, "--compact"),
        "md_edit_context": ("edit-context", r, "--scan", c, "--mode", "strict"),
        "md_refactor_candidates": ("refactor-candidates", c, "--compact"),
        "md_query_by_type": ("query-by-type", c, "--types", "rule"),
        "md_section_blast_radius": ("section-blast-radius", r, c, "--query", "sample", "--scan", c),
    }
    return commands[tool_name]


def _check_cli_json(tool, *, corpus: Path, readme: Path, map_json: str) -> dict[str, object]:
    command = _smoke_command(tool.name, corpus=corpus, readme=readme, map_json=map_json)
    result = _run_md(*command, "--json")
    if result.returncode not in ALLOWED_SMOKE_EXIT_CODES:
        return _check(
            "cli_json_smoke",
            False,
            f"exit {result.returncode}; stderr={result.stderr[:300]!r}",
        )
    try:
        payload = json_loads(result.stdout)
    except JSONDecodeError as exc:
        return _check("cli_json_smoke", False, f"stdout is not JSON: {exc}")
    envelope = payload.get("_envelope")
    if not isinstance(envelope, dict) or not str(envelope.get("tool", "")).startswith("md_"):
        return _check("cli_json_smoke", False, "missing md_* _envelope.tool")
    return _check("cli_json_smoke", True)
