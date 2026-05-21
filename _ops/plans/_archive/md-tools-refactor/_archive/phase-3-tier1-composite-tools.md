# Phase 3 — Tier 1 composite tools

**Estimated cost**: ~0.5 дня
**Depends on**: P2 (atomic capabilities)
**Unblocks**: Tier 1 ready

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md`.

## Цель

Создать **2 composite MCP tools** которые объединяют atomic tools в **workflow-specific packets**:

1. **`md_orient(corpus)`** — composite для W1 «попал в незнакомый корпус». Cheap, no HTTP, no semantic. Один call = status + folder listing с link counts + top importance.

2. **`md_edit_context(path, mode)`** — composite для W4 «я буду править file X». Modes:
   - `preview` — descriptions only (cheapest)
   - `full` (default) — preflight + anchor-aware related content + optional semantic search
   - `strict` — только blockers (anchor-drift, missing-target, broken-link, cycles)

Composite живут на **MCP уровне** (не backend) — orchestrate существующие atomic tools. Это позволяет хранить backend минимальным.

## In scope

- Создать `experiments/md-embedding-server/mcp/src/tools/composite-tools.js`
- Implement `md_orient` composite
- Implement `md_edit_context` composite с 3 modes
- Wire composite в `server.js`
- Update README с composite catalog
- Smoke test покрывает все composite + modes

## NOT in scope

- Tier 2 composite (`md_refactor_candidates`, `md_query_by_type`) — P5
- Backend changes (P3 чисто MCP layer)

## Definition of done

- `composite-tools.js` exists, exports `registerCompositeTools(registerTool)`
- `md_orient({ corpus, top? })` зарегистрирован, возвращает `{ status, files, important }`
- `md_edit_context({ path, mode, corpus?, query?, scan?, depth?, token_budget? })` зарегистрирован
- Mode `preview` возвращает: `{ preflight_summary: {must_read_count, must_update_count, blocker_count}, related_preview: [paths+descriptions] }` — no content bodies
- Mode `full` возвращает: `{ preflight, related_content (anchor-aware), semantic_search? }` — full content
- Mode `strict` возвращает: `{ blockers: [{ type, message, path? }], has_blockers: bool }` — только blockers
- Smoke test покрывает все 3 modes + md_orient
- `md_orient` latency на `knowledge/` (~37 files) < 2s (no HTTP calls)
- Tool descriptions явно: `md_orient`: «**Primary tool for W1 orient workflow**. Instant orientation. For deeper analysis → `md_audit`.»

## Stop rules

- `md_edit_context full` mode возвращает >50K tokens content по умолчанию — слишком жирно, добавить cap или сместить default budget
- Composite invocation crashes if any underlying atomic tool fails — wrap with try/catch, return partial result с warning

## Подшаги

### P3.1 — Создать composite-tools.js skeleton (15 минут)

**Файл**: `experiments/md-embedding-server/mcp/src/tools/composite-tools.js`

```js
import { z } from "zod";

import { runNavigator } from "./navigator-tools.js";
import { runGraph } from "./graph-tools.js";
import { build_link_graph_helper, compute_importance_helper } from "../helpers.js"; // optional если делаем direct calls

export function registerCompositeTools(registerTool) {
  // md_orient registered here
  // md_edit_context registered here
}
```

Зарегистрировать import в `src/server.js`:

```js
import { registerCompositeTools } from "./tools/composite-tools.js";
// ... existing imports

