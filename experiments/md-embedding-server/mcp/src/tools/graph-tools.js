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
    throw new Error(`md_graph usage error (exit 2): ${stderr.trim() || stdout.trim()}.`);
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
      result.self_repair = "Blockers found (missing target / broken link / cycle / missing frontmatter). Resolve via md_preflight self_repair hints or read 1md-graph SKILL.md Default Workflow.";
    }
    return result;
  }
  return { ...parsed, exit_code: code };
}

// Dry-run helper for md_init: walk graph and count files that would be modified.
async function estimateInitScope(paths, path_include, path_exclude) {
  // `scan` returns issues including missing-frontmatter; init modifies only those.
  const args = ["scan", "--json"];
  pushRepeated(args, "--path-include", path_include);
  pushRepeated(args, "--path-exclude", path_exclude);
  if (Array.isArray(paths) && paths.length > 0) {
    args.push(...paths);
  }
  const result = await runGraph(args, { timeoutMs: 60_000 });
  const issues = result.issues || [];
  const wouldModify = new Set();
  for (const f of issues) {
    if (f.code === "MISSING_FRONTMATTER") {
      if (f.path) wouldModify.add(f.path);
    }
  }
  return {
    files_to_modify: [...wouldModify],
    file_count: wouldModify.size,
    issues_total: issues.length
  };
}

// Dry-run helper for md_strip: scan for legacy fields.
async function estimateStripScope(paths, alsoRelatedSection, path_include, path_exclude) {
  const args = ["scan", "--json"];
  pushRepeated(args, "--path-include", path_include);
  pushRepeated(args, "--path-exclude", path_exclude);
  if (Array.isArray(paths) && paths.length > 0) {
    args.push(...paths);
  }
  const result = await runGraph(args, { timeoutMs: 60_000 });
  const issues = result.issues || [];
  const wouldModify = new Set();
  for (const f of issues) {
    if (f.code === "LEGACY_FIELD" || f.code === "UNKNOWN_FIELD") {
      if (f.path) wouldModify.add(f.path);
    }
  }
  let issuesTotal = issues.length;
  if (alsoRelatedSection) {
    const checkArgs = ["check", "--json"];
    pushRepeated(checkArgs, "--path-include", path_include);
    pushRepeated(checkArgs, "--path-exclude", path_exclude);
    if (Array.isArray(paths) && paths.length > 0) {
      checkArgs.push(...paths);
    }
    const checkResult = await runGraph(checkArgs, { timeoutMs: 60_000 });
    const checkIssues = checkResult.issues || [];
    issuesTotal += checkIssues.length;
    for (const f of checkIssues) {
      if (f.code === "RELATED_SECTION_PRESENT" && f.path) {
        wouldModify.add(f.path);
      }
    }
  }
  return {
    files_to_modify: [...wouldModify],
    file_count: wouldModify.size,
    also_related_section: !!alsoRelatedSection,
    issues_total: issuesTotal,
    note: alsoRelatedSection
      ? "Will also remove '## Связанные документы' / '## Related documents' sections from body."
      : "Frontmatter-only strip. Pass also_related_section:true to also remove related-docs body sections."
  };
}

