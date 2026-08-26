"""Controlled metadata vocabulary shared by capture and retrieval.

Types stay a fixed speech-act vocabulary. Topics are owned by the corpus
itself: the set of long-lived subjects already used by its records, extended
deliberately at capture time rather than drawn from a hardcoded list.
"""

import re
from pathlib import Path

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
NON_TOPIC_STEMS = frozenset({"AGENTS", "CLAUDE", "README", "INDEX"})
TOMBSTONE_HEADING = re.compile(
    r"^[ \t]{0,3}#{1,6}[ \t]+отменено(?:[ \t]+#+)?[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)


def _topic_parts(path: Path) -> tuple[str | None, str | None, bool]:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError):
        return None, None, False

    title: str | None = None
    body_start = 0
    if lines and lines[0].strip() == "---":
        body_start = len(lines)
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start = index + 1
                break
            key, separator, value = line.partition(":")
            if separator and key.strip() == "title":
                title = " ".join(value.strip().strip("\"'").split()) or None

    paragraph: list[str] = []
    for raw_line in lines[body_start:]:
        line = raw_line.strip()
        if not line:
            if paragraph:
                break
            continue
        if line.startswith("#"):
            continue
        if line.startswith(("- ", "* ")):
            break
        paragraph.append(line)
    return title, " ".join(paragraph) or None, True


def topic_description(path: Path) -> str:
    """Return the shortest useful reader-facing description of a topic."""
    title, introduction, readable = _topic_parts(path)
    if not readable:
        return "[краткое описание недоступно]"
    if title and title != path.stem:
        return title
    return introduction or title or "[краткое описание отсутствует]"


def topic_search_text(path: Path) -> str:
    """Return title plus the topic boundary used only for retrieval."""
    title, introduction, readable = _topic_parts(path)
    if not readable:
        return "[краткое описание недоступно]"
    parts = [part for part in (title, introduction) if part]
    return "\n".join(dict.fromkeys(parts)) or "[краткое описание отсутствует]"


def topic_diagnostics(corpus_dir: Path) -> list[str]:
    """Return reader-facing topic schema violations beside a raw corpus."""
    root = corpus_dir.parent if corpus_dir.name == "raw" else corpus_dir
    layer = root / "topics"
    if not layer.is_dir():
        return []
    problems: list[str] = []
    for path in sorted(layer.glob("*.md")):
        if path.stem in NON_TOPIC_STEMS:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            continue
        if TOMBSTONE_HEADING.search(text):
            problems.append(f"topics/{path.name}: forbidden-topic-tombstone")
    return problems


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
