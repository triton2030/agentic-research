from __future__ import annotations

from pathlib import Path

from navigator import index
from navigator.workflows import canon_check


def _write_corpus(root: Path, *, with_config: bool = True) -> tuple[Path, Path]:
    root.mkdir()
    if with_config:
        (root / ".md-tools.toml").write_text('[canon]\nroot = ["criteria*"]\nfuture = ["future*"]\n', encoding="utf-8")
    criteria = root / "criteria.md"
    criteria.write_text(
        "---\ndescription: Canon criteria\ndepends-on: []\n---\n\n"
        "# Criteria\n\n## Rule\n\nСтудия должна платить только после события Принять.\n",
        encoding="utf-8",
    )
    source = root / "source.md"
    source.write_text(
        "# Source\n\n## Правило\n\nСтудия должна платить только после события Принять.\n",
        encoding="utf-8",
    )
    (root / "noise.md").write_text(
        "# Noise\n\n## Rule\n\nСтудия должна платить до события Принять.\n",
        encoding="utf-8",
    )
    return source, criteria


def test_canon_check_returns_pairs_from_warm_index(tmp_path: Path, mock_embed) -> None:
    source, criteria = _write_corpus(tmp_path / "corpus")
    index(str(source.parent), confirm=True)

    payload = canon_check(str(source), str(source.parent), mode="single")

    assert payload["workflow"] == "md_canon_check"
    assert payload["pairs"]
    quote = payload["pairs"][0]["quotes"][0]
    assert quote["relative_path"] == criteria.name
    assert quote["start_line"] is not None
    assert quote["quote"]


def test_canon_check_no_config_is_graceful(tmp_path: Path, mock_embed) -> None:
    source, _criteria = _write_corpus(tmp_path / "corpus", with_config=False)
    index(str(source.parent), confirm=True)

    payload = canon_check(str(source), str(source.parent), mode="single")

    assert "no_canon_config" in payload["quality_flags"]
    assert payload["pairs"][0]["quotes"][0]["zone"] is None


def test_canon_check_scopes_to_canon_root(tmp_path: Path, mock_embed) -> None:
    source, _criteria = _write_corpus(tmp_path / "corpus")
    index(str(source.parent), confirm=True)

    payload = canon_check(str(source), str(source.parent), mode="single")

    paths = {quote["relative_path"] for pair in payload["pairs"] for quote in pair["quotes"]}
    assert paths == {"criteria.md"}


def test_canon_check_separates_authority_dependent_and_parking_quotes(tmp_path: Path, mock_embed) -> None:
    root = tmp_path / "corpus"
    root.mkdir()
    (root / ".md-tools.toml").write_text('[canon]\nroot = ["01_*"]\nfuture = ["05_*"]\n', encoding="utf-8")
    canon_dir = root / "01_Canon"
    product_dir = root / "02_Product"
    future_dir = root / "05_Future"
    canon_dir.mkdir()
    product_dir.mkdir()
    future_dir.mkdir()
    product_dir.joinpath("AGENTS.md").write_text(
        "---\ndescription: Product route\ndepends-on: []\nzone: product\n---\n\n"
        "# Product\n\nСтудия должна платить только после события Принять.\n",
        encoding="utf-8",
    )
    future_dir.joinpath("AGENTS.md").write_text(
        "---\ndescription: Future route\ndepends-on: []\nzone: future\n---\n\n# Future\n",
        encoding="utf-8",
    )
    canon_dir.joinpath("criteria.md").write_text(
        "# Criteria\n\n## Rule\n\nСтудия должна платить только после события Принять.\n",
        encoding="utf-8",
    )
    product_dir.joinpath("screen.md").write_text(
        "# Screen\n\n## Copy\n\nСтудия должна платить только после события Принять.\n",
        encoding="utf-8",
    )
    future_dir.joinpath("idea.md").write_text(
        "# Future\n\n## Later\n\nСтудия должна платить только после события Принять.\n",
        encoding="utf-8",
    )
    source = root / "source.md"
    source.write_text("# Source\n\n## Правило\n\nСтудия должна платить только после события Принять.\n", encoding="utf-8")
    index(str(root), confirm=True)

    payload = canon_check(str(source), str(root), mode="single", limit=5)

    pair = payload["pairs"][0]
    assert pair["authority_quotes"]
    assert pair["authority_quotes"][0]["evidence_role"] == "authority"
    assert pair["parking_quotes"]
    assert pair["parking_quotes"][0]["evidence_role"] == "parking"
    assert "future_only" in pair["parking_quotes"][0]["flags"]
    assert pair["dependent_quotes"]
    assert pair["dependent_quotes"][0]["evidence_role"] == "dependent_context"
    assert pair["dependent_quotes"][0]["badge"] == "ПРОДУКТ"
    all_paths = {
        quote["relative_path"]
        for quote in [*pair["authority_quotes"], *pair["dependent_quotes"], *pair["parking_quotes"]]
    }
    assert "02_Product/AGENTS.md" not in all_paths


def test_canon_check_cold_index_returns_warmup(tmp_path: Path) -> None:
    source, _criteria = _write_corpus(tmp_path / "corpus")

    payload = canon_check(str(source), str(source.parent), mode="single")

    assert payload["error"] == "index_warmup_required"
    assert payload["_exit_code"] == 4


def test_canon_check_rejects_file_outside_corpus(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n\nСтудия должна платить.\n", encoding="utf-8")

    payload = canon_check(str(outside), str(corpus))

    assert payload["error"] == "file_outside_corpus"
    assert payload["_exit_code"] == 2


def test_canon_check_no_claims_exits_zero(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    source = corpus / "source.md"
    source.write_text("# Source\n\nNeutral descriptive note.\n", encoding="utf-8")

    payload = canon_check(str(source), str(corpus))

    assert payload["pairs"] == []
    assert "no_normative_claims" in payload["quality_flags"]
