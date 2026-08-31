"""Controlled metadata vocabulary shared by capture and retrieval.

Types stay a fixed speech-act vocabulary. Topics are owned by the corpus
itself: the set of long-lived subjects already used by its records, extended
deliberately at capture time rather than drawn from a hardcoded list.
"""

import re
from pathlib import Path
from typing import NamedTuple

TYPE_DESCRIPTIONS = {
    "решение": "принятый долгоживущий курс или состояние",
    "коррекция": "исправление прежнего понимания, решения или действия",
    "предпочтение": "устойчивый способ, вкус или рабочее ожидание владельца",
    "идея": "возможность или гипотеза, которая ещё не принята",
    "критерий": "условие, по которому оценивают качество или успех",
    "правило-кандидат": "повторяемое правило до продвижения в owner-инструкцию",
    "обо-мне": "устойчивый личный или рабочий факт о владельце",
    "факт": "фактическое утверждение владельца, не независимая проверка истины",
}

REPAIR_TYPE = "неопределено"
REPAIR_TOPIC = "без-темы"
TYPES = (*TYPE_DESCRIPTIONS, REPAIR_TYPE)

TOPIC_ROW_RE = re.compile(r"^-\s+`(?P<handle>[^`]+)`\s+—\s+(?P<description>.+?)\s*$")
RETIRED_HEADING_RE = re.compile(r"^##\s+Не переиспользовать\s*$")


class TopicMap(NamedTuple):
    """The vocabulary of topics, owned by one file instead of a folder."""

    path: Path
    live: dict[str, str]
    retired: dict[str, str]


def parse_topic_map(path: Path) -> TopicMap | None:
    """Parse the live and retired rows of one topic-map file."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return None
    live: dict[str, str] = {}
    retired: dict[str, str] = {}
    target = live
    for line in lines:
        if RETIRED_HEADING_RE.match(line):
            target = retired
            continue
        match = TOPIC_ROW_RE.match(line)
        if match:
            target[match["handle"]] = match["description"]
    return TopicMap(path, live, retired)


def corpus_topics(log_dir: Path) -> dict[str, int]:
    """Topics already used by this corpus: name -> number of conversations."""
    counts: dict[str, int] = {}
    if not log_dir.is_dir():
        return counts
    for path in sorted(log_dir.glob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except OSError:
            continue
        if not lines or lines[0].strip() != "---":
            continue
        in_topics = False
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("topics:"):
                in_topics = True
                continue
            if in_topics:
                if line.startswith("  - "):
                    topic = line[4:].strip()
                    if topic and topic != REPAIR_TOPIC:
                        counts[topic] = counts.get(topic, 0) + 1
                else:
                    in_topics = False
    return counts
