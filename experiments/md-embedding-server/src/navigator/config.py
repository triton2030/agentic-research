"""Per-project filter config for md-tools.

Reads `.md-tools.toml` at the corpus root. Resolved once per CLI/MCP entry
and applied as a baseline to `path_include` / `path_exclude` — CLI flags
**append** to that baseline (user decision 2026-05-23), they do not replace
it. To temporarily ignore the config a future `--no-config-filters` flag
may be added; on day one we keep the merge rule single and predictable.

Schema (current; extend cautiously):

    [index]
    include = []        # narrow indexed sections to these globs
    exclude = []        # drop indexed sections matching these globs

    [graph]
    include = []
    exclude = []

Missing file → empty config (no-op).
Broken TOML / wrong-typed entries → SystemExit with file path + reason.
Silent fallback would re-enable the very noise this config exists to suppress.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .value_coercion import coerce_string_list

CONFIG_FILENAME = ".md-tools.toml"


@dataclass(frozen=True)
class DomainFilters:
    include: tuple[str, ...]
    exclude: tuple[str, ...]

    @classmethod
    def empty(cls) -> "DomainFilters":
        return cls(include=(), exclude=())


@dataclass(frozen=True)
class CorpusConfig:
    index: DomainFilters
    graph: DomainFilters
    source: Path | None  # config file path, or None for empty/missing

    @classmethod
    def empty(cls) -> "CorpusConfig":
        return cls(
            index=DomainFilters.empty(),
            graph=DomainFilters.empty(),
            source=None,
        )


def _read_glob_list(
    section: dict, key: str, section_name: str, source: Path
) -> tuple[str, ...]:
    raw = section.get(key, [])
    if not isinstance(raw, list):
        raise SystemExit(
            f"{source}: [{section_name}].{key} must be a list of glob "
            f"strings, got {type(raw).__name__}"
        )
    out: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            raise SystemExit(
                f"{source}: [{section_name}].{key} entries must be strings, "
                f"got {type(item).__name__}: {item!r}"
            )
        cleaned = item.strip()
        if cleaned:
            out.append(cleaned)
    return tuple(out)


def _read_domain(
    data: dict, section_name: str, source: Path
) -> DomainFilters:
    section = data.get(section_name, {}) or {}
    if not isinstance(section, dict):
        raise SystemExit(
            f"{source}: [{section_name}] must be a table"
        )
    return DomainFilters(
        include=_read_glob_list(section, "include", section_name, source),
        exclude=_read_glob_list(section, "exclude", section_name, source),
    )


def load_corpus_config(corpus_root: Path) -> CorpusConfig:
    """Read `<corpus_root>/.md-tools.toml`. Missing file → empty config.

    Broken TOML or wrong-typed entries → SystemExit with file path + reason.
    """
    config_path = (Path(corpus_root) / CONFIG_FILENAME).resolve()
    if not config_path.exists():
        return CorpusConfig.empty()
    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"{config_path}: cannot read config — {exc}") from exc
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f"{config_path}: invalid TOML — {exc}") from exc

    return CorpusConfig(
        index=_read_domain(data, "index", config_path),
        graph=_read_domain(data, "graph", config_path),
        source=config_path,
    )


def merge_cli_with_config(
    config_list: tuple[str, ...],
    cli_list: list[str] | None,
) -> list[str]:
    """Append CLI patterns onto the config baseline.

    Config defines the always-on baseline; CLI flags add temporary
    narrowing. Empty / None CLI list → just the config baseline. Order
    is preserved (config first, CLI second) so downstream
    `apply_path_filters` semantics (include first, then exclude) are
    unchanged.
    """
    merged: list[str] = list(config_list)
    if cli_list:
        merged.extend(cli_list)
    return merged


def _normalize_to_list(value: Any) -> list[str]:
    return coerce_string_list(value)


def resolve_filters_for_domain(
    corpus_root: str | Path,
    *,
    domain: str,
    path_include: Any = None,
    path_exclude: Any = None,
) -> tuple[list[str], list[str]]:
    """Merge `.md-tools.toml` baseline with caller-supplied filters.

    Single entry point used by `navigator.api.*` so CLI and MCP paths
    apply the same config-baseline merge. `domain` is `"index"` or
    `"graph"`. CLI/MCP-supplied filters are appended onto the baseline
    (user decision 2026-05-23) so the config never silently disables
    explicit narrowing.
    """
    if domain not in {"index", "graph"}:
        raise ValueError(f"unknown filter domain: {domain!r}")
    cfg = load_corpus_config(Path(corpus_root))
    section = cfg.index if domain == "index" else cfg.graph
    return (
        merge_cli_with_config(section.include, _normalize_to_list(path_include)),
        merge_cli_with_config(section.exclude, _normalize_to_list(path_exclude)),
    )
