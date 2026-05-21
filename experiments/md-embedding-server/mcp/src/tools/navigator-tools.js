import { z } from "zod";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { randomBytes } from "node:crypto";
import { readdir, stat, writeFile, unlink } from "node:fs/promises";

import { resolveNavigatorScript } from "../paths.js";
import { spawnPython, tryParseJson } from "../subprocess.js";

const NAVIGATOR_EXIT_CODES = {
  NO_RESULTS: 1,
  USAGE_ERROR: 2,
  DEPENDENCY: 3,
  INDEX_WARMUP: 4
};

// Approximate cost per chunk for OpenRouter bge-m3 embeddings.
// Used by md_index / md_profile_sections dry_run estimates.
const COST_PER_CHUNK_USD = 0.00002;          // ~$0.02 per 1000 chunks
const COST_PER_PROFILE_USD = 0.0005;         // heuristic by default; LLM ~$0.0005/section

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

function normalizePathPatterns(patterns, corpus) {
  if (!Array.isArray(patterns)) return [];
  const root = resolve(corpus);
  const prefix = `${root}/`;
  return patterns
    .map((pattern) => String(pattern || "").trim())
    .filter(Boolean)
    .map((pattern) => {
      if (pattern.startsWith(prefix)) return pattern.slice(prefix.length);
      if (pattern.startsWith("./")) return pattern.slice(2);
      return pattern;
    });
}

function pathMatchesAny(relativePath, patterns) {
  for (const pattern of patterns || []) {
    if (!pattern.includes("*") && !pattern.includes("?") && !pattern.includes("[")) {
      if (relativePath.includes(pattern)) return true;
      continue;
    }
    const escaped = pattern.replace(/[.+^${}()|[\]\\]/g, "\\$&")
      .replace(/\*/g, ".*")
      .replace(/\?/g, ".");
    if (new RegExp(`^${escaped}$`).test(relativePath)) return true;
  }
  return false;
}

function applyPathScope(files, corpus, path_include, path_exclude) {
  const include = normalizePathPatterns(path_include, corpus);
  const exclude = normalizePathPatterns(path_exclude, corpus);
  return (files || []).filter((file) => {
    const rel = file.relative_path || "";
    if (include.length && !pathMatchesAny(rel, include)) return false;
    if (exclude.length && pathMatchesAny(rel, exclude)) return false;
    return true;
  });
}

