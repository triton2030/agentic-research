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
    `Cheap corpus orientation: status + map with link counts + top graph-important files.

WHEN: New Markdown corpus / folder, 'orient me in this repo', first call before any md_* deep dive.
WHY OURS: Three signals (status / files / importance) in one shot, no embeddings, no HTTP. Bash ls + grep + wc loop equivalent at ~3x token cost.
INPUT: corpus (path), max_heading_level (default 2 in composite), top (default 10).
OUTPUT: { workflow:'md_orient', corpus, status, files, importance, next } — files include in_degree/out_degree.
ALT: md_status / md_ls / md_importance separately if only one signal needed.
COST: Free.`,
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
    `Smallest useful packet before editing one .md file. Modes: preview / full / strict.

WHEN: Before editing a .md file you don't fully know — anchor file + linked context + (optional) semantic neighbors + graph blockers.
WHY OURS: Bundles md_preflight + md_read_related (+ optional md_search) — one call instead of 2-3.
INPUT: path, mode ('preview'|'full'|'strict', default full), scan, depth, query (full mode adds search), corpus (for query).
OUTPUT (preview): preflight + related (descriptions only).
OUTPUT (full): preflight + related (bodies) + optional search.
OUTPUT (strict): preflight only — { blockers: { has_blockers, ... } }.
ALT: md_preflight alone for blocker check. md_section_blast_radius for rename.
COST: Free unless full+query (~$0.001 if rerank, normally cached).`,
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
    },
    { openWorldHint: true }
  );

  registerTool(
    "md_refactor_candidates",
    `Generate human-reviewed Markdown refactor proposals. Never edits files.

WHEN: 'find refactor opportunities', IA hygiene pass, before split/merge planning. Output is suggestion list for human review.
WHY OURS: Combines section profiles + originality + owner candidates into ranked proposals with evidence/confidence/why. Manual heuristic combo is hours; this is one call.
INPUT: corpus (warm index), top (default 10), uniqueness_threshold (default 0.35), owner_confidence_threshold (default 0.45).
OUTPUT: { proposals: [{ kind, target, evidence, confidence, why }], no_automation:true } — no_automation:true signals 'human reviews, MCP never edits'.
ALT: md_audit for whole-corpus health. md_query_by_type to filter by semantic shape.
COST: Requires warm index + profiles. Auto-profiles unprofiled sections lazily.`,
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
    },
    { openWorldHint: true }
  );

  registerTool(
    "md_query_by_type",
    `List profiled sections by profile.type: open-question, decision, definition, rule, example, uses, external-citation.

WHEN: 'show me all open questions', 'list rules in this corpus', semantic-shape query.
WHY OURS: Returns only sections that match the type (heuristic or LLM classifier). Bash grep can't classify rule-vs-example.
INPUT: corpus (warm index), types (array), filter (substring over subject/heading), limit (default 50).
OUTPUT: { types, sections: [{ section_id, path, heading_chain, subject, type, confidence }] }.
ALT: md_refactor_candidates for proposal-level. md_search for free-text query.
COST: Lazy-profiles unprofiled sections (heuristic free, llm ~$0.0005/section). Pre-profile via md_profile_sections.`,
    {
      corpus: z.string().min(1).describe("Markdown corpus folder with a warm md-navigator index"),
      types: z.array(z.string().min(1)).min(1).describe("Profile types to return: open-question, decision, definition, rule, example, uses, external-citation, heading-only"),
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
