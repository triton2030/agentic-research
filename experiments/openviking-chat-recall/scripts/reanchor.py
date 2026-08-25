#!/usr/bin/env python3
"""Пересчитать адреса записей по явному корпусу и слою тем.

Номер строки — удобный адрес для человека, но он ломается, когда корпус
дорастает шапкой. Отпечаток самой строки записи остаётся машинным адресом:
по нему ``fix`` находит новую строку и меняет только ссылки в переданных
файлах слоя.

По умолчанию CLI сохраняет старый локальный вызов ``reanchor.py map|fix``.
Для чужого проекта пути должны быть переданы явно:

    python3 reanchor.py map \
        --corpus /foreign/_ops/chat-recall/raw \
        --library-root /foreign/_ops/chat-recall/topics \
        --artifact-root /foreign/work/anchors

``--artifact-root`` означает папку, в которой будет ``anchor-map.json``;
``--map`` позволяет назвать файл карты напрямую. Эти параметры нельзя
смешивать.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections.abc import Iterable
from pathlib import Path

TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")
# Holder names are a corpus contract, not a local date/UUID naming convention.
ANCHOR = re.compile(r"([^\s#\[\](),/]+\.md)#L(\d+)")


def _as_paths(
    values: Iterable[str | os.PathLike[str]] | str | os.PathLike[str],
) -> list[Path]:
    if isinstance(values, (str, os.PathLike)):
        return [Path(values)]
    return [Path(value) for value in values]


def _default_corpus() -> Path:
    return Path.cwd() / "_ops" / "chat-recall" / "raw"


def _default_map() -> Path:
    # The default is only for the historical local CLI. Foreign calls must
    # supply --map/--artifact-root when they supply --corpus.
    return Path(__file__).resolve().parents[1] / "artifacts" / "anchor-map.json"


def resolve_inputs(
    corpus: str | os.PathLike[str] | None = None,
    roots: Iterable[str | os.PathLike[str]] | str | os.PathLike[str] | None = None,
    map_path: str | os.PathLike[str] | None = None,
    artifact_root: str | os.PathLike[str] | None = None,
) -> tuple[Path, list[Path], Path]:
    """Resolve one complete corpus/library/artifact boundary.

    Explicit foreign inputs never fall back to this repository's artifact
    path. If a foreign caller omits the map destination, fail before reading
    or writing anything.
    """
    if map_path is not None and artifact_root is not None:
        raise ValueError("передайте либо map_path, либо artifact_root, но не оба")

    explicit_corpus = corpus is not None
    corpus_path = Path(corpus) if explicit_corpus else _default_corpus()
    root_paths = (
        _as_paths(roots)
        if roots is not None
        else [corpus_path.parent / "topics"]
    )
    if artifact_root is not None:
        output_map = Path(artifact_root) / "anchor-map.json"
    elif map_path is not None:
        output_map = Path(map_path)
    elif explicit_corpus:
        raise ValueError("для внешнего корпуса карта обязательна: map_path или artifact_root")
    else:
        output_map = _default_map()

    if not corpus_path.is_dir():
        raise FileNotFoundError(f"корпус не найден или не папка: {corpus_path}")
    for root in root_paths:
        if not root.is_dir():
            raise FileNotFoundError(f"слой тем не найден или не папка: {root}")
    return corpus_path, root_paths, output_map


def fingerprint(line: str) -> str:
    return hashlib.sha1(line.strip().encode("utf-8")).hexdigest()[:12]


def records(corpus: str | os.PathLike[str] | None = None) -> dict[str, dict[int, str]]:
    """Return holder -> {1-based record line: fingerprint} for one corpus."""
    corpus_path = Path(corpus) if corpus is not None else _default_corpus()
    found: dict[str, dict[int, str]] = {}
    for path in sorted(corpus_path.glob("*.md")):
        name = path.name
        if name == "README.md":
            continue
        rows: dict[int, str] = {}
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if line.startswith("* ") and TYPE.search(line):
                rows[number] = fingerprint(line)
        found[name] = rows
    return found


def library_files(
    roots: Iterable[str | os.PathLike[str]] | str | os.PathLike[str] | None = None,
) -> list[Path]:
    """Return unique Markdown files below the supplied library roots."""
    root_paths = _as_paths(roots) if roots is not None else [
        _default_corpus().parent / "topics"
    ]
    unique = {
        path.resolve()
        for root in root_paths
        for path in root.glob("**/*.md")
        if path.is_file()
    }
    return sorted(unique, key=lambda path: str(path))


def build_map(
    corpus: str | os.PathLike[str] | None = None,
    roots: Iterable[str | os.PathLike[str]] | str | os.PathLike[str] | None = None,
    map_path: str | os.PathLike[str] | None = None,
    *,
    artifact_root: str | os.PathLike[str] | None = None,
) -> int:
    corpus_path, root_paths, output_map = resolve_inputs(
        corpus, roots, map_path, artifact_root
    )
    live = records(corpus_path)
    mapped: dict[str, str] = {}
    missing: list[str] = []
    for path in library_files(root_paths):
        for name, number in ANCHOR.findall(path.read_text(encoding="utf-8")):
            key = f"{name}#L{number}"
            mark = live.get(name, {}).get(int(number))
            if mark:
                mapped[key] = f"{name}@{mark}"
            elif key not in missing:
                missing.append(key)

    # The fingerprint must be unique within each holder or fix could select a
    # neighbor. Check before writing the supplied map destination.
    for name, rows in live.items():
        marks = list(rows.values())
        if len(marks) != len(set(marks)):
            print(f"ОТКАЗ: в {name} отпечатки не уникальны — карта не записана")
            return 1

    output_map.parent.mkdir(parents=True, exist_ok=True)
    output_map.write_text(
        json.dumps(mapped, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"якорей в карте: {len(mapped)} -> {output_map}")
    print(f"не попали ни в одну живую запись: {len(missing)}")
    for key in missing[:12]:
        print(f"  {key}")
    return 0


def fix(
    corpus: str | os.PathLike[str] | None = None,
    roots: Iterable[str | os.PathLike[str]] | str | os.PathLike[str] | None = None,
    map_path: str | os.PathLike[str] | None = None,
    *,
    artifact_root: str | os.PathLike[str] | None = None,
) -> int:
    corpus_path, root_paths, map_file = resolve_inputs(
        corpus, roots, map_path, artifact_root
    )
    if not map_file.exists():
        print(f"карты нет — сначала создай {map_file}")
        return 1
    mapped = json.loads(map_file.read_text(encoding="utf-8"))
    live = records(corpus_path)

    # fingerprint -> current line; a collision makes the entire fix unsafe.
    where: dict[str, int] = {}
    clash: set[str] = set()
    for name, rows in live.items():
        for number, mark in rows.items():
            key = f"{name}@{mark}"
            if key in where:
                clash.add(key)
            where[key] = number
    if clash:
        print(f"ОТКАЗ: неоднозначных отпечатков {len(clash)} — ничего не трогаю")
        return 1

    moved = lost = 0
    for path in library_files(root_paths):
        text = path.read_text(encoding="utf-8")

        def swap(hit: re.Match[str]) -> str:
            nonlocal moved, lost
            key = f"{hit.group(1)}#L{hit.group(2)}"
            mark = mapped.get(key)
            if not mark:
                return hit.group(0)
            number = where.get(mark)
            if number is None:
                lost += 1
                return hit.group(0)
            if number != int(hit.group(2)):
                moved += 1
            return f"{hit.group(1)}#L{number}"

        fresh = ANCHOR.sub(swap, text)
        if fresh != text:
            path.write_text(fresh, encoding="utf-8")
    print(f"ссылок пересчитано: {moved} | запись по отпечатку не найдена: {lost}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("map", "fix"))
    parser.add_argument("positional", nargs="*", help="corpus, library root, map path")
    parser.add_argument("--corpus", dest="corpus")
    parser.add_argument("--library-root", "--root", dest="roots", action="append")
    parser.add_argument("--map", dest="map_path")
    parser.add_argument("--artifact-root", dest="artifact_root")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if len(args.positional) > 3:
        raise SystemExit("ожидались: corpus library-root map-path")
    corpus = args.corpus or (args.positional[0] if args.positional else None)
    roots = args.roots or (args.positional[1] if len(args.positional) > 1 else None)
    map_path = args.map_path or (args.positional[2] if len(args.positional) > 2 else None)
    try:
        if args.command == "map":
            return build_map(corpus, roots, map_path, artifact_root=args.artifact_root)
        return fix(corpus, roots, map_path, artifact_root=args.artifact_root)
    except (FileNotFoundError, ValueError) as error:
        print(f"ОТКАЗ: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
