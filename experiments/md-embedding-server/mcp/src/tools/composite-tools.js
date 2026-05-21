import { z } from "zod";

import { runGraph } from "./graph-tools.js";
import { runNavigator } from "./navigator-tools.js";

function pushFlag(args, flag, value) {
  if (value === undefined || value === null || value === "") return;
  args.push(flag, String(value));
}

function graphBlockers(preflight) {
  const blockerCodes = new Set([
    "MISSING_TARGET",
    "BROKEN_WIKILINK",
    "BROKEN_MARKDOWN_LINK",
    "MISSING_FRONTMATTER",
    "GRAPH_FIELD_NOT_LIST",
    "GRAPH_LINK_NOT_WIKILINK"
  ]);
  const issueCodes = new Set((preflight.check_only || []).map((item) => item.code));
  return {
    has_blockers: Boolean(
      preflight.has_blockers ||
      (preflight.cycles || []).length ||
      [...issueCodes].some((code) => blockerCodes.has(code))
    ),
    check_only: preflight.check_only || [],
    cycles: preflight.cycles || [],
    anchor_drift_risk: preflight.anchor_drift_risk || {},
    must_update: preflight.must_update || [],
    update_cascade: preflight.update_cascade || []
  };
}

export function registerCompositeTools(registerTool) {
  registerTool(
    "md_orient",
    "**PRIMARY for W1 unfamiliar-corpus orientation workflow.** Instant, cheap orientation: index status + file map with link counts + top graph-important files. No embeddings calls.",
    {
      corpus: z.string().min(1).describe("Markdown corpus folder"),
      max_heading_level: z.number().int().min(1).max(6).optional(),
      top: z.number().int().positive().max(50).optional()
    },
    async ({ corpus, max_heading_level, top }) => {
      const status = await runNavigator(["status", corpus], { parseJson: false, timeoutMs: 30_000 });
      const mapArgs = ["map", corpus, "--json", "--with-link-counts"];
      pushFlag(mapArgs, "--max-heading-level", max_heading_level ?? 2);
      const files = await runNavigator(mapArgs, { timeoutMs: 30_000 });
      const importance = await runNavigator(
        ["importance", corpus, "--json", "--top", String(top ?? 10)],
        { timeoutMs: 30_000 }
      );
      return {
        workflow: "md_orient",
        corpus,
        status,
        files,
        importance,
        next: "For semantic duplicate/drift health use md_audit. For editing one file use md_edit_context."
      };
    }
  );

  registerTool(
    "md_edit_context",
    "**PRIMARY for W4 pre-edit context workflow.** Build the smallest useful packet before editing one Markdown file. Modes: preview, full, strict.",
    {
      path: z.string().min(1).describe("Markdown file to edit"),
      mode: z.enum(["preview", "full", "strict"]).optional(),
      scan: z.string().optional().describe("Graph/link scan root (default repo cwd)"),
      depth: z.number().int().positive().max(10).optional(),
      query: z.string().optional().describe("Optional semantic query to add search results in full mode"),
      corpus: z.string().optional().describe("Corpus root for optional query search")
    },
    async ({ path, mode, scan, depth, query, corpus }) => {
      const selectedMode = mode ?? "full";
      const graphArgs = ["preflight", path, "--json"];
      pushFlag(graphArgs, "--scan", scan);
      pushFlag(graphArgs, "--depth", depth);
      const preflight = await runGraph(graphArgs, { expectFindings: true, timeoutMs: 60_000 });

      if (selectedMode === "strict") {
        return {
          workflow: "md_edit_context",
          mode: "strict",
          path,
          blockers: graphBlockers(preflight)
        };
      }

      const relatedArgs = ["read-related", path, "--json", "--anchor-aware"];
      pushFlag(relatedArgs, "--scan", scan);
      relatedArgs.push("--mode", selectedMode === "preview" ? "preview" : "full");
      if (selectedMode === "preview") {
        relatedArgs.push("--token-budget", "1200");
      } else {
        relatedArgs.push("--token-budget", "6000");
      }
      const related = await runNavigator(relatedArgs, { timeoutMs: 60_000 });

      let search = null;
      if (selectedMode === "full" && query) {
        const searchCorpus = corpus || scan || ".";
        search = await runNavigator(
          ["search", searchCorpus, query, "--json", "--limit", "8"],
          { timeoutMs: 120_000 }
        );
      }

      return {
        workflow: "md_edit_context",
        mode: selectedMode,
        path,
        preflight,
        related,
        search,
        usage_note: "Graph rows are obligations/checks; related/search rows are context candidates."
      };
    }
  );

  registerTool(
    "md_refactor_candidates",
    "**PRIMARY for W7 refactor-opportunity workflow.** Generate human-reviewed Markdown refactor proposals. Returns evidence/confidence/why and never edits files.",
    {
      corpus: z.string().min(1).describe("Markdown corpus folder with a warm md-navigator index"),
      top: z.number().int().positive().max(50).optional(),
      uniqueness_threshold: z.number().min(0).max(1).optional(),
      owner_confidence_threshold: z.number().min(0).max(1).optional()
    },
    async ({ corpus, top, uniqueness_threshold, owner_confidence_threshold }) => {
      const args = ["refactor-candidates", corpus, "--json"];
      pushFlag(args, "--top", top);
      pushFlag(args, "--uniqueness-threshold", uniqueness_threshold);
      pushFlag(args, "--owner-confidence-threshold", owner_confidence_threshold);
      return await runNavigator(args, { timeoutMs: 120_000 });
    }
  );

  registerTool(
    "md_query_by_type",
    "**PRIMARY for W8 semantic-shape query workflow.** Filter profiled sections by profile.type, e.g. open-question, decision, definition, rule.",
    {
      corpus: z.string().min(1).describe("Markdown corpus folder with a warm md-navigator index"),
      types: z.array(z.string().min(1)).min(1).describe("Profile types to return"),
      filter: z.string().optional().describe("Optional substring filter over subject/heading"),
      limit: z.number().int().positive().max(200).optional()
    },
    async ({ corpus, types, filter, limit }) => {
      const args = ["query-by-type", corpus, "--json", "--types", types.join(",")];
      pushFlag(args, "--filter", filter);
      pushFlag(args, "--limit", limit);
      return await runNavigator(args, { timeoutMs: 120_000 });
    }
  );
}
