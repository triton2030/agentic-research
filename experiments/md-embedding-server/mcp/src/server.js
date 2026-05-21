#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { registerNavigatorTools } from "./tools/navigator-tools.js";
import { registerGraphTools } from "./tools/graph-tools.js";
import { registerHybridTools } from "./tools/hybrid-tools.js";
import { registerCompositeTools } from "./tools/composite-tools.js";
import { wrap as wrapEnvelope, resetTurn, quickCorpusState } from "./envelope.js";

function corpusRootFromArgs(args) {
  if (!args || typeof args !== "object") return null;
  return typeof args.corpus === "string"
    ? args.corpus
    : typeof args.scan === "string"
      ? args.scan
      : null;
}

const SERVER_VERSION = "0.6.1";

const server = new McpServer({
  name: "md-mcp",
  version: SERVER_VERSION
});

function exitOnClosedStdio() {
  let exiting = false;
  const exit = () => {
    if (exiting) return;
    exiting = true;
    setImmediate(() => process.exit(0));
  };
  process.stdin.once("end", exit);
  process.stdin.once("close", exit);
}

function textResult(value, options = {}) {
  return {
    content: [
      {
        type: "text",
        text: typeof value === "string" ? value : JSON.stringify(value, null, 2)
      }
    ],
    ...options
  };
}

/**
 * Register a tool with optional MCP annotations.
 *
 * annotations is the MCP "tool annotations" hint set (spec 2025-06-18):
 *   - readOnlyHint: tool does not mutate persistent state
 *   - destructiveHint: tool can destroy data (default false on read-only tools)
 *   - openWorldHint: tool interacts with external systems (network, APIs)
 *   - idempotentHint: repeated calls produce same effect
 *
 * Backwards-compatible signature: registerTool(name, description, inputSchema, handler)
 * still works — annotations defaults to undefined.
 */
const DEFAULT_ANNOTATIONS = {
  readOnlyHint: true,
  destructiveHint: false,
  openWorldHint: false,
  idempotentHint: true
};

const TOOL_ANNOTATION_ALLOWLIST = {
  md_audit: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: true },
  md_changed: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_check: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_corpus_scan: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_cycles: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_deps: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_edit_context: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: true },
  md_extract: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_health: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_impact: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_importance: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_index: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: false },
  md_init: { readOnlyHint: false, destructiveHint: true, openWorldHint: false, idempotentHint: true },
  md_ls: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_orient: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_overlaps: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: true },
  md_ping: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_preflight: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_profile_sections: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: false },
  md_query_by_type: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: true },
  md_read_related: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_refactor_candidates: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: true },
  md_repeated_concepts: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: true },
  md_scan: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_search: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: true },
  md_section_blast_radius: { readOnlyHint: false, destructiveHint: false, openWorldHint: true, idempotentHint: true },
  md_status: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
  md_strip: { readOnlyHint: false, destructiveHint: true, openWorldHint: false, idempotentHint: true },
  md_toc: { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true }
};

export function registerTool(name, description, inputSchema, handler, annotations) {
  const allowlistedAnnotations = TOOL_ANNOTATION_ALLOWLIST[name];
  if (!allowlistedAnnotations) {
    throw new Error(`Missing MCP annotation allowlist entry for tool: ${name}`);
  }
  const config = {
    title: name,
    description,
    inputSchema,
    annotations: { ...DEFAULT_ANNOTATIONS, ...(annotations || {}), ...allowlistedAnnotations }
  };
  server.registerTool(
    name,
    config,
    async (args) => {
      resetTurn();
      // Fire corpus_state probe in parallel with the actual handler. Cached
      // (30s TTL) so back-to-back tools on the same corpus pay once.
      const corpusRoot = corpusRootFromArgs(args);
      const corpusStatePromise = corpusRoot
        ? quickCorpusState(corpusRoot).catch(() => null)
        : Promise.resolve(null);
      try {
        const result = await handler(args);
        const corpusState = await corpusStatePromise;
        return textResult(wrapEnvelope(result, { toolName: name, args, corpusState }));
      } catch (error) {
        const errResult = {
          error: error instanceof Error ? error.message : String(error)
        };
        const corpusState = await corpusStatePromise;
        return textResult(
          wrapEnvelope(errResult, { toolName: name, args, corpusState }),
          { isError: true }
        );
      }
    }
  );
}

registerTool(
  "md_ping",
  `Health check: server name, version, resolved script paths. No backend call.

WHEN: md_* tools throw 'spawn failed', debugging server install, verifying MCP wiring after restart.
WHY OURS: Confirms server alive + script resolution before deeper tools fail with cryptic errors.
INPUT: none.
OUTPUT: { name, version, navigator_script, navigator_error, graph_script, graph_error }.
ALT: claude mcp list / Codex /mcp to verify connection. md_status to check corpus state.
COST: Free.`,
  {},
  async () => {
    const { resolveNavigatorScript, resolveGraphScript } = await import("./paths.js");
    let navigator = null;
    let graph = null;
    let navigatorError = null;
    let graphError = null;
    try { navigator = resolveNavigatorScript(); } catch (e) { navigatorError = e.message; }
    try { graph = resolveGraphScript(); } catch (e) { graphError = e.message; }
    return {
      name: "md-mcp",
      version: SERVER_VERSION,
      navigator_script: navigator,
      navigator_error: navigatorError,
      graph_script: graph,
      graph_error: graphError
    };
  },
  { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true }
);

registerNavigatorTools(registerTool);
registerGraphTools(registerTool);
registerHybridTools(registerTool);
registerCompositeTools(registerTool);

const transport = new StdioServerTransport();
exitOnClosedStdio();
await server.connect(transport);