export function registerGraphTools(registerTool) {
  registerTool(
    "md_preflight",
    `Pre-edit safety report for one .md file. Sets has_blockers if cycles / broken links / missing frontmatter.

WHEN: Before editing any .md file with frontmatter graph fields, especially when changing title or major sections.
WHY OURS: One-pass surface of must-read sources + must-update cascade + check-only refs + anchor-drift risk. Bash grep can't synthesize this from frontmatter.
INPUT: path (.md), scan (reverse-scan root), depth (cascade default 2), path_include/exclude.
OUTPUT: { command, must_read, must_update, check_only, cycles, anchor_drift_risk, has_blockers } — has_blockers:true if MISSING_TARGET / BROKEN_LINK / cycle.
ALT: md_edit_context composite bundles preflight + read-related + optional search. md_section_blast_radius adds semantic layer.
COST: Free.`,
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
    `What breaks if a .md file is deleted or renamed.

WHEN: Before rm / mv on a .md file, before merging two files, planning a refactor.
WHY OURS: Cascade holders + reference holders + body wikilinks + body markdown-links — each row carries the holder's frontmatter description. grep returns matches but not the contract intent.
INPUT: path, scan, path_include/exclude.
OUTPUT: { command:'impact', cascade_holders, reference_holders, body_wikilinks, body_markdown_links } — anchor-specific wikilinks marked via #heading.
ALT: md_section_blast_radius for rename of one section (adds semantic layer).
COST: Free.`,
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
    `Forward edges (read-before-edit / edit-after-edit) + reverse holders for one file.

WHEN: 'what does this file depend on', 'who depends on this file', understand graph position before navigating.
WHY OURS: Both directions in one call, depth>1 walks transitive cascade. Each row carries target's description.
INPUT: path, scan, depth (default 1), path_include/exclude.
OUTPUT: { command:'deps', forward, reverse } — each row has path + description.
ALT: md_impact for delete/rename specifically. md_preflight for edit safety.
COST: Free.`,
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
    `Repo-level graph summary: description coverage, hubs, orphans, broken links, cycles.

WHEN: 'is this repo's md healthy', monthly hygiene, before opening a PR with many .md changes.
WHY OURS: Rolls up scan + check + doctor + cycles into one summary with percentages, hubs, top issues. Replaces 4-command bash dance.
INPUT: paths (default '.'), path_include/exclude.
OUTPUT: { description_coverage, todo_files, files_without_frontmatter, broken_graph_links, orphans, top_hubs, cycles_count, ... }.
ALT: md_scan / md_check / md_cycles for individual probes. md_audit for semantic + structural.
COST: Free.`,
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

  registerTool(
    "md_cycles",
    `Find edit-after-edit cycles in the Markdown graph.

WHEN: 'do we have circular dependencies', after add/remove edit-after-edit refs, debugging stuck cascades.
WHY OURS: Tarjan SCC over graph edges — Bash awk over frontmatter can't traverse transitively.
INPUT: paths (default '.'), path_include/exclude.
OUTPUT: { command:'cycles', cycles: [[file1, file2, ...]] } — each cycle as a list. Non-zero exit when cycles present.
ALT: md_health bundles cycles count + hubs + orphans. md_preflight for one-file cycle check.
COST: Free.`,
    {
      paths: z.array(z.string().min(1)).optional().describe("Files or directories (default: current directory)"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ paths, path_include, path_exclude }) => {
      const args = ["cycles", "--json"];
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      if (Array.isArray(paths) && paths.length > 0) {
        args.push(...paths);
      }
      return await runGraph(args, { expectFindings: true, timeoutMs: 60_000 });
    }
  );

  registerTool(
    "md_check",
    `Validate wikilinks / anchors / markdown-links across the corpus.

WHEN: 'are any links broken', before committing many .md edits, after rename/move operations.
WHY OURS: Validates wikilink targets + anchor existence + markdown-link paths in one pass + detects related-docs sections. Bash regex can't resolve [[wikilink]] targets.
INPUT: paths (default '.'), path_include/exclude.
OUTPUT: { command:'check', findings: [{ code, path, line, message, ... }] } — codes: BROKEN_WIKILINK / BROKEN_ANCHOR / BROKEN_MARKDOWN_LINK. Non-zero exit when findings.
ALT: md_health rolls up check + scan + cycles. md_preflight for one-file pre-edit.
COST: Free.`,
    {
      paths: z.array(z.string().min(1)).optional().describe("Files or directories (default: current directory)"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ paths, path_include, path_exclude }) => {
      const args = ["check", "--json"];
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      if (Array.isArray(paths) && paths.length > 0) {
        args.push(...paths);
      }
      return await runGraph(args, { expectFindings: true, timeoutMs: 60_000 });
    }
  );

  registerTool(
    "md_scan",
    `Detect frontmatter form issues: missing / legacy / unknown / malformed fields.

WHEN: Onboarding new .md files into graph, after schema change, before md_init/md_strip.
WHY OURS: One pass over every .md frontmatter with canonical schema check. Replaces grep + yaml-parse loop.
INPUT: paths (default '.'), path_include/exclude.
OUTPUT: { command:'scan', issues: [{ code, path, detail }] } — codes: MISSING_FRONTMATTER / LEGACY_FIELD / UNKNOWN_FIELD / FRONTMATTER_INVALID.
ALT: md_health rolls up scan + check + cycles. md_init to add templates. md_strip to remove legacy.
COST: Free.`,
    {
      paths: z.array(z.string().min(1)).optional().describe("Files or directories (default: current directory)"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ paths, path_include, path_exclude }) => {
      const args = ["scan", "--json"];
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      if (Array.isArray(paths) && paths.length > 0) {
        args.push(...paths);
      }
      return await runGraph(args, { expectFindings: true, timeoutMs: 60_000 });
    }
  );

  registerTool(
    "md_changed",
    `Preflight check on every .md file touched by git diff.

WHEN: Pre-commit pass, before opening a PR, batch-validate a feature branch.
WHY OURS: git diff → list .md files → preflight each — one call. Reports deleted files separately.
INPUT: scan (default repo root), depth (cascade, default 2), base (git ref) | staged (boolean), path_include/exclude.
OUTPUT: { command:'changed', changed: [{ path, preflight: {...} }], deleted: [...] }.
ALT: Pre-commit hook. md_preflight for one file by path.
COST: Free.`,
    {
      scan: z.string().optional().describe("Reverse-scan scope (default: repo root)"),
      depth: z.number().int().positive().max(10).optional().describe("Cascade depth (default 2)"),
      base: z.string().optional().describe("Git ref to diff against (e.g. 'main')"),
      since: z.string().optional().describe("Git ref to diff against (default: HEAD, includes staged + unstaged)"),
      staged: z.boolean().optional().describe("Use staged changes from git diff --cached"),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ scan, depth, base, since, staged, path_include, path_exclude }) => {
      const args = ["changed", "--json"];
      pushFlag(args, "--scan", scan);
      pushFlag(args, "--depth", depth);
      pushFlag(args, "--base", base);
      pushFlag(args, "--since", since);
      if (staged) args.push("--staged");
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      return await runGraph(args, { expectFindings: true, timeoutMs: 60_000 });
    }
  );

  registerTool(
    "md_init",
    `Add graph frontmatter template to .md files missing it. MUTATING (writes to disk).

WHEN: Onboarding new files / folder into graph workflow, after migration scan flagged missing frontmatter.
WHY OURS: One pass that respects existing frontmatter — adds missing graph fields with canonical defaults. Bash sed can't merge YAML safely.
INPUT: paths, confirm (required true), dry_run (list affected files without writing), path_include/exclude.
OUTPUT (live): { command:'init', modified: [...] } — files touched.
OUTPUT (dry_run): { dry_run: true, files_to_modify, file_count }.
ALT: md_scan first to see what would change.
COST: Free but DESTRUCTIVE — modifies .md files in place. Use dry_run first.`,
    {
      paths: z.array(z.string().min(1)).optional().describe("Files or directories (default: current directory)"),
      confirm: z.boolean().optional().describe("Required true to actually run. Default false rejects with destructive warning."),
      dry_run: z.boolean().optional().describe("If true, return list of files that would be modified without writing."),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ paths, confirm, dry_run, path_include, path_exclude }) => {
      if (dry_run) {
        const est = await estimateInitScope(paths, path_include, path_exclude);
        return {
          dry_run: true,
          ...est,
          hint: est.file_count === 0
            ? "No files need init — frontmatter present everywhere."
            : `Pass confirm:true to add frontmatter template to ${est.file_count} files.`
        };
      }
      if (!confirm) {
        return {
          error: "confirm_required",
          reason: "Destructive operation: modifies .md files in place.",
          hint: "Pass dry_run:true to see affected files, then confirm:true to proceed."
        };
      }
      const args = ["init", "--json"];
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      if (Array.isArray(paths) && paths.length > 0) {
        args.push(...paths);
      }
      return await runGraph(args, { timeoutMs: 60_000 });
    },
    { readOnlyHint: false, destructiveHint: true, idempotentHint: true }
  );

  registerTool(
    "md_strip",
    `Remove legacy graph fields (and optionally related-docs body sections). MUTATING.

WHEN: Schema migration cleanup, deprecation of old fields, hygiene pass after rename.
WHY OURS: One pass over frontmatter — removes only fields flagged by scan as legacy/unknown. Bash sed risks YAML corruption.
INPUT: paths, confirm (required true), dry_run, also_related_section, path_include/exclude.
OUTPUT (live): { command:'strip', modified: [...] }.
OUTPUT (dry_run): { dry_run: true, files_to_modify, file_count, also_related_section }.
ALT: md_scan to see what's flagged. Manual edit for surgical removal.
COST: Free but DESTRUCTIVE — modifies .md files. Use dry_run first.`,
    {
      paths: z.array(z.string().min(1)).optional().describe("Files or directories (default: current directory)"),
      confirm: z.boolean().optional().describe("Required true to actually run."),
      dry_run: z.boolean().optional().describe("If true, return list of files that would be modified."),
      also_related_section: z.boolean().optional().describe("Also remove '## Связанные документы' / '## Related documents' sections from body."),
      path_include: z.array(z.string().min(1)).optional(),
      path_exclude: z.array(z.string().min(1)).optional()
    },
    async ({ paths, confirm, dry_run, also_related_section, path_include, path_exclude }) => {
      if (dry_run) {
        const est = await estimateStripScope(paths, also_related_section, path_include, path_exclude);
        return {
          dry_run: true,
          ...est,
          hint: est.file_count === 0
            ? "No legacy fields found — nothing to strip."
            : `Pass confirm:true to strip legacy fields from ${est.file_count} files.`
        };
      }
      if (!confirm) {
        return {
          error: "confirm_required",
          reason: "Destructive operation: removes frontmatter fields and optionally body sections.",
          hint: "Pass dry_run:true to see affected files, then confirm:true to proceed."
        };
      }
      const args = ["strip", "--json"];
      if (also_related_section) args.push("--also-related-section");
      pushRepeated(args, "--path-include", path_include);
      pushRepeated(args, "--path-exclude", path_exclude);
      if (Array.isArray(paths) && paths.length > 0) {
        args.push(...paths);
      }
      return await runGraph(args, { timeoutMs: 60_000 });
    },
    { readOnlyHint: false, destructiveHint: true, idempotentHint: true }
  );
}

export { runGraph };
