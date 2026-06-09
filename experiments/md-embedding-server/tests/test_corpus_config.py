"""Tests for `.md-tools.toml` per-project filter config loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from navigator.config import (
    CONFIG_FILENAME,
    CorpusConfig,
    DomainFilters,
    load_corpus_config,
    merge_cli_with_config,
    resolve_filter_layers_for_domain,
    resolve_filters_for_domain,
)


def test_filename_is_md_tools_toml() -> None:
    assert CONFIG_FILENAME == ".md-tools.toml"


def test_missing_file_returns_empty_config(tmp_path: Path) -> None:
    cfg = load_corpus_config(tmp_path)
    assert cfg == CorpusConfig.empty()
    assert cfg.source is None
    assert cfg.index.include == ()
    assert cfg.graph.exclude == ()


def test_empty_toml_returns_empty_filters_but_records_source(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / CONFIG_FILENAME
    config_path.write_text("", encoding="utf-8")
    cfg = load_corpus_config(tmp_path)
    assert cfg.index == DomainFilters.empty()
    assert cfg.graph == DomainFilters.empty()
    assert cfg.source == config_path.resolve()


def test_loads_both_sections(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILENAME).write_text(
        "[index]\n"
        'include = ["knowledge/*"]\n'
        'exclude = ["experiments/all-my-messages/*"]\n'
        "\n"
        "[graph]\n"
        "include = []\n"
        'exclude = ["_ops/plans/*", "drafts/**"]\n',
        encoding="utf-8",
    )
    cfg = load_corpus_config(tmp_path)
    assert cfg.index.include == ("knowledge/*",)
    assert cfg.index.exclude == ("experiments/all-my-messages/*",)
    assert cfg.graph.include == ()
    assert cfg.graph.exclude == ("_ops/plans/*", "drafts/**")


def test_only_index_section_present(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILENAME).write_text(
        '[index]\nexclude = ["foo/*"]\n', encoding="utf-8"
    )
    cfg = load_corpus_config(tmp_path)
    assert cfg.index.exclude == ("foo/*",)
    assert cfg.graph == DomainFilters.empty()


def test_strips_whitespace_and_drops_empty_entries(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILENAME).write_text(
        "[index]\n"
        'include = ["  knowledge/*  ", "", "    "]\n',
        encoding="utf-8",
    )
    cfg = load_corpus_config(tmp_path)
    assert cfg.index.include == ("knowledge/*",)


def test_broken_toml_exits_with_file_path(tmp_path: Path) -> None:
    config_path = tmp_path / CONFIG_FILENAME
    config_path.write_text("[index\nbroken", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        load_corpus_config(tmp_path)
    assert str(config_path) in str(exc.value)
    assert "invalid TOML" in str(exc.value)


def test_wrong_type_for_include_list_exits(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILENAME).write_text(
        '[index]\ninclude = "not-a-list"\n', encoding="utf-8"
    )
    with pytest.raises(SystemExit) as exc:
        load_corpus_config(tmp_path)
    msg = str(exc.value)
    assert "[index].include" in msg
    assert "list" in msg


def test_wrong_type_for_entry_exits(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILENAME).write_text(
        "[index]\ninclude = [1, 2]\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit) as exc:
        load_corpus_config(tmp_path)
    msg = str(exc.value)
    assert "[index].include" in msg
    assert "strings" in msg


def test_section_not_a_table_exits(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILENAME).write_text(
        'index = "not-a-table"\n', encoding="utf-8"
    )
    with pytest.raises(SystemExit) as exc:
        load_corpus_config(tmp_path)
    assert "[index] must be a table" in str(exc.value)


def test_frozen_dataclass_rejects_mutation() -> None:
    cfg = CorpusConfig.empty()
    with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
        cfg.index = DomainFilters(include=("x",), exclude=())  # type: ignore[misc]


# merge_cli_with_config


def test_merge_no_cli_returns_config_baseline() -> None:
    assert merge_cli_with_config(("a", "b"), None) == ["a", "b"]
    assert merge_cli_with_config(("a", "b"), []) == ["a", "b"]


def test_merge_cli_appends_to_config() -> None:
    assert merge_cli_with_config(("a", "b"), ["c"]) == ["a", "b", "c"]


def test_merge_empty_config_returns_cli_only() -> None:
    assert merge_cli_with_config((), ["x"]) == ["x"]


def test_merge_both_empty_returns_empty_list() -> None:
    assert merge_cli_with_config((), None) == []
    assert merge_cli_with_config((), []) == []


# resolve_filters_for_domain


def test_resolve_no_config_returns_normalized_input(tmp_path: Path) -> None:
    inc, exc = resolve_filters_for_domain(
        tmp_path,
        domain="index",
        path_include=["a", "b"],
        path_exclude=None,
    )
    assert inc == ["a", "b"]
    assert exc == []


def test_resolve_appends_cli_onto_config_baseline(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILENAME).write_text(
        "[index]\n"
        'exclude = ["experiments/all-my-messages/*"]\n'
        "\n"
        "[graph]\n"
        'exclude = ["_ops/plans/*"]\n',
        encoding="utf-8",
    )
    inc, exc = resolve_filters_for_domain(
        tmp_path,
        domain="index",
        path_include=None,
        path_exclude=["drafts/*"],
    )
    assert inc == []
    assert exc == ["experiments/all-my-messages/*", "drafts/*"]


def test_resolve_filter_layers_separates_config_and_operation(
    tmp_path: Path,
) -> None:
    (tmp_path / CONFIG_FILENAME).write_text(
        "[index]\n"
        'include = ["canon/*"]\n'
        'exclude = ["legacy/*"]\n',
        encoding="utf-8",
    )

    layers = resolve_filter_layers_for_domain(
        tmp_path,
        domain="index",
        path_include="scratch/*",
        path_exclude=["tmp/*"],
    )

    assert layers.config_include == ["canon/*"]
    assert layers.config_exclude == ["legacy/*"]
    assert layers.operation_include == ["scratch/*"]
    assert layers.operation_exclude == ["tmp/*"]
    assert layers.effective_include == ["canon/*", "scratch/*"]
    assert layers.effective_exclude == ["legacy/*", "tmp/*"]
    assert layers.source == (tmp_path / CONFIG_FILENAME).resolve()


def test_resolve_graph_uses_graph_section(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILENAME).write_text(
        '[index]\nexclude = ["one"]\n[graph]\nexclude = ["two"]\n',
        encoding="utf-8",
    )
    _, exc_graph = resolve_filters_for_domain(
        tmp_path, domain="graph", path_include=None, path_exclude=None
    )
    _, exc_index = resolve_filters_for_domain(
        tmp_path, domain="index", path_include=None, path_exclude=None
    )
    assert exc_graph == ["two"]
    assert exc_index == ["one"]


def test_resolve_accepts_comma_separated_string(tmp_path: Path) -> None:
    inc, _ = resolve_filters_for_domain(
        tmp_path,
        domain="index",
        path_include="a, b ,c",
        path_exclude=None,
    )
    assert inc == ["a", "b", "c"]


def test_resolve_rejects_unknown_domain(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        resolve_filters_for_domain(
            tmp_path, domain="overlaps", path_include=None, path_exclude=None
        )
