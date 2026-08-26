#!/usr/bin/env python3
"""Guarded routing of new per-record facts into existing topic files.

Обновление отличается от сборки одним: файл темы уже проверен, и переписывать
его целиком нельзя. Новые пункты дописываются в конец своего файла. Явные
`коррекция` остаются вне этой дельты: их по одной применяет typed
`topic_reconcile.py` после загрузки темы и source-record. Здесь только
проверяемая раскладка, сериализованная запись и счёт.

    python3 apply_update.py [--dry] [--project-root ROOT] \
        [--artifact-dir ART] [<папка прогонов>]
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave import strip_fence
from wave_ready import TOMBSTONE_HEADING

from build_retopic_tasks import topics_by_line

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_ROOT = SCRIPT_ROOT / "artifacts"
TRAILING_SHORTS = re.compile(r"\[((?:L\d+)(?:\s*,\s*L\d+)*)\]\s*$")
SHORT = re.compile(r"L(\d+)")
SOURCE_ANCHOR = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L\d+")


def project_paths(project_root: str | Path | None = None) -> tuple[Path, Path]:
    root = Path.cwd() if project_root is None else Path(project_root)
    root = root.resolve()
    return root / "_ops/chat-recall/raw", root / "_ops/chat-recall/topics"


def record_topics(
    name: str, project_root: str | Path | None = None
) -> dict[int, str]:
    """Тема каждой записи разговора: с переразметки она позаписная.

    Карта тем размещает разговор целиком, и до 2026-08-24 этого хватало. После
    переразметки 93 разговора из 213 несут по нескольку тем, и holder-маршрут
    отправлял бы новый пункт в тему соседней реплики.
    """
    corpus, _ = project_paths(project_root)
    path = corpus / name
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    return topics_by_line(lines)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@contextlib.contextmanager
def topic_lock(
    topic: str, project_root: str | Path | None = None
) -> Iterator[None]:
    """Share the same per-project lock protocol as 1chat-recall runtime."""
    root = Path.cwd() if project_root is None else Path(project_root)
    lock_path = topic_lock_path(root, topic)
    with lock_path.open("a", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def topic_lock_path(project: Path, topic: str) -> Path:
    lock_root = Path(tempfile.gettempdir()) / f"chat-recall-topic-locks-{os.getuid()}"
    lock_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    key = digest(f"{project.resolve()}\0{topic}")
    return lock_root / f"{key}.lock"


def write_atomic(path: Path, text: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), stat.S_IMODE(path.stat().st_mode))
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def normalize_sources(text: str) -> str:
    holders = set(SOURCE_ANCHOR.findall(text))
    rendered, count = re.subn(
        r"^sources:\s*\d+\s*$",
        f"sources: {len(holders)}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError("topic must contain exactly one numeric sources scalar")
    return rendered


def route_point(
    name: str,
    anchors: list[str],
    by_record: dict[int, str],
    want: set[tuple[str, int]],
    project_root: str | Path | None = None,
) -> tuple[str | None, list[int], str | None]:
    numbers = [int(anchor) for anchor in anchors]
    if any((name, number) not in want for number in numbers):
        return None, numbers, "пункт сослался не на строку текущей дельты"
    topics = {by_record.get(number) for number in numbers}
    if None in topics:
        return None, numbers, "у записи нет темы"
    if len(topics) != 1:
        return None, numbers, "пункт смешал записи разных тем"
    topic = next(iter(topics))
    assert topic is not None
    _, topics_dir = project_paths(project_root)
    if not (topics_dir / f"{topic}.md").is_file():
        return None, numbers, f"файла темы нет: {topic}"
    return topic, numbers, None


def trailing_anchors(line: str) -> tuple[list[str], str] | None:
    match = TRAILING_SHORTS.search(line)
    if match is None:
        return None
    return SHORT.findall(match.group(1)), line[: match.start()].rstrip()


def append_topic_rows(
    topic: str,
    rows: list[str],
    project_root: str | Path | None = None,
) -> bool:
    _, topics_dir = project_paths(project_root)
    path = topics_dir / f"{topic}.md"
    with topic_lock(topic, project_root):
        if not path.is_file():
            return False
        text = path.read_text(encoding="utf-8").rstrip("\n")
        # Legacy tombstones are history, not reader-facing topic content.
        # The immutable raw holder remains the provenance owner.
        tombstone = TOMBSTONE_HEADING.search(text)
        if tombstone:
            text = text[: tombstone.start()].rstrip()
        block = (
            f"\n\n## Добавлено {datetime.now().astimezone().date().isoformat()}\n\n"
            + "\n".join(rows)
            + "\n"
        )
        rendered = normalize_sources(text + block + "\n")
        write_atomic(path, rendered)
    return True


def main(
    runs: str | Path,
    dry: bool,
    project_root: str | Path | None = None,
    artifact_root: str | Path | None = None,
) -> int:
    artifacts = (
        DEFAULT_ARTIFACT_ROOT
        if artifact_root is None
        else Path(artifact_root).resolve()
    )
    delta = json.loads(
        (artifacts / "update-delta.json").read_text(encoding="utf-8")
    )
    fresh: dict[str, list[str]] = defaultdict(list)
    taken = refused = refused_points = 0
    covered: set[tuple[str, int]] = set()
    want = {(n, i) for n, rows in delta.items() for i in rows}

    for path in sorted(Path(runs).glob("*.json")):
        name = path.stem + ".md"
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            refused += 1
            continue
        body = strip_fence(payload.get("response") or "")
        if not payload.get("ok") or not body.startswith("---"):
            print(f"  не принят: {name}")
            refused += 1
            continue
        by_record = record_topics(name, project_root)
        for line in body.splitlines():
            if line.startswith("- "):
                parsed = trailing_anchors(line)
                if parsed is None:
                    continue
                anchors, claim = parsed
                topic, numbers, error = route_point(
                    name, anchors, by_record, want, project_root
                )
                if error is not None or topic is None:
                    refused_points += 1
                    print(f"  не принят пункт {name} {anchors}: {error}")
                    continue
                full = ", ".join(f"[{name}#L{n}]" for n in anchors)
                text = claim[2:].strip()
                fresh[topic].append(f"- {text} {full}")
                covered |= {(name, number) for number in numbers}
        taken += 1

    print(
        f"прогонов принято: {taken} | не принято: {refused} | "
        f"пунктов отклонено маршрутизацией: {refused_points}"
    )
    print(
        f"записей дельты: {len(want)} | покрыто новыми пунктами: {len(want & covered)}"
    )
    print(
        f"тем затронуто: {len(fresh)} | новых пунктов: {sum(len(v) for v in fresh.values())}"
    )
    missing = want - covered
    if missing:
        print(f"  не покрыты записи дельты: {len(missing)}")
        for name, number in sorted(missing):
            print(f"    {name}#L{number}")
        return 1
    if dry:
        return 1 if refused or refused_points else 0
    written = 0
    for topic, rows in sorted(fresh.items()):
        if append_topic_rows(topic, rows, project_root):
            written += 1
        else:
            print(f"  файл темы исчез до записи: {topic}")
    print(f"влито в {written} файлов тем")
    return 1 if refused or refused_points else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="?", default="_workspace/ox-update/runs")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--dry", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(
        main(args.runs, args.dry, args.project_root, args.artifact_dir)
    )
