# Phase 2 — Tier 1 atomic capabilities

**Estimated cost**: ~0.5 дня
**Depends on**: P1 (foundation refactor must be complete)
**Unblocks**: P3

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md`.

## Цель

Добавить **3 atomic capability** на foundation P1:

1. **Link counts** (`in_degree`, `out_degree`) в `md_ls` и `md_toc` outputs — through `link_graph` из P1
2. **`md_importance`** — новый atomic MCP tool, ranked файлы по centrality metrics
3. **Preview mode** в `md_read_related` — descriptions/titles only, no content body

Это **building blocks** для composite tools P3 (`md_orient` использует все три).

## In scope

- Extend `navigator/folder_map.py:build_map` с optional link counts
- Расширить CLI флаги для `map` / `headings` subcommands
- Создать новый CLI subcommand `importance`
- Расширить `navigator/related.py:collect_related_items` с `mode` parameter
- Update MCP wrapper: `md_ls`, `md_toc`, `md_read_related` принимают новые параметры; новый `md_importance` MCP tool
- Smoke test расширяется на новые capabilities

## NOT in scope

- Composite tools (`md_orient`, `md_edit_context`) — P3
- Section profile / classifier — P4
- Tier 2 capabilities — P5

## Definition of done

- `folder_map.build_map(path, max_heading_level, with_tokens, with_link_counts)` принимает `with_link_counts: bool`. Когда `True`, каждый file entry содержит `in_degree`, `out_degree`
- CLI: `md_navigator.py map <path> --with-link-counts` работает
- CLI: `md_navigator.py headings <path> --with-link-counts` работает
- CLI: `md_navigator.py importance <corpus> [--top N] [--sort-by pagerank|in_degree|out_degree|centrality]` работает
- CLI: `md_navigator.py read-related <path> --mode preview` работает, возвращает items без `content` field
- MCP `md_ls`/`md_toc` принимают `with_link_counts: boolean`
- MCP `md_read_related` принимает `mode: "preview" | "full"`, default `"full"`
- MCP `md_importance({ corpus, top?, sort_by? })` зарегистрирован, exposed в `listTools`
- Smoke test 15/15 → 17/17 (добавляется assertion для md_importance + md_ls с link counts)
- Manual sanity: `md_importance knowledge` returns top files match intuitive expectations (top hubs visible by name)

## Stop rules

- Link counts computation > 5s на корпусе ≤500 файлов — performance issue, investigate
- Smoke regression на existing tools — rollback, investigate

## Подшаги

### P2.1 — Extend folder_map.build_map (1 час)

**Файл**: `experiments/md-embedding-server/scripts/navigator/folder_map.py`

Добавить параметр `with_link_counts: bool = False`. Когда True:

```python
from .link_graph import build_link_graph

def build_map(
    path: Path,
    max_heading_level: int,
    with_tokens: bool = False,
    with_link_counts: bool = False,
) -> dict[str, Any]:
    root = path.resolve()
    files: list[dict[str, Any]] = []
    
    # If link counts requested, build graph once for the whole corpus
    link_graph = None
    if with_link_counts and root.is_dir():
        link_graph = build_link_graph(root)
    
    for file_index, file_path in enumerate(iter_markdown(path), start=1):
        # ... existing code ...
        file_entry = {
            # ... existing fields ...
        }
        if with_link_counts and link_graph is not None:
            rel = relative_path(file_path.resolve(), root)
            file_entry["in_degree"] = link_graph.in_degree(rel) if link_graph.has_node(rel) else 0
            file_entry["out_degree"] = link_graph.out_degree(rel) if link_graph.has_node(rel) else 0
        files.append(file_entry)
    
    # ... rest existing ...
```

**Test**:
```bash
md_navigator.py map /path/to/knowledge --with-link-counts --json | jq '.files[0]'
# Expected: includes "in_degree" and "out_degree" fields
```

### P2.2 — CLI flag --with-link-counts (15 минут)

**Файл**: `experiments/md-embedding-server/scripts/navigator/cli.py`

В существующем loop для `map` / `headings`:
```python
for name in ("map", "headings"):
    cmd = sub.add_parser(...)
    # ... existing flags ...
    cmd.add_argument(
        "--with-link-counts",
        action="store_true",
        help=(
            "Add in_degree and out_degree per file (file-level link counts "
            "from wikilinks, markdown-links, and frontmatter graph edges). "
            "Adds ~50-200ms for medium corpora."
        ),
    )
```

В `_dispatch_inline`:
```python
if args.command in {"map", "headings"}:
    data = build_map(
        Path(args.path),
        args.max_heading_level,
        with_tokens=args.with_tokens,
        with_link_counts=args.with_link_counts,  # NEW
    )
    # ... rest existing ...