async function runNavigator(args, { timeoutMs = 60_000, parseJson = true } = {}) {
  const script = resolveNavigatorScript();
  const { code, stdout, stderr } = await spawnPython(script, args, { timeoutMs });

  if (code === NAVIGATOR_EXIT_CODES.INDEX_WARMUP) {
    return {
      error: "index_warmup_required",
      self_repair: `Run md_index with confirm:true (or pass dry_run:true first to see estimated cost). New-section delta exceeds --max-auto-embed cap. ~$0.02 per ~1000 chunks.`,
      stderr: stderr.trim() || null
    };
  }
  if (code === NAVIGATOR_EXIT_CODES.USAGE_ERROR) {
    throw new Error(`navigator usage error (exit 2): ${stderr.trim() || stdout.trim()}`);
  }
  if (code === NAVIGATOR_EXIT_CODES.DEPENDENCY) {
    throw new Error(`navigator dependency/API failure (exit 3): ${stderr.trim() || stdout.trim()}. Check OPENROUTER_API_KEY or .openrouter.key file.`);
  }
  if (code === NAVIGATOR_EXIT_CODES.NO_RESULTS) {
    return {
      empty: true,
      self_repair: "Empty result. Check path exists and contains .md files. For semantic queries returning empty, try broader wording or scope='descriptions'.",
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

// Repo-wide corpus scan: walks filesystem, finds .md-navigator/ corpora and
// folders with .md files that have no corpus. Filesystem only — no subprocess
// per-corpus state probe (agent calls md_status for that).
const SCAN_EXCLUDED_DIRS = new Set([
  ".git", ".github", ".claude", ".codex", ".md-navigator",
  ".cache", ".venv", "venv", "__pycache__", ".pytest_cache",
  ".mypy_cache", ".ruff_cache", "node_modules", ".next", ".nuxt",
  "dist", "build", "out", "target", "_archive", "runs"
]);

async function fileExists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

async function scanRepoForCorpora(repoRoot, maxDepth = 10) {
  const root = resolve(repoRoot);
  const corpora = [];
  const unindexed = [];

  async function walk(dir, depth) {
    if (depth > maxDepth) return;

    let entries;
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }

    const indexPath = join(dir, ".md-navigator", "index.sqlite");
    const hasCorpus = await fileExists(indexPath);
    if (hasCorpus) {
      const entry = { root: dir, index_path: indexPath };
      try {
        const st = await stat(indexPath);
        entry.last_touched = st.mtime.toISOString();
        entry.index_size_bytes = st.size;
      } catch {}
      corpora.push(entry);
    }

    let mdCount = 0;
    for (const e of entries) {
      if (e.isFile() && (e.name.endsWith(".md") || e.name.endsWith(".mdx"))) {
        mdCount++;
      }
    }
    if (mdCount > 0 && !hasCorpus) {
      unindexed.push({ folder: dir, md_files: mdCount });
    }

    for (const e of entries) {
      if (!e.isDirectory()) continue;
      if (SCAN_EXCLUDED_DIRS.has(e.name)) continue;
      if (e.name.startsWith(".") && e.name !== "." && e.name !== "..") continue;
      await walk(join(dir, e.name), depth + 1);
    }
  }

  await walk(root, 0);

  // Filter unindexed: drop folders covered by an ancestor corpus. The agent
  // cares about "where is .md without coverage", not "subfolder of an indexed
  // corpus that doesn't have its own nested .md-navigator".
  const corpusRoots = corpora.map((c) => c.root);
  const reallyUnindexed = unindexed.filter((u) => {
    return !corpusRoots.some((cr) => u.folder === cr || u.folder.startsWith(cr + "/"));
  });

  return {
    repo_root: root,
    corpora,
    unindexed_with_md: reallyUnindexed,
    excluded_dirs_skipped: [...SCAN_EXCLUDED_DIRS].sort()
  };
}

// Dry-run helper: estimate pending chunks via `status` command (no HTTP).
async function estimateIndexCost(corpus, path_include, path_exclude) {
  const args = ["status", corpus];
  pushRepeated(args, "--path-include", path_include);
  pushRepeated(args, "--path-exclude", path_exclude);
  const result = await runNavigator(args, { parseJson: false, timeoutMs: 30_000 });
  const text = result.text || "";
  // Parse "added=X pending_chunks=Y" lines. Sum across scopes.
  let pendingChunks = 0;
  let addedSections = 0;
  for (const m of text.matchAll(/pending_chunks=(\d+)/g)) {
    pendingChunks += parseInt(m[1], 10);
  }
  for (const m of text.matchAll(/added=(\d+)/g)) {
    addedSections += parseInt(m[1], 10);
  }
  const noIndex = /Status: NO INDEX/.test(text);
  return {
    pending_chunks: pendingChunks,
    added_sections: addedSections,
    no_index: noIndex,
    estimated_cost_usd: Number((pendingChunks * COST_PER_CHUNK_USD).toFixed(4)),
    status_text: text.trim()
  };
}

// Profile dry-run: count unprofiled sections via section_profile metadata.
async function estimateProfileCost(corpus, mode, path_include, path_exclude) {
  // Use a JSON probe — call profile-sections with --limit 0 in dry-emulation
  // shape. Backend does not have a separate dry_run flag; we count sections
  // from `map` and assume all unprofiled when no profile DB exists.
  // For first-cut estimate, return section count from headings map.
  const mapResult = await runNavigator(["map", corpus, "--json"], { timeoutMs: 30_000 });
  let sectionCount = 0;
  if (mapResult && Array.isArray(mapResult.files)) {
    for (const file of applyPathScope(mapResult.files, corpus, path_include, path_exclude)) {
      if (Array.isArray(file.headings)) sectionCount += file.headings.length;
    }
  }
  const perUnit = mode === "llm" || mode === "auto" ? COST_PER_PROFILE_USD : 0;
  return {
    sections_to_profile_estimate: sectionCount,
    mode: mode || "heuristic",
    estimated_cost_usd: Number((sectionCount * perUnit).toFixed(4)),
    note: mode === "heuristic" || !mode
      ? "Heuristic mode runs locally — no API cost. Cost only for --mode llm/auto."
      : "Estimate assumes all sections need profiling. Already-profiled sections are skipped at runtime (unless force=true)."
  };
}

export function registerNavigatorTools(registerTool) {
  registerTool(
    "md_status",
    `Index freshness for a Markdown corpus. Cheap, no HTTP.

WHEN: Before md_search on a corpus you've been editing. To check if md_index is needed.
WHY OURS: One-call answer — FRESH / HEALTHY / NEEDS WARMUP / NO INDEX with pending-chunk counts. No grep over .md-navigator/.
INPUT: corpus (path), path_include/exclude to check a deliberately partial index scope.
OUTPUT: text block with Corpus / Index / Last touched / Status / per-scope deltas.
ALT: md_orient bundles status + map + importance.
COST: Free (no embedding calls).`,
    {
      corpus: z.string().min(1).describe("Path to Markdown corpus folder"),
      path_include: z.array(z.string().min(1)).optional().describe("Only check/index paths matching these globs or bare substrings"),
      path_exclude: z.array(z.string().min(1)).optional().describe("Exclude matching paths from this status check")
    },
    async ({ corpus, path_include, path_exclude }) => {
      const args = ["status", corpus];
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runNavigator(args, { parseJson: false, timeoutMs: 30_000 });
    }
  );

  registerTool(
    "md_ls",
    `List Markdown files with frontmatter descriptions, titles, heading counts.

WHEN: 'what files are in this folder', folder overview, file inventory, before md_search to scope-down.
WHY OURS: Frontmatter description per file in one packet — Bash ls + cat-loop equivalent at ~10x token cost.
INPUT: path (folder or .md), max_heading_level, match (substring filter), with_tokens, with_link_counts.
OUTPUT: { files: [{ id, relative_path, description, title, heading_count, ...optional }] } — used as map_data for md_extract.
ALT: md_orient for full corpus orientation. md_toc when heading-level detail needed.
COST: Free (no embedding).`,
    {
      path: z.string().min(1).describe("Folder or .md file path"),
      max_heading_level: z.number().int().min(1).max(6).optional(),
      match: z.string().optional().describe("Case-insensitive substring filter over description/title/headings"),
      with_tokens: z.boolean().optional().describe("Attach approximate token counts per file"),
      with_link_counts: z.boolean().optional().describe("Attach in_degree/out_degree per file from the Markdown link graph")
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

  registerTool(
    "md_toc",
    `Table of contents with stable heading ids usable as md_extract input.

WHEN: 'show me headings of folder', need handles before md_extract, planning which sections to read.
WHY OURS: Stable ids (1.2, 4.3) survive heading-text edits. grep '^#' returns text, not ids.
INPUT: path, max_heading_level (default 6), match, with_tokens, with_link_counts.
OUTPUT: { files: [{ id, headings: [{ id, text, level, line }] }] } — map_data for md_extract.
ALT: md_ls when headings unneeded. md_orient for whole corpus.
COST: Free.`,
    {
      path: z.string().min(1),
      max_heading_level: z.number().int().min(1).max(6).optional(),
      match: z.string().optional(),
      with_tokens: z.boolean().optional(),
      with_link_counts: z.boolean().optional()
    },
    async ({ path, max_heading_level, match, with_tokens, with_link_counts }) => {
      const args = ["headings", path, "--json"];
      pushFlag(args, "--max-heading-level", max_heading_level);
      pushFlag(args, "--match", match);
      if (with_tokens) args.push("--with-tokens");
      if (with_link_counts) args.push("--with-link-counts");
      return await runNavigator(args, { timeoutMs: 30_000 });
    }
  );

  registerTool(
    "md_search",
    `Find Markdown sections by natural-language query (BM25F + dense via RRF).

WHEN: 'where is X discussed', 'find sections about Y', any meaning question over .md. Default tool for non-exact searches.
WHY OURS: Semantic + keyword hybrid ranks heading-bounded sections (not line matches). Beats grep for paraphrased / multi-lingual / morphologically-varied queries.
INPUT: corpus, query, scope ('sections'|'descriptions'), limit (10), rerank (false), path_include/exclude.
OUTPUT: { results: [{ path, heading_chain, signals, rrf, snippet }] } ranked. scope='descriptions' returns one item per file.
ALT: Exact strings / regex → rg via Bash. For one file by path → md_extract.
COST: First call on cold corpus returns index_warmup_required (exit 4) — run md_index first. Rerank flag adds ~$0.001.`,
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
    },
    { readOnlyHint: false, openWorldHint: true }
  );

  registerTool(
    "md_extract",
    `Extract file metadata or section bodies from a saved map (md_ls / md_toc / md_search output).

WHEN: After md_ls/md_toc/md_search returned a map and you need to pull specific files/headings — metadata only (extract=false) or full text (extract=true).
WHY OURS: One call instead of pick→cat chain. Heading-aware (extract=true pulls only the section, not whole file). Token-budgeted.
INPUT: map_data (JSON from md_ls/md_toc/md_search), files (comma ids '1,4'), headings (comma ids '1.2,4.3'), extract (false=metadata, true=bodies), token_budget.
OUTPUT: { files: [...], headings: [{ id, text, body? }] } — body present only when extract=true.
ALT: For one whole file by path → built-in Read. For semantic-aware extract → md_read_related with paths.
COST: Free.`,
    {
      map_data: z.unknown().describe("JSON map object from md_ls / md_toc / md_search"),
      files: z.string().optional().describe("Comma list of file ids, e.g. '1,4,7'"),
      headings: z.string().optional().describe("Comma list of heading ids, e.g. '1.2,4.3'"),
      extract: z.boolean().optional().describe("false (default): return metadata only. true: include section text bodies."),
      token_budget: z.number().int().nonnegative().optional()
    },
    async ({ map_data, files, headings, extract, token_budget }) => {
      if (map_data === null || map_data === undefined) {
        throw new Error("map_data is required. First call md_ls / md_toc / md_search to get the map.");
      }
      return await withTempMap(map_data, async (mapPath) => {
        if (extract) {
          // extract=true → use `read` subcommand for heading-aware bodies
          const args = ["read", mapPath, "--json"];
          pushFlag(args, "--files", files);
          pushFlag(args, "--headings", headings);
          pushFlag(args, "--token-budget", token_budget);
          return await runNavigator(args, { timeoutMs: 30_000 });
        }
        // extract=false → use `pick` for metadata-only selection
        const args = ["pick", mapPath, "--json"];
        pushFlag(args, "--files", files);
        pushFlag(args, "--headings", headings);
        pushFlag(args, "--token-budget", token_budget);
        return await runNavigator(args, { timeoutMs: 30_000 });
      });
    }
  );

  registerTool(
    "md_audit",
    `Orchestrated corpus health audit: overlaps + repeated concepts + clusters + heading signals. Slow.

WHEN: 'is this corpus healthy', monthly hygiene pass, before major refactor, suspect IA drift.
WHY OURS: Bundles 4 IA probes + 6 issue-class scoring + 0-100 health gauge — single call instead of 4-tool sequence.
INPUT: corpus, path_include/exclude.
OUTPUT: { classes, findings, health_score, ... } — IA classes with severity ratings.
ALT: For one probe only → md_overlaps / md_repeated_concepts directly. For graph hygiene → md_health.
COST: Slow (minutes), 300s timeout. Cloud embeddings if not cached. Auto-skipped in fast smoke (SMOKE_AUDIT=1 to include).`,
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
    },
    { readOnlyHint: false, openWorldHint: true }
  );

  registerTool(
    "md_read_related",
    `Read an anchor file and its linked neighborhood.

WHEN: Before editing a file you don't know well, understand its graph dependencies, gather context for a question that spans files.
WHY OURS: Walks wikilinks + markdown-links + backlinks + (optional) semantic neighbors in one packet. preview mode omits bodies for fast scan.
INPUT: paths (anchor file(s)), scan (root, default cwd), include (csv: self/frontmatter/wikilinks/markdown-links/backlinks), mode ('preview' | 'full'), anchor_aware (default true), semantic_radius (0=off), check_links, token_budget.
OUTPUT: { anchors, items: [{ path, kind, content? }] } — content present only in full mode.
ALT: md_edit_context composite bundles this with preflight. md_extract for known sections without graph walk.
COST: Free unless semantic_radius>0 or check_links (uses on-disk vecs, no HTTP).`,
    {
      paths: z.array(z.string().min(1)).min(1).describe("Anchor file path(s) — the document(s) you want enriched"),
      scan: z.string().optional().describe("Markdown root to scan for backlinks (default: cwd)"),
      include: z.string().optional().describe("Comma list: self,frontmatter,wikilinks,markdown-links,backlinks (default all)"),
      mode: z.enum(["preview", "full"]).optional().describe("preview: descriptions/headings only. full: include content bodies. Default full."),
      anchor_aware: z.boolean().optional().describe("If a link points to `file#Heading`, extract only that section instead of whole file. Default true."),
      token_budget: z.number().int().nonnegative().optional(),
      semantic_radius: z.number().int().nonnegative().optional().describe("Append top-K semantic neighbors not in the link graph (0 = off)"),
      check_links: z.boolean().optional().describe("Flag explicit links that are semantically far from the anchor — candidates for off-topic review"),
      link_distance_threshold: z.number().positive().optional()
    },
    async ({ paths, scan, include, mode, anchor_aware, token_budget, semantic_radius, check_links, link_distance_threshold }) => {
      const args = ["read-related", ...paths];
      pushFlag(args, "--scan", scan);
      pushFlag(args, "--include", include);
      pushFlag(args, "--mode", mode);
      if (anchor_aware !== false) args.push("--anchor-aware");
      pushFlag(args, "--token-budget", token_budget);
      pushFlag(args, "--semantic-radius", semantic_radius);
      if (check_links) args.push("--check-links");
      pushFlag(args, "--link-distance-threshold", link_distance_threshold);
      args.push("--json");
      return await runNavigator(args, { timeoutMs: 60_000 });
    }
  );

  registerTool(
    "md_importance",
    `Rank Markdown files by link-graph importance (pagerank / in_degree / out_degree / centrality).

WHEN: 'what are the central docs', orient on new corpus, prioritize reading order, find hubs.
WHY OURS: NetworkX pagerank over the Markdown link graph in one call. No grep loops, no embedding cost.
INPUT: corpus, top (default 10), sort_by ('pagerank'|'in_degree'|'out_degree'|'centrality').
OUTPUT: { files: [{ relative_path, pagerank, in_degree, out_degree }] } ranked.
ALT: md_orient bundles importance + status + map.
COST: Free (no embeddings, no HTTP).`,
    {
      corpus: z.string().min(1),
      top: z.number().int().positive().max(100).optional(),
      sort_by: z.enum(["pagerank", "in_degree", "out_degree", "centrality"]).optional()
    },
    async ({ corpus, top, sort_by }) => {
      const args = ["importance", corpus, "--json"];
      pushFlag(args, "--top", top);
      pushFlag(args, "--sort-by", sort_by);
      return await runNavigator(args, { timeoutMs: 30_000 });
    }
  );

  registerTool(
    "md_overlaps",
    `Find section pairs with high semantic similarity (smeared-information detector).

WHEN: 'are there duplicate ideas across files', IA audit for owner-truth violation, before merging two files.
WHY OURS: Section-level cosine pairs ranked by similarity — pinpoints duplicates Bash grep can't catch (paraphrase, different wording).
INPUT: corpus, threshold (default 0.85), top (default 10), include_same_file (false), min_tokens (30), path_include/exclude.
OUTPUT: { pairs: [{ similarity, a: {section, path}, b: {section, path} }], stats } ranked.
ALT: md_audit bundles this + repeated_concepts + clusters. md_repeated_concepts groups by connected components.
COST: Requires warm index (md_index first). Returns index_warmup_required if cold.`,
    {
      corpus: z.string().min(1).describe("Corpus root with warm md-navigator index"),
      threshold: z.number().min(0).max(1).optional().describe("Cosine similarity threshold (default 0.85)"),
      top: z.number().int().positive().max(100).optional().describe("Top-N pairs to return (default 10)"),
      min_tokens: z.number().int().nonnegative().optional().describe("Skip sections below this token count (default 30)"),
      include_same_file: z.boolean().optional().describe("Include section pairs from the same file (default false)"),
      max_heading_level: z.number().int().min(1).max(6).optional(),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ corpus, threshold, top, min_tokens, include_same_file, max_heading_level, path_include, path_exclude }) => {
      const args = ["overlaps", corpus, "--json"];
      pushFlag(args, "--threshold", threshold);
      pushFlag(args, "--top", top);
      pushFlag(args, "--min-tokens", min_tokens);
      if (include_same_file) args.push("--include-same-file");
      pushFlag(args, "--max-heading-level", max_heading_level);
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runNavigator(args, { timeoutMs: 120_000 });
    },
    { readOnlyHint: false, openWorldHint: true }
  );

  registerTool(
    "md_repeated_concepts",
    `Find ideas that recur across the corpus via connected components on section-similarity graph.

WHEN: 'what concepts keep coming up', owner-truth probe, recurring topic discovery, before splitting a topic into a dedicated file.
WHY OURS: Concept-level clustering (not just pair-wise like md_overlaps). Each concept lists files it touches + representative section.
INPUT: corpus, threshold (default 0.80), top (default 30), min_files (default 2), min_sections, path_include/exclude.
OUTPUT: { concepts: [{ medoid_section, files, member_sections, cohesion }], stats } + writes <corpus>/.md-navigator/repeated-concepts.md as side-effect report.
ALT: md_audit bundles this + overlaps + clusters. md_overlaps for pair-level only.
COST: Requires warm index (md_index first). Writes one Markdown file inside .md-navigator/.`,
    {
      corpus: z.string().min(1).describe("Corpus root with warm md-navigator index"),
      threshold: z.number().min(0).max(1).optional().describe("Cosine threshold for graph edges (default 0.80)"),
      top: z.number().int().positive().max(200).optional().describe("Top-N concepts (default 30)"),
      min_files: z.number().int().positive().optional().describe("Drop concepts spanning fewer than this many files (default 2)"),
      min_sections: z.number().int().positive().optional(),
      min_tokens: z.number().int().nonnegative().optional(),
      top_members: z.number().int().positive().optional(),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ corpus, threshold, top, min_files, min_sections, min_tokens, top_members, path_include, path_exclude }) => {
      const args = ["repeated-concepts", corpus, "--json"];
      pushFlag(args, "--threshold", threshold);
      pushFlag(args, "--top", top);
      pushFlag(args, "--min-files", min_files);
      pushFlag(args, "--min-sections", min_sections);
      pushFlag(args, "--min-tokens", min_tokens);
      pushFlag(args, "--top-members", top_members);
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runNavigator(args, { timeoutMs: 180_000 });
    },
    { readOnlyHint: false, openWorldHint: true }
  );

  registerTool(
    "md_index",
    `Cold-start or top-up the persistent embedding index for a corpus. MUTATING + COST-BEARING.

WHEN: New corpus / md_search returns index_warmup_required / large delta detected by md_status.
WHY OURS: One-shot warmup; subsequent md_search / md_overlaps / md_repeated_concepts become instant.
INPUT: corpus, confirm (required true), dry_run (estimate cost without running), batch_size, batch_pause_ms, path_include/exclude for partial indexes.
OUTPUT (live): index summary text — chunks embedded, time, cost.
OUTPUT (dry_run): { dry_run: true, pending_chunks, estimated_cost_usd, status_text }.
ALT: md_status to check state first.
COST: ~$0.02 per ~1000 chunks via OpenRouter bge-m3. Use dry_run:true first. Refuses without confirm:true.`,
    {
      corpus: z.string().min(1).describe("Markdown corpus folder"),
      confirm: z.boolean().optional().describe("Required true to actually run. Default false rejects with cost warning."),
      dry_run: z.boolean().optional().describe("If true, return estimated cost / pending chunks without embedding."),
      batch_size: z.number().int().positive().max(128).optional(),
      batch_pause_ms: z.number().int().nonnegative().optional(),
      max_heading_level: z.number().int().min(1).max(6).optional(),
      path_include: z.array(z.string().min(1)).optional().describe("Only index paths matching these globs or bare substrings"),
      path_exclude: z.array(z.string().min(1)).optional().describe("Exclude matching paths from this index run")
    },
    async ({ corpus, confirm, dry_run, batch_size, batch_pause_ms, max_heading_level, path_include, path_exclude }) => {
      if (dry_run) {
        const est = await estimateIndexCost(corpus, path_include, path_exclude);
        return {
          dry_run: true,
          ...est,
          hint: est.pending_chunks === 0 && !est.no_index
            ? "Index is fresh — no embedding needed. Skip md_index."
            : `Pass confirm:true to embed ${est.pending_chunks} chunks (~$${est.estimated_cost_usd}).`
        };
      }
      if (!confirm) {
        return {
          error: "confirm_required",
          reason: "Cost-bearing operation: embeds Markdown sections via OpenRouter (~$0.02 per ~1000 chunks).",
          hint: "Pass dry_run:true for estimate, then confirm:true to proceed."
        };
      }
      const args = ["index", corpus];
      pushFlag(args, "--batch-size", batch_size);
      pushFlag(args, "--batch-pause-ms", batch_pause_ms);
      pushFlag(args, "--max-heading-level", max_heading_level);
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runNavigator(args, { parseJson: false, timeoutMs: 600_000 });
    },
    { readOnlyHint: false, openWorldHint: true, idempotentHint: false }
  );

  registerTool(
    "md_profile_sections",
    `Classify indexed sections and cache section profiles in index.sqlite. MUTATING (writes profile rows).

WHEN: Before md_query_by_type / md_refactor_candidates on a fresh index, after large corpus edits.
WHY OURS: One-pass classifier — heuristic (free) or LLM (~$0.0005/section). Profiles cached, subsequent reads instant.
INPUT: corpus, confirm (required true), dry_run (estimate), limit, force, mode ('heuristic'|'llm'|'auto'), model, path_include/exclude.
OUTPUT (live): { stats, sample } — sections profiled, counts per type.
OUTPUT (dry_run): { dry_run: true, sections_to_profile_estimate, mode, estimated_cost_usd }.
ALT: md_query_by_type / md_refactor_candidates lazy-profile what they need.
COST: Heuristic mode free. LLM mode ~$0.0005/section (haiku). Use dry_run first.`,
    {
      corpus: z.string().min(1).describe("Corpus root with warm md-navigator index"),
      confirm: z.boolean().optional().describe("Required true to actually run."),
      dry_run: z.boolean().optional().describe("If true, return section count + estimated cost without classifying."),
      limit: z.number().int().nonnegative().optional().describe("Max sections to profile (0=all)"),
      force: z.boolean().optional().describe("Re-profile even cached rows"),
      mode: z.enum(["heuristic", "llm", "auto"]).optional(),
      model: z.string().optional().describe("LLM classifier model id for mode=llm/auto"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ corpus, confirm, dry_run, limit, force, mode, model, path_include, path_exclude }) => {
      if (dry_run) {
        const est = await estimateProfileCost(corpus, mode, path_include, path_exclude);
        return {
          dry_run: true,
          ...est,
          hint: `Pass confirm:true to profile ${est.sections_to_profile_estimate} sections (mode=${est.mode}).`
        };
      }
      if (!confirm) {
        return {
          error: "confirm_required",
          reason: "Cost-bearing operation: classifies sections (heuristic=free, llm mode=~$0.0005/section).",
          hint: "Pass dry_run:true for estimate, then confirm:true to proceed."
        };
      }
      const args = ["profile-sections", corpus, "--json"];
      pushFlag(args, "--limit", limit);
      if (force) args.push("--force");
      pushFlag(args, "--mode", mode);
      pushFlag(args, "--model", model);
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runNavigator(args, { timeoutMs: 600_000 });
    },
    { readOnlyHint: false, openWorldHint: true, idempotentHint: false }
  );

  registerTool(
    "md_corpus_scan",
    `Repo-wide scan: find all md-navigator corpora and folders with .md files without a corpus.

WHEN: Cold session start, "what's indexed where?" agent question, repo-wide health check before committing to one corpus.
WHY OURS: Single filesystem walk replaces manually checking every .md-navigator/. Surfaces unindexed .md folders so you know what was NOT covered (intentionally or by oversight).
INPUT: root (default cwd).
OUTPUT: { repo_root, corpora: [{root, index_path, last_touched, index_size_bytes}], unindexed_with_md: [{folder, md_files}], excluded_dirs_skipped }.
ALT: md_status for one corpus's freshness state. md_orient for cold-start of one corpus.
COST: Free. Filesystem walk only, no subprocess, no HTTP.`,
    {
      root: z.string().optional().describe("Repo root to scan from (default: server cwd).")
    },
    async ({ root }) => {
      const target = root || process.cwd();
      return await scanRepoForCorpora(target);
    },
    { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true }
  );
}

export { runNavigator };
