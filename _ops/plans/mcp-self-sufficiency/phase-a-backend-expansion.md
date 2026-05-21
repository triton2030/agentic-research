# Phase A — Backend expansion + self-sufficient descriptions

**Owner**: 1 subagent (general-purpose), sequential work inside one window
**Parent plan**: [README](README.md)
**Blocks**: Phase B1-B4 (skills rewrite depends on new MCP tools being real)

## Цель

Расширить MCP surface с 19 до 27 public tools + переписать ВСЕ tool descriptions в self-sufficient формат. Backend в `experiments/md-embedding-server/mcp/` (Node + Python).

## Context — что уже есть

- Python backend: `experiments/md-embedding-server/scripts/navigator/` — ALL CLI commands работают (overlaps, cluster, repeated-concepts, scan, check, doctor, cycles, changed, index, init, strip, profile-sections и т.д.)
- Node MCP server: `experiments/md-embedding-server/mcp/src/server.js` + `src/tools/{navigator-tools.js, graph-tools.js, hybrid-tools.js, composite-tools.js}`
- Текущий surface: 19 tools, version 0.5.x
- Subprocess helper: `mcp/src/subprocess.js` (`runNavigator`, `runGraph` — already exist)
- Smoke: `mcp/test/smoke.js`

## Read FIRST

