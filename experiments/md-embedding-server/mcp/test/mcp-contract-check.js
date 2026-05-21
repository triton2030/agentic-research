#!/usr/bin/env node
// Contract check for md-mcp 0.6.1: tool names, annotations, text-only results,
// guarded errors, and subprocess safety behavior.

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { mkdir, mkdtemp, readFile, realpath, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { spawnPython } from "../src/subprocess.js";

const here = dirname(fileURLToPath(import.meta.url));
const SERVER = resolve(here, "..", "src", "server.js");
const BAD_PATH = `/tmp/md-mcp-contract-missing-${process.pid}`;

const EXPECTED_TOOLS = [
  "md_audit",
  "md_changed",
  "md_check",
  "md_cycles",
  "md_deps",
  "md_edit_context",
  "md_extract",
  "md_health",
  "md_impact",
  "md_importance",
  "md_index",
  "md_init",
  "md_ls",
  "md_orient",
  "md_overlaps",
  "md_ping",
  "md_preflight",
  "md_profile_sections",
  "md_query_by_type",
  "md_read_related",
  "md_refactor_candidates",
  "md_repeated_concepts",
  "md_scan",
  "md_search",
  "md_section_blast_radius",
  "md_status",
  "md_strip",
  "md_toc"
].sort();

const EXPECTED_ANNOTATIONS = {
  md_audit: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
  md_changed: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_check: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_cycles: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_deps: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_edit_context: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
  md_extract: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_health: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_impact: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_importance: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_index: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
  md_init: { readOnlyHint: false, destructiveHint: true, idempotentHint: true, openWorldHint: false },
  md_ls: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_orient: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_overlaps: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
  md_ping: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_preflight: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_profile_sections: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
  md_query_by_type: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
  md_read_related: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_refactor_candidates: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
  md_repeated_concepts: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
  md_scan: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_search: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
  md_section_blast_radius: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
  md_status: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  md_strip: { readOnlyHint: false, destructiveHint: true, idempotentHint: true, openWorldHint: false },
  md_toc: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
};

let passed = 0;
let failed = 0;

function record(name, ok, detail = "") {
  if (ok) passed++;
  else failed++;
  const tag = ok ? "PASS" : "FAIL";
  console.log(`  [${tag}] ${name}${detail ? " - " + detail : ""}`);
}

function sameJson(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function sameAnnotations(actual, expected) {
  const keys = ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"];
  return (
    actual &&
    keys.every((key) => actual[key] === expected[key]) &&
    Object.keys(actual).every((key) => keys.includes(key))
  );
}

function isTextOnlyResult(result) {
  return (
    Array.isArray(result.content) &&
    result.content.length === 1 &&
    result.content[0]?.type === "text" &&
    typeof result.content[0]?.text === "string" &&
    !("structuredContent" in result)
  );
}

function processAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function sleep(ms) {
  return new Promise((resolveSleep) => setTimeout(resolveSleep, ms));
}

async function checkMcpContract() {
  const transport = new StdioClientTransport({ command: "node", args: [SERVER] });
  const client = new Client({ name: "md-mcp-contract-check", version: "0.0.1" });
  await client.connect(transport);

  try {
    const list = await client.listTools();
    const names = list.tools.map((tool) => tool.name).sort();
    record("listTools names", names.length === 28 && sameJson(names, EXPECTED_TOOLS), `${names.length} tools`);

    const toolsByName = new Map(list.tools.map((tool) => [tool.name, tool]));
    let annotationsOk = true;
    let schemasOk = true;
    for (const name of EXPECTED_TOOLS) {
      const tool = toolsByName.get(name);
      if (!tool || !sameAnnotations(tool.annotations, EXPECTED_ANNOTATIONS[name])) {
        annotationsOk = false;
        break;
      }
      if ("outputSchema" in tool) {
        schemasOk = false;
        break;
      }
    }
    record("annotation allowlist", annotationsOk);
    record("no outputSchema", schemasOk);

    const ping = await client.callTool({ name: "md_ping", arguments: {} });
    const pingPayload = JSON.parse(ping.content[0].text);
    record("md_ping version", pingPayload.name === "md-mcp" && pingPayload.version === "0.6.1");
    record("text-only result shape", isTextOnlyResult(ping));

    const badPath = await client.callTool({
      name: "md_status",
      arguments: { corpus: BAD_PATH }
    });
    record("bad-path isError", badPath.isError === true && isTextOnlyResult(badPath));
  } finally {
    await client.close();
  }
}

async function callJson(client, name, args) {
  const result = await client.callTool({ name, arguments: args });
  if (result.isError) {
    throw new Error(`${name} returned isError: ${result.content?.[0]?.text || ""}`);
  }
  return JSON.parse(result.content[0].text);
}

async function checkGraphMutatorParity() {
  const transport = new StdioClientTransport({ command: "node", args: [SERVER] });
  const client = new Client({ name: "md-mcp-contract-mutators", version: "0.0.1" });
  const root = await realpath(await mkdtemp(join(tmpdir(), "md-mcp-contract-")));
  await client.connect(transport);

  try {
    const includeDir = join(root, "include");
    const excludeDir = join(root, "exclude");
    await mkdir(includeDir, { recursive: true });
    await mkdir(excludeDir, { recursive: true });
    const includePattern = `${root}/include/*.md`;

    const missing = join(includeDir, "missing.md");
    const excluded = join(excludeDir, "excluded.md");
    await writeFile(missing, "# Missing\n\nBody.\n", "utf8");
    await writeFile(excluded, "# Excluded\n\nBody.\n", "utf8");

    const initDry = await callJson(client, "md_init", {
      paths: [root],
      path_include: [includePattern],
      dry_run: true
    });
    const initLive = await callJson(client, "md_init", {
      paths: [root],
      path_include: [includePattern],
      confirm: true
    });
    const missingText = await readFile(missing, "utf8");
    const excludedText = await readFile(excluded, "utf8");
    record(
      "md_init dry_run/live parity",
      initDry.file_count === 1 &&
        initLive.parse_failed !== true &&
        initLive.changed === 1 &&
        initDry.file_count === initLive.changed &&
        missingText.startsWith("---\n") &&
        !excludedText.startsWith("---\n")
    );

    const legacy = join(includeDir, "legacy.md");
    await writeFile(
      legacy,
      [
        "---",
        "description: Keep me",
        "read-before-edit: []",
        "edit-after-edit: []",
        "owner: old",
        "foo: bar",
        "---",
        "# Legacy",
        "",
        "Keep this body.",
        "",
        "## Related documents",
        "",
        "- [[old.md]]",
        "",
        "## Next",
        "",
        "Keep next section.",
        ""
      ].join("\n"),
      "utf8"
    );

    const stripDry = await callJson(client, "md_strip", {
      paths: [root],
      path_include: [includePattern],
      also_related_section: true,
      dry_run: true
    });
    const stripLive = await callJson(client, "md_strip", {
      paths: [root],
      path_include: [includePattern],
      also_related_section: true,
      confirm: true
    });
    const stripped = await readFile(legacy, "utf8");
    record(
      "md_strip dry_run/live parity",
      stripDry.file_count === 1 &&
        stripLive.parse_failed !== true &&
        stripLive.changed === 1 &&
        stripDry.file_count === stripLive.changed &&
        stripped.includes("description: Keep me") &&
        stripped.includes("read-before-edit: []") &&
        stripped.includes("edit-after-edit: []") &&
        stripped.includes("Keep this body.") &&
        stripped.includes("## Next") &&
        !stripped.includes("owner: old") &&
        !stripped.includes("foo: bar") &&
        !stripped.includes("## Related documents")
    );
  } finally {
    await client.close();
    await rm(root, { recursive: true, force: true });
  }
}

async function checkSubprocessTimeoutGroupKill() {
  const script = `
    const { spawn } = require("node:child_process");
    const child = spawn(process.execPath, ["-e", "setInterval(() => {}, 1000)"], {
      stdio: ["ignore", "ignore", "ignore"]
    });
    console.log(child.pid);
    setInterval(() => {}, 1000);
  `;

  try {
    await spawnPython(process.execPath, ["-e", script], {
      timeoutMs: 1000,
      maxStdoutBytes: 4096,
      maxStderrBytes: 4096
    });
    record("subprocess timeout group kill", false, "process completed unexpectedly");
  } catch (error) {
    const pid = Number(String(error.stdout || "").match(/\d+/)?.[0]);
    await sleep(300);
    const childKilled = process.platform === "win32" || (Number.isInteger(pid) && !processAlive(pid));
    record(
      "subprocess timeout group kill",
      error.kind === "timeout" && childKilled,
      process.platform === "win32" ? "group kill skipped on win32" : `child pid ${pid || "missing"}`
    );
  }
}

async function checkSubprocessOutputCap() {
  const result = await spawnPython(
    process.execPath,
    ["-e", "process.stdout.write('x'.repeat(2048)); process.stderr.write('e'.repeat(1024));"],
    {
      timeoutMs: 5000,
      maxStdoutBytes: 128,
      maxStderrBytes: 64
    }
  );

  record(
    "subprocess output cap",
    result.truncated === true &&
      result.stdout_dropped_bytes === 1920 &&
      result.stderr_dropped_bytes === 960 &&
      result.stdout.includes("[TRUNCATED:") &&
      result.stderr.includes("[TRUNCATED:")
  );
}

console.log(`md-mcp contract check - server: ${SERVER}`);
await checkMcpContract();
await checkGraphMutatorParity();
await checkSubprocessTimeoutGroupKill();
await checkSubprocessOutputCap();

console.log("");
console.log(`md-mcp contract check: ${passed} passed, ${failed} failed`);
process.exit(failed === 0 ? 0 : 1);
