#!/usr/bin/env node
import { pathToFileURL } from "node:url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { askClaude, compactClaudeAskError } from "./claude-ask.js";
import { claudeAskInputSchema } from "./claude-policy.js";
import { claudeSessionsInputSchema, createClaudeSessionsReader } from "./claude-sessions.js";
import {
  claudeObserveInputSchema,
  claudeSessionInputSchema,
  createClaudeSessionAdapter
} from "./claude-session.js";

const askResultSchema = {
  text: z.string(),
  session_id: z.string().uuid(),
  requested_model: z.literal("opus").nullable(),
  requested_effort: z.enum(["xhigh", "max"]).nullable(),
  resolved_model: z.string().min(1),
  duration_ms: z.number().int().nonnegative(),
  warnings: z.array(z.string())
};

const observationFields = {
  session_id: z.string().uuid(),
  state: z.enum([
    "starting",
    "thinking",
    "tool",
    "subagent",
    "retrying",
    "steering",
    "requires_action",
    "closing",
    "idle",
    "failed",
    "timed_out",
    "closed"
  ]),
  cursor: z.number().int().nonnegative(),
  changed: z.boolean(),
  last_activity_age_ms: z.number().int().nonnegative(),
  direction: z.string(),
  active_tool: z.string().nullable(),
  thinking_tokens: z.number().int().nonnegative().nullable(),
  background_tasks: z.number().int().nonnegative(),
  possibly_stalled: z.boolean(),
  requested_model: z.literal("opus").nullable(),
  requested_effort: z.enum(["xhigh", "max"]).nullable(),
  resolved_model: z.string().nullable(),
  terminal: z.record(z.string(), z.unknown()).nullable(),
  warnings: z.array(z.string()),
  events: z.array(z.object({
    cursor: z.number().int().nonnegative(),
    at_ms: z.number().int().nonnegative(),
    type: z.string(),
    summary: z.string()
  })),
  messages: z.array(z.object({
    cursor: z.number().int().nonnegative(),
    role: z.enum(["user", "assistant"]),
    text: z.string()
  })),
  diagnostic: z.record(z.string(), z.unknown()).optional()
};

const nativeSessionFields = {
  session_id: z.string().uuid(),
  name: z.string().nullable(),
  kind: z.string(),
  cwd: z.string(),
  started_at_ms: z.number().int().nonnegative().nullable(),
  title: z.string().nullable(),
  git_branch: z.string().nullable()
};

const activeSessionSchema = z.object(nativeSessionFields);

const sessionInfoSchema = z.object(nativeSessionFields);

const visibleMessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  text: z.string()
});

function success(result) {
  return {
    content: [{ type: "text", text: "Claude bridge returned a structured result." }],
    structuredContent: result
  };
}

function failure(error) {
  const compact = compactClaudeAskError(error);
  return { isError: true, content: [{ type: "text", text: JSON.stringify({ error: compact }) }] };
}

function combinedSignal(...signals) {
  const present = signals.filter(Boolean);
  if (!present.length) return undefined;
  return present.length === 1 ? present[0] : AbortSignal.any(present);
}

/** Create the blocking, transient-session, and read-only discovery MCP boundary. */
export function createClaudeAskServer(
  ask = askClaude,
  sessionAdapter = createClaudeSessionAdapter(),
  sessionsReader = createClaudeSessionsReader()
) {
  const server = new McpServer({ name: "claude-advisor", version: "2.0.0" });
  const shutdownController = new AbortController();
  const activeRequests = new Set();

  async function tracked(callback) {
    const pending = Promise.resolve().then(callback);
    activeRequests.add(pending);
    try {
      return success(await pending);
    } catch (error) {
      return failure(error);
    } finally {
      activeRequests.delete(pending);
    }
  }

  server.registerTool(
    "claude_ask",
    {
      title: "Ask Claude",
      description:
        "Ask native Claude Opus 5 for blocking independent advice or review through the logged-in Claude.ai subscription. " +
        "Claude retains native local tools, skills, hooks, settings and MCP integrations; instruct it not to modify state. " +
        "Returns one bounded answer and native session_id.",
      inputSchema: claudeAskInputSchema,
      outputSchema: askResultSchema,
      annotations: {
        readOnlyHint: false,
        destructiveHint: true,
        idempotentHint: false,
        openWorldHint: true
      }
    },
    (args, extra) => tracked(() => ask(args, combinedSignal(extra.signal, shutdownController.signal)))
  );

  server.registerTool(
    "claude_session",
    {
      title: "Control Claude Session",
      description:
        "Open, continue, steer, or stop a transient native Claude advisor process. " +
        "Use open_fresh/open_resume with an initial prompt, send only while idle, and steer only while a turn is active. " +
        "The returned native session_id remains resumable after this process-local lease disappears.",
      inputSchema: claudeSessionInputSchema,
      outputSchema: {
        accepted_op: z.enum(["open_fresh", "open_resume", "send", "steer", "stop"]),
        ...observationFields
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: true,
        idempotentHint: false,
        openWorldHint: true
      }
    },
    (args, extra) => tracked(() => sessionAdapter.command(
      args,
      combinedSignal(extra.signal, shutdownController.signal)
    ))
  );

  server.registerTool(
    "claude_observe",
    {
      title: "Observe Claude Session",
      description:
        "Pull one bounded snapshot for an active native Claude session. Summary is context-cheap; activity, conversation, " +
        "and diagnostic detail are explicit bounded peeks. Never returns hidden reasoning, raw tool I/O, or an event stream.",
      inputSchema: claudeObserveInputSchema,
      outputSchema: observationFields,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false
      }
    },
    (args, extra) => tracked(() => sessionAdapter.observe(
      args,
      combinedSignal(extra.signal, shutdownController.signal)
    ))
  );

  server.registerTool(
    "claude_sessions",
    {
      title: "Read Active Claude Sessions",
      description:
        "List active local Claude Code or Claude Desktop sessions, or read a bounded visible user/assistant conversation " +
        "from one active native session_id. Never returns hidden reasoning, system messages, tool I/O, hooks, or subagent transcripts.",
      inputSchema: claudeSessionsInputSchema,
      outputSchema: {
        op: z.enum(["list_active", "read"]),
        sessions: z.array(activeSessionSchema),
        session: sessionInfoSchema.nullable(),
        messages: z.array(visibleMessageSchema),
        warnings: z.array(z.string())
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false
      }
    },
    (args, extra) => tracked(() => sessionsReader.read(
      args,
      combinedSignal(extra.signal, shutdownController.signal)
    ))
  );

  return {
    server,
    async shutdown() {
      shutdownController.abort();
      await sessionAdapter.shutdown();
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
