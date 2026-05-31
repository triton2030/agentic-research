from __future__ import annotations

import argparse
import importlib
import sys
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
    """Build argparse arguments from structural catalog data.

    Positional arguments and their order come from ``tool.positional_args``;
    everything else (types, required, enum choices, array repetition, help)
    is read straight from ``tool.input_schema``. No prose parsing — the
    human-readable ``cli_signature`` is rendered from this same structure for
    docs/help, never parsed back to reconstruct it.
    """
    required = set(tool.input_schema.get("required") or [])
    properties = tool.input_schema.get("properties") or {}
    positional = tool.positional_args

    for name in positional:
        schema = properties.get(name, {})
        kwargs: dict[str, Any] = {"help": _schema_help(schema)}
        if name not in required:
            kwargs["nargs"] = "?"
        parser.add_argument(name, **kwargs)

    for key, schema in properties.items():
        if key in positional:
            continue
        flag = f"--{key.replace('_', '-')}"
        if schema.get("type") == "boolean":
            parser.add_argument(flag, dest=key, action="store_true", help=_schema_help(schema))
            continue
        kwargs = {
            "dest": key,
            "required": key in required,
            "help": _schema_help(schema),
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

    # Transactional mutators accept --transaction-id as a CLI safety token.
    # A few specs (md_index, md_profile_sections) carry the token in their
    # signature but not in input_schema (the MCP layer takes `fingerprint`
    # instead), so derive it from the structural `transaction_required` flag
    # rather than from any one of those two sources.
    if tool.transaction_required and "transaction_id" not in properties:
        parser.add_argument(
            "--transaction-id",
            dest="transaction_id",
            help="Token from a prior dry_run; required for confirm:true to detect file drift.",
        )

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
    if tool.handler_module is None:
        # Generic dispatch: no bespoke handler module, route straight through
        # the shared generic runner keyed by tool id.
        from .handlers import _generic

        return run_tool(tool.tool_id, lambda a: _generic.run_tool(tool.tool_id, a), args)
    try:
        module = importlib.import_module(tool.handler_module)
    except ModuleNotFoundError as exc:
        if exc.name == tool.handler_module:
            return _print_not_implemented(tool, args)
        raise
    return run_tool(tool.tool_id, module.run, args)