1. `experiments/md-embedding-server/mcp/README.md` — current state + "Excluded by design" section (what we're now reversing)
2. `experiments/md-embedding-server/mcp/src/server.js` — registration patterns
3. `experiments/md-embedding-server/mcp/src/tools/composite-tools.js` — example of composite tool wrappers
4. `experiments/md-embedding-server/mcp/src/tools/navigator-tools.js` — example of atomic tool wrappers
5. `experiments/md-embedding-server/mcp/src/subprocess.js` — `runNavigator(command, args, options)` and `runGraph(...)` helpers + exit-code semantics
6. `experiments/md-embedding-server/scripts/navigator/cli.py` — argparse surface for every command (subagent must check `--help` shape for new tools)
7. `/Users/triton/Documents/GitHub/agentic-research/_ops/plans/mcp-self-sufficiency/README.md` — full design rationale

## Work breakdown

### A.1 — Add 7 new read-only atomic tools

In `mcp/src/tools/navigator-tools.js` (or split between navigator-tools.js and graph-tools.js by ownership):

**Navigator-side (3 new tools)**:
1. `md_overlaps` — CLI subcommand `overlaps`. Required args: `corpus`. Optional: `threshold` (default 0.85), `top` (default 10), `include_same_file` (default false), `path_include`, `path_exclude`. Returns ranked pairs `{ section_a, section_b, cosine, path_a, path_b }`. Handles `index_warmup_required` (exit 4).
2. `md_repeated_concepts` — CLI subcommand `repeated-concepts`. Required: `corpus`. Optional: `threshold` (default 0.80), `top` (default 30), `path_include`, `path_exclude`. Returns concept-graph: medoid section, file breakdown, mean cohesion per connected component. Side-effect: writes `<corpus>/.md-navigator/repeated-concepts.md`. Handles warmup.
3. `md_extract` — **MERGE** of current `md_pick` + `md_cat` (which both wrap `pick --json` + `pick --extract`). Input: `map_data` (JSON map from md_search/md_ls/md_toc) + `ids` (heading or file ids) + `extract: bool` (default false). When extract=false → metadata; extract=true → extracted content.

**Graph-side (4 new tools)**:
4. `md_cycles` — CLI subcommand `cycles`. Optional: `paths`. Returns `edit-after-edit` cycles list. Non-zero exit when cycles exist.
5. `md_check` — CLI subcommand `check`. Optional: `paths`. Returns wikilink/anchor/markdown-link validation issues + related-docs section detection.
6. `md_scan` — CLI subcommand `scan`. Optional: `paths`. Returns frontmatter form issues (missing/legacy/unknown/malformed).
7. `md_changed` — CLI subcommand `changed` with `--base|--staged` options. Returns preflight on every .md file in git diff. Deleted files listed separately.

For each new tool:
- Add `registerTool` block in appropriate `src/tools/*.js`
- Zod input schema (typed, with describe() calls for self-sufficient hints)
- Use `runNavigator(...)` or `runGraph(...)` for invocation
- Handle exit codes per existing pattern in `subprocess.js`
- Result envelope: parsed JSON when CLI supports `--json`; else `{ text }`
- Timeout: 30s for cheap, 60-120s for graph/profile, 300s for audit-like

### A.2 — Add 4 mutating tools with guards

In `mcp/src/tools/navigator-tools.js` and `graph-tools.js`:

1. `md_index` (navigator) — CLI `index`. Cost-bearing (~$0.02 per ~1000 chunks).
2. `md_init` (graph) — CLI `init`. Destructive (modifies files).
3. `md_strip` (graph) — CLI `strip`. Destructive.
4. `md_profile_sections` (navigator) — CLI `profile-sections`. Cost-bearing.

**Guard pattern** for all 4:

```javascript
inputSchema: z.object({
  // required and optional args specific to tool
  confirm: z.boolean().optional().describe("Required true to actually run. Default false rejects with cost/destructive warning."),
  dry_run: z.boolean().optional().describe("If true, return estimated cost/scope without performing operation."),
}),
handler: async (args) => {
  if (args.dry_run) {
    // return estimated_cost_usd / estimated_chunks / files_to_modify / no actual operation
    return { dry_run: true, estimated_cost_usd: <number>, scope: <preview> };
  }
  if (!args.confirm) {
    return {
      error: "confirm_required",
      reason: "Cost-bearing operation" | "Destructive operation",
      hint: "Pass dry_run:true for estimate, then confirm:true to proceed",
    };
  }
  // proceed with runNavigator/runGraph
}
```

For `md_index` and `md_profile_sections`: dry_run estimates cost by counting chunks/sections × per-unit price (look up navigator code for actual logic).
For `md_init` and `md_strip`: dry_run lists files that would be modified.

### A.3 — Rewrite ALL 27 tool descriptions in self-sufficient format

For each of the 27 tools (6 composite + 17 atomic + 4 mutating), rewrite description following template:

```
md_<name>
---------
<one-line action description>.

WHEN: <trigger phrases / typical situations / which user question>
WHY OURS: <what we add vs Bash ls/grep/find>
INPUT: <main params and defaults — short, schema has details>
OUTPUT: <shape preview — key fields, when array vs object, size hint>
ALT: <when to prefer composite tool / another tool>
COST/RISK: <only for mutating: estimated cost / what changes on disk>
```

**Examples of self-sufficient descriptions** for guidance:

```
md_search:
"Find Markdown sections by natural-language query.

WHEN: 'where is X discussed', 'find sections about Y', any meaning question.
      Default tool for non-exact searches in any Markdown corpus.
WHY OURS: Semantic + BM25 hybrid via RRF. Returns ranked sections (not line
      matches like grep). Beats grep -r for paraphrased / multi-lingual /
      morphologically-varied queries.
INPUT: corpus (path), query (text), scope ('sections'|'descriptions'), limit (10),
      rerank (false), path_include/exclude.
OUTPUT: ranked sections with path, heading_chain, signals (BM25/Dense/both),
      rrf score, snippet. Use scope='descriptions' to return one item per file.
ALT: Exact strings / regex → rg via 1cli-tools. For files instead of sections,
      use scope='descriptions'.
COST: First call on cold corpus returns index_warmup_required (exit 4).
      Run md_index once to warm up."
```

```
md_index (mutating):
"Cold-start the persistent embedding index for a Markdown corpus.

WHEN: Setting up a new corpus / md_search returns index_warmup_required /
      large delta detected by md_status.
WHY OURS: One-shot warmup; subsequent md_search etc. become instant for
      that corpus.
INPUT: corpus (path), confirm (required true to proceed), dry_run (estimate
      cost without running).
OUTPUT: index summary — chunks embedded, time, cost_usd.
ALT: md_status to check current state before deciding.
COST: ~$0.02 per 1000 chunks via OpenRouter. Use dry_run:true first to see
      estimated cost. Refuses without confirm:true."
```

Apply this style to all 27 tools. **Keep descriptions tight** — agent reads listTools once, but each description must teach itself.

### A.4 — Update smoke (~+13 assertions)

In `mcp/test/smoke.js`:

- Add assertions for 7 new read-only tools (call each with minimal args, expect non-error result)
- Add assertions for 4 mutating tools with `dry_run: true` (estimate path)
- Add 1 assertion that mutating WITHOUT confirm returns `confirm_required`
- Ensure total tools list now matches 27 (currently expected 19)

Run `npm run smoke` — must end with 100% pass. Adjust if needed (e.g. ensure dry_run works without write side-effect).

### A.5 — Update `mcp/README.md`

Final catalog matching new surface. Replace "Excluded by design" section with new framing: "MCP self-sufficient — listTools is the API spec; skills are workflow overlay".

Bump `package.json` version 0.5.x → 0.6.0.

### A.6 — Bump `md_ping` version response

`md_ping` reports MCP version; bump to 0.6.0 in `mcp/src/server.js`.

## Rules

- **Don't break existing**: 19 current tools keep same name / args / behavior. Only descriptions rewritten.
- **No backend Python changes** unless adding a missing JSON output flag (most CLI commands already support `--json`).
- **No skill folder changes** (Phase B does that).
- **No git commits** — parent session commits after verification.

## Definition of done (Phase A)

- 11 new wrappers exist in `mcp/src/tools/*.js`
- All 27 tools have self-sufficient descriptions
- `mcp/test/smoke.js` runs 100% pass with ~37 assertions
- `mcp/README.md` reflects 27-tool catalog
- `package.json` + `md_ping` version → 0.6.0
- Smoke output snippet attached to report

## Report (concise, <500 words)

- New tools added (list)
- Descriptions rewritten (count + style notes if surprising)
- Smoke assertions count + pass
- Any deviation from spec (e.g. CLI doesn't support --json for X — workaround)
- Files touched
- Any concerns for skill rewrite phase

Don't pad with what you did per template — focus on what surprised or needed judgment.
