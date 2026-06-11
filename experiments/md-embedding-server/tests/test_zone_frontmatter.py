from __future__ import annotations

from pathlib import Path

from navigator.api import scan, strip
from navigator.canon.zones import build_zone_map, load_zone_config, resolve_zone


def test_zone_is_allowed_and_non_string_is_finding(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    good = tmp_path / "good.md"
    good.write_text("---\ndescription: Good\ndepends-on: []\nzone: canon\n---\n\n# Good\n", encoding="utf-8")
    bad = tmp_path / "bad.md"
    bad.write_text("---\ndescription: Bad\ndepends-on: []\nzone: [canon]\n---\n\n# Bad\n", encoding="utf-8")

    payload = scan(paths=[str(tmp_path)])

    issues = payload["issues"]
    assert not [item for item in issues if item["path"] == "good.md" and item["code"] == "UNKNOWN_FIELD"]
    assert [item for item in issues if item["path"] == "bad.md" and item["code"] == "ZONE_NOT_STRING"]


def test_strip_dry_run_keeps_zone(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("---\ndescription: Doc\ndepends-on: []\nzone: canon\nlegacy: x\n---\n\n# Doc\n", encoding="utf-8")

    payload = strip(paths=[str(path)], dry_run=True)

    removed = payload["changes"][0]["removed_fields"]
    assert "zone" not in removed
    assert "legacy" in removed


def test_resolve_zone_prefers_nearest_agents_then_glob(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    product = root / "02_Product"
    nested = product / "Nested"
    nested.mkdir(parents=True)
    (root / ".md-tools.toml").write_text('[canon]\nroot = ["01_*"]\nfuture = ["05_*"]\n', encoding="utf-8")
    (product / "AGENTS.md").write_text("---\ndescription: Product\ndepends-on: []\nzone: product\n---\n\n# Agents\n", encoding="utf-8")
    (nested / "doc.md").write_text("# Doc\n", encoding="utf-8")

    cfg = load_zone_config(root)
    zone_map = build_zone_map(root)

    assert resolve_zone("02_Product/Nested/doc.md", zone_map, cfg) == "product"
    assert resolve_zone("01_Canon/doc.md", zone_map, cfg) == "canon"
    assert resolve_zone("05_Future/doc.md", zone_map, cfg) == "future"
