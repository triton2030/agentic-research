#!/usr/bin/env node
import { pathToFileURL } from "node:url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { askClaude, compactClaudeAskError } from "./claude-ask.js";
import { claudeAskInputSchema } from "./claude-policy.js";

const resultSchema = {
  text: z.string(),
  session_id: z.string().uuid(),
  requested_model: z.enum(["opus", "fable"]).nullable(),
  resolved_model: z.string().min(1),
  duration_ms: z.number().int().nonnegative(),
  warnings: z.array(z.string())
};

function success(result) {
  return {
    content: [{ type: "text", text: JSON.stringify(result) }],
    structuredContent: result
  };
}

function failure(error) {
  const compact = compactClaudeAskError(error);
  return { isError: true, content: [{ type: "text", text: JSON.stringify({ error: compact }) }] };
}

/** Create the one-tool MCP boundary around the deep askClaude interface. */
export function createClaudeAskServer(ask = askClaude) {
  const server = new McpServer({ name: "claude-ask", version: "1.0.0" });
  const shutdownController = new AbortController();
  const activeRequests = new Set();

  server.registerTool(
    "claude_ask",
    {
      title: "Ask Claude",
      description:
        "Ask native Claude Opus 5 or Fable 5 for a blocking independent review through the logged-in Claude.ai subscription. " +
        "Claude retains native local tools, skills, hooks, settings and MCP integrations; instruct it not to modify state. " +
        "Returns one bounded answer and native session_id.",
      inputSchema: claudeAskInputSchema,
      outputSchema: resultSchema,
      annotations: {
        readOnlyHint: false,
        destructiveHint: true,
        idempotentHint: false,
        openWorldHint: true
      }
    },
    async (args, extra) => {
      const signals = [extra.signal, shutdownController.signal].filter(Boolean);
      const signal = signals.length === 1 ? signals[0] : AbortSignal.any(signals);
      const pending = ask(args, signal);
      activeRequests.add(pending);
      try {
        return success(await pending);
      } catch (error) {
        return failure(error);
      } finally {
        activeRequests.delete(pending);
      }
    }
  );

  return {
    server,
    async shutdown() {
      shutdownController.abort();
      await Promise.allSettled([...activeRequests]);
      await server.close().catch(() => {});
    }
  };
}

async function main() {
  const instance = createClaudeAskServer();
  let shuttingDown = false;
  const shutdown = async (exitCode) => {
    if (shuttingDown) return;
    shuttingDown = true;
    process.exitCode = exitCode;
    await instance.shutdown();
  };
  process.stdin.once("end", () => void shutdown(0));
  process.stdin.once("close", () => void shutdown(0));
  process.once("SIGTERM", () => void shutdown(0));
  process.once("SIGINT", () => void shutdown(130));
  await instance.server.connect(new StdioServerTransport());
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) await main();
