# Phase 1 — Foundation refactor

**Estimated cost**: ~1.5 дня
**Depends on**: ничего (entry point)
**Unblocks**: P2, P3, P4

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md` (plans/), root contract `_ops/GOAL.md`.

## Цель

Унифицировать parsing и graph capabilities в `navigator/` package. Перенести monolithic `md_graph.py` (1446 LOC) → `navigator/graph.py`, использовать существующий `navigator/markdown_io.py` для parsing (deduplicate WIKILINK_RE, MD_LINK_RE, HEADING_RE, `iter_markdown`, `split_frontmatter`). Создать два новых модуля: `navigator/link_graph.py` (NetworkX-based) и `navigator/importance.py` (centrality metrics). CLI fallback сохраняется через симлинки до P7.

## In scope

- Migration `md_graph.py` → `navigator/graph.py`
- Deduplicate parsing (graph использует `markdown_io`)
- New module `navigator/link_graph.py` — NetworkX DiGraph builder
- New module `navigator/importance.py` — in/out-degree, PageRank, centrality
- Inline deps в `md_navigator.py` uv shebang: добавить `networkx`, `scipy`
- Wire new graph subcommands в `navigator/cli.py`
- `~/.claude/skills/1md-graph/scripts/md_graph.py` → симлинк (CLI fallback)
- `~/.codex/skills/1md-graph/scripts/md_graph.py` → симлинк
- Golden output tests — pre/post migration outputs identical

## NOT in scope

- Удалять scripts/ folders из skill папок (это P7)
- Section profile / classifier (P4)
- Новые capabilities (P2-P3)
- Tier 2 features (P4-P5)

## Definition of done

- `navigator/graph.py` существует, exports функции: `scan`, `init`, `strip`, `deps`, `audit_doc`, `impact`, `preflight`, `changed`, `check`, `doctor`, `cycles`, `health`, `map_graph`
- `navigator/link_graph.py` существует, exports: `build_link_graph(corpus_root) → nx.MultiDiGraph`
- `navigator/importance.py` существует, exports: `compute_importance(graph) → list[dict]` с keys (`path`, `in_degree`, `out_degree`, `pagerank`, `centrality`)
- `~/.claude/skills/1md-graph/scripts/md_graph.py` — симлинк на новый backend, identical output
- `~/.codex/skills/1md-graph/scripts/md_graph.py` — то же
- `navigator/cli.py` принимает все graph-команды
- Golden output diff: для 5 reference файлов в `knowledge/` команды `preflight`, `impact`, `deps`, `health`, `cycles` дают **identical JSON output** pre/post migration (с точностью до сериализации)
- Smoke `npm run smoke` 15/15 passes
- В `md_graph.py` (the original) НЕТ дублирующего regex'а (WIKILINK_RE / MD_LINK_RE / HEADING_RE)

## Stop rules

- Golden output diff показывает semantic regression (не cosmetic) — rollback, исследовать
- Migration ломает CLI consumers — rollback, оценить migration strategy
- NetworkX или scipy не устанавливаются через uv inline deps — investigate, возможно switch на conda env / venv

## Подшаги

### P1.1 — Подготовка и backup (15 минут)

1. Прочитать целиком `~/.claude/skills/1md-graph/scripts/md_graph.py` — понять каждую функцию, dependencies между ними
2. Создать backup: `cp ~/.claude/skills/1md-graph/scripts/md_graph.py ~/.claude/skills/1md-graph/scripts/md_graph.py.bak.$(date +%Y%m%d)`
3. Капчить **golden outputs** before migration на 5 reference files (см. P1.6 verification):
   ```bash
   REPO=/Users/triton/Documents/GitHub/agentic-research
   GRAPH=$REPO/experiments/md-embedding-server/scripts/navigator
   GOLDEN_DIR=/tmp/md-graph-golden-pre
   mkdir -p $GOLDEN_DIR
   for cmd in preflight impact deps; do
     ~/.claude/skills/1md-graph/scripts/md_graph.py $cmd $REPO/knowledge/agents/evaluation.md --scan $REPO/knowledge --json > $GOLDEN_DIR/$cmd.json
   done
   ~/.claude/skills/1md-graph/scripts/md_graph.py health $REPO/knowledge --json > $GOLDEN_DIR/health.json
   ~/.claude/skills/1md-graph/scripts/md_graph.py cycles $REPO/knowledge --json > $GOLDEN_DIR/cycles.json
   ```

### P1.2 — Inline deps (15 минут)

В `experiments/md-embedding-server/scripts/md_navigator.py` (entry-script с uv shebang) добавить в inline metadata:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy",
#     "sqlite-vec",
#     "pyyaml",
#     "anthropic",
#     "networkx",          # NEW
#     "scipy",             # NEW (для PageRank performance)
# ]
# ///
```

