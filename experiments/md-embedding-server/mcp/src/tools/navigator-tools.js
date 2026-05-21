import { z } from "zod";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { randomBytes } from "node:crypto";
import { writeFile, unlink } from "node:fs/promises";

import { resolveNavigatorScript } from "../paths.js";
import { spawnPython, tryParseJson } from "../subprocess.js";

const NAVIGATOR_EXIT_CODES = {
  NO_RESULTS: 1,
  USAGE_ERROR: 2,
  DEPENDENCY: 3,
  INDEX_WARMUP: 4
};

function pushFlag(args, flag, value) {
  if (value === undefined || value === null || value === "") return;
  args.push(flag, String(value));
}

function pushRepeated(args, flag, values) {
  if (!Array.isArray(values)) return;
  for (const v of values) {
    if (v) args.push(flag, String(v));
  }
}

async function runNavigator(args, { timeoutMs = 60_000, parseJson = true } = {}) {
  const script = resolveNavigatorScript();
  const { code, stdout, stderr } = await spawnPython(script, args, { timeoutMs });

  if (code === NAVIGATOR_EXIT_CODES.INDEX_WARMUP) {
    return {
      error: "index_warmup_required",
      self_repair: `Skill 1md-navigator → Quick start: run \`${script} index <corpus>\` once (~$0.02 per ~1000 chunks). Then retry. New-section delta exceeds --max-auto-embed.`,
      stderr: stderr.trim() || null
    };
  }
  if (code === NAVIGATOR_EXIT_CODES.USAGE_ERROR) {
    throw new Error(`navigator usage error (exit 2): ${stderr.trim() || stdout.trim()}`);
  }
  if (code === NAVIGATOR_EXIT_CODES.DEPENDENCY) {
    throw new Error(`navigator dependency/API failure (exit 3): ${stderr.trim() || stdout.trim()}. Check OPENROUTER_API_KEY or .openrouter.key file. Skill 1md-navigator → references/setup.md.`);
  }
  if (code === NAVIGATOR_EXIT_CODES.NO_RESULTS) {
    return {
      empty: true,
      self_repair: "Empty result. Check that the path exists and contains .md files. For semantic queries returning empty, try broader wording or `--scope descriptions`. Skill 1md-navigator → Search contract.",
      stderr: stderr.trim() || null
    };
  }
  if (code !== 0) {
    throw new Error(`navigator exit ${code}: ${stderr.trim() || stdout.trim()}`);
  }

  if (!parseJson) {
    return { text: stdout, stderr: stderr.trim() || null };
  }
  const parsed = tryParseJson(stdout);
  if (parsed === null) {
    return { text: stdout, stderr: stderr.trim() || null, parse_failed: true };
  }
  return parsed;
}

async function withTempMap(mapData, callback) {
  const path = join(tmpdir(), `md-mcp-map-${randomBytes(8).toString("hex")}.json`);
  await writeFile(path, JSON.stringify(mapData), "utf-8");
  try {
    return await callback(path);
  } finally {
    await unlink(path).catch(() => {});
  }
}

