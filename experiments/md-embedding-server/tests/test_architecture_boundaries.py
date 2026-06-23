from __future__ import annotations

import ast
import importlib
from pathlib import Path

from md_cli.catalog import TOOLS


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


def test_every_catalog_tool_is_dispatchable() -> None:
    # Each tool resolves through exactly one of two dispatch paths: a bespoke
    # handler_module that imports and exposes run(), or generic dispatch
    # (handler_module is None) routed through handlers._generic.run_tool.
    from md_cli.handlers import _generic

    assert callable(_generic.run_tool)
    for tool in TOOLS:
        if tool.handler_module is None:
            # Generic path: the runner resolves the tool by id from the catalog.
            from md_cli.catalog import get_tool

            assert get_tool(tool.tool_id) is tool
        else:
            module = importlib.import_module(tool.handler_module)
            assert callable(getattr(module, "run", None)), tool.handler_module


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


def test_public_api_stays_thin_facade() -> None:
    text = (SRC / "navigator" / "api.py").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 300
    assert "importlib.import_module" not in text
    assert "from .graph_core" not in text
    assert "from .graph_reports" not in text
    assert "query_by_type" not in text
    assert "refactor_candidates" not in text


def test_source_files_stay_under_1000_lines() -> None:
    oversized = [
        path.relative_to(SRC).as_posix()
        for path in _py_files(SRC)
        if len(path.read_text(encoding="utf-8").splitlines()) >= 1000
    ]
    assert oversized == []


def test_audit_cli_render_and_severity_are_split_from_detection_engine() -> None:
    audit_text = (SRC / "navigator" / "audit.py").read_text(encoding="utf-8")
    assert "def cmd_audit" not in audit_text
    assert "def render_audit" not in audit_text
    assert "def register_audit" not in audit_text
    assert (SRC / "navigator" / "audit_cli.py").exists()
    assert (SRC / "navigator" / "audit_render.py").exists()
    assert (SRC / "navigator" / "audit_severity.py").exists()


def test_index_context_is_named_boundary() -> None:
    text = (SRC / "navigator" / "api_index_context.py").read_text(encoding="utf-8")
    assert "@dataclass(frozen=True)" in text
    assert "class IndexContext" in text
    assert "tuple[Any, ...]" not in text


def test_graph_api_does_not_create_fake_module_namespace() -> None:
    text = (SRC / "navigator" / "api_graph.py").read_text(encoding="utf-8")
    assert "SimpleNamespace" not in text
    assert "_GRAPH" not in text


def test_graph_edges_reuses_markdown_io_link_parser() -> None:
    text = (SRC / "navigator" / "graph_edges.py").read_text(encoding="utf-8")
    assert "MD_LINK_RE" not in text
    assert "WIKILINK_RE" not in text
    assert "markdown_links_from_text" in text
    assert "wikilinks_with_anchors_from_text" in text
    assert "resolve_markdown_target" in text


def test_markdown_io_owns_section_reading_without_pick_import() -> None:
    markdown_text = (SRC / "navigator" / "markdown_io.py").read_text(encoding="utf-8")
    pick_text = (SRC / "navigator" / "pick.py").read_text(encoding="utf-8")

    assert "class MarkdownSection" in markdown_text
    assert "def extract_section_by_line" in markdown_text
    assert "def find_section_by_anchor" in markdown_text
    assert "from .pick" not in markdown_text
    assert "extract_section_by_line" in pick_text


def test_search_and_audit_api_delegate_to_domain_payloads() -> None:
    search_text = (SRC / "navigator" / "api_search.py").read_text(encoding="utf-8")
    assert "search_payload" in search_text
    for private_name in ("_search_bm25", "_search_dense", "_rrf_merge", "_hydrate_rows"):
        assert private_name not in search_text

    audit_text = (SRC / "navigator" / "api_audit.py").read_text(encoding="utf-8")
    assert "audit_payload" in audit_text
    assert "importlib.import_module" not in audit_text
    assert "audit_mod._check_" not in audit_text


def test_graph_mutators_use_rollback_write_plan() -> None:
    api_text = (SRC / "navigator" / "api_graph.py").read_text(encoding="utf-8")
    core_text = (SRC / "navigator" / "graph_core.py").read_text(encoding="utf-8")
    assert "_apply_graph_write_plan" not in api_text
    assert "DocWrite.from_frontmatter(doc, template, doc.body)" in api_text
    assert "write_doc_plan(plan)" in api_text
    assert "class DocWrite" in core_text
    assert "def write_doc_plan" in core_text
    assert "Iterable[DocWrite]" in core_text
    assert "tuple[Doc" not in core_text
    assert "tuple[Any" not in api_text
    assert "os.replace" in core_text


def test_read_related_reuses_link_graph_iterator() -> None:
    text = (SRC / "navigator" / "related.py").read_text(encoding="utf-8")
    link_graph_text = (SRC / "navigator" / "link_graph.py").read_text(encoding="utf-8")
    assert "iter_explicit_link_edges" in text
    assert "wikilinks_from_text" not in text
    assert "markdown_links_from_text" not in text
    assert "resolve_markdown_target" not in text
    assert "class ExplicitLinkEdge" in link_graph_text
    assert "Iterator[ExplicitLinkEdge]" in link_graph_text
    assert "Iterator[tuple" not in link_graph_text


def test_semantic_index_open_does_not_swallow_all_exceptions() -> None:
    text = (SRC / "navigator" / "index.py").read_text(encoding="utf-8")
    assert "except (FileNotFoundError, Exception)" not in text


def test_index_facade_has_no_runtime_semantic_helpers() -> None:
    text = (SRC / "navigator" / "index.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    function_names = {
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    }

    assert "find_semantic_neighbors" not in function_names
    assert "check_explicit_link_coherence" not in function_names
    assert "sqlite3" not in text


def test_related_and_index_context_import_focused_index_owners() -> None:
    related_text = (SRC / "navigator" / "related.py").read_text(encoding="utf-8")
    index_context_text = (SRC / "navigator" / "api_index_context.py").read_text(encoding="utf-8")

    assert "from .index import" not in related_text
    assert "from .index import" not in index_context_text
    assert "from .semantic_neighbors import _check_explicit_link_coherence" in related_text
    assert "from .status_core import find_corpus_root_for" in related_text
    assert "from .index_build import ensure_index" in index_context_text
    assert "from .index_meta import _index_dir_for_corpus" in index_context_text


def test_index_write_path_has_no_dead_dry_run_branch() -> None:
    tree = ast.parse((SRC / "navigator" / "index_build.py").read_text(encoding="utf-8"))
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    args = [arg.arg for arg in functions["_ensure_index_unlocked"].args.args]
    assert "dry_run" not in args


def test_index_lifecycle_uses_storage_owner_not_index_build() -> None:
    text = (SRC / "navigator" / "index_lifecycle.py").read_text(encoding="utf-8")
    assert "from .index_store import" in text
    assert "from .index_build import" not in text


def test_profile_backed_workflows_do_not_lazy_write_profiles() -> None:
    for name in ("query_by_type.py", "refactor_candidates.py"):
        text = (SRC / "navigator" / "workflows" / name).read_text(encoding="utf-8")
        assert "profile_unprofiled_sections" not in text
        assert "section_profile" not in text
        assert "refactor_proposals" not in text


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
