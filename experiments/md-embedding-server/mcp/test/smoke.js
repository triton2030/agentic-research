#!/usr/bin/env node
// Smoke test for md-mcp: spawns the server, calls every tool once, asserts shape.
// Run: `npm run smoke` (or `node test/smoke.js`).
// Uses the local agentic-research corpus as fixture — relies on a warm index
// at `<repo>/knowledge/.md-navigator/index.sqlite`.

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { dirname, resolve } from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const SERVER = resolve(here, "..", "src", "server.js");

const REPO = "/Users/triton/Documents/GitHub/agentic-research";
const KNOWLEDGE = resolve(REPO, "knowledge");
const AGENTS = resolve(KNOWLEDGE, "agents");
const FILE = resolve(AGENTS, "evaluation.md");

if (!existsSync(KNOWLEDGE) || !existsSync(FILE)) {
  console.error("Smoke fixture missing: expected agentic-research knowledge folder at " + KNOWLEDGE);
  process.exit(2);
}

let passed = 0;
let failed = 0;
const results = [];

function record(name, ok, detail) {
  if (ok) passed++;
  else failed++;
  results.push({ name, ok, detail });
  const tag = ok ? "PASS" : "FAIL";
  console.log(`  [${tag}] ${name}${detail ? " — " + detail : ""}`);
}

async function expect(name, args, predicate) {
  return await expectTool(name, name, args, predicate);
}

async function expectTool(label, name, args, predicate) {
  try {
    const r = await client.callTool({ name, arguments: args });
    if (r.isError) {
      record(label, false, `tool returned isError: ${r.content[0].text.slice(0, 120)}`);
      return null;
    }
    const text = r.content[0].text;
    let payload;
    try {
      payload = JSON.parse(text);
    } catch {
      payload = { text };
    }
    const ok = predicate(payload);
    if (ok === true) {
      record(label, true, `${text.length}B`);
    } else if (typeof ok === "string") {
      record(label, false, ok);
    } else {
      record(label, false, "predicate returned false");
    }
    return payload;
  } catch (e) {
    record(label, false, `threw: ${e.message}`);
    return null;
  }
}

const transport = new StdioClientTransport({ command: "node", args: [SERVER] });
const client = new Client({ name: "md-mcp-smoke", version: "0.0.1" });

console.log(`md-mcp smoke — server: ${SERVER}`);
await client.connect(transport);

const list = await client.listTools();
record(
  "listTools",
  list.tools.length >= 17,
  `${list.tools.length} tools`
);

await expect("md_ping", {}, (p) => Boolean(p.name === "md-mcp" && p.navigator_script && p.graph_script));

await expect("md_status", { corpus: KNOWLEDGE }, (p) =>
  typeof p.text === "string" && p.text.includes("Corpus:") ? true : "missing Corpus: line"
);

await expect("md_ls", { path: AGENTS }, (p) =>
  Array.isArray(p.files) && p.files.length >= 1 ? true : "no files in map"
);

await expectTool("md_ls link counts", "md_ls", { path: KNOWLEDGE, with_link_counts: true }, (p) =>
  Array.isArray(p.files) && p.files.some((f) => Number.isInteger(f.in_degree) && Number.isInteger(f.out_degree))
    ? true
    : "missing in_degree/out_degree"
);

await expect("md_toc", { path: AGENTS, max_heading_level: 3 }, (p) =>
  Array.isArray(p.files) && p.files.some((f) => f.headings && f.headings.length > 0)
    ? true
    : "no headings"
);

const searchResult = await expect(
  "md_search",
  { corpus: KNOWLEDGE, query: "tool design boundaries", limit: 3 },
  (p) => (Array.isArray(p.results) && p.results.length >= 1) || p.error === "index_warmup_required"
);

// md_cat now requires map_data (path-mode removed in 0.3.0; use built-in Read for that)
const tocForCat = await client.callTool({ name: "md_toc", arguments: { path: AGENTS } });
const tocData = JSON.parse(tocForCat.content[0].text);
const firstHeadingId = tocData.files?.[0]?.headings?.[0]?.id;
if (firstHeadingId) {
  await expect("md_cat", { map_data: tocData, headings: firstHeadingId }, (p) =>
    Array.isArray(p.headings) && p.headings.length > 0 ? true : "no extracted heading"
  );
}