export function registerNavigatorTools(registerTool) {
  registerTool(
    "md_status",
    "Index freshness for a Markdown corpus. No HTTP, no writes. Returns FRESH / HEALTHY / NEEDS WARMUP / NO INDEX.",
    {
      corpus: z.string().min(1).describe("Path to Markdown corpus folder")
    },
    async ({ corpus }) => {
      const args = ["status", corpus];
      return await runNavigator(args, { parseJson: false, timeoutMs: 30_000 });
    }
  );

  registerTool(
    "md_ls",
    "List Markdown files in a folder with frontmatter description, title, and heading count. Faster than `ls` + reading frontmatter manually. No index needed.",
    {
      path: z.string().min(1).describe("Folder or .md file path"),
      max_heading_level: z.number().int().min(1).max(6).optional(),
      match: z.string().optional().describe("Case-insensitive substring filter over description/title/headings"),
      with_tokens: z.boolean().optional().describe("Attach approximate token counts per file")
    },
    async ({ path, max_heading_level, match, with_tokens }) => {
      const args = ["map", path, "--json"];
      pushFlag(args, "--max-heading-level", max_heading_level);
      pushFlag(args, "--match", match);
      if (with_tokens) args.push("--with-tokens");
      return await runNavigator(args, { timeoutMs: 30_000 });
    }
  );

  registerTool(
    "md_toc",
    "Table of contents for a Markdown folder: every heading with a stable id (`1.2`, `4.3`) usable as input to md_pick. No index needed.",
    {
      path: z.string().min(1),
      max_heading_level: z.number().int().min(1).max(6).optional(),
      match: z.string().optional(),
      with_tokens: z.boolean().optional()
    },
    async ({ path, max_heading_level, match, with_tokens }) => {
      const args = ["headings", path, "--json"];
      pushFlag(args, "--max-heading-level", max_heading_level);
      pushFlag(args, "--match", match);
      if (with_tokens) args.push("--with-tokens");
      return await runNavigator(args, { timeoutMs: 30_000 });
    }
  );

  registerTool(
    "md_search",
    "Semantic + keyword search across a Markdown corpus (BM25F + dense via RRF). Returns ranked sections, not lines. Use for natural-language «which section talks about X». For exact strings / regex / known symbols use `rg` — cheaper, no spawn overhead, no index needed.",
    {
      corpus: z.string().min(1),
      query: z.string().min(1),
      scope: z.enum(["sections", "descriptions"]).optional().describe("sections (default): rank heading-bounded sections. descriptions: rank files by frontmatter description"),
      limit: z.number().int().positive().max(100).optional(),
      candidates: z.number().int().positive().max(500).optional(),
      max_heading_level: z.number().int().min(1).max(6).optional(),
      rerank: z.boolean().optional().describe("Cross-encoder rerank top-N (~$0.001, ~300-700ms)"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ corpus, query, scope, limit, candidates, max_heading_level, rerank, path_include, path_exclude }) => {
      const args = ["search", corpus, query, "--json"];
      pushFlag(args, "--scope", scope);
      pushFlag(args, "--limit", limit);
      pushFlag(args, "--candidates", candidates);
      pushFlag(args, "--max-heading-level", max_heading_level);
      if (rerank) args.push("--rerank");
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runNavigator(args, { timeoutMs: 120_000 });
    }
  );

  registerTool(
    "md_pick",
    "Select files/headings from a saved map (output of md_ls / md_toc / md_search). Pass map_data inline; with extract:true returns section bodies.",
    {
      map_data: z.unknown().describe("JSON map object from md_ls / md_toc / md_search"),
      files: z.string().optional().describe("Comma list of file ids, e.g. '1,4,7'"),
      headings: z.string().optional().describe("Comma list of heading ids, e.g. '1.2,4.3'"),
      extract: z.boolean().optional().describe("Include section text body for selected headings"),
      token_budget: z.number().int().nonnegative().optional()
    },
    async ({ map_data, files, headings, extract, token_budget }) => {
      if (map_data === null || map_data === undefined) {
        throw new Error("map_data is required. First call md_ls / md_toc / md_search to get the map.");
      }
      return await withTempMap(map_data, async (mapPath) => {
        const args = ["pick", mapPath, "--json"];
        pushFlag(args, "--files", files);
        pushFlag(args, "--headings", headings);
        if (extract) args.push("--extract");
        pushFlag(args, "--token-budget", token_budget);
        return await runNavigator(args, { timeoutMs: 30_000 });
      });
    }
  );

  registerTool(
    "md_cat",
    "Heading-aware section extract from a saved map (output of md_ls / md_toc / md_search). Pass map_data + heading ids to get section bodies in one packet, optionally token-budgeted. For one file by path use built-in Read — it's shorter and identical for whole-file reads.",
    {
      map_data: z.unknown().describe("JSON map from md_ls / md_toc / md_search"),
      files: z.string().optional(),
      headings: z.string().optional(),
      token_budget: z.number().int().nonnegative().optional()
    },
    async ({ map_data, files, headings, token_budget }) => {
      if (map_data === null || map_data === undefined) {
        throw new Error("map_data is required. First call md_ls / md_toc / md_search to get the map. For one file by path use built-in Read.");
      }
      const argsBase = ["read"];
      pushFlag(argsBase, "--token-budget", token_budget);
      pushFlag(argsBase, "--files", files);
      pushFlag(argsBase, "--headings", headings);
      argsBase.push("--json");
      return await withTempMap(map_data, async (mapPath) => {
        return await runNavigator([...argsBase.slice(0, 1), mapPath, ...argsBase.slice(1)], {
          timeoutMs: 30_000
        });
      });
    }
  );

  registerTool(
    "md_audit",
    "Orchestrated corpus health audit: overlaps + repeated concepts + clusters + heading signals. Six IA classes with severity and 0-100 health gauge. Slow (~minutes), 300s timeout.",
    {
      corpus: z.string().min(1),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ corpus, path_include, path_exclude }) => {
      const args = ["audit", corpus, "--json"];
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runNavigator(args, { timeoutMs: 300_000 });
    }
  );

  registerTool(
    "md_read_related",
    "Read an anchor file and pull content from its linked neighborhood in one packet: wikilinks, markdown-links, frontmatter graph edges, backlinks. When a link targets a specific heading (`[[file#Heading]]`), pulls only that section, not the whole file (anchor_aware default true). Use to enrich understanding of a document with context from its references in one call.",
    {
      paths: z.array(z.string().min(1)).min(1).describe("Anchor file path(s) — the document(s) you want enriched"),
      scan: z.string().optional().describe("Markdown root to scan for backlinks (default: cwd)"),
      include: z.string().optional().describe("Comma list: self,frontmatter,wikilinks,markdown-links,backlinks (default all)"),
      anchor_aware: z.boolean().optional().describe("If a link points to `file#Heading`, extract only that section instead of whole file. Default true. Set false to revert to whole-file behavior."),
      token_budget: z.number().int().nonnegative().optional(),
      semantic_radius: z.number().int().nonnegative().optional().describe("Append top-K semantic neighbors not in the link graph (0 = off)"),
      check_links: z.boolean().optional().describe("Flag explicit links that are semantically far from the anchor — candidates for off-topic review"),
      link_distance_threshold: z.number().positive().optional()
    },
    async ({ paths, scan, include, anchor_aware, token_budget, semantic_radius, check_links, link_distance_threshold }) => {
      const args = ["read-related", ...paths];
      pushFlag(args, "--scan", scan);
      pushFlag(args, "--include", include);
      if (anchor_aware !== false) args.push("--anchor-aware");
      pushFlag(args, "--token-budget", token_budget);
      pushFlag(args, "--semantic-radius", semantic_radius);
      if (check_links) args.push("--check-links");
      pushFlag(args, "--link-distance-threshold", link_distance_threshold);
      args.push("--json");
      return await runNavigator(args, { timeoutMs: 60_000 });
    }
  );
}

export { runNavigator };
