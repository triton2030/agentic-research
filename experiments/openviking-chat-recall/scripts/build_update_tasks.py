#!/usr/bin/env python3
"""Обновление библиотеки: только то, чего слой тем ещё не видел.

Протокол умел собирать всё с нуля и не умел догонять. А корпус растёт каждый
день: между сборкой и этим прогоном накопилось 223 записи в 35 разговорах.
Полная пересборка их бы забрала, но заодно переписала бы 1100 уже проверенных
фактов — дорого и бессмысленно.

Поэтому агент получает разговор целиком (иначе реплика без соседей теряет
предмет), но отвечает **только за перечисленные строки**. Всё остальное в
файле для него контекст, а не задание.

    python3 build_update_tasks.py [--project-root ROOT] [--artifact-dir ART] \
        <папка заданий>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_retopic_tasks import topics_by_line
from record_identity import (
    RecordIdentity,
    load_noop_identities,
    record_identity,
    session_from_lines,
)

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_ROOT = SCRIPT_ROOT / "artifacts"
CONTRACT = SCRIPT_ROOT / "prompts/flatten-file.v1.md"
TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")
NOT_A_TOPIC = {"AGENTS.md", "README.md"}
ANCH = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")
REPAIR_TYPES = {"коррекция"}


def topic_distribution(text: str, rows: list[int]) -> dict[str, list[int]]:
    """Group task rows by their own canonical topic, never by holder."""
    by_record = topics_by_line(text.splitlines())
    grouped: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        grouped[by_record.get(row, "<без-topic>")].append(row)
    return dict(grouped)


def project_paths(project_root: str | Path | None = None) -> tuple[Path, Path]:
    root = Path.cwd() if project_root is None else Path(project_root)
    root = root.resolve()
    return root / "_ops/chat-recall/raw", root / "_ops/chat-recall/topics"


def classify_uncovered(
    name: str,
    lines: list[str],
    covered: set[tuple[str, int]],
    acknowledged_noops: set[RecordIdentity] | None = None,
) -> tuple[list[int], list[int]]:
    acknowledged_noops = acknowledged_noops or set()
    session = session_from_lines(lines)
    by_record = topics_by_line(lines)
    appendable: list[int] = []
    repair: list[int] = []
    for row, line in enumerate(lines, start=1):
        match = TYPE.search(line)
        identity = record_identity(session, line)
        if (
            not line.startswith("* ")
            or match is None
            or (name, row) in covered
            or identity in acknowledged_noops
        ):
            continue
        target = (
            repair
            if by_record.get(row) is None or match.group(1) in REPAIR_TYPES
            else appendable
        )
        target.append(row)
    return appendable, repair


def noop_identities(project_root: str | Path | None = None) -> set[RecordIdentity]:
    _, topics = project_paths(project_root)
    return load_noop_identities(topics / "reconcile-noops.json")


def pending_record(name: str, row: int, lines: list[str]) -> dict[str, object]:
    session = session_from_lines(lines)
    if session is None:
        raise ValueError(f"repair record has no session identity: {name}#L{row}")
    line = lines[row - 1]
    identity = record_identity(session, line)
    if identity is None:
        raise ValueError(f"repair record has no session identity: {name}#L{row}")
    topic = topics_by_line(lines).get(row)
    pending: dict[str, object] = {
        "topic": topic,
        "session": identity[0],
        "record_sha256": identity[1],
        "anchor": f"{name}#L{row}",
    }
    if topic is None:
        match = TYPE.search(line)
        pending["reason"] = "missing-topic"
        pending["type"] = match.group(1) if match else None
    return pending


def deltas(
    project_root: str | Path | None = None,
) -> tuple[dict[str, list[int]], list[dict[str, object]]]:
    corpus, topics = project_paths(project_root)
    covered: set[tuple[str, int]] = set()
    for path in sorted(topics.glob("*.md")):
        if path.name in NOT_A_TOPIC:
            continue
        text = path.read_text(encoding="utf-8")
        covered |= {(n, int(i)) for n, i in ANCH.findall(text)}
    fresh: dict[str, list[int]] = {}
    repair: list[dict[str, object]] = []
    acknowledged_noops = noop_identities(project_root)
    for path in sorted(corpus.glob("*.md")):
        name = path.name
        if name == "README.md":
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        appendable, pending = classify_uncovered(
            name, lines, covered, acknowledged_noops
        )
        if appendable:
            fresh[name] = appendable
        if pending:
            repair.extend(pending_record(name, row, lines) for row in pending)
    return fresh, repair


def delta(project_root: str | Path | None = None) -> dict[str, list[int]]:
    """Compatibility view: only rows safe for append-only update."""
    return deltas(project_root)[0]


def main(
    out_dir: str | Path,
    project_root: str | Path | None = None,
    artifact_root: str | Path | None = None,
) -> int:
    corpus, _ = project_paths(project_root)
    artifacts = (
        DEFAULT_ARTIFACT_ROOT
        if artifact_root is None
        else Path(artifact_root).resolve()
    )
    contract = CONTRACT.read_text(encoding="utf-8")
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    fresh, repair = deltas(project_root)
    for name, rows in fresh.items():
        text = (corpus / name).read_text(encoding="utf-8")
        numbered = "\n".join(
            f"{i}: {line}" for i, line in enumerate(text.splitlines(), 1)
        )
        distribution = topic_distribution(text, rows)
        placement = "\n".join(
            f"- `{topic}`: " + ", ".join(f"L{row}" for row in topic_rows)
            for topic, topic_rows in sorted(distribution.items())
        )
        (output / f"{name[:-3]}.txt").write_text(
            f"""Роль: редактор, превращающий запись разговора в сухое знание. Ниже контракт
работы, затем разговор целиком с пронумерованными строками.

**Отвечаешь только за перечисленные строки.** Остальной разговор дан как
контекст: без соседей реплика теряет предмет, и именно поэтому файл идёт
целиком. Но пункты пиши только по этим строкам — прочее уже разобрано раньше.

Строки задания: {", ".join(f"L{i}" for i in rows)}

Тема принадлежит каждой записи, не разговору целиком. Раскладка задания:

{placement}

Не схлопывай в один пункт anchors из разных тем. `<без-topic>` — повреждённая
запись: не угадывай её тему и не создавай по ней пункт.

{contract}

## Разговор `{name}`

```
{numbered}
```

## Ответ

Верни только содержимое выходного файла — от `---` до последнего пункта, без
пояснений и markdown-обёртки. Пунктов ровно столько, сколько самостоятельных
знаний нашлось в перечисленных строках; повтор внутри них схлопывается.
""",
            encoding="utf-8",
        )
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "update-delta.json").write_text(
        json.dumps(fresh, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (artifacts / "update-repair-pending.json").write_text(
        json.dumps(repair, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    missing_topics = sum(
        item.get("reason") == "missing-topic" for item in repair
    )
    print(
        f"заданий обновления: {len(fresh)} разговоров, {sum(len(v) for v in fresh.values())} записей -> {out_dir}"
    )
    print(
        "correction records left raw-only for explicit typed repair: "
        f"{len(repair)} -> "
        f"{artifacts / 'update-repair-pending.json'}"
    )
    if missing_topics:
        print(f"ОШИБКА: typed records без topic: {missing_topics}")
        return 1
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir", nargs="?", default="_workspace/ox-update/tasks")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.out_dir, args.project_root, args.artifact_dir))
