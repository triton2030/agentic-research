from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from md_cli.catalog import get_tool
from md_cli.envelope import LARGE_REPLY_BYTES, wrap
from md_cli.main import build_parser
from navigator.api import status


ROOT = Path(__file__).resolve().parents[1]


def _signature_tokens(signature: str) -> list[str]:
    body = signature.removeprefix("md ").split(maxsplit=1)
    if len(body) < 2:
        return []
    raw_tokens = re.findall(r"\[[^\]]+\]|\S+", body[1])
    tokens: list[str] = []
    for raw in raw_tokens:
        if raw.startswith("[") and raw.endswith("]"):
            parts = raw[1:-1].split()
            tokens.extend(f"[{part}]" for part in parts)
        else:
            tokens.append(raw)
    return tokens


def _signature_layout(signature: str) -> tuple[list[str], list[tuple[str, str]]]:
    positionals: list[str] = []
    flags: list[tuple[str, str]] = []
    tokens = _signature_tokens(signature)
    index = 0
    while index < len(tokens):
        token = tokens[index]
        bare = token[1:-1] if token.startswith("[") and token.endswith("]") else token
        if bare.startswith("--"):
            key = bare[2:].replace("-", "_")
            if key != "json":
                flags.append((key, bare))
            next_token = tokens[index + 1] if index + 1 < len(tokens) else ""
            next_bare = (
                next_token[1:-1]
                if next_token.startswith("[") and next_token.endswith("]")
                else next_token
            )
            index += 2 if next_bare and not next_bare.startswith("--") and next_bare.upper() == next_bare else 1
            continue
        if bare.upper() == bare:
            positionals.append(bare.lower())
        index += 1
    return positionals, flags


def _action_to_argv(action: dict[str, Any]) -> list[str]:
    tool = get_tool(str(action["tool"]))
    assert tool is not None, f"unknown generated tool: {action['tool']}"
    args = dict(action.get("args") or {})
    known = set(tool.input_schema.get("properties") or {})
    unknown = set(args) - known
    assert not unknown, f"{tool.name} generated unknown args: {sorted(unknown)}"

    argv = [tool.subcommand]
    positionals, flags = _signature_layout(tool.cli_signature)
    for key in positionals:
        if key not in args or args[key] in (None, False):
            continue
        value = args.pop(key)
        if isinstance(value, list):
            argv.extend(str(item) for item in value)
        else:
            argv.append(str(value))

    for key, flag in flags:
        if key not in args or args[key] in (None, False):
            continue
        value = args.pop(key)
        if value is True:
            argv.append(flag)
        elif isinstance(value, list):
            for item in value:
                argv.extend([flag, str(item)])
        else:
            argv.extend([flag, str(value)])

    assert not args, f"{tool.name} args are valid schema keys but not CLI args: {sorted(args)}"
    return [*argv, "--json"]


def _iter_generated_actions(value: Any):
    if isinstance(value, dict):
        if isinstance(value.get("tool"), str) and isinstance(value.get("args"), dict):
            yield value
        for item in value.values():
            yield from _iter_generated_actions(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_generated_actions(item)


def _assert_no_bare_confirm(action: dict[str, Any]) -> None:
    args = action.get("args") or {}
    assert not (
        args.get("confirm") is True
        and not (args.get("transaction_id") or args.get("fingerprint"))
    ), f"bare confirm generated: {action}"


def _assert_action_contract(action: dict[str, Any]) -> None:
    _assert_no_bare_confirm(action)
    build_parser().parse_args(_action_to_argv(action))


def test_large_reply_next_steps_parse_against_current_cli() -> None:
    payloads = [
        wrap(
            {"results": [{"snippet": "x" * (LARGE_REPLY_BYTES + 100)}]},
            tool_name="md_search",
            args={"corpus": "knowledge", "query": "agent", "limit": 10},
        ),
        wrap(
            {"sections": [{"body": "x" * (LARGE_REPLY_BYTES + 100)}]},
            tool_name="md_search_read",
            args={"corpus": "knowledge", "query": "agent", "limit": 3},
        ),
        wrap(
            {"concepts": [{"members": "x" * (LARGE_REPLY_BYTES + 100)}]},
            tool_name="md_repeated_concepts",
            args={"corpus": "knowledge", "top": 50},
        ),
    ]
    for payload in payloads:
        actions = list(_iter_generated_actions(payload["_envelope"]["next_step"]))
        assert actions
        for action in actions:
            _assert_action_contract(action)


def test_success_guidance_next_steps_parse_against_current_cli() -> None:
    payloads = [
        wrap(
            {"root": "knowledge", "file_count": 2, "heading_count": 3, "files": []},
            tool_name="md_ls",
            args={"path": "knowledge"},
        ),
        wrap(
            {"root": "knowledge", "file_count": 2, "heading_count": 3, "files": []},
            tool_name="md_toc",
            args={"path": "knowledge"},
        ),
        wrap(
            {
                "scope": "descriptions",
                "read_next": [
                    {
                        "tool": "md_search_read",
                        "args": {"corpus": "knowledge", "query": "agent", "expanded": True},
                        "reason": "Expand selected search results into section bodies.",
                    }
                ],
            },
            tool_name="md_search_read",
            args={"corpus": "knowledge", "query": "agent", "scope": "descriptions"},
        ),
        wrap(
            {
                "stats": {"stopped_reason": "no_anchored_outlink"},
                "chain": [],
            },
            tool_name="md_walk",
            args={"path": "knowledge/example.md", "anchor": "Start", "scan": "knowledge"},
        ),
        wrap(
            {
                "state": "HEALTHY",
                "recommended_action": {
                    "tool": "md_index",
                    "args": {"corpus": "knowledge", "path_include": ["guides/**"]},
                    "reason": "Optional eager warmup; dry-run previews cost before embedding the small delta.",
                },
            },
            tool_name="md_status",
            args={"corpus": "knowledge", "path_include": ["guides/**"]},
        ),
    ]
    for payload in payloads:
        actions = list(_iter_generated_actions(payload["_envelope"]["next_step"]))
        assert actions
        for action in actions:
            _assert_action_contract(action)


def test_status_recommended_action_is_safe_and_preserves_scope(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    keep = corpus / "keep"
    skip = corpus / "skip"
    keep.mkdir(parents=True)
    skip.mkdir()
    (keep / "a.md").write_text("# A\n\nKept.\n", encoding="utf-8")
    (skip / "b.md").write_text("# B\n\nSkipped.\n", encoding="utf-8")

    payload = status(str(corpus), path_include=["keep/*"])
    action = payload["recommended_action"]
    assert action["tool"] == "md_index"
    assert action["args"]["dry_run"] is True
    assert action["args"]["path_include"] == ["keep/*"]
    assert "confirm" not in action["args"]
    _assert_action_contract(action)


def test_golden_generated_actions_parse_and_do_not_use_bare_confirm() -> None:
    golden_dir = ROOT / "tests/golden/mcp-responses"
    actions = []
    for path in sorted(golden_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        actions.extend(_iter_generated_actions(payload))
    assert actions
    for action in actions:
        _assert_action_contract(action)