```

### P2.3 — New CLI subcommand `importance` (30 минут)

**Файл**: `experiments/md-embedding-server/scripts/navigator/cli.py`

Добавить:
```python
imp = sub.add_parser(
    "importance",
    help="Rank files by graph centrality (in/out-degree, PageRank, centrality).",
)
imp.add_argument("path", help="Corpus root.")
imp.add_argument("--top", type=int, default=10, help="Show top N (default 10, 0 = all).")
imp.add_argument(
    "--sort-by",
    choices=["pagerank", "in_degree", "out_degree", "centrality"],
    default="pagerank",
    help="Sort key (default: pagerank).",
)
imp.add_argument("--json", action="store_true", help="Print JSON.")
```

В `_dispatch_inline`:
```python
if args.command == "importance":
    from .link_graph import build_link_graph
    from .importance import compute_importance
    graph = build_link_graph(Path(args.path))
    ranked = compute_importance(graph, top=args.top or None, sort_by=args.sort_by)
    if args.json:
        print(json.dumps({"corpus": str(Path(args.path).resolve()), "ranked": ranked}, ensure_ascii=False, indent=2))
    else:
        print(f"# importance: top {len(ranked)} by {args.sort_by}\n")
        for r in ranked:
            print(f"  {r['path']}: in={r['in_degree']:3d} out={r['out_degree']:3d} pr={r['pagerank']:.4f}")
    return 0
```

**Test**:
```bash
md_navigator.py importance /path/to/knowledge --top 5
# Expected: list of 5 files with metrics
```

### P2.4 — Preview mode в read-related (45 минут)

**Файл**: `experiments/md-embedding-server/scripts/navigator/related.py`

В `collect_related_items(args)`:

```python
def collect_related_items(args) -> dict[str, Any]:
    # ... existing setup ...
    mode = getattr(args, "mode", "full")  # NEW
    
    # ... existing collection logic ...
    
    # NEW: preview mode trim
    if mode == "preview":
        for item in kept:
            item.pop("content", None)
            # Keep: path, relative_path, description, title, reasons, tokens
            # Drop: content, anchor (if it was added), anchor_status (if was added)
            for key in ("anchor", "anchor_status"):
                item.pop(key, None)
    
    # ... rest existing ...
```

**Файл**: `experiments/md-embedding-server/scripts/navigator/cli.py`

```python
read_related = sub.add_parser(...)
# ... existing args ...
read_related.add_argument(
    "--mode",
    choices=["preview", "full"],
    default="full",
    help=(
        "preview: descriptions + titles + reasons only, no content body "
        "(cheap, for deciding whether to go deeper). "
        "full: include anchor-aware section content (default)."
    ),
)
```

**Test**:
```bash
md_navigator.py read-related path/to/file.md --mode preview --json | jq '.items[0]'
# Expected: no "content" field, only metadata
```

### P2.5 — MCP wrapper update (1 час)

**Файл**: `experiments/md-embedding-server/mcp/src/tools/navigator-tools.js`

#### md_ls extension

```js
registerTool(
  "md_ls",
  "Building block — folder listing for Markdown corpus: paths + frontmatter description + heading count. Optionally + in/out-degree (`with_link_counts`). No index, no HTTP, instant. Faster than `ls` + manual frontmatter read. Usually called via `md_orient` composite.",
  {
    path: z.string().min(1).describe("Folder or .md file path"),
    max_heading_level: z.number().int().min(1).max(6).optional(),
    match: z.string().optional(),
    with_tokens: z.boolean().optional(),
    with_link_counts: z.boolean().optional().describe("Add in_degree and out_degree per file. ~50-200ms for medium corpora."),
  },
  async ({ path, max_heading_level, match, with_tokens, with_link_counts }) => {
    const args = ["map", path, "--json"];
    pushFlag(args, "--max-heading-level", max_heading_level);
    pushFlag(args, "--match", match);
    if (with_tokens) args.push("--with-tokens");
    if (with_link_counts) args.push("--with-link-counts");
    return await runNavigator(args, { timeoutMs: 30_000 });
  }
);
```

То же для `md_toc` — добавить `with_link_counts` параметр.

#### md_read_related extension

```js
registerTool(
  "md_read_related",
  "Read anchor file and pull content from its linked neighborhood. Anchor-aware default: `[[file#Heading]]` pulls only that section. `mode: 'preview'` returns only descriptions+titles (cheap), `mode: 'full'` (default) includes content.",
  {
    paths: z.array(z.string().min(1)).min(1),
    scan: z.string().optional(),
    include: z.string().optional(),
    anchor_aware: z.boolean().optional(),
    mode: z.enum(["preview", "full"]).optional().describe("preview = descriptions only (cheap). full = with content (default)."),
    token_budget: z.number().int().nonnegative().optional(),
    semantic_radius: z.number().int().nonnegative().optional(),
    check_links: z.boolean().optional(),
    link_distance_threshold: z.number().positive().optional()
  },
  async ({ paths, scan, include, anchor_aware, mode, token_budget, semantic_radius, check_links, link_distance_threshold }) => {
    const args = ["read-related", ...paths];
    pushFlag(args, "--scan", scan);
    pushFlag(args, "--include", include);
    if (anchor_aware !== false) args.push("--anchor-aware");
    if (mode) args.push("--mode", mode);
    pushFlag(args, "--token-budget", token_budget);
    pushFlag(args, "--semantic-radius", semantic_radius);
    if (check_links) args.push("--check-links");
    pushFlag(args, "--link-distance-threshold", link_distance_threshold);
    args.push("--json");
    return await runNavigator(args, { timeoutMs: 60_000 });
  }
);
```

#### md_importance new tool

```js
registerTool(
  "md_importance",
  "Building block — rank Markdown files by graph centrality: in_degree, out_degree, PageRank, betweenness centrality. **Note: centrality ≠ semantic ownership.** High in_degree means many files reference this one (critical to edit carefully). High out_degree means this file references many (often 'operator' rather than 'owner'). Usually called via `md_orient` composite.",
  {
    corpus: z.string().min(1).describe("Corpus root path"),
    top: z.number().int().nonnegative().optional().describe("Show top N (default 10, 0 = all)"),
    sort_by: z.enum(["pagerank", "in_degree", "out_degree", "centrality"]).optional()
  },
  async ({ corpus, top, sort_by }) => {
    const args = ["importance", corpus, "--json"];
    if (top !== undefined) args.push("--top", String(top));
    if (sort_by) args.push("--sort-by", sort_by);
    return await runNavigator(args, { timeoutMs: 60_000 });
  }
);
```

### P2.6 — Smoke test extension (15 минут)

**Файл**: `experiments/md-embedding-server/mcp/test/smoke.js`

Добавить assertions:

```js
// md_ls with link counts
await expect("md_ls", { path: AGENTS, with_link_counts: true }, (p) =>
  Array.isArray(p.files) && p.files[0]?.in_degree !== undefined ? true : "missing in_degree"
);

