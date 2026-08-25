#!/usr/bin/env python3
"""Сдвинуть горизонт слоя тем: докуда он знает корпус.

Горизонт был ручным шагом в конце обновления, и ручные шаги в этой системе
стабильно забывают: слой, обещающий меньше, чем знает, безобиден, а слой,
знающий меньше обещанного, врёт читателю уверенно. Поэтому число считается
из тех же файлов, что и всё остальное, а не проставляется рукой.

    python3 set_horizon.py [--dry] [--project-root ROOT]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_retopic_tasks import topics_by_line
from record_identity import (
    RecordIdentity,
    load_noop_identities,
    record_identity,
    session_from_lines,
)

TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")
NOT_A_TOPIC = {"AGENTS.md", "README.md"}
ANCHOR = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")


def project_paths(project_root: str | Path | None = None) -> tuple[Path, Path]:
    root = Path.cwd() if project_root is None else Path(project_root)
    root = root.resolve()
    return root / "_ops/chat-recall/raw", root / "_ops/chat-recall/topics"


def noop_identities(topics_dir: str | Path | None = None) -> set[RecordIdentity]:
    if topics_dir is None:
        _, topics_dir = project_paths()
    return load_noop_identities(Path(topics_dir) / "reconcile-noops.json")


def main(dry: bool, project_root: str | Path | None = None) -> int:
    corpus, topics_dir = project_paths(project_root)
    records = conversations = 0
    records_without_topic = 0
    record_identities: set[RecordIdentity] = set()
    acknowledged_noops = noop_identities(topics_dir)
    for path in sorted(corpus.glob("*.md")):
        if path.name == "README.md":
            continue
        conversations += 1
        lines = path.read_text(encoding="utf-8").splitlines()
        session = session_from_lines(lines)
        by_line = topics_by_line(lines)
        for number, stripped in enumerate(lines, start=1):
            if stripped.startswith("* ") and TYPE.search(stripped):
                records += 1
                identity = record_identity(session, stripped)
                if (
                    by_line.get(number) is None
                    and identity not in acknowledged_noops
                ):
                    records_without_topic += 1
                if identity is not None:
                    record_identities.add(identity)

    covered: set[tuple[str, int]] = set()
    topics = 0
    for path in sorted(topics_dir.glob("*.md")):
        if path.name in NOT_A_TOPIC:
            continue
        topics += 1
        text = path.read_text(encoding="utf-8")
        covered |= {(n, int(i)) for n, i in ANCHOR.findall(text)}

    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        cwd=Path(project_root).resolve() if project_root is not None else Path.cwd(),
    )
    commit = head.stdout.strip() if head.returncode == 0 else None
    horizon = {
        "commit": commit,
        "date": date.today().isoformat(),
        "records": records,
        "conversations": conversations,
        "topics": topics,
        "anchors_in_layer": len(covered),
        "records_with_no_topic_effect": len(
            record_identities & acknowledged_noops
        ),
        "records_without_topic": records_without_topic,
    }
    print(json.dumps(horizon, ensure_ascii=False, indent=1))
    if records_without_topic:
        print(f"ОШИБКА: typed records без topic: {records_without_topic}")
        return 1
    if dry:
        return 0
    horizon_path = topics_dir / "horizon.json"
    horizon_path.write_text(
        json.dumps(horizon, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"горизонт сдвинут -> {horizon_path}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--dry", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.dry, args.project_root))
