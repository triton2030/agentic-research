"""Top-level CLI entry: argparse aggregation + dispatch.

The big commands (`search`, `index`, `status`, `cluster`, `overlaps`,
`repeated-concepts`, `schema`) live in their own modules and expose a
`register_X(sub)` function — kept short by `cli_common` helpers that
hold the shared --embed-model / --cache-dir / --json blocks.

The smaller commands (`manifest`, `map`, `headings`, `pick`, `read`,
`read-related`) stay inline here because they're one-off argparse
shapes with no shared boilerplate.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

from .audit import register_audit
from .folder_map import apply_match_filter, build_map, render_map
from .index_build import DEFAULT_MAX_AUTO_EMBED, register_index
from .index_cluster import register_cluster
from .index_status import register_status
from .overlaps import register_overlaps
from .pick import parse_csv, pick_items, render_pick
from .related import collect_related_items, render_related_packet
from .repeated_concepts import register_repeated_concepts
from .schemas import register_schema
from .search import register_search


def build_manifest() -> dict[str, object]:
    """Machine-readable summary of the navigator's command surface.

    Helps the agent that is calling md_navigator avoid drift between
    documentation, --help text, and runtime behaviour — pulls the
    canonical list and exit-code contract from one place."""
    return {
        "version": "1.0.0",
        "commands": [
            "manifest",
            "map",
            "headings",
            "pick",
            "read",
            "read-related",
            "search",
            "overlaps",
            "repeated-concepts",
            "index",
            "status",
            "cluster",
            "audit",
            "schema",
        ],
        "defaults": {
            "embed_model": "sticky from index meta or `baai/bge-m3` for fresh corpora",
            "embedding_api_url": "https://openrouter.ai/api/v1",
            "rerank_api_url": "https://openrouter.ai/api/v1/rerank",
            "rerank_model": "cohere/rerank-v3.5",
            "max_auto_embed": DEFAULT_MAX_AUTO_EMBED,
        },
        "exit_codes": {
            "0": "success or status report",
            "1": "no Markdown/items or no indexed vectors for requested operation",
            "2": "usage/path/input error",
            "3": "dependency or embedding API failure",
            "4": "index warmup required before search-like command can continue",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Map Markdown files by frontmatter descriptions and headings, "
        "and run hybrid section search."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "manifest",
        help="Print the machine-readable md_navigator command/default contract.",
    )

    # `map` and `headings` share identical argparse — built in a loop.
    for name in ("map", "headings"):
        cmd = sub.add_parser(name, help=f"Build a Markdown {name} view for a folder.")
        cmd.add_argument("path", help="Folder or Markdown file to scan.")
        cmd.add_argument(
            "--max-heading-level",
            type=int,
            default=6,
            choices=range(1, 7),
            metavar="1-6",
            help="Deepest heading level to include.",
        )
        cmd.add_argument(
            "--output",
            help="Write the full JSON map to this file for a later pick command.",
        )
        cmd.add_argument(
            "--json",
            action="store_true",
            help="Print JSON instead of the human Markdown view.",
        )
        cmd.add_argument(
            "--match",
            default="",
            help=(
                "Case-insensitive substring filter over description, title, "
                "and heading texts. File is kept if any of those matches."
            ),
        )
        cmd.add_argument(
            "--with-tokens",
            action="store_true",
            help=(
                "Attach approximate token counts (chars/4) per file and per "
                "section heading. Useful for fitting a reading set into a "
                "context budget."
            ),
        )

    pick = sub.add_parser("pick", help="Select files/headings from a saved JSON map.")
    pick.add_argument(
        "map_json",
        nargs="?",
        default=None,
        help="JSON map written by `map` or `headings`. May also be supplied via --map.",
    )
    pick.add_argument(
        "--map",
        dest="map_alias",
        default=None,
        help="Alias for the positional map_json argument.",
    )
    pick.add_argument("--files", default="", help="Comma list of file ids, e.g. 1,4,7.")
    pick.add_argument(
        "--headings",
        default="",
        help="Comma list of heading ids, e.g. 1.2,4.3,7.1.",
    )
    pick.add_argument(
        "--extract",
        nargs="?",
        const=True,
        default=False,
        metavar="FILE",
        help=(
            "Include section text for selected heading ids. "
            "Bare `--extract` prints to stdout; `--extract FILE` writes to disk."
        ),
    )
    pick.add_argument(
        "--token-budget",
        "--max-tokens",
        dest="token_budget",
        type=int,
        default=0,
        help=(
            "Keep the selection within this approximate token budget. "
            "Items are dropped from the tail of the selection list until "
            "the running total fits."
        ),
    )
    pick.add_argument("--json", action="store_true", help="Print JSON selection.")

    read = sub.add_parser(
        "read",
        help=(
            "Universal UTF-8 text reader — built-in Read replacement for "
            "any non-binary file (.md/.mdx, .py/.ts/.yaml/.toml/.txt, "
            "config and source). Accepts either a direct path (prints the "
            "file with --offset/--limit/--line-numbers parity) or a JSON "
            "map written by `map`, `headings`, or `search --output` "
            "(extracts the selected files/headings into one reading packet). "
            "Binary files (images, PDFs, .ipynb) stay with built-in Read."
        ),
    )
    read.add_argument(
        "map_json",
        nargs="?",
        default=None,
        help=(
            "Either a path to any UTF-8 text file (printed directly) or a "
            "JSON map from `map` / `headings` / `search --output`. May also "
            "be supplied via --map."
        ),
    )
    read.add_argument(
        "--map",
        dest="map_alias",
        default=None,
        help="Alias for the positional map_json argument.",
    )
    read.add_argument("--files", default="", help="Comma list of file ids, e.g. 1,4,7.")
    read.add_argument(
        "--headings",
        default="",
        help="Comma list of heading ids, e.g. 1.2,4.3,7.1.",
    )
    read.add_argument(
        "--token-budget",
        "--max-tokens",
        dest="token_budget",
        type=int,
        default=0,
        help="Keep the reading packet within this approximate token budget.",
    )
    read.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help="Write the rendered packet to FILE instead of stdout.",
    )
    read.add_argument(
        "--offset",
        type=int,
        default=1,
        metavar="N",
        help="Start at line N (1-based, like the built-in Read tool). Default: 1.",
    )
    read.add_argument(
        "--limit",
        type=int,
        default=2000,
        metavar="M",
        help="Read at most M lines (default: 2000, same as the built-in Read tool).",
    )
    read.add_argument(
        "--line-numbers",
        "-n",
        action="store_true",
        help="Prefix each line with its 1-based line number (cat -n style).",
    )
    read.add_argument("--json", action="store_true", help="Print JSON selection.")

    read_related = sub.add_parser(
        "read-related",
        help="Read linked Markdown neighborhood for context only, not graph obligations.",
    )
    read_related.add_argument("paths", nargs="+", help="Markdown file(s) to anchor context.")
    read_related.add_argument(
        "--scan",
        default=".",
        help="Markdown root to scan for backlinks and link target resolution (default: cwd).",
    )
    read_related.add_argument(
        "--include",
        default="self,frontmatter,wikilinks,markdown-links,backlinks",
        help=(
            "Comma list: self,frontmatter,wikilinks,markdown-links,backlinks "
            "(default: all)."
        ),
    )
    read_related.add_argument(
        "--token-budget",
        "--max-tokens",
        dest="token_budget",
        type=int,
        default=0,
        help=(
            "Best-effort cap on the reading packet (approx chars/4). "
            "The anchor file is always included even if it alone exceeds "
            "the budget — only neighbour/semantic items get trimmed. "
            "Expect the reported total to overshoot when an anchor is large; "
            "if a hard cap is required, drop anchors that are too big first."
        ),
    )
    read_related.add_argument(
        "--semantic-radius",
        type=int,
        default=0,
        metavar="K",
        help=(
            "Append top-K semantically nearest sections from files that are "
            "not in the explicit link neighborhood. Reuses on-disk embeddings — "
            "no HTTP calls. Skipped silently if the corpus has no index. "
            "Default 0 (off)."
        ),
    )
    read_related.add_argument(
        "--check-links",
        action="store_true",
        help=(
            "Report explicit links (wikilinks / markdown-links) whose target "
            "is semantically far from the anchor — candidates for off-topic "
            "review. Owner of the verdict is 1md-graph, this command only "
            "surfaces evidence."
        ),
    )
    read_related.add_argument(
        "--link-distance-threshold",
        type=float,
        default=0.4,
        metavar="T",
        help=(
            "L2-distance threshold for --check-links (lower = stricter). "
            "Default 0.4 ≈ cosine 0.92 — fires only on genuinely distant pairs."
        ),
    )
    read_related.add_argument(
        "--anchor-aware",
        action="store_true",
        help=(
            "When a wikilink or markdown-link points to a specific heading "
            "(`[[file#Heading]]` / `[text](file.md#Heading)`), extract only "
            "that section instead of the whole file. Same file linked via "
            "different headings yields multiple items. Default off "
            "(whole-file behavior preserved for compatibility)."
        ),
    )
    read_related.add_argument("--json", action="store_true", help="Print JSON packet.")

    # Big commands — each module owns its own argparse via register_X.
    register_search(sub)
    register_overlaps(sub)
    register_index(sub)
    register_status(sub)
    register_repeated_concepts(sub)
    register_cluster(sub)
    register_audit(sub)
    register_schema(sub)

    return parser.parse_args()


def _dispatch_inline(args: argparse.Namespace) -> int | None:
    """Handle the inline commands (manifest / map / headings / pick /
    read / read-related). Returns an int exit code if handled, or None
    if `args.command` isn't one of these (caller should fall back to
    `args.func`)."""
    if args.command == "manifest":
        print(json.dumps(build_manifest(), ensure_ascii=False, indent=2))
        return 0

    if args.command in {"map", "headings"}:
        data = build_map(Path(args.path), args.max_heading_level, with_tokens=args.with_tokens)
        data = apply_match_filter(data, args.match)
        if args.output:
            Path(args.output).write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(
                render_map(
                    data,
                    include_headings=args.command == "headings",
                    with_tokens=args.with_tokens,
                ),
                end="",
            )
        return 0

    if args.command in {"pick", "read"}:
        return _dispatch_pick_or_read(args)

    if args.command == "read-related":
        packet = collect_related_items(args)
        if args.json:
            print(json.dumps(packet, ensure_ascii=False, indent=2))
        else:
            print(render_related_packet(packet), end="")
        return 0

    return None


def _dispatch_pick_or_read(args: argparse.Namespace) -> int:
    """Pick / read share the same map-resolution + extraction flow.
    Extracted from `main` to keep the dispatch readable."""
    map_arg = args.map_json or getattr(args, "map_alias", None)
    if not map_arg:
        print(
            f"`{args.command}` needs either a positional path or `--map <path>`.\n"
            f"  Expected:\n"
            f"    • a JSON map written by `map`, `headings`, or `search --output`, or\n"
            f"    • (for `read` only) a direct path to a .md / .mdx file.",
            file=sys.stderr,
        )
        return 2
    map_path = Path(map_arg).expanduser()

    if args.command == "pick":
        raw_extract = args.extract
        extract_flag = bool(raw_extract)
        extract_out_path = raw_extract if isinstance(raw_extract, str) else None
    else:
        extract_flag = True
        extract_out_path = getattr(args, "output", None)

    # `read` covers the built-in Read tool's text-file scope: any UTF-8
    # decodable file (not just .md/.mdx), with offset/limit and optional
    # line-number prefix. Binary files (images, PDFs, notebooks) stay
    # with the built-in Read tool — they are multimodal and cannot
    # round-trip through stdout.
    if (
        args.command == "read"
        and map_path.is_file()
        and map_path.suffix.lower() != ".json"
    ):
        try:
            raw = map_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            print(
                f"`read` only supports UTF-8 text files. {map_path} is not text "
                f"({exc.reason} at byte {exc.start}).\n"
                f"  For PDFs, images, or Jupyter notebooks use the built-in "
                f"`Read` tool. For binary text in another encoding, pre-convert.",
                file=sys.stderr,
            )
            return 2

        offset = max(1, int(getattr(args, "offset", 1) or 1))
        limit = int(getattr(args, "limit", 2000) or 2000)
        lines = raw.splitlines(keepends=True)
        total_lines = len(lines)
        start = offset - 1
        end = start + limit if limit > 0 else total_lines
        sliced = lines[start:end]

        if getattr(args, "line_numbers", False):
            rendered_lines = []
            for i, line in enumerate(sliced, start=offset):
                body = line if line.endswith("\n") else line + "\n"
                rendered_lines.append(f"{i:>6}\t{body}")
            text = "".join(rendered_lines)
        else:
            text = "".join(sliced)

        truncated_token_budget = False
        if args.token_budget and args.token_budget > 0:
            max_chars = args.token_budget * 4
            if len(text) > max_chars:
                text = text[:max_chars]
                truncated_token_budget = True

        if args.json:
            payload_obj = {
                "path": str(map_path),
                "offset": offset,
                "limit": limit,
                "lines_returned": len(sliced),
                "lines_total": total_lines,
                "body": text,
            }
            if truncated_token_budget:
                payload_obj["truncated_token_budget"] = args.token_budget
            payload = json.dumps(payload_obj, ensure_ascii=False, indent=2)
            if extract_out_path:
                Path(extract_out_path).expanduser().write_text(
                    payload + "\n", encoding="utf-8"
                )
            else:
                print(payload)
        else:
            if truncated_token_budget:
                text = text.rstrip() + (
                    f"\n\n...[truncated to ~{args.token_budget} approx tokens]\n"
                )
            trailing = "" if text.endswith("\n") or not text else "\n"
            if extract_out_path:
                Path(extract_out_path).expanduser().write_text(
                    text + trailing, encoding="utf-8"
                )
            else:
                print(text, end=trailing)
        return 0

    if not map_path.exists():
        print(
            f"`{args.command}` could not find {map_path}.\n"
            f"  Expected either:\n"
            f"    • a JSON map written by `map`, `headings`, or `search --output`, or\n"
            f"    • (for `read` only) a direct path to a .md / .mdx file.",
            file=sys.stderr,
        )
        return 2

    if map_path.is_dir():
        # Common confusion: `map`/`headings` take a directory, `pick`/`read`
        # take the JSON map those commands produced. Surface the two-step
        # recipe with the user's actual flags rebuilt so the next step is
        # copy-pasteable.
        suggested_map = "/tmp/md-navigator-map.json"
        rebuilt_flags: list[str] = []
        if args.files:
            rebuilt_flags.append(f"--files {args.files}")
        if args.headings:
            rebuilt_flags.append(f"--headings {args.headings}")
        if args.command == "pick":
            raw_extract = getattr(args, "extract", False)
            if isinstance(raw_extract, str):
                rebuilt_flags.append(f"--extract {shlex.quote(raw_extract)}")
            elif raw_extract:
                rebuilt_flags.append("--extract")
        if getattr(args, "token_budget", 0):
            rebuilt_flags.append(f"--token-budget {args.token_budget}")
        if getattr(args, "json", False):
            rebuilt_flags.append("--json")
        rebuilt = " ".join(rebuilt_flags)
        then_cmd_body = f"md_navigator.py {args.command} {suggested_map}"
        if rebuilt:
            then_cmd_body += f" {rebuilt}"
        quoted_dir = shlex.quote(str(map_path))
        print(
            f"`{args.command}` expects a JSON map written by `map`/`headings`/"
            f"`search --output`, not a directory.\n"
            f"  Got directory: {map_path}\n\n"
            f"  Build a headings map first:\n"
            f"    md_navigator.py headings {quoted_dir} --output {suggested_map}\n"
            f"  Then re-run:\n"
            f"    {then_cmd_body}",
            file=sys.stderr,
        )
        return 2

    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        hint = ""
        if args.command == "read" and map_path.suffix.lower() in {".md", ".mdx"}:
            hint = (
                "\n  Hint: this looks like a Markdown file, not a JSON map.\n"
                "  Pass a .md/.mdx path directly to `read` and it will print "
                "the file."
            )
        else:
            hint = (
                "\n  Hint: this command expects a JSON map written by "
                "`map`, `headings`, or `search --output`.\n"
                "  To read a Markdown file directly, use `read <file.md>`."
            )
        print(f"`{args.command}` could not parse {map_path} as JSON.{hint}", file=sys.stderr)
        return 2

    file_ids = parse_csv(args.files)
    heading_ids = parse_csv(args.headings)
    if args.command == "read" and not file_ids and not heading_ids:
        if args.token_budget <= 0:
            print(
                "`read` needs --files/--headings, or --token-budget, when given "
                "a JSON map. To read one Markdown file, pass its path directly.",
                file=sys.stderr,
            )
            return 2
        file_ids = {str(item["id"]) for item in data["files"]}
    selection = pick_items(
        data,
        file_ids,
        heading_ids,
        extract_flag,
        token_budget=args.token_budget,
    )
    if args.json:
        payload = json.dumps(selection, ensure_ascii=False, indent=2)
        if extract_out_path:
            Path(extract_out_path).expanduser().write_text(
                payload + "\n", encoding="utf-8"
            )
        else:
            print(payload)
    else:
        rendered = render_pick(selection, extract_flag)
        if extract_out_path:
            Path(extract_out_path).expanduser().write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    return 0


def main() -> int:
    args = parse_args()

    # Inline-handled commands (manifest, map/headings, pick, read, read-related).
    inline_result = _dispatch_inline(args)
    if inline_result is not None:
        return inline_result

    # register_X commands set `func` via set_defaults — dispatch via attribute.
    func = getattr(args, "func", None)
    if func is not None:
        return func(args)

    return 0
