#!/usr/bin/env python3
"""Ремонт якорей слоя после переразметки тем записей.

Переразметка меняет ``topic:`` внутри строк записей, поэтому карта fingerprint
из ``reanchor.py`` больше не может связать старую и новую строку. Этот helper
сравнивает явный pre-retopic corpus с явным live corpus, маскирует только
служебное поле темы и переносит якоря по порядку одинаковых строк.

``base`` может быть каталогом pre-retopic corpus (удобный foreign/test seam)
либо git revision для исторического локального вызова. В обоих случаях слой
тем и live corpus передаются явно при работе с чужим проектом.

    python3 fix_anchors_after_retopic.py <base> [--write] \
        --corpus /foreign/_ops/chat-recall/raw \
        --library-root /foreign/_ops/chat-recall/topics
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_retopic_tasks import TOPIC_FIELD, meta_at
from reanchor import ANCHOR, _default_corpus, library_files, resolve_inputs


def masked(line: str) -> str:
    """Mask only the topic in the record's service tail."""
    line = line.strip()
    meta = meta_at(line)
    if meta is None:
        return line
    field = TOPIC_FIELD.search(line, meta)
    if not field:
        return line
    return line[: field.start()] + field.group(1) + "@" + field.group(3) + line[field.end() :]


def blob(commit: str, path: str, repo_root: str | Path | None = None) -> list[str] | None:
    """Read one holder from a revision in the supplied repository root."""
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        capture_output=True,
        text=True,
        cwd=str(repo_root) if repo_root is not None else None,
        check=False,
    )
    return proc.stdout.splitlines() if proc.returncode == 0 else None


def _read_directory_holder(root: Path, name: str) -> list[str] | None:
    path = root / name
    return path.read_text(encoding="utf-8").splitlines() if path.is_file() else None


def _base_holder(
    base: str | Path,
    name: str,
    corpus: Path,
    base_corpus: str | Path | None,
    repo_root: str | Path | None,
) -> list[str] | None:
    base_path = Path(base)
    if base_corpus is not None:
        return _read_directory_holder(Path(base_corpus), name)
    if base_path.is_dir():
        return _read_directory_holder(base_path, name)

    root = Path(repo_root) if repo_root is not None else Path.cwd()
    try:
        relative_corpus = corpus.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(
            "для git base corpus должен находиться под repo_root; "
            "либо передайте base_corpus как pre-retopic папку"
        ) from error
    return blob(str(base), (relative_corpus / name).as_posix(), root)


def main(
    base: str,
    write: bool,
    corpus: str | Path | None = None,
    roots: Iterable[str | Path] | str | Path | None = None,
    *,
    base_corpus: str | Path | None = None,
    repo_root: str | Path | None = None,
) -> int:
    """Remap anchors from one explicit pre-retopic/live corpus boundary."""
    corpus_path, root_paths, _ = resolve_inputs(
        corpus,
        roots,
        # This helper does not own an artifact map; give the shared resolver a
        # harmless destination solely for foreign path validation.
        map_path=Path(corpus or _default_corpus()).parent / ".unused-anchor-map.json",
    )
    library = library_files(root_paths)
    remap: dict[tuple[str, int], int] = {}
    lost: list[str] = []
    names = {
        name
        for path in library
        for name, _ in ANCHOR.findall(path.read_text(encoding="utf-8"))
    }

    for name in sorted(names):
        old = _base_holder(base, name, corpus_path, base_corpus, repo_root)
        if old is None:
            continue  # the holder did not exist in the pre-retopic snapshot
        new_path = corpus_path / name
        if not new_path.is_file():
            continue
        new = new_path.read_text(encoding="utf-8").splitlines()
        positions: dict[str, list[int]] = defaultdict(list)
        for number, line in enumerate(new, 1):
            positions[masked(line)].append(number)
        seen: dict[str, int] = defaultdict(int)
        for number, line in enumerate(old, 1):
            key = masked(line)
            rank = seen[key]
            seen[key] += 1
            candidates = positions.get(key, [])
            remap[(name, number)] = candidates[rank] if rank < len(candidates) else -1

    moved = kept = missing = 0
    for path in library:
        text = path.read_text(encoding="utf-8")

        def swap(hit: re.Match[str]) -> str:
            nonlocal moved, kept, missing
            target = remap.get((hit.group(1), int(hit.group(2))))
            if target is None or target == -1:
                missing += 1
                lost.append(hit.group(0))
                return hit.group(0)
            if target == int(hit.group(2)):
                kept += 1
                return hit.group(0)
            moved += 1
            return f"{hit.group(1)}#L{target}"

        fresh = ANCHOR.sub(swap, text)
        if write and fresh != text:
            path.write_text(fresh, encoding="utf-8")
    verb = "переставлено" if write else "переставилось бы"
    print(f"{verb}: {moved} | на месте: {kept} | не найдено: {missing}")
    for key in lost[:10]:
        print(f"  потерян: {key}")
    return 1 if missing else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", help="pre-retopic directory or git revision")
    parser.add_argument("positional", nargs="*", help="corpus and library root")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--corpus")
    parser.add_argument("--library-root", "--root", dest="roots", action="append")
    parser.add_argument("--base-corpus")
    parser.add_argument("--repo-root")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    if len(args.positional) > 2:
        raise SystemExit("ожидались: base corpus library-root")
    corpus = args.corpus or (args.positional[0] if args.positional else None)
    roots = args.roots or (args.positional[1] if len(args.positional) > 1 else None)
    try:
        raise SystemExit(
            main(
                args.base,
                args.write,
                corpus,
                roots,
                base_corpus=args.base_corpus,
                repo_root=args.repo_root,
            )
        )
    except (FileNotFoundError, ValueError) as error:
        print(f"ОТКАЗ: {error}", file=sys.stderr)
        raise SystemExit(2)
