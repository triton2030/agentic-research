from __future__ import annotations

from pathlib import Path

from md_cli.catalog import TOOLS


ROOT = Path(__file__).resolve().parents[1]


def test_catalog_signatures_match_canonical_doc() -> None:
    signatures = {}
    for line in (ROOT / "docs/cli-signatures-canonical.md").read_text().splitlines():
        if not line.startswith("| md_"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        signatures[parts[0]] = parts[2].strip("`")
    for tool in TOOLS:
        assert tool.cli_signature == signatures[tool.name]