// ... existing register calls
registerCompositeTools(registerTool);
```

### P3.2 — Implement md_orient (1 час)

```js
registerTool(
  "md_orient",
  "**PRIMARY for W1 orient workflow.** Instant orientation in unfamiliar Markdown corpus: index freshness + folder listing (with link counts) + top important files. No HTTP, no semantic search, returns in <2s. For deeper analysis use `md_audit` (slow, embedding-based).",
  {
    corpus: z.string().min(1).describe("Corpus root path"),
    top: z.number().int().positive().max(50).optional().describe("Top N important files (default 10)"),
    max_heading_level: z.number().int().min(1).max(6).optional()
  },
  async ({ corpus, top, max_heading_level }) => {
    const top_n = top ?? 10;

    // Run in parallel — all independent calls
    const statusArgs = ["status", corpus];
    const lsArgs = ["map", corpus, "--with-link-counts", "--json"];
    if (max_heading_level) lsArgs.push("--max-heading-level", String(max_heading_level));
    const impArgs = ["importance", corpus, "--top", String(top_n), "--sort-by", "pagerank", "--json"];

    const [statusResult, lsResult, impResult] = await Promise.all([
      runNavigator(statusArgs, { parseJson: false, timeoutMs: 15_000 }),
      runNavigator(lsArgs, { timeoutMs: 30_000 }),
      runNavigator(impArgs, { timeoutMs: 30_000 })
    ]);

    return {
      corpus,
      status_summary: statusResult.text ?? statusResult,
      file_count: lsResult.file_count,
      description_gap_count: lsResult.description_gap_count,
      heading_count: lsResult.heading_count,
      files: lsResult.files,  // includes in_degree / out_degree
      important: impResult.ranked,
      hint: "Critical files (high in_degree) — edit carefully. High out_degree — usually 'operator' files. Centrality ≠ semantic ownership."
    };
  }
);
```

**Test**:
```bash
# After MCP server reload
node -e "
import('@modelcontextprotocol/sdk/client/index.js').then(async ({ Client }) => {
  const { StdioClientTransport } = await import('@modelcontextprotocol/sdk/client/stdio.js');
  const transport = new StdioClientTransport({ command: 'node', args: ['./src/server.js'] });
  const client = new Client({ name: 'test', version: '0.0.1' });
  await client.connect(transport);
  console.time('md_orient');
  const r = await client.callTool({ name: 'md_orient', arguments: { corpus: '/Users/triton/Documents/GitHub/agentic-research/knowledge', top: 5 } });
  console.timeEnd('md_orient');
  const data = JSON.parse(r.content[0].text);
  console.log('file_count:', data.file_count);
  console.log('important top 3:', data.important.slice(0,3).map(f => f.path));
  await client.close();
});
"
```

Expected: `md_orient` < 2000ms. Includes file_count, top important files.

### P3.3 — Implement md_edit_context (1.5 часа)

```js
registerTool(
  "md_edit_context",
  "**PRIMARY for W4 edit-safety workflow.** Inward context packet before editing a file. Modes: `preview` (descriptions only, cheap), `full` (default; preflight + anchor-aware linked content + optional search), `strict` (only blockers — anchor-drift, missing-target, broken-link, cycles).",
  {
    path: z.string().min(1).describe("File path to be edited"),
    mode: z.enum(["preview", "full", "strict"]).optional().describe("preview: metadata only. full: + content. strict: only blockers."),
    corpus: z.string().optional().describe("Corpus root for optional semantic search (only used in 'full' mode with query)"),
    query: z.string().optional().describe("Semantic query for additional context (only in 'full' mode)"),
    scan: z.string().optional().describe("Graph scan scope (default: repo root)"),
    depth: z.number().int().positive().max(5).optional().describe("Cascade depth (default 2)"),
    token_budget: z.number().int().nonnegative().optional()
  },
  async ({ path, mode = "full", corpus, query, scan, depth, token_budget }) => {
    // Common: graph preflight always run
    const preflightArgs = ["preflight", path, "--json"];
    if (scan) preflightArgs.push("--scan", scan);
    if (depth) preflightArgs.push("--depth", String(depth));
    const preflight = await runGraph(preflightArgs, { expectFindings: true, timeoutMs: 60_000 });

    // STRICT mode — return only blockers
    if (mode === "strict") {
      const blockers = [];
      // Extract from preflight: missing_target, broken_link, cycles, missing_frontmatter, anchor_drift
      // (exact fields depend on existing preflight output shape — adjust during impl)
      if (preflight.must_read?.some(r => r.status === "MISSING_TARGET")) {
        for (const r of preflight.must_read.filter(x => x.status === "MISSING_TARGET")) {
          blockers.push({ type: "missing_target", path: r.path, message: r.reason });
        }
      }
      if (preflight.cycles?.length) {
        for (const c of preflight.cycles) blockers.push({ type: "cycle", cycle: c });
      }
      if (preflight.anchor_drift_risk?.length) {
        // anchor-drift is signal, not blocker, but include in strict for completeness
        for (const a of preflight.anchor_drift_risk) blockers.push({ type: "anchor_drift_signal", anchor: a });
      }
      return { mode: "strict", path, blockers, has_blockers: preflight.has_blockers === true };
    }

    // PREVIEW mode — descriptions/titles only
    if (mode === "preview") {
      const relatedArgs = ["read-related", path, "--mode", "preview", "--json"];
      if (scan) relatedArgs.push("--scan", scan);
      const related = await runNavigator(relatedArgs, { timeoutMs: 30_000 });
      return {
        mode: "preview",
        path,
        preflight_summary: {
          has_blockers: preflight.has_blockers,
          must_read_count: (preflight.must_read || []).length,
          must_update_count: (preflight.must_update || []).length,
          cascade_depth: preflight.depth,
          anchor_drift_count: (preflight.anchor_drift_risk || []).length
        },
        related_preview: (related.items || []).map(i => ({
          path: i.relative_path,
          description: i.description,
          title: i.title,
          reasons: i.reasons
        }))
      };
    }

    // FULL mode (default) — preflight + related content + optional search
    const relatedArgs = ["read-related", path, "--anchor-aware", "--json"];
    if (scan) relatedArgs.push("--scan", scan);
    if (token_budget) relatedArgs.push("--token-budget", String(token_budget));

    const calls = [runNavigator(relatedArgs, { timeoutMs: 60_000 })];
    if (corpus && query) {
      const searchArgs = ["search", corpus, query, "--limit", "5", "--json"];
      calls.push(runNavigator(searchArgs, { timeoutMs: 60_000 }));
    } else {
      calls.push(Promise.resolve(null));
    }

    const [related, searchResult] = await Promise.all(calls);

    return {
      mode: "full",
      path,
      preflight,
      related,
      semantic_search: searchResult,
      hint: searchResult ? null : "For additional semantic context, pass `corpus` + `query` params"
    };
  }
);
```

### P3.4 — Smoke test extension (15 минут)

**Файл**: `experiments/md-embedding-server/mcp/test/smoke.js`

```js
// md_orient
await expect("md_orient", { corpus: KNOWLEDGE, top: 5 }, (p) =>
  p.file_count > 0 && Array.isArray(p.important) ? true : "missing orient fields"
);

