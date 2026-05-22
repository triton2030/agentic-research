from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_handlers_do_not_own_json_or_envelope() -> None:
    handlers = ROOT / "src" / "md_cli" / "handlers"
    for path in handlers.glob("*.py"):
        if path.name == "__init__.py":
            continue
        text = path.read_text(encoding="utf-8")
        assert "print(json" not in text
        assert "md_cli.envelope" not in text


def test_workflows_do_not_import_md_cli() -> None:
    workflows = ROOT / "src" / "navigator" / "workflows"
    for path in workflows.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "from md_cli" not in text
        assert "import md_cli" not in text

