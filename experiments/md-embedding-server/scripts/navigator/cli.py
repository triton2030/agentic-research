from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .embeddings import (
    SEARCH_DEFAULT_EMBED_MODEL,
    SEARCH_DEFAULT_EMBEDDING_API_URL,
    SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
)
from .folder_map import apply_match_filter, build_map, render_map
from .index import (
    DEFAULT_INDEX_BATCH,
    DEFAULT_INDEX_PAUSE_S,
    DEFAULT_MAX_AUTO_EMBED,
    cmd_cluster,
    cmd_index,
    cmd_status,
)
from .overlaps import cmd_overlaps
from .repeated_concepts import cmd_repeated_concepts
from .pick import parse_csv, pick_items, render_pick
from .related import collect_related_items, render_related_packet
from .search import (
    SEARCH_DEFAULT_CANDIDATES,
    SEARCH_DEFAULT_LIMIT,
    SEARCH_DEFAULT_SCOPE,
    SEARCH_SCOPES,
    cmd_search,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Map Markdown files by frontmatter descriptions and headings, "
        "and run hybrid section search."
    )
    sub = parser.add_subparsers(dest="command", required=True)

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
            "Read Markdown content. Accepts either a direct path to a "
            ".md/.mdx file (prints the file) or a JSON map written by "
            "`map`, `headings`, or `search --output` (extracts the "
            "selected files/headings into one reading packet)."
        ),
    )
    read.add_argument(
        "map_json",
        nargs="?",
        default=None,
        help=(
            "Either a path to a .md/.mdx file (printed directly) or a JSON "
            "map from `map` / `headings` / `search --output`. May also be "
            "supplied via --map."
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
        help="Keep the reading packet within this approximate token budget.",
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
    read_related.add_argument("--json", action="store_true", help="Print JSON packet.")

    search = sub.add_parser(
        "search",
        help="Hybrid section search: BM25F over Markdown shape fused with dense vectors.",
    )
    search.add_argument("path", help="Folder or Markdown file to search.")
    search.add_argument("query", help="Search query (natural language or keywords).")
    search.add_argument(
        "--scope",
        choices=list(SEARCH_SCOPES),
        default=SEARCH_DEFAULT_SCOPE,
        help=(
            f"What to index and rank (default: {SEARCH_DEFAULT_SCOPE}). "
            f"`sections` — heading-bounded sections; `descriptions` — one item per "
            f"file's frontmatter description, returns file-level handles."
        ),
    )
    search.add_argument(
        "--limit",
        type=int,
        default=SEARCH_DEFAULT_LIMIT,
        help=f"Final top-N after fusion (default: {SEARCH_DEFAULT_LIMIT}).",
    )
    search.add_argument(
        "--candidates",
        type=int,
        default=SEARCH_DEFAULT_CANDIDATES,
        help=f"Candidates from each engine before fusion (default: {SEARCH_DEFAULT_CANDIDATES}).",
    )
    search.add_argument(
        "--embed-model",
        default=SEARCH_DEFAULT_EMBED_MODEL,
        help=f"Embedding model id reported to the server (default: {SEARCH_DEFAULT_EMBED_MODEL}).",
    )
    search.add_argument(
        "--embedding-api-url",
        default=SEARCH_DEFAULT_EMBEDDING_API_URL,
        help=(
            "OpenAI-compatible API base URL for embeddings "
            f"(default: {SEARCH_DEFAULT_EMBEDDING_API_URL})."
        ),
    )
    search.add_argument(
        "--embedding-timeout",
        type=float,
        default=SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
        help=f"Embedding API request timeout in seconds (default: {SEARCH_DEFAULT_EMBEDDING_TIMEOUT}).",
    )
    search.add_argument(
        "--max-heading-level",
        type=int,
        default=6,
        choices=range(1, 7),
        metavar="1-6",
        help="Deepest heading level to index as separate section.",
    )
    search.add_argument(
        "--cache-dir",
        default=None,
        help=(
            "Override the index location. Default: `<corpus>/.md-navigator/` "
            "inside the corpus itself. Set this to use one shared root for "
            "all corpora (hashed per-corpus subdir)."
        ),
    )
    search.add_argument(
        "--max-auto-embed",
        type=int,
        default=DEFAULT_MAX_AUTO_EMBED,
        help=(
            f"If the new-section delta needs more than this many chunks to "
            f"embed, `search` refuses and tells you to run `index` first "
            f"(default: {DEFAULT_MAX_AUTO_EMBED}). Pass 0 to allow any size."
        ),
    )
    search.add_argument(
        "--no-cache",
        action="store_true",
        help="Wipe the on-disk index for this corpus and rebuild from scratch.",
    )
    search.add_argument(
        "--output",
        help="Write the section map (compatible with pick) to this JSON file.",
    )
    search.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of the human Markdown view.",
    )

    overlaps = sub.add_parser(
        "overlaps",
        help="Find section pairs with high semantic similarity (smeared-information detector).",
    )
    overlaps.add_argument("path", help="Folder or Markdown file to scan.")
    overlaps.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Cosine similarity threshold for surfaced pairs (default: 0.85).",
    )
    overlaps.add_argument(
        "--top",
        type=int,
        default=20,
        help="Top-N pairs to return (default: 20).",
    )
    overlaps.add_argument(
        "--min-tokens",
        type=int,
        default=30,
        help="Skip sections below this token count to ignore stubs (default: 30, 0 = no filter).",
    )
    overlaps.add_argument(
        "--include-same-file",
        action="store_true",
        help="Include section pairs from the same file (default: cross-file only).",
    )
    overlaps.add_argument(
        "--max-heading-level",
        type=int,
        default=6,
        choices=range(1, 7),
        metavar="1-6",
        help="Deepest heading level to index as separate section.",
    )
    overlaps.add_argument(
        "--embed-model",
        default=SEARCH_DEFAULT_EMBED_MODEL,
        help=f"Embedding model id reported to the server (default: {SEARCH_DEFAULT_EMBED_MODEL}).",
    )
    overlaps.add_argument(
        "--embedding-api-url",
        default=SEARCH_DEFAULT_EMBEDDING_API_URL,
        help=(
            "OpenAI-compatible API base URL for embeddings "
            f"(default: {SEARCH_DEFAULT_EMBEDDING_API_URL})."
        ),
    )
    overlaps.add_argument(
        "--embedding-timeout",
        type=float,
        default=SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
        help=f"Embedding API request timeout in seconds (default: {SEARCH_DEFAULT_EMBEDDING_TIMEOUT}).",
    )
    overlaps.add_argument(
        "--cache-dir",
        default=None,
        help=(
            "Override the index location. Default: `<corpus>/.md-navigator/` "
            "inside the corpus itself."
        ),
    )
    overlaps.add_argument(
        "--max-auto-embed",
        type=int,
        default=DEFAULT_MAX_AUTO_EMBED,
        help=(
            f"If the new-section delta needs more than this many chunks to "
            f"embed, `overlaps` refuses and tells you to run `index` first "
            f"(default: {DEFAULT_MAX_AUTO_EMBED}). Pass 0 to allow any size."
        ),
    )
    overlaps.add_argument(
        "--no-cache",
        action="store_true",
        help="Wipe the on-disk index for this corpus and rebuild from scratch.",
    )
    overlaps.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of the human Markdown view.",
    )

    index = sub.add_parser(
        "index",
        help=(
            "Build / top up the persistent vector index for a corpus. "
            "Heavy operation: writes embeddings to disk in small batches with a "
            "small pause so a low-spec laptop stays usable. Run this once when "
            "you start working with a project; `search` and `overlaps` after "
            "that are near-instant."
        ),
    )
    index.add_argument("path", help="Folder or Markdown file to index.")
    index.add_argument(
        "--max-heading-level",
        type=int,
        default=6,
        choices=range(1, 7),
        metavar="1-6",
        help="Deepest heading level to index as separate section.",
    )
    index.add_argument(
        "--embed-model",
        default=SEARCH_DEFAULT_EMBED_MODEL,
        help=f"Embedding model id (default: {SEARCH_DEFAULT_EMBED_MODEL}).",
    )
    index.add_argument(
        "--embedding-api-url",
        default=SEARCH_DEFAULT_EMBEDDING_API_URL,
        help=f"Embedding API base URL (default: {SEARCH_DEFAULT_EMBEDDING_API_URL}).",
    )
    index.add_argument(
        "--embedding-timeout",
        type=float,
        default=SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
        help=f"Embedding API request timeout in seconds (default: {SEARCH_DEFAULT_EMBEDDING_TIMEOUT}).",
    )
    index.add_argument(
        "--cache-dir",
        default=None,
        help=(
            "Override the index location. Default: `<corpus>/.md-navigator/` "
            "inside the corpus itself."
        ),
    )
    index.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_INDEX_BATCH,
        help=f"Embedding batch size (default: {DEFAULT_INDEX_BATCH}). Smaller = lower Metal peak.",
    )
    index.add_argument(
        "--batch-pause-ms",
        type=int,
        default=int(DEFAULT_INDEX_PAUSE_S * 1000),
        help=(
            f"Sleep between batches in milliseconds "
            f"(default: {int(DEFAULT_INDEX_PAUSE_S * 1000)}). 0 disables the pause."
        ),
    )

    status = sub.add_parser(
        "status",
        help=(
            "Report freshness of the on-disk index for a corpus without "
            "touching it. Counts pending added / removed sections, classifies "
            "FRESH / HEALTHY / NEEDS WARMUP / NO INDEX. No HTTP calls, no DB writes."
        ),
    )
    status.add_argument("path", help="Folder or Markdown file to check.")
    status.add_argument(
        "--max-heading-level",
        type=int,
        default=6,
        choices=range(1, 7),
        metavar="1-6",
        help="Deepest heading level to consider as a section.",
    )
    status.add_argument(
        "--embed-model",
        default=SEARCH_DEFAULT_EMBED_MODEL,
        help=f"Embedding model id (default: {SEARCH_DEFAULT_EMBED_MODEL}).",
    )
    status.add_argument(
        "--embedding-api-url",
        default=SEARCH_DEFAULT_EMBEDDING_API_URL,
        help=f"Embedding API base URL (default: {SEARCH_DEFAULT_EMBEDDING_API_URL}).",
    )
    status.add_argument(
        "--embedding-timeout",
        type=float,
        default=SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
        help=f"Embedding API request timeout in seconds (default: {SEARCH_DEFAULT_EMBEDDING_TIMEOUT}).",
    )
    status.add_argument(
        "--cache-dir",
        default=None,
        help=(
            "Override the index location. Default: `<corpus>/.md-navigator/` "
            "inside the corpus itself."
        ),
    )
    status.add_argument(
        "--max-auto-embed",
        type=int,
        default=DEFAULT_MAX_AUTO_EMBED,
        help=(
            f"Cap below which `search` / `overlaps` auto-embed inline. "
            f"Above this, status reports NEEDS WARMUP (default: {DEFAULT_MAX_AUTO_EMBED})."
        ),
    )

    rc = sub.add_parser(
        "repeated-concepts",
        help=(
            "Find ideas that recur across the corpus via connected "
            "components on the section-similarity graph. Each concept "
            "lists the files it touches and the representative section. "
            "Writes a persistent Markdown report to "
            "`<corpus>/.md-navigator/repeated-concepts.md`. The primary "
            "concept-level evidence probe for `1ia-audit` owner-truth "
            "questions. Read-only HTTP-wise after `index`."
        ),
    )
    rc.add_argument("path", help="Corpus root (must have an existing index).")
    rc.add_argument(
        "--threshold",
        type=float,
        default=0.80,
        help=(
            "Cosine similarity threshold for graph edges between sections "
            "(default: 0.80). Lower = larger / fuzzier concepts; higher = "
            "tighter / fewer."
        ),
    )
    rc.add_argument(
        "--top",
        type=int,
        default=30,
        help="Top-N concepts to keep in the report (default: 30).",
    )
    rc.add_argument(
        "--min-tokens",
        type=int,
        default=30,
        help="Skip sections below this token count to ignore stubs (default: 30).",
    )
    rc.add_argument(
        "--min-files",
        type=int,
        default=2,
        help=(
            "Drop concepts that live in fewer than this many distinct files "
            "(default: 2 — recurrence across files is the point; raise to 3+ "
            "for stronger owner-truth signals)."
        ),
    )
    rc.add_argument(
        "--min-sections",
        type=int,
        default=2,
        help="Drop concepts with fewer than this many member sections (default: 2).",
    )
    rc.add_argument(
        "--top-members",
        type=int,
        default=5,
        help="How many member sections to list per concept, ranked by similarity to representative (default: 5).",
    )
    rc.add_argument(
        "--max-heading-level",
        type=int,
        default=6,
        choices=range(1, 7),
        metavar="1-6",
        help="Deepest heading level to index as separate section.",
    )
    rc.add_argument(
        "--embed-model",
        default=SEARCH_DEFAULT_EMBED_MODEL,
        help=f"Embedding model id reported to the server (default: {SEARCH_DEFAULT_EMBED_MODEL}).",
    )
    rc.add_argument(
        "--embedding-api-url",
        default=SEARCH_DEFAULT_EMBEDDING_API_URL,
        help=(
            "OpenAI-compatible API base URL for embeddings "
            f"(default: {SEARCH_DEFAULT_EMBEDDING_API_URL})."
        ),
    )
    rc.add_argument(
        "--embedding-timeout",
        type=float,
        default=SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
        help=f"Embedding API request timeout in seconds (default: {SEARCH_DEFAULT_EMBEDDING_TIMEOUT}).",
    )
    rc.add_argument(
        "--cache-dir",
        default=None,
        help=(
            "Override the index location. Default: `<corpus>/.md-navigator/` "
            "inside the corpus itself."
        ),
    )
    rc.add_argument(
        "--max-auto-embed",
        type=int,
        default=DEFAULT_MAX_AUTO_EMBED,
        help=(
            f"If the new-section delta needs more than this many chunks to "
            f"embed, `repeated-concepts` refuses and tells you to run `index` "
            f"first (default: {DEFAULT_MAX_AUTO_EMBED}). Pass 0 to allow any size."
        ),
    )
    rc.add_argument(
        "--no-cache",
        action="store_true",
        help="Wipe the on-disk index for this corpus and rebuild from scratch.",
    )
    rc.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help=(
            "Write the report to FILE instead of the default "
            "`<corpus>/.md-navigator/repeated-concepts.md`."
        ),
    )
    rc.add_argument(
        "--stdout",
        action="store_true",
        help="Print the full report to stdout instead of writing a file.",
    )
    rc.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the human Markdown view.",
    )

    cluster = sub.add_parser(
        "cluster",
        help=(
            "Group all sections of a corpus into K semantic clusters via "
            "K-means on the on-disk vectors. Each cluster suggests a "
            "topic; common_parent vs centroid_path mismatch is an IA "
            "signal for `1ia-audit`. Read-only; no HTTP calls."
        ),
    )
    cluster.add_argument("path", help="Corpus root (must have an existing index).")
    cluster.add_argument(
        "--k",
        type=int,
        default=8,
        metavar="N",
        help="Number of clusters (default: 8).",
    )
    cluster.add_argument(
        "--seed",
        type=int,
        default=42,
        help="K-means seed for reproducible runs (default: 42).",
    )
    cluster.add_argument(
        "--cache-dir",
        default=None,
        help=(
            "Override the index location. Default: `<corpus>/.md-navigator/` "
            "inside the corpus itself."
        ),
    )
    cluster.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of the human Markdown view.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
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
        # Accept the map argument as positional or via --map; whichever is set.
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

        # `--extract` is a tristate now: False (off), True (stdout),
        # or a path string (write to that file). Normalise for downstream.
        if args.command == "pick":
            raw_extract = args.extract
            extract_flag = bool(raw_extract)
            extract_out_path = raw_extract if isinstance(raw_extract, str) else None
        else:
            # `read` always extracts. Output file comes from `--output`.
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

            # Apply offset/limit on line basis, matching the built-in Read
            # tool semantics (1-based offset, default 2000-line limit).
            offset = max(1, int(getattr(args, "offset", 1) or 1))
            limit = int(getattr(args, "limit", 2000) or 2000)
            lines = raw.splitlines(keepends=True)
            total_lines = len(lines)
            start = offset - 1
            end = start + limit if limit > 0 else total_lines
            sliced = lines[start:end]

            if getattr(args, "line_numbers", False):
                # cat -n style: 6-space-padded line number + tab + content.
                rendered_lines = []
                for i, line in enumerate(sliced, start=offset):
                    body = line if line.endswith("\n") else line + "\n"
                    rendered_lines.append(f"{i:>6}\t{body}")
                text = "".join(rendered_lines)
            else:
                text = "".join(sliced)

            # Token-budget cap applied last; cuts at character level.
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

    if args.command == "read-related":
        packet = collect_related_items(args)
        if args.json:
            print(json.dumps(packet, ensure_ascii=False, indent=2))
        else:
            print(render_related_packet(packet), end="")
        return 0

    if args.command == "search":
        return cmd_search(args)

    if args.command == "overlaps":
        return cmd_overlaps(args)

    if args.command == "repeated-concepts":
        return cmd_repeated_concepts(args)

    if args.command == "index":
        return cmd_index(args)

    if args.command == "status":
        return cmd_status(args)

    if args.command == "cluster":
        return cmd_cluster(args)

    return 0