// md_edit_context — preview
await expect("md_edit_context", { path: FILE, mode: "preview" }, (p) =>
  p.mode === "preview" && p.preflight_summary && Array.isArray(p.related_preview) ? true : "bad preview"
);

// md_edit_context — full
await expect("md_edit_context", { path: FILE, mode: "full" }, (p) =>
  p.mode === "full" && p.preflight && p.related ? true : "bad full"
);

// md_edit_context — strict
await expect("md_edit_context", { path: FILE, mode: "strict" }, (p) =>
  p.mode === "strict" && Array.isArray(p.blockers) ? true : "bad strict"
);
```

### P3.5 — Description discipline (15 минут)

Пройти по всем atomic tools в `navigator-tools.js` / `graph-tools.js` и **переписать descriptions** чтобы явно сказать «Building block — usually called via X composite»:

Examples:
- `md_search`: «Building block — semantic search across Markdown corpus. Used standalone for ad-hoc queries; composites like `md_orient` and `md_edit_context` use it internally.»
- `md_preflight`: «Building block — pre-edit graph safety report. Composed inside `md_edit_context`; use directly when you need just the graph slice without related content.»
- `md_impact`: «Building block — delete/rename blast radius. For section rename (not file) use `md_section_blast_radius` composite.»

`md_ls`, `md_toc`, `md_read_related`, `md_status`, `md_audit` — оставить как есть (они real primary для simpler use cases).

### P3.6 — Update mcp/README.md (15 минут)

Reorganize tools table: split в composite + atomic + internal sections.

```markdown
## Tool catalog

### Composite primary (use these first)

| Tool | Workflow | When to use |
|---|---|---|
| `md_orient` | W1 orient | Cold start in unfamiliar corpus |
| `md_edit_context` | W4 edit safety | Before editing a file |
| `md_section_blast_radius` | W5 rename safety | Renaming/rewriting a section |
| `md_audit` | W6 corpus health | Full corpus audit (slow) |

### Atomic public (building blocks)

| Tool | Note |
|---|---|
| `md_search` | Used standalone or via composites |
| `md_ls` | Folder listing + (optional) link counts |
| `md_toc` | Heading menu |
| `md_read_related` | Linked neighborhood, anchor-aware |
| `md_preflight` | Pre-edit graph report |
| ... | ... |

### Internal (not in listTools)

`md_pick`, `md_cat`, `md_deps` — used by composites internally.
```

## Verification (общая для P3)

- [ ] `composite-tools.js` exists
- [ ] `md_orient` зарегистрирован, smoke passes
- [ ] `md_edit_context` зарегистрирован, smoke passes для всех 3 modes
- [ ] `md_orient knowledge` < 2s (manual time check)
- [ ] `md_edit_context path mode=preview` < 1s, no content bodies
- [ ] `md_edit_context path mode=full` includes graph + anchor-aware related content
- [ ] `md_edit_context path mode=strict` returns only blockers
- [ ] Atomic tool descriptions updated с "Building block" framing
- [ ] mcp/README.md обновлён с composite vs atomic vs internal split
- [ ] Smoke 20/20 (or current+5 new) passed

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| md_edit_context full mode token bloat | token_budget cap (default 5000 для related content) |
| md_orient latency > 2s | Profile: identify bottleneck (likely importance computation). Consider caching link_graph |
| Preflight output shape changes after P1 migration | Test schema explicitly во время implementation. If shape changed — adjust strict mode parser |
| Composite tool failures partial | Wrap atomic calls с try/catch, return partial result с `errors[]` field |

## Hand-off to next phase

После P3 готов: **Tier 1 ready**. Все Tier 1 user-visible capabilities работают. Skill workflow recipes (P6) могут быть написаны и для Tier 1 уже работающего.

Next: P4 (section profile foundation для Tier 2) OR P6 (recipes для Tier 1) — выбор в зависимости от burn-in confidence.

## Anchors / Evidence

- High-level контракт: `task-001-md-tools-unified-backend.md`
- P2 deliverable: atomic tools with link counts, md_importance, preview mode
- Composite pattern reference: existing `md_section_blast_radius` в `hybrid-tools.js`
