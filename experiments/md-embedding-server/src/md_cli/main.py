from __future__ import annotations

import argparse
import importlib
import sys
import re
from typing import Any, Sequence

from . import __version__
from .catalog import TOOLS, ToolSpec
from .runner import run_tool


def _add_placeholder_subparser(subparsers: argparse._SubParsersAction, tool: ToolSpec) -> None:
    parser = subparsers.add_parser(
        tool.subcommand,
        help=tool.summary,
        description=f"{tool.summary}\n\nCanonical signature: {tool.cli_signature}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _add_signature_args(parser, tool)
    parser.set_defaults(_tool=tool)


def _add_signature_args(parser: argparse.ArgumentParser, tool: ToolSpec) -> None:
    required = set(tool.input_schema.get("required") or [])
    properties = tool.input_schema.get("properties") or {}
    seen: set[str] = set()
    body = tool.cli_signature.removeprefix("md ").split(maxsplit=1)
    if len(body) < 2:
        parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
        return
    raw_tokens = re.findall(r"\[[^\]]+\]|\S+", body[1])
    tokens: list[str] = []
    for raw in raw_tokens:
        if raw.startswith("[") and raw.endswith("]"):
            parts = raw[1:-1].split()
            if len(parts) > 1:
                tokens.extend(f"[{part}]" for part in parts)
            else:
                tokens.append(raw)
        else:
            tokens.append(raw)
    index = 0
    while index < len(tokens):
        token = tokens[index]
        optional = token.startswith("[") and token.endswith("]")
        bare = token[1:-1] if optional else token
        if bare.startswith("--"):
            flag = bare
            key = flag[2:].replace("-", "_")
            if key in seen:
                index += 1
                continue
            seen.add(key)
            next_token = tokens[index + 1] if index + 1 < len(tokens) else ""
            next_bare = next_token[1:-1] if next_token.startswith("[") and next_token.endswith("]") else next_token
            schema = properties.get(key, {})
            help_text = _schema_help(schema)
            if next_bare and not next_bare.startswith("--") and next_bare.upper() == next_bare:
                kwargs: dict[str, Any] = {
                    "dest": key,
                    "required": key in required,
                    "help": help_text,
                }
                if schema.get("type") == "integer":
                    kwargs["type"] = int
                elif schema.get("type") == "number":
                    kwargs["type"] = float
                if schema.get("type") == "array":
                    kwargs["action"] = "append"
                if "enum" in schema:
                    kwargs["choices"] = schema["enum"]
                parser.add_argument(flag, **kwargs)
                index += 2
                continue
            parser.add_argument(flag, dest=key, action="store_true", help=help_text)
            index += 1
            continue
        if bare.upper() == bare:
            name = bare.lower()
            kwargs: dict[str, Any] = {"help": _schema_help(properties.get(name, {}))}
            if optional:
                kwargs["nargs"] = "?"
            parser.add_argument(name, **kwargs)
        index += 1
    if "json" not in seen:
        parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")


def _schema_help(schema: dict[str, Any]) -> str | None:
    description = schema.get("description")
    if description:
        return str(description)
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="md", description="Markdown corpus tools.")
    parser.add_argument(
        "--version",
        action="version",
        version=f"md-tools {__version__}",
    )
    parser.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="subcommand", metavar="subcommand")
    tools_parser = subparsers.add_parser(
        "tools",
        help="Show the md-tools catalog.",
        description="Show the md-tools catalog.",
    )
    tools_parser.add_argument("tool_name", nargs="?", help="Optional MCP tool id or CLI subcommand.")
    tools_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    tools_parser.set_defaults(_handler_module="md_cli.handlers.tools", _tool_name="md_tools")
    selftest_parser = subparsers.add_parser("selftest", help="Run md-tools self checks.")
    selftest_parser.add_argument("--corpus", default="tests/fixtures/sample-corpus", help="Fixture corpus path.")
    selftest_parser.add_argument("--tool", default=None, help="Run one MCP tool id or CLI subcommand.")
    selftest_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    selftest_parser.set_defaults(_handler_module="md_cli.handlers.selftest", _tool_name="md_selftest")
    doctor_parser = subparsers.add_parser("doctor", help="Diagnose local md-tools installation.")
    doctor_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    doctor_parser.set_defaults(_handler_module="md_cli.handlers.doctor", _tool_name="md_doctor")
    for tool in TOOLS:
        _add_placeholder_subparser(subparsers, tool)
    return parser


def _print_not_implemented(tool: ToolSpec, args: argparse.Namespace) -> int:
    print(f"md {tool.subcommand}: handler not implemented yet", file=sys.stderr)
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    tool: ToolSpec | None = getattr(args, "_tool", None)
    handler_module = getattr(args, "_handler_module", None)
    if handler_module:
        module = importlib.import_module(handler_module)
        return run_tool(getattr(args, "_tool_name", handler_module), module.run, args)
    if tool is None:
        parser.print_help()
        return 0
    try:
        module = importlib.import_module(tool.handler_module)
    except ModuleNotFoundError as exc:
        if exc.name == tool.handler_module:
            return _print_not_implemented(tool, args)
        raise
    return run_tool(tool.tool_id, module.run, args)
