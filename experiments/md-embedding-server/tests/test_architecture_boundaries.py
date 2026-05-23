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


def test_envelope_delegates_next_step_policy() -> None:
    envelope_text = (SRC / "md_cli" / "envelope.py").read_text(encoding="utf-8")
    next_steps_text = (SRC / "md_cli" / "next_steps.py").read_text(encoding="utf-8")

    assert "from .next_steps import LARGE_REPLY_BYTES, derive_next_step" in envelope_text
    assert "def derive_next_step" not in envelope_text
    assert "def _narrow_for_large_reply" not in envelope_text
    assert "index_warmup_required" not in envelope_text
    assert "confirm_required" not in envelope_text
    assert "transaction_not_found" not in envelope_text

    assert "def derive_next_step" in next_steps_text
    assert "def _narrow_for_large_reply" in next_steps_text
    assert "from .envelope" not in next_steps_text
    assert "import md_cli.envelope" not in next_steps_text


def test_navigator_library_does_not_import_md_cli() -> None:
    for path in _py_files(SRC / "navigator"):
        text = path.read_text(encoding="utf-8")
        assert "from md_cli" not in text
        assert "import md_cli" not in text


def test_legacy_status_adapter_does_not_export_core_internals() -> None:
    text = (SRC / "navigator" / "index_status.py").read_text(encoding="utf-8")
    assert "from .status_core import _" not in text
    tree = ast.parse(text)
    exported: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            continue
        if isinstance(node.value, ast.List):
            exported = [
                item.value
                for item in node.value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            ]
    assert exported
    assert all(not name.startswith("_") for name in exported)
