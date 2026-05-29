from __future__ import annotations

import importlib
import json
from pathlib import Path

from md_cli.catalog import TOOLS_BY_ID
from md_cli.main import build_parser
from md_cli.result import ToolResult


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"

ATOMIC_COMMANDS = {
    "md_ping": ["ping", "--json"],
    "md_status": ["status", str(CORPUS), "--json"],
    "md_ls": ["ls", str(CORPUS), "--json"],
    "md_toc": ["toc", str(CORPUS), "--json"],
    "md_read_related": ["read-related", "--paths", str(README), "--scan", str(CORPUS), "--json"],
    "md_importance": ["importance", str(CORPUS), "--json"],
    "md_extract": ["extract", "--map-data", json.dumps({"root": str(CORPUS), "files": []}), "--json"],
    "md_search": ["search", str(CORPUS), "--query", "sample", "--json"],
    "md_overlaps": ["overlaps", str(CORPUS), "--json"],
    "md_repeated_concepts": ["repeated-concepts", str(CORPUS), "--json"],
    "md_audit": ["audit", str(CORPUS), "--json"],
    "md_corpus_scan": ["corpus-scan", str(CORPUS), "--json"],
    "md_index": ["index", str(CORPUS), "--dry-run", "--allow-nested-corpus", "--json"],
    "md_init": ["init", "--paths", str(CORPUS), "--dry-run", "--json"],
    "md_strip": ["strip", "--paths", str(CORPUS), "--dry-run", "--json"],
    "md_profile_sections": ["profile-sections", str(CORPUS), "--dry-run", "--mode", "llm", "--json"],
    "md_scan": ["scan", "--paths", str(CORPUS), "--json"],
    "md_check": ["check", "--paths", str(CORPUS), "--json"],
    "md_health": ["health", "--paths", str(CORPUS), "--json"],
    "md_cycles": ["cycles", "--paths", str(CORPUS), "--json"],
    "md_deps": ["deps", str(README), "--scan", str(CORPUS), "--json"],
    "md_impact": ["impact", str(README), "--scan", str(CORPUS), "--json"],
    "md_preflight": ["preflight", str(README), "--scan", str(CORPUS), "--json"],
    "md_cluster": ["cluster", str(CORPUS), "--json"],
    "md_coherence_audit": ["coherence-audit", str(README), "--scan", str(CORPUS), "--json"],
}


def test_25_atomic_handlers_return_tool_result() -> None:
    parser = build_parser()
    assert len(ATOMIC_COMMANDS) == 25
    for tool_id, argv in ATOMIC_COMMANDS.items():
        args = parser.parse_args(argv)
        module = importlib.import_module(TOOLS_BY_ID[tool_id].handler_module)
        result = module.run(args)
        assert isinstance(result, ToolResult), tool_id
        assert isinstance(result.payload, dict), tool_id
        assert result.exit_code in {0, 1, 2, 3, 4}, tool_id


def test_atomic_handlers_are_thin() -> None:
    for tool_id in ATOMIC_COMMANDS:
        spec = TOOLS_BY_ID[tool_id]
        path = ROOT / "src" / Path(spec.handler_module.replace(".", "/")).with_suffix(".py")
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(lines) <= 30, spec.handler_module
        text = "\n".join(lines)
        assert "md_cli.envelope" not in text
        assert "print(" not in text
        assert "sys.exit" not in text


def test_atomic_help_works_for_all_25() -> None:
    parser = build_parser()
    for _tool_id, argv in ATOMIC_COMMANDS.items():
        try:
            parser.parse_args([argv[0], "--help"])
        except SystemExit as exc:
            assert exc.code == 0
