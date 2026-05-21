import { z } from "zod";

import { runNavigator } from "./navigator-tools.js";
import { runGraph } from "./graph-tools.js";

export function registerHybridTools(registerTool) {
  registerTool(
    "md_section_blast_radius",
    "Hybrid blast-radius for a section before rename/rewrite. Combines graph hard layer (md_preflight: explicit wikilinks, anchor-drift, must-update) with semantic soft layer (md_search: paraphrase / named-citation neighbors). One call instead of two. `query` is required — formulate it to capture the section's contract intent.",
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
    }
  );
}
