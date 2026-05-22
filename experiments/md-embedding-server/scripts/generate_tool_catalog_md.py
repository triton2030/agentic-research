#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from md_cli.catalog import TOOLS  # noqa: E402


def _cli_command(tool) -> str:
    parts = tool.cli_signature.split()
    return " ".join(parts[:2])


def _cli_text(text: str) -> str:
    replacements = {
        tool.name: _cli_command(tool)
        for tool in sorted(TOOLS, key=lambda item: len(item.name), reverse=True)
    }
    out = text
    for old, new in replacements.items():
        out = out.replace(old, new)
    out = out.replace("md_* tools", "md CLI commands")
    out = out.replace("md_*", "md CLI")
    out = out.replace("MCP wiring after restart", "CLI installation after restart")
    out = out.replace("server alive", "CLI import path is alive")
    out = out.replace("claude mcp list / Codex /mcp to verify connection", "md --version / md tools --json to verify the CLI")
    out = out.replace("MCP never edits", "CLI never auto-edits")
    return out


def main() -> int:
    print("# md CLI tools — каталог")
    print()
    print("Сгенерировано автоматически. Не править руками.")
    print()
    print("| Command | Category | WHEN | CLI signature |")
    print("|---|---|---|---|")
    for tool in TOOLS:
        when = _cli_text(tool.description.get("when", "")).replace("|", "\\|")
        print(f"| {_cli_command(tool)} | {tool.category} | {when} | `{tool.cli_signature}` |")
    print()
    print("## Полные описания")
    for tool in TOOLS:
        desc = tool.description
        print()
        print(f"### {_cli_command(tool)}")
        print()
        print(f"**WHEN**: {_cli_text(desc.get('when', ''))}")
        print()
        print(f"**WHY**: {_cli_text(desc.get('why', ''))}")
        print()
        print(f"**INPUT**: {_cli_text(desc.get('input', ''))}")
        print()
        print(f"**OUTPUT**: {_cli_text(desc.get('output', ''))}")
        print()
        print(f"**ALT**: {_cli_text(desc.get('alt', ''))}")
        print()
        print(f"**COST**: {_cli_text(desc.get('cost', ''))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
