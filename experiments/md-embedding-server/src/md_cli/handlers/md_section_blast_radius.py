from __future__ import annotations

from md_cli.catalog import from_catalog
from md_cli.handlers._generic import run_tool
from md_cli.result import ToolResult


@from_catalog('md_section_blast_radius')
def run(args) -> ToolResult:
    return run_tool('md_section_blast_radius', args)