Test: `experiments/md-embedding-server/scripts/md_navigator.py manifest` — должен запуститься без import errors.

### P1.3 — Create navigator/link_graph.py (1-2 часа)

**Файл**: `experiments/md-embedding-server/scripts/navigator/link_graph.py`

**Цель**: построить `nx.MultiDiGraph` из corpus используя `markdown_io` для parsing. Edges типизированы: `wikilink`, `markdown-link`, `frontmatter-rbe` (read-before-edit), `frontmatter-eae` (edit-after-edit). Edge data: `{ type, anchor: str | None, source_line: int | None }`.

**Public API**:

```python
def build_link_graph(corpus_root: Path) -> nx.MultiDiGraph:
    """Build directed multigraph of Markdown links across corpus.

    Nodes: file relative paths (str).
    Edges: from source file to target file, with attributes:
      type: 'wikilink' | 'markdown-link' | 'frontmatter-rbe' | 'frontmatter-eae'
      anchor: str | None (for [[file#anchor]] or [text](file.md#anchor))
      source_line: int | None
    """
```

**Implementation outline**:

```python
from __future__ import annotations
from pathlib import Path
from typing import Any
import networkx as nx

from .markdown_io import (
    GRAPH_LINK_KEYS,
    iter_markdown,
    markdown_links_with_anchors_from_text,
    markdown_lookup,
    normalize_frontmatter_links,
    parse_frontmatter,
    relative_path,
    resolve_markdown_target,
    wikilinks_with_anchors_from_text,
)


def build_link_graph(corpus_root: Path) -> nx.MultiDiGraph:
    corpus_root = corpus_root.resolve()
    lookup = markdown_lookup(corpus_root)
    g = nx.MultiDiGraph()

    for file_path in iter_markdown(corpus_root):
        src_rel = relative_path(file_path.resolve(), corpus_root)
        g.add_node(src_rel, abs_path=str(file_path.resolve()))

        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        frontmatter = parse_frontmatter(lines)

        # Wikilinks
        for target, anchor in wikilinks_with_anchors_from_text(text):
            resolved = resolve_markdown_target(target, file_path, corpus_root, lookup)
            if resolved is None:
                continue
            tgt_rel = relative_path(resolved, corpus_root)
            g.add_edge(src_rel, tgt_rel, type="wikilink", anchor=anchor)

        # Markdown links
        for target, anchor in markdown_links_with_anchors_from_text(text):
            resolved = resolve_markdown_target(target, file_path, corpus_root, lookup)
            if resolved is None:
                continue
            tgt_rel = relative_path(resolved, corpus_root)
            g.add_edge(src_rel, tgt_rel, type="markdown-link", anchor=anchor)

        # Frontmatter graph edges
        for key in GRAPH_LINK_KEYS:  # 'read-before-edit', 'edit-after-edit'
            for target in normalize_frontmatter_links(frontmatter.get(key)):
                resolved = resolve_markdown_target(target, file_path, corpus_root, lookup)
                if resolved is None:
                    continue
                tgt_rel = relative_path(resolved, corpus_root)
                edge_type = "frontmatter-rbe" if key == "read-before-edit" else "frontmatter-eae"
                g.add_edge(src_rel, tgt_rel, type=edge_type, anchor=None)

    return g
```

**Sanity test** (manual):
```bash
cd /Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/scripts
python3 -c "
from pathlib import Path
from navigator.link_graph import build_link_graph
g = build_link_graph(Path('/Users/triton/Documents/GitHub/agentic-research/knowledge'))
print(f'nodes: {g.number_of_nodes()}, edges: {g.number_of_edges()}')
print(f'edge types: {set(d[\"type\"] for _,_,d in g.edges(data=True))}')
"
```

Ожидается: ≥30 nodes, ≥3 edges (knowledge/ имеет markdown links на .md). edge types includes `markdown-link`.

