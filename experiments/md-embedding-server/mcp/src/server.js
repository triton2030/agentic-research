#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { registerNavigatorTools } from "./tools/navigator-tools.js";
import { registerGraphTools } from "./tools/graph-tools.js";
import { registerHybridTools } from "./tools/hybrid-tools.js";
import { registerCompositeTools } from "./tools/composite-tools.js";

const server = new McpServer({
  name: "md-mcp",
  version: "0.4.0"
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

export function registerTool(name, description, inputSchema, handler) {
  server.registerTool(
    name,
    {
      title: name,
      description,
      inputSchema
    },
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
  "Health check: server name, version, and resolved script paths. No backend call. Use when md_* tools throw `spawn failed` to verify script resolution.",
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
      version: "0.4.0",
      navigator_script: navigator,
      navigator_error: navigatorError,
      graph_script: graph,
      graph_error: graphError
    };
  }
);

registerNavigatorTools(registerTool);
registerGraphTools(registerTool);
registerHybridTools(registerTool);
registerCompositeTools(registerTool);

const transport = new StdioServerTransport();
exitOnClosedStdio();
await server.connect(transport);
