# Doc Staleness Analysis: md-embedding-server Post-Refactor

## Context
A major refactor just deleted:
- `src/navigator/cli.py` (legacy argparse aggregation layer)
- `src/navigator/graph.py` (legacy argparse + cmd_* dispatchers for scripts/md_graph.py)
- `scripts/md_navigator.py` (legacy entry point)
- `scripts/md_graph.py` (legacy entry point) — currently deleted but not yet committed
- All cmd_* functions (19 legacy dispatchers in navigator/graph.py)
- Proxy magic in navigator/__init__.py (replaced with clean CallableModule pattern)

## Current Code State
- `api_graph.py` now uses `@dataclass GraphArgs` instead of `argparse.Namespace`
- `graph_core.py` raises domain `PathNotFound` exception instead of sys.exit
- Severity policy moved from `audit.py` to dedicated `audit_severity.py`
- `audit_cli.py` is now an intentional stub (only module docstring)
- Main dispatch in `main.py` falls back to generic `_generic.run_tool` when handler_module is None
- Navigator/__init__.py uses CallableModule class pattern (documented with docstring)
- Only remaining handler-side module is `md_extract.py`

## STALE PASSAGES FOUND

### AGENTS.md
**Line 23:** "Не редактируй legacy `src/navigator/cli.py` для установленной команды `md`..."
- **WHY STALE:** File `src/navigator/cli.py` is DELETED (staged in git status)
- **CURRENT REALITY:** Entry point is `md_cli.main:main` (in pyproject.toml); no cli.py exists
- **CORRECTION:** Delete entire sentence. Replace with: "Entry point for the `md` command is `md_cli.main:main` (src/md_cli/main.py). Library behavior lives in src/navigator/ and is wrapped by domain adapters in src/navigator/api_*.py."

**Line 34:** "...строят `argparse.Namespace` через shared helpers (`_graph_args`, `_graph_docs`, `_graph_scan_docs`) в `api_graph.py`..."
- **WHY STALE:** `GraphArgs` is now a dataclass, not `argparse.Namespace`
- **CURRENT REALITY:** `api_graph.py` lines 34-46 define `_graph_args()` which returns `GraphArgs(...)` (from graph_core.py lines 104-117, a @dataclass)
- **CORRECTION:** Replace `argparse.Namespace` with `GraphArgs` (a dataclass). Update to: "...строят `GraphArgs` (dataclass в `graph_core.py`) через shared helpers (`_graph_args`, `_graph_docs`, `_graph_scan_docs`) в `api_graph.py`..."

**Line 36:** "...и не импортируют legacy `navigator.graph`."
- **WHY STALE:** Misleading phrasing. `navigator.graph` is DELETED but the comment implies it still exists as legacy.
- **CURRENT REALITY:** `src/navigator/graph.py` is deleted. The module does not exist.
- **CORRECTION:** Change to: "...и не импортируют удалённый `navigator.graph` (legacy wrapper для scripts/md_graph.py)."

### README.md
**Line 45:** "Graph-facing wrappers build `argparse.Namespace` in `api_graph.py`..."
- **WHY STALE:** `GraphArgs` is the new type, not `argparse.Namespace`
- **CURRENT REALITY:** api_graph.py builds `GraphArgs(...)` dataclass instances
- **CORRECTION:** Replace with: "Graph-facing wrappers build `GraphArgs` (dataclass) in `api_graph.py`..."

**Lines 47-49:** "`src/navigator/graph.py` is legacy argparse compatibility for `scripts/md_graph.py`; the installed `md` command does not dispatch through its `cmd_*` functions."
- **WHY STALE:** BOTH `src/navigator/graph.py` and `scripts/md_graph.py` are DELETED
- **CURRENT REALITY:** No graph.py, no md_graph.py, no cmd_* functions anywhere in codebase
- **CORRECTION:** Delete these 3 lines entirely. The statement is no longer relevant. The info was accurate when those files were marked LEGACY FALLBACK in commit 921fe6b but now they're gone.

**Line 186:** "...touch legacy `navigator.graph` only for compatibility behavior"
- **WHY STALE:** `navigator.graph` is DELETED
- **CURRENT REALITY:** The module does not exist
- **CORRECTION:** Delete "touch legacy `navigator.graph` only for compatibility behavior". Replace entire cell with: "Graph contract, frontmatter, `read-before-edit`, `edit-after-edit`, rename/delete, or link-health logic | graph primitives in `src/navigator/graph_core.py` / `graph_reports.py` plus graph-facing adapters in `api_graph.py`"

## ACCURATE PASSAGES (Keep as-is)
- AGENTS.md line 29-31: "src/navigator/* не импортирует md_cli" ✓ Correct
- AGENTS.md line 30: "api.py — thin callable facade" ✓ Correct
- AGENTS.md line 32-38: Domain adapters pattern ✓ Correct (though Namespace → GraphArgs)
- AGENTS.md line 39-40: markdown_io.py sole parser ✓ Correct
- AGENTS.md line 42-45: audit.py split ✓ Correct
- AGENTS.md line 46-48: handlers stay thin ✓ Correct
- AGENTS.md line 48: runner owns envelope ✓ Correct
- README.md line 31-37: Unified backend architecture ✓ Correct
- README.md line 38-44: api.py and adapters (except Namespace → GraphArgs) ✓ Correct
- README.md line 50-52: link_graph.py ownership ✓ Correct
- README.md line 53-56: Tier 2 refactor signals ✓ Correct
- README.md line 57-62: md_cli/ ownership ✓ Correct
- README.md line 142-177: CLI subcommands listing ✓ Correct
- All embedding/index sections ✓ Correct (unaffected by refactor)
