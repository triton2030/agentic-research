#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML>=6.0"]
# ///
"""Mechanical checker for the bundled planning format.

The checker deliberately does not interpret Markdown prose.  It verifies the
file shape, typed frontmatter, links, relationships, derived values and the
small amount of progress syntax that the format makes mechanical.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - uv supplies the declared dependency.
    yaml = None  # type: ignore[assignment]


PLAN_TYPES = {"эпик", "задача", "вопрос"}
WORK_STATUSES = {"✅ готово", "🔨 в работе", "◽ в очереди", "🔒 заблокировано", "🛑 затык", "⏳ отложено"}
ACTIVE_STATUS = "🔨 в работе"
CLOSED_STATUS = "✅ готово"
QUESTION_STATUSES = {"открыт", "отвечен"}
HEALTH_VALUES = {"🟢", "🟠", "🔴", "не проверено"}
MODES = {"execution", "wayfinding"}
DERIVED_EPIC_FIELDS = {"задач", "задачи", "задач-готово"}
DERIVED_TASK_FIELDS = {"подзадач", "подзадач-готово"}
DERIVED_FIELDS = DERIVED_EPIC_FIELDS | DERIVED_TASK_FIELDS
SERVICE_NAMES = {"readme.md", "agents.md", "claude.md"}
MISSING = object()
EXPECTED_SECTIONS = {
    "эпик": ("Зачем", "Цель", "Канон", "Границы", "Критерии завершения", "Аппетит", "Состояние"),
    "задача": ("Задача", "Зачем", "Цель", "Критерии приёмки", "Канон", "Подзадачи", "Состояние"),
    "вопрос": ("Вопрос", "Влияние", "Варианты", "Ответ"),
}

FRONTMATTER_OPEN = "---"
WIKILINK_RE = re.compile(r"^\[\[(?P<target>[^\[\]]+)\]\]$")
H2_RE = re.compile(r"^[ \t]{0,3}##[ \t]+(?P<title>.*?)[ \t]*$")
FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})(?P<rest>.*)$")
CHECKBOX_RE = re.compile(r"^[ \t]*[-*+][ \t]+\[(?P<mark>[ xX])\][ \t]+(?P<label>.+?)[ \t]*$")
REPORT_RE = re.compile(r"^>[ \t]*\[!note\]-[ \t]*Отчёт[ \t]*$")
REPORT_STATUS_RE = re.compile(r"^>[ \t]*статус[ \t]+(?P<date>\d{4}-\d{2}-\d{2}):[ \t]*(?P<text>.*?)[ \t]*$")
REPORT_EVIDENCE_RE = re.compile(r"^>[ \t]*доказательство:[ \t]*(?P<value>.*?)[ \t]*$")
TOP_LEVEL_KEY_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<key>[^:#\s][^:]*?)[ \t]*:(?P<tail>.*?)(?P<newline>\r?\n|\Z)$")


@dataclass
class Issue:
    path: Path | None
    message: str
    derived: bool = False

    def format(self, root: Path) -> str:
        if self.path is None:
            where = "project"
        else:
            try:
                where = str(self.path.relative_to(root))
            except ValueError:
                where = str(self.path)
        prefix = "derived: " if self.derived else ""
        return f"{where}: {prefix}{self.message}"


@dataclass
class Report:
    root: Path
    issues: list[Issue] = field(default_factory=list)
    project: "Project | None" = None

    @property
    def ok(self) -> bool:
        return not self.issues

    def add(self, path: Path | None, message: str, *, derived: bool = False) -> None:
        self.issues.append(Issue(path, message, derived))


@dataclass
class Section:
    title: str
    heading: str
    content: str
    body_start_line: int


@dataclass
class Document:
    path: Path
    raw: str
    frontmatter_text: str
    body: str
    frontmatter: dict[str, Any]
    frontmatter_start: int
    frontmatter_end: int
    body_start: int
    hint: str | None = None
    kind: str | None = None
    sections: list[Section] = field(default_factory=list)
    preamble: str = ""


class InvocationError(Exception):
    """The command cannot be run against the supplied root or arguments."""


class DuplicateKeyError(ValueError):
    """A YAML mapping repeats a root key that safe_load would otherwise hide."""


def _safe_load(text: str) -> Any:
    """Load YAML safely and reject duplicate keys in a root mapping."""

    if yaml is None:
        raise RuntimeError("PyYAML is required (install PyYAML or run through uv)")
    node = yaml.compose(text, Loader=yaml.SafeLoader)
    if isinstance(node, yaml.nodes.MappingNode):
        seen: set[str] = set()
        for key_node, _ in node.value:
            if not isinstance(key_node, yaml.nodes.ScalarNode):
                continue
            key = key_node.value
            if key in seen:
                raise DuplicateKeyError(f"duplicate root YAML key: {key!r}")
            seen.add(key)
    return yaml.safe_load(text)


class Project:
    def __init__(self, root: Path, plans: Path, docs: Sequence[Document]):
        self.root = root
        self.plans = plans
        self.docs = list(docs)
        self.by_path = {doc.path.resolve(): doc for doc in docs}
        try:
            self.markdown_files = sorted(
                path.resolve()
                for path in root.rglob("*.md")
                if path.is_file()
            )
        except OSError:
            self.markdown_files = [doc.path.resolve() for doc in docs]
        self.epics = [doc for doc in docs if doc.kind == "эпик"]
        self.tasks = [doc for doc in docs if doc.kind == "задача"]
        self.questions = [doc for doc in docs if doc.kind == "вопрос"]

    def relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.root.resolve()).as_posix()

    def canonical_link(self, doc: Document) -> str:
        relative = self.relative(doc.path)
        if relative.lower().endswith(".md"):
            relative = relative[:-3]
        return f"[[{relative}]]"


def _normalise_newlines(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _read_utf8(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _split_frontmatter(raw: str) -> tuple[str, str, int, int, int] | None:
    """Return YAML/body and byte-like character offsets for a frontmatter block."""

    lines = raw.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != FRONTMATTER_OPEN:
        return None
    for index in range(1, len(lines)):
        line = lines[index]
        if line.rstrip("\r\n") == FRONTMATTER_OPEN:
            yaml_start = len(lines[0])
            yaml_end = sum(len(item) for item in lines[:index])
            body_start = yaml_end + len(line)
            return raw[yaml_start:yaml_end], raw[body_start:], yaml_start, yaml_end, body_start
    return None


def _parse_document(path: Path, hint: str | None = None) -> tuple[Document | None, str | None]:
    try:
        raw = _read_utf8(path)
    except (OSError, UnicodeError) as exc:
        return None, f"cannot read file: {exc}"
    split = _split_frontmatter(raw)
    if split is None:
        return None, "missing YAML frontmatter delimited by ---"
    frontmatter_text, body, fm_start, fm_end, body_start = split
    if yaml is None:
        return None, "PyYAML is required (install PyYAML or run through uv)"
    try:
        loaded = _safe_load(frontmatter_text)
    except (yaml.YAMLError, DuplicateKeyError) as exc:
        return None, f"invalid YAML frontmatter: {exc}"
    if not isinstance(loaded, dict):
        return None, "frontmatter must be a YAML mapping"
    document = Document(path, raw, frontmatter_text, body, dict(loaded), fm_start, fm_end, body_start, hint=hint)
    document.kind = _as_kind(document.frontmatter.get("тип")) or hint
    document.sections, document.preamble = _parse_sections(body)
    return document, None


def _as_kind(value: Any) -> str | None:
    return value if isinstance(value, str) and value in PLAN_TYPES else None


def _fence_transition(line: str, fence: tuple[str, int] | None) -> tuple[str, int] | None:
    match = FENCE_RE.match(line.rstrip("\r\n"))
    if fence is None:
        if match:
            token = match.group("fence")
            return token[0], len(token)
        return None
    if match and match.group("fence")[0] == fence[0] and len(match.group("fence")) >= fence[1]:
        if not match.group("rest").strip():
            return None
    return fence


def _parse_sections(body: str) -> tuple[list[Section], str]:
    lines = body.splitlines(keepends=True)
    headings: list[tuple[int, str, str]] = []
    fence: tuple[str, int] | None = None
    for index, line in enumerate(lines):
        previous = fence
        fence = _fence_transition(line, fence)
        if previous is not None or fence is not None:
            continue
        match = H2_RE.match(line.rstrip("\r\n"))
        if match:
            title = match.group("title")
            headings.append((index, title, line))
    if not headings:
        return [], body
    sections: list[Section] = []
    preamble = "".join(lines[: headings[0][0]])
    for position, (line_index, title, heading) in enumerate(headings):
        end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        sections.append(Section(title, heading, "".join(lines[line_index + 1 : end]), line_index + 1))
    return sections, preamble


def _service_file(path: Path) -> bool:
    return path.name.casefold() in SERVICE_NAMES


def _path_parts(path: Path, base: Path) -> tuple[str, ...]:
    return path.relative_to(base).parts


def _prefix_hint(path: Path) -> str | None:
    if path.name.startswith("epic - "):
        return "эпик"
    if path.name.startswith("task - "):
        return "задача"
    return None


def _candidate_path(path: Path, plans: Path) -> tuple[bool, str | None]:
    """Decide whether a Markdown file can be a plan without treating notes as plans."""

    if _service_file(path):
        return False, None
    rel = _path_parts(path, plans)
    if not rel:
        return False, None
    hint = _prefix_hint(path)
    if rel[0] == "вопросы":
        return True, "вопрос"
    if hint:
        return True, hint
    # The caller has already parsed frontmatter to identify a correctly typed
    # plan whose filename is malformed and therefore needs a placement error.
    return False, None


def _discover(plans: Path, report: Report) -> list[Document]:
    documents: list[Document] = []
    try:
        paths = sorted(plans.rglob("*.md"), key=lambda item: item.as_posix())
    except OSError as exc:
        report.add(plans, f"cannot scan plans directory: {exc}")
        return documents
    for path in paths:
        try:
            relative_parts = _path_parts(path, plans)
        except ValueError:
            continue
        if "_evidence" in relative_parts or _service_file(path):
            continue
        hint = _prefix_hint(path)
        is_question_location = bool(relative_parts and relative_parts[0] == "вопросы")
        # Parse prefixes/questions first so a missing тип is reported instead
        # of being silently treated as a note.
        if hint or is_question_location:
            document, error = _parse_document(path, hint if hint else ("вопрос" if is_question_location else None))
            if error:
                report.add(path, error)
                continue
            assert document is not None
            documents.append(document)
            continue
        # A malformed-name plan still has a type in frontmatter.  Reading the
        # frontmatter is harmless and lets us detect it without classifying
        # every arbitrary Markdown note as a plan.
        try:
            raw = _read_utf8(path)
        except (OSError, UnicodeError):
            continue
        split = _split_frontmatter(raw)
        if split is None or yaml is None:
            continue
        try:
            loaded = _safe_load(split[0])
        except (yaml.YAMLError, DuplicateKeyError):
            continue
        if not isinstance(loaded, dict) or "тип" not in loaded:
            continue
        if not isinstance(loaded.get("тип"), str) or loaded.get("тип") not in PLAN_TYPES:
            continue
        document, error = _parse_document(path)
        if error:
            report.add(path, error)
        elif document is not None:
            documents.append(document)
    return documents


def _require(mapping: Mapping[str, Any], key: str, doc: Document, report: Report) -> Any:
    if key not in mapping:
        report.add(doc.path, f"missing required field {key!r}")
        return MISSING
    return mapping[key]


def _string(value: Any, doc: Document, report: Report, key: str, *, nonempty: bool = False) -> bool:
    if not isinstance(value, str):
        report.add(doc.path, f"field {key!r} must be a string")
        return False
    if nonempty and not value.strip():
        report.add(doc.path, f"field {key!r} must not be empty")
        return False
    return True


def _integer(value: Any, doc: Document, report: Report, key: str, *, positive: bool = False, nonnegative: bool = False) -> bool:
    if isinstance(value, bool) or not isinstance(value, int):
        report.add(doc.path, f"field {key!r} must be an integer")
        return False
    if positive and value <= 0:
        report.add(doc.path, f"field {key!r} must be a positive integer")
        return False
    if nonnegative and value < 0:
        report.add(doc.path, f"field {key!r} must be non-negative")
        return False
    return True


def _iso_date(value: Any, doc: Document, report: Report, key: str, *, empty_allowed: bool = False) -> bool:
    if empty_allowed and value == "":
        return True
    if isinstance(value, dt.datetime):
        report.add(doc.path, f"field {key!r} must be an ISO date, not a datetime")
        return False
    if isinstance(value, dt.date):
        return True
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            dt.date.fromisoformat(value)
        except ValueError:
            pass
        else:
            return True
    report.add(doc.path, f"field {key!r} must be an ISO date")
    return False


def _list(value: Any, doc: Document, report: Report, key: str) -> bool:
    if not isinstance(value, list):
        report.add(doc.path, f"field {key!r} must be a list")
        return False
    return True


def _has_evidence(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip() not in {"—", "-"}


def _validate_frontmatter_common(doc: Document, report: Report) -> None:
    if "тип" not in doc.frontmatter:
        report.add(doc.path, "missing required field 'тип'")
    elif not isinstance(doc.frontmatter.get("тип"), str) or doc.frontmatter.get("тип") not in PLAN_TYPES:
        report.add(doc.path, "field 'тип' must be эпик, задача or вопрос")
    _require(doc.frontmatter, "статус", doc, report)
    if "обновлено" not in doc.frontmatter:
        report.add(doc.path, "missing required field 'обновлено'")
    else:
        _iso_date(doc.frontmatter["обновлено"], doc, report, "обновлено")


def _validate_sections(doc: Document, report: Report) -> None:
    if doc.kind not in EXPECTED_SECTIONS:
        return
    actual = tuple(section.title for section in doc.sections)
    expected = EXPECTED_SECTIONS[doc.kind]
    if actual != expected:
        report.add(doc.path, f"H2 sections must be exactly {list(expected)!r} in order; got {list(actual)!r}")
        return
    for section in doc.sections:
        if doc.kind == "вопрос" and section.title == "Ответ":
            continue
        if not section.content.strip():
            report.add(doc.path, f"section {section.title!r} must not be empty")


def _validate_placement(doc: Document, project: Project, report: Report) -> None:
    try:
        rel = _path_parts(doc.path, project.plans)
    except ValueError:
        report.add(doc.path, "plan file is outside _ops/plans")
        return
    valid = False
    if doc.kind == "эпик":
        valid = len(rel) == 3 and rel[0] == "эпики" and rel[2].startswith("epic - ") and rel[2].endswith(".md")
        if valid:
            folder_name = rel[1]
            file_name = rel[2][len("epic - ") : -3]
            if folder_name != file_name:
                report.add(doc.path, "epic filename and folder name must match")
    elif doc.kind == "задача":
        valid = len(rel) == 3 and rel[0] == "эпики" and rel[2].startswith("task - ") and rel[2].endswith(".md")
    elif doc.kind == "вопрос":
        valid = len(rel) == 2 and rel[0] == "вопросы" and rel[1].endswith(".md")
    if not valid:
        report.add(doc.path, f"{doc.kind or 'plan'} has an invalid placement or filename")


def _validate_epic_fields(doc: Document, report: Report) -> None:
    fm = doc.frontmatter
    status = _require(fm, "статус", doc, report)
    if status is not MISSING and (not isinstance(status, str) or status not in WORK_STATUSES):
        report.add(doc.path, "epic status is outside the shared status dictionary")
    for key in ("описание", "область", "ранний-индикатор", "допуск", "evidence"):
        value = _require(fm, key, doc, report)
        if value is not MISSING:
            _string(value, doc, report, key, nonempty=key in {"описание", "область", "ранний-индикатор"})
    order = _require(fm, "порядок", doc, report)
    if order is not MISSING:
        _integer(order, doc, report, "порядок", positive=True)
    launch = _require(fm, "запуск", doc, report)
    if launch is not None and not isinstance(launch, bool):
        report.add(doc.path, "field 'запуск' must be boolean")
    health = _require(fm, "health", doc, report)
    if health is not MISSING and (not isinstance(health, str) or health not in HEALTH_VALUES):
        report.add(doc.path, "field 'health' must be 🟢, 🟠, 🔴 or не проверено")
    canon = _require(fm, "канон", doc, report)
    if canon is not MISSING and _list(canon, doc, report, "канон"):
        for item in canon:
            if not isinstance(item, str):
                report.add(doc.path, "every канон item must be a project-relative Markdown path")
    deps = _require(fm, "зависит-от", doc, report)
    if deps is not MISSING and _list(deps, doc, report, "зависит-от"):
        for item in deps:
            if not isinstance(item, str):
                report.add(doc.path, "every depends-on item must be a wikilink")
    for key in ("задач", "задач-готово"):
        value = _require(fm, key, doc, report)
        if value is not MISSING:
            _integer(value, doc, report, key, nonnegative=True)
    tasks = _require(fm, "задачи", doc, report)
    if tasks is not MISSING and _list(tasks, doc, report, "задачи"):
        for item in tasks:
            if not isinstance(item, str):
                report.add(doc.path, "every задачи item must be a wikilink")
    if status == CLOSED_STATUS and isinstance(fm.get("evidence"), str) and not _has_evidence(fm["evidence"]):
        report.add(doc.path, "closed epic requires non-empty evidence")
    elif status != CLOSED_STATUS and isinstance(fm.get("evidence"), str) and fm["evidence"].strip():
        report.add(doc.path, "epic evidence must stay empty until the epic is accepted")


def _validate_task_fields(doc: Document, report: Report) -> None:
    fm = doc.frontmatter
    status = _require(fm, "статус", doc, report)
    if status is not MISSING and (not isinstance(status, str) or status not in WORK_STATUSES):
        report.add(doc.path, "task status is outside the shared status dictionary")
    for key in ("эпик", "допуск", "эпик-снимок", "траектория", "режим", "evidence"):
        value = _require(fm, key, doc, report)
        if value is not MISSING:
            _string(value, doc, report, key, nonempty=key in {"эпик", "допуск", "эпик-снимок", "траектория"})
    if isinstance(fm.get("эпик-снимок"), str) and not re.fullmatch(r"[0-9a-fA-F]{64}", fm["эпик-снимок"]):
        report.add(doc.path, "field 'эпик-снимок' must contain 64 hexadecimal characters")
    if "режим" in fm and (not isinstance(fm.get("режим"), str) or fm.get("режим") not in MODES):
        report.add(doc.path, "field 'режим' must be execution or wayfinding")
    order = _require(fm, "порядок", doc, report)
    if order is not MISSING:
        _integer(order, doc, report, "порядок", positive=True)
    for key in ("подзадач", "подзадач-готово"):
        value = _require(fm, key, doc, report)
        if value is not MISSING:
            _integer(value, doc, report, key, nonnegative=True)
    if "вопрос" in fm:
        if fm["вопрос"] is None:
            report.add(doc.path, "optional field 'вопрос' must be a wikilink or empty string")
        elif fm["вопрос"] != "":
            _string(fm["вопрос"], doc, report, "вопрос", nonempty=True)
    if status == CLOSED_STATUS:
        if isinstance(fm.get("evidence"), str) and not _has_evidence(fm["evidence"]):
            report.add(doc.path, "closed task requires non-empty evidence")
    elif isinstance(fm.get("evidence"), str) and fm["evidence"].strip():
        report.add(doc.path, "task evidence must stay empty until the task is accepted")


def _validate_question_fields(doc: Document, report: Report) -> None:
    fm = doc.frontmatter
    status = _require(fm, "статус", doc, report)
    if status is not MISSING and (not isinstance(status, str) or status not in QUESTION_STATUSES):
        report.add(doc.path, "question status must be открыт or отвечен")
    for key in ("касается", "адресат", "ответ-опора"):
        value = _require(fm, key, doc, report)
        if value is not MISSING:
            _string(value, doc, report, key, nonempty=key == "адресат")
    deadline = _require(fm, "срок", doc, report)
    if deadline is not MISSING:
        _iso_date(deadline, doc, report, "срок", empty_allowed=True)
    answer_support = fm.get("ответ-опора")
    answer_section = next((section for section in doc.sections if section.title == "Ответ"), None)
    answer_text = answer_section.content.strip() if answer_section else ""
    if status == "отвечен":
        if not answer_text:
            report.add(doc.path, "answered question requires non-empty Ответ section")
        if isinstance(answer_support, str) and not answer_support.strip():
            report.add(doc.path, "answered question requires non-empty ответ-опора")
    elif status == "открыт" and isinstance(answer_support, str) and answer_support.strip():
        report.add(doc.path, "ответ-опора must stay empty until the question is answered")


def _normalise_link_target(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    match = WIKILINK_RE.fullmatch(value.strip())
    if not match:
        return None
    target = match.group("target").strip()
    if not target or any(mark in target for mark in ("|", "#", "^")):
        return None
    if "\\" in target or "\x00" in target:
        return None
    while target.startswith("./"):
        target = target[2:]
    if target.startswith("/") or any(part in ("", "..") for part in target.split("/")):
        return None
    return target


def _resolve_link(project: Project, value: str, allowed: set[str] | None = None) -> tuple[Document | None, str | None]:
    target = _normalise_link_target(value)
    if target is None:
        return None, "invalid wikilink"
    path_target = target[:-3] if target.lower().endswith(".md") else target
    if "/" in path_target:
        exact: dict[Path, Document] = {}
        for base in (project.root, project.plans):
            candidate = (base / (path_target + ".md")).resolve()
            if not _inside(project.root, candidate) or not candidate.is_file():
                continue
            document = project.by_path.get(candidate)
            if document is not None and (allowed is None or document.kind in allowed):
                exact[candidate] = document
        if len(exact) == 1:
            return next(iter(exact.values())), None
        if len(exact) > 1:
            return None, "ambiguous wikilink"
        return None, "broken wikilink"

    # A target without a slash is a short stem.  Its uniqueness is a property
    # of the whole vault: a non-plan Markdown note with the same stem makes the
    # link ambiguous even when one of the matching files is a plan.
    matching_paths = [path for path in project.markdown_files if path.stem == path_target]
    if len(matching_paths) > 1:
        return None, "ambiguous wikilink"
    if not matching_paths:
        return None, "broken wikilink"
    document = project.by_path.get(matching_paths[0])
    if document is None or (allowed is not None and document.kind not in allowed):
        return None, "broken wikilink"
    return document, None


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _validate_canon_path(project: Project, doc: Document, value: str, report: Report) -> None:
    if not value or "\\" in value or "\x00" in value:
        report.add(doc.path, "канон paths must be project-relative Markdown files")
        return
    path_value = Path(value)
    if path_value.is_absolute() or ".." in path_value.parts or not value.lower().endswith(".md"):
        report.add(doc.path, f"канон path is not a project-relative Markdown path: {value!r}")
        return
    candidate = (project.root / path_value).resolve()
    if not _inside(project.root, candidate) or not candidate.is_file():
        report.add(doc.path, f"канон path does not exist inside project root: {value!r}")


def _checkbox_entries(content: str) -> list[tuple[int, bool, str, list[str]]]:
    lines = content.splitlines()
    entries: list[tuple[int, bool, str, list[str]]] = []
    fence: tuple[str, int] | None = None
    for index, line in enumerate(lines):
        previous = fence
        fence = _fence_transition(line, fence)
        if previous is not None or fence is not None:
            continue
        match = CHECKBOX_RE.match(line)
        if not match:
            continue
        checked = match.group("mark").lower() == "x"
        # The report belongs to this checkbox until the next checkbox.
        next_index = len(lines)
        for probe in range(index + 1, len(lines)):
            if CHECKBOX_RE.match(lines[probe]):
                next_index = probe
                break
        entries.append((index, checked, match.group("label"), lines[index + 1 : next_index]))
    return entries


def _valid_report(entry: tuple[int, bool, str, list[str]], doc: Document, report: Report) -> None:
    line_index, checked, label, following = entry
    if not label.strip():
        report.add(doc.path, f"subtask checkbox on line {line_index + 1} has empty text")
    cursor = 0
    while cursor < len(following) and not following[cursor].strip():
        cursor += 1
    if cursor == len(following) or not REPORT_RE.match(following[cursor]):
        report.add(doc.path, f"subtask checkbox on line {line_index + 1} must be followed by '> [!note]- Отчёт'")
        return
    report_lines = following[cursor + 1 :]
    status_match = next((REPORT_STATUS_RE.match(line) for line in report_lines if REPORT_STATUS_RE.match(line)), None)
    if status_match is None:
        report.add(doc.path, f"subtask report on line {line_index + 1} must include status YYYY-MM-DD: text")
    else:
        date_value = status_match.group("date")
        if not _valid_iso_date_value(date_value) or not status_match.group("text").strip():
            report.add(doc.path, f"subtask report on line {line_index + 1} has an invalid status date or empty text")
    if checked:
        evidence_match = next((REPORT_EVIDENCE_RE.match(line) for line in report_lines if REPORT_EVIDENCE_RE.match(line)), None)
        if evidence_match is None or not evidence_match.group("value").strip() or evidence_match.group("value").strip() in {"—", "-"}:
            report.add(doc.path, f"checked subtask report on line {line_index + 1} requires non-empty evidence")


def _valid_iso_date_value(value: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate_task_subtasks(doc: Document, report: Report) -> tuple[int, int] | None:
    section = next((item for item in doc.sections if item.title == "Подзадачи"), None)
    if section is None:
        return None
    entries = _checkbox_entries(section.content)
    if not 3 <= len(entries) <= 7:
        report.add(doc.path, "Подзадачи must contain between 3 and 7 checkboxes")
    for entry in entries:
        _valid_report(entry, doc, report)
    return len(entries), sum(1 for _, checked, _, _ in entries if checked)


def _normalise_value(value: Any) -> Any:
    if isinstance(value, dt.datetime):
        return value.isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _normalise_value(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_normalise_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _intent_body(doc: Document) -> str:
    parts = [doc.preamble]
    for section in doc.sections:
        if section.title == "Состояние":
            continue
        parts.extend((section.heading, section.content))
    return _normalise_newlines("".join(parts))


def compute_epic_snapshot(project: Project, epic: Document) -> str:
    excluded = {"статус", "health", "обновлено", "задач", "задачи", "задач-готово", "evidence"}
    frontmatter = {key: value for key, value in epic.frontmatter.items() if key not in excluded}
    canon_values = epic.frontmatter.get("канон", [])
    canon_files: list[dict[str, str]] = []
    if isinstance(canon_values, list):
        for value in canon_values:
            if not isinstance(value, str):
                continue
            candidate = (project.root / Path(value)).resolve()
            if _inside(project.root, candidate) and candidate.is_file():
                try:
                    text = _read_utf8(candidate)
                except (OSError, UnicodeError):
                    continue
                canon_files.append({"path": value, "content": _normalise_newlines(text)})
    goal_path = project.root / "_ops" / "GOAL.md"
    try:
        goal_text = _normalise_newlines(_read_utf8(goal_path))
    except (OSError, UnicodeError):
        goal_text = ""
    payload = {
        "frontmatter": _normalise_value(frontmatter),
        "intent": _intent_body(epic),
        "goal": goal_text,
        "canon": canon_files,
    }
    serialised = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialised.encode("utf-8")).hexdigest()


def _validate_relationships(project: Project, report: Report, *, include_derived: bool) -> dict[Path, Document | None]:
    parent_by_task: dict[Path, Document | None] = {}
    epic_deps: dict[Path, list[Document]] = {}
    for epic in project.epics:
        deps: list[Document] = []
        values = epic.frontmatter.get("зависит-от")
        if isinstance(values, list):
            for value in values:
                target, error = _resolve_link(project, value, {"эпик"})
                if error:
                    report.add(epic.path, f"зависит-от item: {error}")
                elif target is not None:
                    deps.append(target)
                    if target.path.resolve() == epic.path.resolve():
                        report.add(epic.path, "epic cannot depend on itself")
        epic_deps[epic.path.resolve()] = deps
    # Detect cycles in the explicit epic graph.
    visiting: set[Path] = set()
    visited: set[Path] = set()

    def visit(node: Document) -> None:
        key = node.path.resolve()
        if key in visiting:
            report.add(node.path, "epic dependency cycle detected")
            return
        if key in visited:
            return
        visiting.add(key)
        for dep in epic_deps.get(key, []):
            visit(dep)
        visiting.remove(key)
        visited.add(key)

    for epic in project.epics:
        visit(epic)

    for task in project.tasks:
        target, error = _resolve_link(project, task.frontmatter.get("эпик"), {"эпик"})
        if error:
            report.add(task.path, f"эпик: {error}")
            parent_by_task[task.path.resolve()] = None
            continue
        assert target is not None
        parent_by_task[task.path.resolve()] = target
        if task.path.parent.resolve() != target.path.parent.resolve():
            report.add(task.path, "task's эпик link must point to the epic in the same folder")
        admission = task.frontmatter.get("допуск")
        if admission == "эпик" and isinstance(target.frontmatter.get("допуск"), str) and not target.frontmatter["допуск"].strip():
            report.add(task.path, "допуск: эпик requires non-empty epic допуск")
        if task.frontmatter.get("вопрос") not in (None, ""):
            question, question_error = _resolve_link(project, task.frontmatter.get("вопрос"), {"вопрос"})
            if question_error:
                report.add(task.path, f"вопрос: {question_error}")
        # A task dependency field is tolerated as an optional extension and is
        # checked when present; the bundled schema does not require it.
        task_dependencies = task.frontmatter.get("зависит-от")
        if task_dependencies is not None:
            if not isinstance(task_dependencies, list):
                report.add(task.path, "optional task зависит-от must be a list")
            else:
                for value in task_dependencies:
                    dependency, dependency_error = _resolve_link(project, value, {"эпик", "задача"})
                    if dependency_error:
                        report.add(task.path, f"task dependency: {dependency_error}")
                    elif task.frontmatter.get("статус") == ACTIVE_STATUS and dependency is not None and dependency.frontmatter.get("статус") != CLOSED_STATUS:
                        report.add(task.path, "active task is behind an unfinished necessary dependency")

        if task.frontmatter.get("статус") == ACTIVE_STATUS:
            if target.frontmatter.get("статус") != ACTIVE_STATUS:
                report.add(task.path, "active task requires an active epic")
            if not isinstance(admission, str) or not admission.strip():
                report.add(task.path, "active task requires non-empty допуск")
            for dependency in epic_deps.get(target.path.resolve(), []):
                if dependency.frontmatter.get("статус") != CLOSED_STATUS:
                    report.add(task.path, "active task is behind an unfinished necessary epic dependency")

    # Validate a question's target after all plans are known.
    for question in project.questions:
        value = question.frontmatter.get("касается")
        target, error = _resolve_link(project, value, {"эпик", "задача"})
        if error:
            report.add(question.path, f"касается: {error}")
        elif target is None:  # defensive; _resolve_link returns an error otherwise.
            report.add(question.path, "касается: broken wikilink")
    return parent_by_task


def _validate_order(project: Project, report: Report, parent_by_task: Mapping[Path, Document | None]) -> None:
    seen_epic_orders: dict[int, Path] = {}
    for epic in project.epics:
        if epic.frontmatter.get("запуск") is not True:
            continue
        value = epic.frontmatter.get("порядок")
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        previous = seen_epic_orders.get(value)
        if previous is not None:
            report.add(epic.path, f"main-path epic order {value} duplicates {previous}")
        else:
            seen_epic_orders[value] = epic.path
    grouped: dict[Path, dict[int, Path]] = {}
    for task in project.tasks:
        parent = parent_by_task.get(task.path.resolve())
        if parent is None:
            continue
        value = task.frontmatter.get("порядок")
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        by_order = grouped.setdefault(parent.path.resolve(), {})
        previous = by_order.get(value)
        if previous is not None:
            report.add(task.path, f"task order {value} duplicates {previous}")
        else:
            by_order[value] = task.path


def _validate_derived(project: Project, report: Report, parent_by_task: Mapping[Path, Document | None], *, include_derived: bool) -> dict[Path, tuple[int, int]]:
    task_subtasks: dict[Path, tuple[int, int]] = {}
    for task in project.tasks:
        result = _validate_task_subtasks(task, report)
        if result is not None:
            task_subtasks[task.path.resolve()] = result
            if include_derived:
                count, done = result
                if task.frontmatter.get("подзадач") != count:
                    report.add(task.path, f"подзадач must equal checkbox count ({count})", derived=True)
                if task.frontmatter.get("подзадач-готово") != done:
                    report.add(task.path, f"подзадач-готово must equal checked checkbox count ({done})", derived=True)
        # A missing section is already reported by the exact H2 check; retain
        # zero values only for sync's defensive calculations.
        elif task.kind == "задача":
            task_subtasks[task.path.resolve()] = (0, 0)

    for epic in project.epics:
        colocated = [task for task in project.tasks if task.path.parent.resolve() == epic.path.parent.resolve()]
        colocated.sort(key=lambda item: (item.frontmatter.get("порядок", 0) if isinstance(item.frontmatter.get("порядок"), int) else 0, item.path.name))
        count = len(colocated)
        done = sum(1 for task in colocated if task.frontmatter.get("статус") == CLOSED_STATUS)
        expected_links = [project.canonical_link(task) for task in colocated]
        if include_derived:
            if epic.frontmatter.get("задач") != count:
                report.add(epic.path, f"задач must equal colocated task count ({count})", derived=True)
            if epic.frontmatter.get("задач-готово") != done:
                report.add(epic.path, f"задач-готово must equal closed task count ({done})", derived=True)
            if epic.frontmatter.get("задачи") != expected_links:
                report.add(epic.path, f"задачи must equal ordered full wikilinks {expected_links!r}", derived=True)
        if epic.frontmatter.get("статус") == CLOSED_STATUS:
            if isinstance(epic.frontmatter.get("evidence"), str) and not epic.frontmatter["evidence"].strip():
                # Field validation emits this too; keeping closure checks in
                # one place makes the reason visible when the field is present.
                pass
            if any(task.frontmatter.get("статус") != CLOSED_STATUS for task in colocated):
                report.add(epic.path, "closed epic cannot contain unfinished tasks")
    return task_subtasks


def _validate_snapshots(project: Project, report: Report, parent_by_task: Mapping[Path, Document | None]) -> None:
    snapshots: dict[Path, str] = {}
    for epic in project.epics:
        try:
            snapshots[epic.path.resolve()] = compute_epic_snapshot(project, epic)
        except (OSError, UnicodeError, ValueError) as exc:
            report.add(epic.path, f"cannot compute epic snapshot: {exc}")
    for task in project.tasks:
        value = task.frontmatter.get("эпик-снимок")
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
            continue
        parent = parent_by_task.get(task.path.resolve())
        if parent is None or parent.path.resolve() not in snapshots:
            continue
        if task.frontmatter.get("статус") != CLOSED_STATUS and value.lower() != snapshots[parent.path.resolve()]:
            report.add(task.path, "эпик-снимок is stale for an unfinished task")


def validate_root(root: Path, *, include_derived: bool = True) -> Report:
    """Validate a project root and return all mechanical issues found."""

    root = root.resolve()
    report = Report(root)
    plans = root / "_ops" / "plans"
    if not root.exists() or not root.is_dir():
        report.add(root, "root does not exist or is not a directory")
        return report
    if not plans.exists() or not plans.is_dir():
        report.add(root, "root must contain _ops/plans")
        return report
    for base_name in ("Дашборд.base", "Планы.base"):
        base_path = plans / base_name
        if not base_path.is_file():
            report.add(base_path, "required Bases file is missing")
            continue
        if yaml is None:
            report.add(base_path, "PyYAML is required (install PyYAML or run through uv)")
            continue
        try:
            loaded = _safe_load(_read_utf8(base_path))
        except (yaml.YAMLError, DuplicateKeyError, OSError, UnicodeError) as exc:
            report.add(base_path, f"invalid Bases YAML: {exc}")
            continue
        if not isinstance(loaded, dict) or "views" not in loaded or not loaded.get("views"):
            report.add(base_path, "Bases file must be a non-empty YAML mapping with views")
    goal = root / "_ops" / "GOAL.md"
    if not goal.is_file():
        report.add(goal, "required _ops/GOAL.md is missing")
    documents = _discover(plans, report)
    for document in documents:
        # Prefix files without тип are retained with their inferred kind so the
        # rest of the report remains useful; the missing field is still fatal.
        _validate_frontmatter_common(document, report)
        if document.kind not in PLAN_TYPES:
            continue
        _validate_placement(document, Project(root, plans, documents), report)
        _validate_sections(document, report)
        if document.kind == "эпик":
            _validate_epic_fields(document, report)
        elif document.kind == "задача":
            _validate_task_fields(document, report)
        else:
            _validate_question_fields(document, report)
    project = Project(root, plans, documents)
    report.project = project
    for epic in project.epics:
        canon = epic.frontmatter.get("канон")
        if isinstance(canon, list):
            for value in canon:
                if isinstance(value, str):
                    _validate_canon_path(project, epic, value, report)
    parent_by_task = _validate_relationships(project, report, include_derived=include_derived)
    _validate_order(project, report, parent_by_task)
    _validate_derived(project, report, parent_by_task, include_derived=include_derived)
    _validate_snapshots(project, report, parent_by_task)
    return report


def _frontmatter_key(line: str) -> str | None:
    match = TOP_LEVEL_KEY_RE.match(line)
    if not match or match.group("indent"):
        return None
    key = match.group("key").strip()
    if len(key) >= 2 and key[0] == key[-1] and key[0] in {"'", '"'}:
        key = key[1:-1]
    return key


def _render_derived_value(key: str, value: Any) -> str:
    if key == "задачи":
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _line_start(text: str, index: int) -> int:
    newline = text.rfind("\n", 0, index)
    return 0 if newline < 0 else newline + 1


def _line_end(text: str, start: int) -> tuple[int, str]:
    newline = text.find("\n", start)
    if newline < 0:
        return len(text), ""
    if newline > start and text[newline - 1] == "\r":
        return newline - 1, "\r\n"
    return newline, "\n"


def _preserve_block_comments(text: str, start: int, end: int) -> str:
    """Keep blank/comment lines that compose includes in a block node span."""

    preserved: list[str] = []
    cursor = start
    while cursor < end:
        raw_end, newline = _line_end(text, cursor)
        line_end = raw_end + len(newline)
        if line_end > end:
            line_end = end
        line = text[cursor:line_end]
        if not line.strip() or line.lstrip().startswith("#"):
            preserved.append(line)
        cursor = line_end
        if line_end == end:
            break
    return "".join(preserved)


def _compose_derived_nodes(frontmatter_text: str) -> dict[str, tuple[Any, Any]]:
    if yaml is None:
        raise RuntimeError("PyYAML is required (install PyYAML or run through uv)")
    root_node = yaml.compose(frontmatter_text, Loader=yaml.SafeLoader)
    if not isinstance(root_node, yaml.nodes.MappingNode):
        raise ValueError("frontmatter must be a YAML mapping")
    nodes: dict[str, tuple[Any, Any]] = {}
    for key_node, value_node in root_node.value:
        if not isinstance(key_node, yaml.nodes.ScalarNode):
            continue
        nodes[key_node.value] = (key_node, value_node)
    return nodes


def _rewrite_frontmatter(raw: str, document: Document, updates: Mapping[str, Any]) -> str:
    """Rewrite only existing top-level derived fields and preserve all else."""

    fm_raw = raw[document.frontmatter_start : document.frontmatter_end]
    nodes = _compose_derived_nodes(fm_raw)
    replacements: list[tuple[int, int, str]] = []
    for key, value in updates.items():
        pair = nodes.get(key)
        if pair is None:
            raise ValueError(f"cannot rewrite missing frontmatter field: {key!r}")
        key_node, value_node = pair
        rendered = _render_derived_value(key, value)
        value_start = value_node.start_mark.index
        value_end = value_node.end_mark.index
        # Flow/scalar values can be replaced by node span alone, preserving
        # comments and whitespace around the value byte-for-byte.
        if key != "задачи" or key_node.start_mark.line == value_node.start_mark.line:
            replacements.append((value_start, value_end, rendered))
            continue

        # A block sequence's node end includes intervening comments up to the
        # next root key. Rebuild the key line as an inline list and retain only
        # blank/comment lines from that span. This handles both '- item' and
        # indented '  - item' YAML sequences without deleting outside comments.
        key_line_start = _line_start(fm_raw, key_node.start_mark.index)
        key_line_end, newline = _line_end(fm_raw, key_line_start)
        key_end = key_node.end_mark.index
        colon_offset = key_end - key_line_start
        if colon_offset < 0 or colon_offset > len(fm_raw[key_line_start:key_line_end]):
            raise ValueError(f"cannot locate colon for frontmatter field: {key!r}")
        key_line = fm_raw[key_line_start:key_line_end]
        tail = key_line[colon_offset:]
        if not tail.startswith(":"):
            raise ValueError(f"cannot locate colon for frontmatter field: {key!r}")
        after_colon = tail[1:]
        comment_at = after_colon.find("#")
        comment = ""
        if comment_at >= 0:
            comment = after_colon[comment_at:]
            if comment and not comment.startswith(" "):
                comment = " " + comment
        new_key_line = key_line[:colon_offset] + ": " + rendered + comment + newline
        after_key_line = key_line_end + len(newline)
        preserved = _preserve_block_comments(fm_raw, after_key_line, value_end)
        replacements.append((key_line_start, value_end, new_key_line + preserved))

    rewritten = fm_raw
    for start, end, replacement in sorted(replacements, reverse=True):
        rewritten = rewritten[:start] + replacement + rewritten[end:]
    return raw[: document.frontmatter_start] + rewritten + raw[document.frontmatter_end :]


def sync_root(root: Path) -> tuple[Report, int]:
    """Synchronize derived fields after a non-derived preflight."""

    preflight = validate_root(root, include_derived=False)
    if not preflight.ok or preflight.project is None:
        return preflight, 0
    project = preflight.project
    parent_by_task = {
        task.path.resolve(): _resolve_link(project, task.frontmatter.get("эпик"), {"эпик"})[0]
        for task in project.tasks
    }
    updates_by_path: dict[Path, dict[str, Any]] = {}
    for task in project.tasks:
        entries = _validate_task_subtasks(task, Report(project.root))
        if entries is None:
            continue
        updates_by_path[task.path.resolve()] = {"подзадач": entries[0], "подзадач-готово": entries[1]}
    for epic in project.epics:
        colocated = [task for task in project.tasks if task.path.parent.resolve() == epic.path.parent.resolve()]
        colocated.sort(key=lambda item: (item.frontmatter.get("порядок", 0) if isinstance(item.frontmatter.get("порядок"), int) else 0, item.path.name))
        updates_by_path[epic.path.resolve()] = {
            "задач": len(colocated),
            "задачи": [project.canonical_link(task) for task in colocated],
            "задач-готово": sum(1 for task in colocated if task.frontmatter.get("статус") == CLOSED_STATUS),
        }
    changed: list[tuple[Document, str]] = []
    try:
        for document in project.docs:
            updates = updates_by_path.get(document.path.resolve())
            if not updates:
                continue
            if all(document.frontmatter.get(key) == value for key, value in updates.items()):
                continue
            changed.append((document, _rewrite_frontmatter(document.raw, document, updates)))
        for document, content in changed:
            with document.path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(content)
    except (OSError, ValueError, UnicodeError) as exc:
        failure = Report(project.root)
        failure.add(None, f"sync failed before post-check: {exc}")
        return failure, 0
    result = validate_root(root, include_derived=True)
    return result, len(changed)


def snapshot_path(root: Path, path_value: str) -> tuple[str | None, Report]:
    report = Report(root.resolve())
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not _inside(root, path) or not path.is_file():
        report.add(path, "snapshot target must be an existing file inside root")
        return None, report
    if not path.name.startswith("epic - "):
        report.add(path, "snapshot target must be an epic file")
        return None, report
    plans = root / "_ops" / "plans"
    document, error = _parse_document(path, "эпик")
    if error or document is None:
        report.add(path, error or "cannot parse snapshot target")
        return None, report
    project = Project(root.resolve(), plans.resolve(), [document])
    # The target's canonical files and GOAL are validated enough for snapshot
    # mode to avoid silently hashing an unreadable source.
    if not (root / "_ops" / "GOAL.md").is_file():
        report.add(root / "_ops" / "GOAL.md", "required _ops/GOAL.md is missing")
    canon = document.frontmatter.get("канон")
    if not isinstance(canon, list):
        report.add(path, "epic канон must be a list")
    else:
        for value in canon:
            if isinstance(value, str):
                _validate_canon_path(project, document, value, report)
            else:
                report.add(path, "every канон item must be a project-relative Markdown path")
    if report.issues:
        return None, report
    return compute_epic_snapshot(project, document), report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check the bundled _ops/plans format")
    parser.add_argument("--root", required=True, help="project root containing _ops/plans")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--sync", action="store_true", help="synchronize derived counters and task links")
    mode.add_argument("--snapshot", metavar="EPIC", help="print the SHA-256 snapshot for one epic")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse's documented invocation status.
        return int(exc.code)
    root = Path(args.root).expanduser()
    if not root.exists() or not root.is_dir():
        print(f"root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2
    if args.snapshot:
        digest, report = snapshot_path(root, args.snapshot)
        if not report.ok or digest is None:
            for issue in report.issues:
                print(issue.format(report.root), file=sys.stderr)
            return 1
        print(digest)
        return 0
    if args.sync:
        report, changed = sync_root(root)
    else:
        report = validate_root(root)
        changed = 0
    if report.ok:
        if args.sync:
            print(f"OK (synchronized {changed} file(s))")
        else:
            print("OK")
        return 0
    for issue in report.issues:
        print(issue.format(report.root), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
