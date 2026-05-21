import { z } from "zod";

import { resolveGraphScript } from "../paths.js";
import { spawnPython, tryParseJson } from "../subprocess.js";

const GRAPH_EXIT_CODES = {
  FINDINGS: 1,
  USAGE: 2
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

async function runGraph(args, { timeoutMs = 60_000, expectFindings = false } = {}) {
  const script = resolveGraphScript();
  const { code, stdout, stderr } = await spawnPython(script, args, { timeoutMs });

  if (code === GRAPH_EXIT_CODES.USAGE) {
    throw new Error(`md_graph usage error (exit 2): ${stderr.trim() || stdout.trim()}. Skill 1md-graph → Schema or Commands section for valid input shape.`);
  }
  if (code !== 0 && code !== GRAPH_EXIT_CODES.FINDINGS) {
    throw new Error(`md_graph exit ${code}: ${stderr.trim() || stdout.trim()}`);
  }

  const parsed = tryParseJson(stdout);
  if (parsed === null) {
    return { text: stdout, stderr: stderr.trim() || null, parse_failed: true, exit_code: code };
  }
  if (expectFindings) {
    const result = { ...parsed, has_blockers: code === GRAPH_EXIT_CODES.FINDINGS };
    if (result.has_blockers) {
      result.self_repair = "Blockers found (missing target / broken link / cycle / missing frontmatter). Skill 1md-graph → Default Workflow for how to resolve each label.";
    }
    return result;
  }
  return { ...parsed, exit_code: code };
}

export function registerGraphTools(registerTool) {
  registerTool(
    "md_preflight",
    "Pre-edit safety report for a .md file: must-read sources, must-update cascade, check-only refs, anchor-drift risk. Sets has_blockers:true on missing-target / broken-link / cycle / missing-frontmatter.",
    {
      path: z.string().min(1).describe("Markdown file path"),
      scan: z.string().optional().describe("Reverse-scan scope (default: repo root)"),
      depth: z.number().int().positive().max(10).optional().describe("Cascade depth (default 2)"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ path, scan, depth, path_include, path_exclude }) => {
      const args = ["preflight", path, "--json"];
      pushFlag(args, "--scan", scan);
      pushFlag(args, "--depth", depth);
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runGraph(args, { expectFindings: true, timeoutMs: 60_000 });
    }
  );

  registerTool(
    "md_impact",
    "What breaks if a .md file is deleted or renamed: cascade holders, reference holders, body wikilinks (anchor-specific marked via #heading), body Markdown links. Each row carries the holder's description.",
    {
      path: z.string().min(1),
      scan: z.string().optional(),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ path, scan, path_include, path_exclude }) => {
      const args = ["impact", path, "--json"];
      pushFlag(args, "--scan", scan);
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runGraph(args, { timeoutMs: 60_000 });
    }
  );

  registerTool(
    "md_deps",
    "Forward edges (read-before-edit, edit-after-edit) for one file plus reverse-scan of who holds it. Each line carries the target's description. With depth>1, walks transitive cascade.",
    {
      path: z.string().min(1),
      scan: z.string().optional(),
      depth: z.number().int().positive().max(10).optional().describe("Cascade depth (default 1)"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ path, scan, depth, path_include, path_exclude }) => {
      const args = ["deps", path, "--json"];
      pushFlag(args, "--scan", scan);
      pushFlag(args, "--depth", depth);
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runGraph(args, { timeoutMs: 60_000 });
    }
  );

  registerTool(
    "md_health",
    "Repo-level graph summary: description coverage percent, TODO files, files without frontmatter, broken graph links, orphans, top hubs, cycles count. Rolls up scan + check + doctor + cycles.",
    {
      paths: z.array(z.string().min(1)).optional().describe("Files or directories (default: current directory)"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ paths, path_include, path_exclude }) => {
      const args = ["health", "--json"];
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      if (Array.isArray(paths) && paths.length > 0) {
        args.push(...paths);
      }
      return await runGraph(args, { timeoutMs: 120_000 });
    }
  );
}

export { runGraph };
