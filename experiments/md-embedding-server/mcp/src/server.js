#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { registerNavigatorTools } from "./tools/navigator-tools.js";
import { registerGraphTools } from "./tools/graph-tools.js";
import { registerHybridTools } from "./tools/hybrid-tools.js";
import { registerCompositeTools } from "./tools/composite-tools.js";

const server = new McpServer({
  name: "md-mcp",
  version: "0.6.0"
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
// Safe default annotations for our tool surface. Almost everything is
// read-only and stays inside the corpus / SQLite index. Tools that hit
// OpenRouter (semantic search, embeddings, profile classifier) override
// with openWorldHint=true. Tools that write to .md-navigator/ (md_audit)
// override with readOnlyHint=false.
const DEFAULT_ANNOTATIONS = {
  readOnlyHint: true,
  destructiveHint: false,
  openWorldHint: false,
  idempotentHint: true
};

export function registerTool(name, description, inputSchema, handler, annotations) {
  const config = {
    title: name,
    description,
    inputSchema,
    annotations: { ...DEFAULT_ANNOTATIONS, ...(annotations || {}) }
  };
  server.registerTool(
    name,
    config,
    async (args) => {
      try {
        return textResult(await handler(args));
      } catch (error) {
        return textResult(
          {
            error: error instanceof Error ? error.message : String(error)
          },
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
      version: "0.6.0",
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
