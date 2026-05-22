from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _py_files(path: Path) -> list[Path]:
    return sorted(p for p in path.rglob("*.py") if p.name != "__pycache__")


def test_handlers_boundary() -> None:
    for path in _py_files(SRC / "md_cli" / "handlers"):
        if path.name == "__init__.py" or path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8")
        assert "print(json" not in text
        assert "json.dumps" not in text
        assert "from md_cli.envelope" not in text
        assert "from md_cli import envelope" not in text
        assert "sys.exit" not in text
        tree = ast.parse(text)
        run_defs = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run"]
        assert len(run_defs) == 1


def test_workflows_boundary() -> None:
    for path in _py_files(SRC / "navigator" / "workflows"):
        text = path.read_text(encoding="utf-8")
        assert "from md_cli" not in text
        assert "import md_cli" not in text
        assert "subprocess" not in text
        assert "json.dumps" not in text


def test_runner_owns_envelope_and_json_printing() -> None:
    envelope_users = []
    json_printers = []
    for path in _py_files(SRC / "md_cli"):
        text = path.read_text(encoding="utf-8")
        if "envelope.wrap" in text:
            envelope_users.append(path.relative_to(ROOT).as_posix())
        if "print(json.dumps" in text:
            json_printers.append(path.relative_to(ROOT).as_posix())
    assert envelope_users == ["src/md_cli/runner.py"]
    assert json_printers == ["src/md_cli/runner.py"]


def test_navigator_library_does_not_import_md_cli() -> None:
    for path in _py_files(SRC / "navigator"):
        text = path.read_text(encoding="utf-8")
        assert "from md_cli" not in text
        assert "import md_cli" not in text
