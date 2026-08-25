#!/usr/bin/env python3
"""Провал П5 из ACCEPTANCE.md — исчерпывающе, а не выборкой, и с адресом потери.

«Молчаливая неполнота» задумывалась выборкой: берём случайные записи корпуса и
ищем их в библиотеке. Но у каждой записи есть точный адрес `файл.md#Lстрока`, а
каждая стадия конвейера носит эти же адреса. Значит отсутствие не оценивается,
а считается — и считается постадийно: разность множеств называет не только
сколько потеряно, но и где.

Корпус живёт дальше и после сборки, поэтому судить его состоянием на диске
нечестно вдвойне: появились новые разговоры, а старые доросли новыми строками.
Правду о том, что библиотека вообще видела, хранит git — снимок читается из
коммита сборки.

    python3 check_coverage.py [--live] [--project-root ROOT] \
        [--artifact-dir ART] [<коммит-снимка>]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
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

# Разделитель перед `type:` за год поменялся: ранние записи пишут `— type:`,
# поздние — `| type:`. Оба формата остаются живыми записями корпуса.
TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")
# Якорь одинаков во всех трёх записях: голый в темах, в ссылке на страницах.
ANCHOR = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")

Address = tuple[str, int]


def project_paths(project_root: str | Path | None = None) -> tuple[Path, Path]:
    root = Path.cwd() if project_root is None else Path(project_root)
    root = root.resolve()
    return root / "_ops/chat-recall/raw", root / "_ops/chat-recall/topics"


def noop_identities(project_root: str | Path | None = None) -> set[RecordIdentity]:
    _, topics = project_paths(project_root)
    return load_noop_identities(topics / "reconcile-noops.json")


def blob_at(
    rev: str, path: str, project_root: str | Path | None = None
) -> str | None:
    root = Path.cwd() if project_root is None else Path(project_root)
    done = subprocess.run(
        ["git", "show", f"{rev}:{path}"],
        capture_output=True,
        text=True,
        cwd=root,
    )
    return done.stdout if done.returncode == 0 else None


def as_of_snapshot(
    name: str,
    rev: str | None,
    project_root: str | Path | None = None,
) -> str:
    """Разговор в том виде, в каком его взяла сборка.

    Копия на диске взята из рабочего дерева, а часть разговоров попала в git
    позже неё — в том числе разговор, который сессия сборки писала про себя
    же. Для таких берём первый коммит, где файл появился: ближайшее к снимку
    зафиксированное состояние. Читать их сегодняшними — приписать библиотеке
    пропуск строк, которых на момент сборки не существовало.
    """
    corpus, _ = project_paths(project_root)
    if rev is None:
        return (corpus / name).read_text(encoding="utf-8")
    text = blob_at(rev, f"_ops/chat-recall/raw/{name}", project_root)
    if text is not None:
        return text
    added = subprocess.run(
        [
            "git",
            "log",
            "--format=%H",
            "--diff-filter=A",
            "--",
            f"_ops/chat-recall/raw/{name}",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=project_root,
    ).stdout.split()
    if added:
        text = blob_at(added[-1], f"_ops/chat-recall/raw/{name}", project_root)
        if text is not None:
            return text
    return (corpus / name).read_text(encoding="utf-8")


def snapshot(
    rev: str | None,
    project_root: str | Path | None = None,
    artifact_root: str | Path | None = None,
) -> tuple[
    dict[Address, str],
    dict[str, str | None],
    dict[Address, str | None],
]:
    """Записи корпуса на момент сборки: адрес -> строка целиком.

    Состав снимка задаёт не git, а сама сборка: имена файлов в `flat/`.
    """
    records: dict[Address, str] = {}
    sessions: dict[str, str | None] = {}
    topics: dict[Address, str | None] = {}
    artifacts = (
        DEFAULT_ARTIFACT_ROOT
        if artifact_root is None
        else Path(artifact_root).resolve()
    )
    flat_dir = artifacts / "flatten-v1/flat"
    for path in sorted(flat_dir.glob("*.md")):
        name = path.name
        lines = as_of_snapshot(name, rev, project_root).splitlines()
        sessions[name] = session_from_lines(lines)
        by_line = topics_by_line(lines)
        for number, line in enumerate(lines, start=1):
            if line.startswith("* ") and TYPE.search(line):
                records[(name, number)] = line.strip()
                topics[(name, number)] = by_line.get(number)
    return records, sessions, topics


def flat_anchors(artifact_root: str | Path | None = None) -> set[Address]:
    """Стадия 1 адресует строки числом `L20`, а файл называет в шапке."""
    found: set[Address] = set()
    artifacts = (
        DEFAULT_ARTIFACT_ROOT
        if artifact_root is None
        else Path(artifact_root).resolve()
    )
    for path in sorted((artifacts / "flatten-v1/flat").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        head = re.search(r"^source:\s*(\S+)", text, re.M)
        source = head.group(1) if head else path.name
        for line in text.splitlines():
            if line.startswith("- "):
                found |= {(source, int(n)) for n in re.findall(r"L(\d+)", line)}
    return found


# Слой тем держит рядом свой контракт для агентов; пример якоря внутри него
# засчитался бы покрытой записью и молча выбросил её из дельты обновления.
NOT_A_TOPIC = {"AGENTS.md", "README.md"}


def anchors(topics_dir: str | Path) -> set[Address]:
    found: set[Address] = set()
    for path in sorted(Path(topics_dir).glob("*.md")):
        if path.name in NOT_A_TOPIC:
            continue
        text = path.read_text(encoding="utf-8")
        found |= {(name, int(n)) for name, n in ANCHOR.findall(text)}
    return found


def main(
    rev: str | None,
    project_root: str | Path | None = None,
    artifact_root: str | Path | None = None,
) -> int:
    _, topics_dir = project_paths(project_root)
    artifacts = (
        DEFAULT_ARTIFACT_ROOT
        if artifact_root is None
        else Path(artifact_root).resolve()
    )
    records, snapshot_sessions, snapshot_topics = snapshot(
        rev, project_root, artifacts
    )
    known = set(records)
    acknowledged_noops = noop_identities(project_root)
    # Конечный продукт — слой тем. Стадия страниц снята 2026-08-24, и пока она
    # стояла здесь последней, вердикт «ничего не потеряно» выносился по снятой
    # библиотеке: проверка честно судила продукт, которым никто не пользуется.
    stages = [
        ("1  снимок -> сжатые файлы", flat_anchors(artifacts)),
        ("3  сжатые -> темы", anchors(topics_dir)),
    ]

    print(f"снимок {rev or 'live'}: {len(records)} записей корпуса\n")
    seen = known
    for label, reached in stages:
        print(
            f"стадия {label:28s} адресов {len(reached):5d}"
            f" | дошло {len(reached & known):5d} | потеряно {len(seen - reached):4d}"
        )
        seen = reached & known

    library = stages[-1][1]  # слой тем
    # Запись без адреса в библиотеке бывает двух разных вещей, и мешать их
    # нельзя: пропущенная молча — дефект, а признанная не несущей знания —
    # результат работы. Весь смысл добора в том, чтобы вторых не оставалось
    # без имени, поэтому они считаются отдельно и в дефект не идут.
    declared: dict[Address, str] = {}
    decisions = artifacts / "coverage-decisions.tsv"
    if decisions.is_file():
        for row in decisions.read_text(encoding="utf-8").splitlines():
            fields = row.split("\t", 2)
            if len(fields) < 2:
                continue
            anchor, verdict = fields[:2]
            name, _, number = anchor.rpartition("#L")
            if number.isdigit():
                declared[(name, int(number))] = verdict
    noop_addresses = {
        address
        for address, line in records.items()
        if record_identity(snapshot_sessions.get(address[0]), line)
        in acknowledged_noops
    }
    no_topic = sorted(
        address
        for address in known
        if snapshot_topics.get(address) is None and address not in noop_addresses
    )
    no_topic_set = set(no_topic)
    silent = sorted(
        address
        for address in known - library - noop_addresses - no_topic_set
        if declared.get(address) in (None, "без-решения")
    )
    named = sorted((known - library) - set(silent) - no_topic_set)
    dangling = sorted(library - known)
    accounted = len(records) - len(silent) - len(no_topic)
    print(
        f"\nстоит в слое тем: {len(known & library)} из {len(records)}"
        f" ({100 * len(known & library) / max(len(records), 1):.1f}%)"
    )
    print(
        f"учтено — в теме либо названо: {accounted}"
        f" ({100 * accounted / max(len(records), 1):.1f}%)"
    )
    print(f"НЕ покрыто молча (П5): {len(silent)}")
    print(f"typed records без topic: {len(no_topic)}")
    print(f"названо не несущим знания (не дефект): {len(named)}")
    print(f"адрес слоя не указывает на запись снимка: {len(dangling)}")

    if silent:
        print(
            "\nнепокрытые по типу записи:",
            dict(
                Counter(
                    TYPE.search(records[a]).group(1) for a in silent
                ).most_common()
            ),
        )
        for name, number in silent:
            print(f"  {name}#L{number}")
    if no_topic:
        print("\ntyped records без topic:")
        for name, number in no_topic:
            print(f"  {name}#L{number}")
    if dangling:
        print("\nвисячие адреса слоя:")
        for name, number in dangling:
            print(f"  {name}#L{number}")

    # Горизонт библиотеки. Проверка выше судит только то, что сборка видела, —
    # иначе она наказывала бы за разговоры, которых на момент сборки не было.
    # Но у этой честности есть цена: провалиться на свежих записях она не может
    # по построению, а именно там и живёт опасность. Библиотека, ставшая
    # рекомендуемым маршрутом, всегда отстаёт от разговора, и отставание растёт
    # молча. Поэтому горизонт считается отдельным числом и печатается всегда.
    live: set[Address] = set()
    live_noops: set[Address] = set()
    live_no_topic: set[Address] = set()
    corpus, _ = project_paths(project_root)
    for path in sorted(corpus.glob("*.md")):
        name = path.name
        if name == "README.md":
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        session = session_from_lines(lines)
        by_line = topics_by_line(lines)
        for number, line in enumerate(lines, start=1):
            if line.startswith("* ") and TYPE.search(line):
                address = (name, number)
                live.add(address)
                identity = record_identity(session, line)
                if by_line.get(number) is None and identity not in acknowledged_noops:
                    live_no_topic.add(address)
                if identity in acknowledged_noops:
                    live_noops.add(address)
    # Горизонт мерится по слою, а не по снимку стадии сжатия: обновление идёт
    # из корпуса прямо в темы, минуя `flat/`, и разница со снимком говорит о
    # маршруте, которым свежие разговоры не ходят. Читателю важно одно —
    # сколько живых записей корпуса слой ещё не знает.
    unseen = sorted(live - library - live_noops)
    print(
        f"\nгоризонт: в корпусе {len(live)} записей, слой знает {len(live & library)}"
    )
    print(f"признано без эффекта на тему: {len(live_noops)}")
    print(f"в живом корпусе без topic: {len(live_no_topic)}")
    print(
        f"слой ещё не знает: {len(unseen)} записей"
        f" ({100 * len(unseen) / max(len(live), 1):.1f}%)"
    )
    fresh = sorted({name for name, _ in unseen})
    if fresh:
        print(f"разговоров с непрочитанными записями: {len(fresh)}")
        for name in fresh[:10]:
            print(f"  {name}")
    return 1 if silent or no_topic or live_no_topic or dangling else 0


def snapshot_commit(project_root: str | Path | None = None) -> str | None:
    """Коммит снимка живёт рядом со слоем, а не константой в проверке.

    Зашитый коммит делает проверку вечно привязанной к одной сборке: после
    полного догона она продолжала печатать «слой их не видел никогда» про
    записи, которые в слое уже стоят.
    """
    _, topics = project_paths(project_root)
    horizon = topics / "horizon.json"
    if not horizon.is_file():
        return None
    commit = json.loads(horizon.read_text(encoding="utf-8")).get("commit")
    return commit if isinstance(commit, str) and commit else None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision", nargs="?")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args(argv)
    if args.live and args.revision is not None:
        parser.error("--live cannot be combined with a revision")
    if not args.live and args.revision is None:
        args.revision = snapshot_commit(args.project_root)
    if args.live:
        args.revision = None
    return args


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.revision, args.project_root, args.artifact_dir))
