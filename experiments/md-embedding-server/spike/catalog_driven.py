#!/usr/bin/env python3
import argparse
import json
from copy import deepcopy


CATALOG = {
    "section-blast-radius": {
        "properties": {
            "path": {"type": "string", "positional": True},
            "corpus": {"type": "string", "positional": True},
            "query": {"type": "string", "required": True},
            "heading_id": {"type": "string"},
            "scan": {"type": "string"},
            "depth": {"type": "integer", "default": 2},
            "limit": {"type": "integer", "default": 5},
            "path_include": {"type": "array"},
            "path_exclude": {"type": "array"},
        }
    },
    "query-by-type": {
        "properties": {
            "corpus": {"type": "string", "positional": True},
            "types": {"type": "array", "required": True, "csv": True},
            "filter": {"type": "string"},
            "limit": {"type": "integer", "default": 10},
            "path_include": {"type": "array"},
            "path_exclude": {"type": "array"},
            "compact": {"type": "boolean"},
        }
    },
    "edit-context": {
        "properties": {
            "path": {"type": "string", "positional": True},
            "mode": {"type": "string", "choices": ["preview", "full", "strict"], "default": "preview"},
            "scan": {"type": "string"},
            "depth": {"type": "integer", "default": 2},
            "query": {"type": "string"},
            "corpus": {"type": "string"},
        }
    },
}


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _arg_type(spec: dict):
    if spec.get("csv"):
        return _csv
    if spec["type"] == "integer":
        return int
    return str


def add_from_schema(subparsers, name: str, schema: dict) -> None:
    parser = subparsers.add_parser(name)
    for key, spec in schema["properties"].items():
        kwargs = {}
        if spec["type"] == "boolean":
            kwargs["action"] = "store_true"
        elif spec["type"] == "array":
            kwargs["action"] = "append"
            kwargs["default"] = []
            if spec.get("csv"):
                kwargs = {"type": _csv, "required": spec.get("required", False)}
        else:
            kwargs["type"] = _arg_type(spec)
        if "choices" in spec:
            kwargs["choices"] = spec["choices"]
        if "default" in spec:
            kwargs["default"] = spec["default"]
        if spec.get("required") and not spec.get("positional"):
            kwargs["required"] = True
        if spec.get("positional"):
            parser.add_argument(key, **kwargs)
        else:
            parser.add_argument(f"--{key.replace('_', '-')}", **kwargs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="md-spike-catalog")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, schema in CATALOG.items():
        add_from_schema(sub, name, deepcopy(schema))
    return parser


def main() -> int:
    args = vars(build_parser().parse_args())
    print(json.dumps({"framework": "catalog-driven-argparse", "args": args}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
