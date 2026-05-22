from __future__ import annotations

from md_cli.catalog import TOOLS, get_tool
from md_cli.result import ToolResult


def run(args) -> ToolResult:
    tool_name = getattr(args, "tool_name", None)
    if tool_name:
        spec = get_tool(tool_name)
        if spec is None:
            return ToolResult({"error": "unknown_tool", "tool": tool_name}, 2)
        if getattr(args, "json", False):
            return ToolResult({"tool": spec.to_dict()})
        return ToolResult({"_human": _render_detail(spec)})
    if getattr(args, "json", False):
        return ToolResult({"tools": [tool.to_dict() for tool in TOOLS]})
    return ToolResult({"_human": _render_list()})


def _render_list() -> str:
    lines = ["md CLI tools", ""]
    for tool in TOOLS:
        lines.append(f"{tool.name:24} {tool.category:8} {tool.summary}")
    return "\n".join(lines)


def _render_detail(tool) -> str:
    desc = tool.description
    return "\n".join(
        [
            tool.name,
            "",
            f"Category: {tool.category}",
            f"CLI: {tool.cli_signature}",
            "",
            f"WHEN: {desc.get('when', '')}",
            f"WHY: {desc.get('why', '')}",
            f"INPUT: {desc.get('input', '')}",
            f"OUTPUT: {desc.get('output', '')}",
            f"ALT: {desc.get('alt', '')}",
            f"COST: {desc.get('cost', '')}",
        ]
    )

