#!/usr/bin/env python3
"""Build the project-level HTML artifact catalog."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from html import escape
from pathlib import Path

from artifact_metadata import read_artifact_metadata

CATALOG_TEMPLATE = (
    Path(__file__).resolve().parent.parent / "assets/catalog/index.template.html"
)


@dataclass(frozen=True)
class CatalogProject:
    slug: str
    title: str
    icon: str
    tags: tuple[str, ...]
    created_epoch: int
    page_count: int


def created_epoch(path: Path) -> int:
    stat = path.stat()
    return int(getattr(stat, "st_birthtime", stat.st_mtime))


def page_count(project_dir: Path) -> int:
    pages_dir = project_dir / "pages"
    if not pages_dir.is_dir():
        return 1

    pages = (
        page
        for page in pages_dir.glob("*.html")
        if page.is_file() and not page.name.startswith("_")
    )
    return 1 + sum(1 for _ in pages)


def collect_projects(artifacts_root: Path) -> list[CatalogProject]:
    projects: list[CatalogProject] = []

    for project_dir in artifacts_root.iterdir():
        if (
            not project_dir.is_dir()
            or project_dir.name == "_catalog"
            or not (project_dir / "index.html").is_file()
        ):
            continue

        metadata = read_artifact_metadata(project_dir / "index.html")
        fallback_title = project_dir.name.replace("-", " ").replace("_", " ")
        projects.append(
            CatalogProject(
                slug=project_dir.name,
                title=metadata.title or fallback_title,
                icon=metadata.icon,
                tags=metadata.tags,
                created_epoch=created_epoch(project_dir),
                page_count=page_count(project_dir),
            )
        )

    return sorted(projects, key=lambda project: project.created_epoch, reverse=True)


def project_payload(projects: list[CatalogProject]) -> str:
    payload = json.dumps(
        [asdict(project) for project in projects],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return payload.replace("</", "<\\/")


def count_label(count: int, one: str, few: str, many: str) -> str:
    last_two = count % 100
    last = count % 10
    if 11 <= last_two <= 14:
        word = many
    elif last == 1:
        word = one
    elif 2 <= last <= 4:
        word = few
    else:
        word = many
    return f"{count} {word}"


def build_html(projects: list[CatalogProject], template: str) -> str:
    count = len(projects)
    projects_label = count_label(count, "проект", "проекта", "проектов")
    generated = datetime.now().astimezone().isoformat(timespec="seconds")
    payload_attribute = escape(project_payload(projects), quote=True)

    return (
        template.replace(
            "__CATALOG_GENERATED_AT__", escape(generated, quote=True)
        )
        .replace("__CATALOG_PROJECT_COUNT__", str(count))
        .replace("__CATALOG_PROJECTS_LABEL__", projects_label)
        .replace("__CATALOG_PROJECT_PAYLOAD__", payload_attribute)
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: build_catalog.py <artifacts-root> <catalog-index>")

    artifacts_root = Path(sys.argv[1])
    catalog_index = Path(sys.argv[2])
    projects = collect_projects(artifacts_root)
    template = CATALOG_TEMPLATE.read_text(encoding="utf-8")
    catalog_index.write_text(build_html(projects, template), encoding="utf-8")


if __name__ == "__main__":
    main()
