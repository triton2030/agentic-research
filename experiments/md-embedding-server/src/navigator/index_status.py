"""Legacy `md_navigator.py status` adapter.

The status state machine lives in `status_core`. This module owns only argparse
registration and stdout/stderr rendering for the legacy CLI surface.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .cli_common import (
    add_cache_arg,
    add_embedding_args,
    add_max_heading_level_arg,
)
from .filters import add_path_filter_args
from .index_build import DEFAULT_MAX_AUTO_EMBED
from .status_core import find_corpus_root_for, status_payload
from .status_render import render_status


def register_status(sub) -> None:
    p = sub.add_parser(
        "status",
        help=(
            "Report freshness of the on-disk index for a corpus without "
            "touching it. Counts pending added / removed sections, classifies "
            "FRESH / HEALTHY / NEEDS WARMUP / NO INDEX. No HTTP calls, no DB writes."
        ),
    )
    p.add_argument("path", help="Folder or Markdown file to check.")
    add_max_heading_level_arg(p)
    add_embedding_args(p)
    add_cache_arg(p)
    add_path_filter_args(p, command_name="status")
    p.add_argument(
        "--max-auto-embed",
        type=int,
        default=DEFAULT_MAX_AUTO_EMBED,
        help=(
            f"Cap below which `search` / `overlaps` auto-embed inline. "
            f"Above this, status reports NEEDS WARMUP (default: {DEFAULT_MAX_AUTO_EMBED})."
        ),
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of human text. Used by the MCP envelope.",
    )
    p.set_defaults(func=lambda args: cmd_status(args))


def cmd_status(args: Any) -> int:
    payload = status_payload(
        args.path,
        path_include=getattr(args, "path_include", None),
        path_exclude=getattr(args, "path_exclude", None),
        max_heading_level=getattr(args, "max_heading_level", None),
        max_auto_embed=getattr(args, "max_auto_embed", None),
        embed_model=getattr(args, "embed_model", None),
        embedding_api_url=getattr(args, "embedding_api_url", None),
        embedding_timeout=getattr(args, "embedding_timeout", None),
        cache_dir=getattr(args, "cache_dir", None),
    )
    code = int(payload.pop("_exit_code", 0))
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_status(payload), file=sys.stderr if code else sys.stdout)
    return code


__all__ = [
    "cmd_status",
    "find_corpus_root_for",
    "register_status",
]