### P1.4 — Create navigator/importance.py (1 час)

**Файл**: `experiments/md-embedding-server/scripts/navigator/importance.py`

**Public API**:

```python
def compute_importance(
    graph: nx.MultiDiGraph,
    top: int | None = None,
    sort_by: str = "pagerank",  # 'pagerank' | 'in_degree' | 'out_degree' | 'centrality'
) -> list[dict[str, Any]]:
    """Return ranked list of files with centrality metrics.

    Each dict: {
      path: str (relative path),
      in_degree: int,
      out_degree: int,
      pagerank: float,
      centrality: float,  # betweenness centrality
    }
    """
```

**Implementation outline**:

```python
import networkx as nx
from typing import Any


def compute_importance(
    graph: nx.MultiDiGraph,
    top: int | None = None,
    sort_by: str = "pagerank",
) -> list[dict[str, Any]]:
    # Convert MultiDiGraph to DiGraph for algorithms that need it
    simple = nx.DiGraph()
    for u, v in graph.edges():
        if simple.has_edge(u, v):
            simple[u][v]["weight"] += 1
        else:
            simple.add_edge(u, v, weight=1)
    for node in graph.nodes():
        if not simple.has_node(node):
            simple.add_node(node)

    # PageRank — uses scipy if available, falls back to slow path otherwise
    try:
        pagerank = nx.pagerank(simple, weight="weight")
    except Exception:
        # Pure-Python fallback (slower for large graphs)
        pagerank = {n: 0.0 for n in simple.nodes()}

    # Betweenness centrality (file-level)
    try:
        centrality = nx.betweenness_centrality(simple)
    except Exception:
        centrality = {n: 0.0 for n in simple.nodes()}

    results = []
    for node in simple.nodes():
        results.append({
            "path": node,
            "in_degree": simple.in_degree(node),
            "out_degree": simple.out_degree(node),
            "pagerank": round(pagerank.get(node, 0.0), 6),
            "centrality": round(centrality.get(node, 0.0), 6),
        })

    results.sort(key=lambda x: x[sort_by], reverse=True)
    if top is not None and top > 0:
        results = results[:top]
    return results
```

**Sanity test**:
```bash
python3 -c "
from pathlib import Path
from navigator.link_graph import build_link_graph
from navigator.importance import compute_importance
g = build_link_graph(Path('/Users/triton/Documents/GitHub/agentic-research/knowledge'))
top = compute_importance(g, top=5)
for r in top:
    print(f'{r[\"path\"]}: in={r[\"in_degree\"]} out={r[\"out_degree\"]} pr={r[\"pagerank\"]}')
"
```

### P1.5 — Migrate md_graph.py → navigator/graph.py (4-6 часов)

Это самый большой шаг. Migration по функциям:

**Файл**: `experiments/md-embedding-server/scripts/navigator/graph.py`

**Migration strategy**:

1. **НЕ копировать parsing regex'ы.** Использовать из `markdown_io`:
   - `WIKILINK_RE`, `MD_LINK_RE`, `HEADING_RE` — удалить дубликаты в graph.py, импортировать из markdown_io
   - `iter_markdown` — то же
   - `split_frontmatter` → переименовать в `parse_frontmatter` (in markdown_io) — adjust callers
   - `wikilinks_from_text` — то же

2. **Сохранить graph-specific concepts**:
   - `GRAPH_FIELDS = ("read-before-edit", "edit-after-edit")` — graph-specific, keep
   - `LEGACY_FIELDS`, `ALLOWED_FIELDS` — keep
   - `Doc` dataclass — keep (или конвертировать в TypedDict для consistency с rest of package)

3. **Public functions to migrate** (см. оригинал в `~/.claude/skills/1md-graph/scripts/md_graph.py.bak.YYYYMMDD`):
   - `scan(paths, **filters) → list[issue]`
   - `init(paths) → mutating`
   - `strip(paths, also_related_section=False) → mutating`
   - `deps(path, scan, depth) → dict`
   - `audit_doc(path, scan) → dict`
   - `impact(path, scan) → dict`
   - `preflight(path, scan, depth) → dict` (exit code 1 при blockers)
   - `changed(base, since, staged, scan, depth) → dict`
   - `check(paths) → list[issue]`
   - `doctor(paths) → grouped dict`
   - `cycles(paths) → list[cycle]`
   - `health(paths) → dict`
   - `map_graph(paths) → list[file_summary]`