// md_importance
await expect("md_importance", { corpus: KNOWLEDGE, top: 5 }, (p) =>
  Array.isArray(p.ranked) && p.ranked.length > 0 && p.ranked[0].pagerank !== undefined
    ? true : "no pagerank"
);

// md_read_related preview mode
await expect(
  "md_read_related",
  { paths: [FILE], scan: KNOWLEDGE, mode: "preview" },
  (p) => Array.isArray(p.items) && p.items[0]?.content === undefined
    ? true : "preview mode left content"
);
```

**Test**: `npm run smoke` → 17/17 passed (or 18/18 if added 3 separate test slots).

## Verification (общая для P2)

- [ ] `md_ls path/to/folder --with-link-counts --json` returns files with `in_degree` + `out_degree`
- [ ] `md_importance corpus --top 5` returns ranked list with all metrics
- [ ] `md_read_related path --mode preview` returns items without `content`
- [ ] MCP `md_ls`, `md_toc` принимают `with_link_counts`
- [ ] MCP `md_read_related` принимает `mode`
- [ ] MCP `md_importance` появляется в `listTools`
- [ ] Smoke 17/17 (или 18/18) passed
- [ ] Manual sanity: top file по pagerank в `knowledge/` — intuitively a hub (e.g. `wisdom-claude-opus-4.7.md` или подобный)

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| `build_link_graph` slow на больших корпусах | Cache в memory если same corpus invoked multiple times in one MCP session (warm cache stretch) |
| Top file по pagerank не соответствует intuition | Sanity check during development. Если расходится — investigate edge cases в parsing (e.g. external links не должны считаться) |
| `with_link_counts` adds significant latency to default md_ls usage | Default `with_link_counts=false`. User/composite explicit opt-in |
| Preview mode не убирает все content references | Code review on preview trim: проверить что anchor / anchor_status тоже не leaked |

## Hand-off to P3

После P2 готов:
- Atomic MCP tools для всех Tier 1 capabilities
- Composite P3 теперь может combine: `md_orient` = status + ls(with_link_counts) + importance; `md_edit_context` = preflight + read-related + search

## Anchors / Evidence

- High-level контракт: `task-001-md-tools-unified-backend.md`
- P1 deliverable: `navigator/link_graph.py` + `navigator/importance.py`
- MCP server: `experiments/md-embedding-server/mcp/`
- Smoke baseline: 15/15 (target after P2: 17/17 or 18/18)
