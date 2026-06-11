from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Callable

from navigator.config import CanonConfig, load_corpus_config
from navigator.filters import path_matches_any
from navigator.markdown_io import iter_markdown, parse_frontmatter

BADGES = {"canon": "КАНОН", "product": "ПРОДУКТ", "future": "FUTURE"}


def load_zone_config(corpus_root: str | Path) -> CanonConfig:
    return load_corpus_config(Path(corpus_root)).canon


def classify_by_glob(rel_path: str, cfg: CanonConfig) -> str | None:
    if path_matches_any(rel_path, list(cfg.future)):
        return "future"
    if path_matches_any(rel_path, list(cfg.root)):
        return "canon"
    return None


def badge_for(zone: str | None) -> str | None:
    if not zone:
        return None
    return BADGES.get(zone, zone.upper())


def build_zone_map(corpus_root: Path) -> dict[str, str]:
    root = corpus_root.resolve()
    zones: dict[str, str] = {}
    for path in iter_markdown(root):
        if path.name != "AGENTS.md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        data = parse_frontmatter(text.splitlines())
        zone = data.get("zone")
        if not isinstance(zone, str) or not zone.strip():
            continue
        folder = path.parent.resolve().relative_to(root).as_posix()
        zones["." if folder == "." else folder] = zone.strip()
    return zones


def resolve_zone(rel_path: str, zone_map: dict[str, str], cfg: CanonConfig) -> str | None:
    path = PurePosixPath(rel_path)
    candidates = [path.parent, *path.parent.parents]
    for parent in candidates:
        key = "." if str(parent) in {"", "."} else parent.as_posix()
        if key in zone_map:
            return zone_map[key]
    return classify_by_glob(rel_path, cfg)


def make_zone_resolver(
    corpus_root: Path,
    zone_map: dict[str, str],
    cfg: CanonConfig,
) -> Callable[[str], tuple[str | None, str | None]]:
    def _resolve(rel_path: str) -> tuple[str | None, str | None]:
        zone = resolve_zone(rel_path, zone_map, cfg)
        return zone, badge_for(zone)

    return _resolve
