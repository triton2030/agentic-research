import { z } from "zod";

import { runNavigator } from "./navigator-tools.js";
import { runGraph } from "./graph-tools.js";

export function registerHybridTools(registerTool) {
  registerTool(
    "md_section_blast_radius",
    `Section rename/rewrite radius: graph hard layer + semantic soft layer.

WHEN: Renaming or rewriting a heading, before splitting a section, evaluating contract impact of a paragraph rewrite.
WHY OURS: Combines author-signed contracts (anchor wikilinks via md_preflight) with paraphrase neighbors (md_search). Two layers in one call — Bash can't synthesize semantic candidates.
INPUT: path (.md), corpus (semantic root), query (REQUIRED — capture section's contract intent), heading_id (optional, annotation), scan, depth, limit (default 8), path_include/exclude.
OUTPUT: { path, query, graph, semantic, usage_note } — graph rows = obligations, semantic rows = manual-review candidates.
ALT: md_preflight alone for hard layer. md_search alone for soft layer. md_impact for delete/rename of whole file.
COST: Embedding call for semantic layer (free if cached). Returns index_warmup_required if cold corpus.`,
    {
      path: z.string().min(1).describe("Markdown file path to inspect"),
      corpus: z.string().min(1).describe("Corpus root for semantic search"),
      query: z.string().min(1).describe("Semantic query capturing the section's meaning. Required."),
      heading_id: z.string().optional().describe("Optional stable heading id (e.g. '4.3') — used for annotation only; soft layer queries corpus-wide"),
      scan: z.string().optional().describe("Graph scan scope (default: repo root)"),
      depth: z.number().int().positive().max(10).optional().describe("Graph cascade depth (default 2)"),
      limit: z.number().int().positive().max(50).optional().describe("Max semantic neighbors (default 8)"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ path, corpus, query, heading_id, scan, depth, limit, path_include, path_exclude }) => {
      const graphArgs = ["preflight", path, "--json"];
      if (scan) graphArgs.push("--scan", scan);
      if (depth) graphArgs.push("--depth", String(depth));
      for (const v of path_include || []) graphArgs.push("--path-include", v);
      for (const v of path_exclude || []) graphArgs.push("--path-exclude", v);

      const navArgs = ["search", corpus, query, "--json"];
      navArgs.push("--limit", String(limit ?? 8));
      for (const v of path_include || []) navArgs.push("--path-include", v);
      for (const v of path_exclude || []) navArgs.push("--path-exclude", v);

      const [graph, semantic] = await Promise.all([
        runGraph(graphArgs, { expectFindings: true, timeoutMs: 60_000 }),
        runNavigator(navArgs, { timeoutMs: 120_000 })
      ]);

      return {
        path,
        heading_id: heading_id ?? null,
        query,
        graph,
        semantic,
        usage_note: "Hard layer = author-signed contracts (anchor wikilinks). Soft layer = candidate semantic neighbors, manual review not obligations."
      };
    },
    { openWorldHint: true }
  );
}