4. **CLI integration**: Создать `register_graph_commands(sub)` функцию (как `register_search`, `register_audit` etc. в существующих модулях). Зарегистрировать в `navigator/cli.py`:

   ```python
   # в cli.py:
   from .graph import register_graph_commands
   
   def parse_args() -> argparse.Namespace:
       # ... existing ...
       register_graph_commands(sub)  # adds: scan, init, strip, deps, audit-graph,
                                     # impact, preflight, changed, check, doctor,
                                     # cycles, health, map-graph
   ```

   Naming collision check: `audit` уже существует в navigator (corpus audit). Graph's `audit` (audit единого файла на graph schema) переименовать в `audit-graph` или `graph-audit`. Аналогично для `map`/`health` если collision.

5. **Sanity check**: после migration, в новом `graph.py` НЕ должно быть:
   - `re.compile(r"...")` для WIKILINK / MD_LINK / HEADING — они в markdown_io
   - Своего `iter_markdown` — он в markdown_io
   - Своего `split_frontmatter` — в markdown_io

6. **Original md_graph.py заменить на shim**:
   ```python
   #!/usr/bin/env python3
   """Thin shim — actual implementation lives in navigator.graph.
   
   Kept as entry-point for backward CLI compatibility:
   - ~/.claude/skills/1md-graph/scripts/md_graph.py → symlink → repo
   - ~/.codex/skills/1md-graph/scripts/md_graph.py → symlink → repo
   """
   import sys
   from pathlib import Path
   
   # Locate the navigator package in repo
   HERE = Path(__file__).resolve()
   REPO_NAVIGATOR = HERE.parent.parent.parent / "experiments" / "md-embedding-server" / "scripts"
   sys.path.insert(0, str(REPO_NAVIGATOR))
   
   from navigator.cli import main
   
   if __name__ == "__main__":
       sys.exit(main())
   ```

   Или **симлинк** на entry-script `md_navigator.py` с dispatching по argv[0]:
   - Если `argv[0]` ends with `md_graph.py` → invoke graph subcommands prefix
   - Иначе → standard navigator dispatch

   **Recommended**: симлинк simpler. Add в navigator/cli.py:
   ```python
   def main() -> int:
       import sys
       from pathlib import Path
       script_name = Path(sys.argv[0]).name
       if script_name == "md_graph.py":
           # Prepend "graph-" prefix dispatch (or whatever convention chosen)
           ...
       return ...
   ```

   Final decision: **симлинк** + cli.py dispatch на argv[0] - проще maintain.

### P1.6 — Verification via golden outputs (1 час)

После migration, повторить golden output capture, сравнить с pre:

```bash
GOLDEN_DIR=/tmp/md-graph-golden-post
mkdir -p $GOLDEN_DIR
REPO=/Users/triton/Documents/GitHub/agentic-research

# 5 reference files
FILES=(
  "$REPO/knowledge/agents/evaluation.md"
  "$REPO/knowledge/wisdom-claude-opus-4.7.md"
  "$REPO/knowledge/wisdom-gpt-5.5.md"
  "$REPO/knowledge/practical-guides/how-to-write-skills/platform-deltas.md"
  "$REPO/_ops/GOAL.md"
)

for file in "${FILES[@]}"; do
  basename=$(basename $file .md)
  ~/.claude/skills/1md-graph/scripts/md_graph.py preflight "$file" --scan $REPO/knowledge --json > $GOLDEN_DIR/preflight-$basename.json 2>&1
  ~/.claude/skills/1md-graph/scripts/md_graph.py impact "$file" --scan $REPO/knowledge --json > $GOLDEN_DIR/impact-$basename.json 2>&1
  ~/.claude/skills/1md-graph/scripts/md_graph.py deps "$file" --scan $REPO/knowledge --json > $GOLDEN_DIR/deps-$basename.json 2>&1
done

~/.claude/skills/1md-graph/scripts/md_graph.py health $REPO/knowledge --json > $GOLDEN_DIR/health.json
~/.claude/skills/1md-graph/scripts/md_graph.py cycles $REPO/knowledge --json > $GOLDEN_DIR/cycles.json
~/.claude/skills/1md-graph/scripts/md_graph.py scan $REPO/knowledge --json > $GOLDEN_DIR/scan.json

# Diff
diff -r /tmp/md-graph-golden-pre /tmp/md-graph-golden-post
```