await expect(
  "md_read_related",
  { paths: [FILE], scan: KNOWLEDGE, token_budget: 1500 },
  (p) => (Array.isArray(p.anchors) && p.anchors.length >= 1) || "no anchors"
);

await expectTool(
  "md_read_related preview",
  "md_read_related",
  { paths: [FILE], scan: KNOWLEDGE, mode: "preview", token_budget: 1500 },
  (p) => {
    if (!Array.isArray(p.items) || p.items.length < 1) return "no related items";
    return p.items.every((item) => item.content === undefined) ? true : "preview leaked content";
  }
);

await expect("md_importance", { corpus: KNOWLEDGE, top: 5 }, (p) =>
  Array.isArray(p.files) && p.files.length >= 1 && p.files[0].pagerank !== undefined
    ? true
    : "missing importance files"
);

await expect("md_orient", { corpus: KNOWLEDGE, top: 5 }, (p) =>
  p.workflow === "md_orient" && p.status && p.files && p.importance ? true : "missing orient blocks"
);

await expectTool("md_edit_context preview", "md_edit_context", { path: FILE, scan: KNOWLEDGE, mode: "preview" }, (p) =>
  p.workflow === "md_edit_context" && p.mode === "preview" && p.preflight && p.related
    ? true
    : "missing edit context preview blocks"
);

await expectTool("md_edit_context full", "md_edit_context", { path: FILE, scan: KNOWLEDGE, mode: "full" }, (p) =>
  p.workflow === "md_edit_context" && p.mode === "full" && p.preflight && p.related
    ? true
    : "missing edit context full blocks"
);

await expectTool("md_edit_context strict", "md_edit_context", { path: FILE, scan: KNOWLEDGE, mode: "strict" }, (p) =>
  p.workflow === "md_edit_context" && p.mode === "strict" && p.blockers && p.blockers.has_blockers === false
    ? true
    : "missing or over-eager edit context strict blockers"
);

await expect("md_query_by_type", { corpus: KNOWLEDGE, types: ["definition", "rule"], limit: 5 }, (p) =>
  Array.isArray(p.sections) ? true : "missing typed sections"
);

await expect("md_refactor_candidates", { corpus: KNOWLEDGE, top: 3 }, (p) =>
  Array.isArray(p.proposals) && p.no_automation === true ? true : "missing proposal list"
);

const map = await expect("md_ls", { path: AGENTS }, () => true);
if (map && Array.isArray(map.files) && map.files.length > 0) {
  await expect(
    "md_pick",
    { map_data: map, files: "1", extract: false },
    (p) => Array.isArray(p.files) && p.files.length === 1 ? true : "wrong file count"
  );
}

// md_audit is slow — only run when SMOKE_AUDIT=1
if (process.env.SMOKE_AUDIT === "1") {
  await expect("md_audit", { corpus: AGENTS }, (p) =>
    p.classes || p.findings || p.health_score !== undefined ? true : "missing audit fields"
  );
} else {
  console.log("  [SKIP] md_audit — set SMOKE_AUDIT=1 to run (~minutes)");
}

await expect("md_preflight", { path: FILE, scan: KNOWLEDGE }, (p) =>
  p.command === "preflight" ? true : "wrong command field"
);

await expect("md_impact", { path: FILE, scan: KNOWLEDGE }, (p) =>
  p.command === "impact" ? true : "wrong command field"
);

await expect("md_deps", { path: FILE, scan: KNOWLEDGE }, (p) =>
  p.command === "deps" ? true : "wrong command field"
);

await expect("md_health", { paths: [AGENTS] }, (p) =>
  p.command === "health" && p.description_coverage ? true : "missing health fields"
);

await expect(
  "md_section_blast_radius",
  {
    path: FILE,
    corpus: KNOWLEDGE,
    query: "trajectory evaluation observable criteria",
    limit: 3
  },
  (p) => p.graph && p.semantic ? true : "missing graph or semantic block"
);

await client.close();

console.log("");
console.log(`md-mcp smoke: ${passed} passed, ${failed} failed`);
process.exit(failed === 0 ? 0 : 1);
