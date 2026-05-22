#!/usr/bin/env python3
import argparse
import json


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="md-spike-argparse")
    sub = parser.add_subparsers(dest="command", required=True)

    blast = sub.add_parser("section-blast-radius", aliases=["md_section_blast_radius"])
    blast.add_argument("path")
    blast.add_argument("corpus")
    blast.add_argument("--query", required=True)
    blast.add_argument("--heading-id")
    blast.add_argument("--scan")
    blast.add_argument("--depth", type=int, default=2)
    blast.add_argument("--limit", type=int, default=5)
    blast.add_argument("--path-include", action="append", default=[])
    blast.add_argument("--path-exclude", action="append", default=[])

    query = sub.add_parser("query-by-type", aliases=["md_query_by_type"])
    query.add_argument("corpus")
    query.add_argument("--types", required=True, type=_csv)
    query.add_argument("--filter")
    query.add_argument("--limit", type=int, default=10)
    query.add_argument("--path-include", action="append", default=[])
    query.add_argument("--path-exclude", action="append", default=[])
    query.add_argument("--compact", action="store_true")

    edit = sub.add_parser("edit-context", aliases=["md_edit_context"])
    edit.add_argument("path")
    edit.add_argument("--mode", choices=["preview", "full", "strict"], default="preview")
    edit.add_argument("--scan")
    edit.add_argument("--depth", type=int, default=2)
    edit.add_argument("--query")
    edit.add_argument("--corpus")

    return parser


def main() -> int:
    args = vars(build_parser().parse_args())
    print(json.dumps({"framework": "argparse", "args": args}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