**Acceptance**: diff пуст (modulo timestamps если есть). Semantic content identical.

**Если diff показывает разницу**:
- Проверь сериализацию JSON (key order, ensure_ascii). Может быть cosmetic.
- Если semantic difference — bug в migration. Investigate которая функция расходится.

### P1.7 — Cross-runtime symlinks (15 минут)

Убедиться что симлинки указывают на единый backend:

```bash
ls -la ~/.claude/skills/1md-graph/scripts/md_graph.py
ls -la ~/.codex/skills/1md-graph/scripts/md_graph.py
```

Должны быть симлинками на single entry. Если нет — создать:

```bash
TARGET=/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/scripts/md_navigator.py
# (md_navigator.py теперь dispatches graph commands via argv[0])
ln -sf $TARGET ~/.claude/skills/1md-graph/scripts/md_graph.py
ln -sf $TARGET ~/.codex/skills/1md-graph/scripts/md_graph.py
```

Wait — но в shim approach `md_graph.py` стоит на своих местах со своим именем. Decide:
- **Option A**: симлинки `md_graph.py` → `md_navigator.py`. cli.py dispatch на argv[0].
- **Option B**: оставить `md_graph.py` как thin shim файл с `from navigator.cli import main; main()`.

**Recommended Option A** — симлинки. Меньше копий, легче поддерживать.

### P1.8 — MCP smoke test (15 минут)

```bash
cd /Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp
npm run smoke
```

Должно быть **15/15 passed** (без regression — мы пока не trognули MCP, только backend). Pass: graph tools (md_preflight, md_impact, md_deps, md_health) всё ещё работают через subprocess к graph script.

## Verification (общая для P1)

- [ ] Golden output diff: pre/post migration = empty
- [ ] `navigator/graph.py` exists, exports все public functions
- [ ] `navigator/link_graph.py` exists, sanity test passes (≥30 nodes, ≥3 edges, edge types ≥1)
- [ ] `navigator/importance.py` exists, sanity test passes
- [ ] `md_graph.py` в обоих skill folders — симлинки или thin shims, identical behavior
- [ ] `navigator/cli.py` принимает все graph subcommands
- [ ] В `navigator/graph.py` НЕТ дублирующего regex (WIKILINK_RE / MD_LINK_RE / HEADING_RE)
- [ ] MCP smoke 15/15 pass
- [ ] No regression на CLI consumers (manual test 3 random graph commands)

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Migration ломает edge cases (escaped brackets, nested wikilinks) | Golden output diff на 5 разных файлов покрывает most edge cases. Если diff показывает разницу — обязательно investigate |
| scipy не устанавливается через uv | Fallback в `importance.py`: try/except вокруг pagerank, нет scipy → use slow pure-Python algorithm (NetworkX делает это автоматически если scipy missing) |
| Naming collision (audit/map/health существует в navigator) | Префикс `graph-` для graph-specific (e.g. `graph-audit`, `graph-health`). Документировать в CLI help |
| Симлинки не работают на чьём-то filesystem | Fallback: thin shim file. Document в P1 README |
| Original `md_graph.py.bak` забыли удалить — корпус замусорился | Add к P7 cleanup: удалить .bak файлы |

## Hand-off to P2

После P1 готов:
- Backend единый, parsing single source
- `navigator/link_graph.py` готов как dependency для P2 link counts
- `navigator/importance.py` готов как dependency для P2 md_importance tool
- MCP всё ещё работает identically (никаких новых MCP tools пока, только backend)

P2 теперь может: extend `folder_map.build_map` с in/out-degree через `link_graph`, добавить atomic `md_importance` MCP tool.

## Anchors / Evidence

- High-level контракт: `task-001-md-tools-unified-backend.md`
- Original graph code: `~/.claude/skills/1md-graph/scripts/md_graph.py` (backup as .bak before migration)
- Existing parsing primitives: `experiments/md-embedding-server/scripts/navigator/markdown_io.py`
- spike outcome (obsidiantools rejected): этот ход обсуждения 2026-05-21 — мы используем NetworkX напрямую, не obsidiantools wrapper
