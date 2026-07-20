#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import {
  CLAUDE_WIRE_LIMITS,
  archiveThread,
  auditSkill,
  cleanupRuns,
  discoverSkills,
  doctor,
  killRun,
  listThreads,
  peekRun,
  profiles,
  relayRun,
  resultRun,
  sendThread,
  startRun,
  startThread,
  waitRun
} from "./runner.js";

const server = new McpServer({
  name: "claude-bridge-control",
  version: "0.3.0"
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

function registerTool(name, description, inputSchema, handler) {
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
  "claude_run",
  "Start a controlled Claude Code run. Returns a compact handle for later observe/wait/result/relay/kill; full evidence stays in the run log directory.",
  {
    prompt: z.string().min(1),
    profile: z.string().optional().default("advisor"),
    cwd: z.string().min(1),
    title: z.string().optional(),
    topic: z.string().optional(),
    model: z.string().optional(),
    effort: z.enum(["low", "medium", "high", "xhigh", "max"]).optional(),
    appendSystemPrompt: z.string().optional(),
    appendSubagentSystemPrompt: z.string().optional(),
    appendSystemPromptFile: z.string().optional(),
    systemPrompt: z.string().optional(),
    systemPromptFile: z.string().optional(),
    maxBudgetUsd: z.number().positive().optional(),
    maxTurns: z.number().int().positive().optional(),
    fallbackModel: z.string().optional(),
    sessionId: z.string().optional(),
    resume: z.union([z.string(), z.boolean()]).optional(),
    forkSession: z.boolean().optional(),
    name: z.string().optional(),
    noSessionPersistence: z.boolean().optional(),
    mcpConfig: z.union([z.string(), z.array(z.string())]).optional(),
    strictMcpConfig: z.boolean().optional(),
    permissionPromptTool: z.string().optional(),
    permissionMode: z.enum(["acceptEdits", "auto", "bypassPermissions", "default", "manual", "dontAsk", "plan"]).optional(),
    jsonSchema: z.union([z.string(), z.record(z.string(), z.unknown())]).optional(),
    agent: z.string().optional(),
    agents: z.union([z.string(), z.record(z.string(), z.unknown())]).optional(),
    settings: z.string().optional(),
    settingSources: z.union([z.string(), z.array(z.string())]).optional(),
    tools: z.union([z.string(), z.array(z.string())]).optional(),
    allowedTools: z.union([z.string(), z.array(z.string())]).optional(),
    disallowedTools: z.union([z.string(), z.array(z.string())]).optional(),
    addDir: z.union([z.string(), z.array(z.string())]).optional(),
    pluginDir: z.union([z.string(), z.array(z.string())]).optional(),
    pluginUrl: z.union([z.string(), z.array(z.string())]).optional(),
    brief: z.boolean().optional(),
    file: z.union([z.string(), z.array(z.string())]).optional(),
    inputFormat: z.enum(["text", "stream-json"]).optional(),
    replayUserMessages: z.boolean().optional(),
    forwardSubagentText: z.boolean().optional(),
    safeMode: z.boolean().optional(),
    writeFiles: z.union([z.string(), z.array(z.string())]).optional(),
    useTmux: z.boolean().optional(),
    tmuxMode: z.boolean().optional(),
    disableAutoMemory: z.boolean().optional(),
    mcpTimeout: z.number().int().positive().optional(),
    maxMcpOutputTokens: z.number().int().positive().optional()
  },
  (args) => startRun(args)
);

registerTool(
  "claude_thread_start",
  "Start a named cwd/Git-ref/addDir-bound Claude advisor conversation. Additional roots are inherited by every turn. Returns thread_id plus run_id; use claude_thread_send to continue it and claude_threads to recover it after restart or compaction.",
  {
    prompt: z.string().min(1),
    topic: z.string().min(1),
    cwd: z.string().min(1),
    profile: z.enum(["advisor", "fable-advisor"]).optional().default("advisor"),
    model: z.enum(["opus", "fable"]).optional(),
    effort: z.enum(["low", "medium", "high", "xhigh", "max"]).optional(),
    addDir: z.union([z.string(), z.array(z.string())]).optional(),
    mcpConfig: z.union([z.string(), z.array(z.string())]).optional(),
    allowedTools: z.union([z.string(), z.array(z.string())]).optional(),
    disallowedTools: z.union([z.string(), z.array(z.string())]).optional(),
    appendSystemPrompt: z.string().optional(),
    appendSubagentSystemPrompt: z.string().optional(),
    forwardSubagentText: z.boolean().optional(),
    useTmux: z.boolean().optional()
  },
  (args) => startThread(args)
);

registerTool(
  "claude_thread_send",
  "Continue one persistent Claude advisor conversation after validating its runtime-owned cwd/worktree/ref/addDir manifest and acquiring an atomic lease. The root manifest is inherited and cannot be changed. This is not an independent fresh opinion.",
  {
    thread_id: z.string().min(1),
    prompt: z.string().min(1),
    cwd: z.string().min(1),
    profile: z.enum(["advisor", "fable-advisor"]).optional(),
    appendSystemPrompt: z.string().optional(),
    appendSubagentSystemPrompt: z.string().optional(),
    forwardSubagentText: z.boolean().optional(),
    useTmux: z.boolean().optional()
  },
  (args) => sendThread(args)
);

registerTool(
  "claude_threads",
  "List bridge-owned persistent Claude conversations with topic, project, model, turns, last run, status, and resumability.",
  {
    cwd: z.string().optional(),
    includeArchived: z.boolean().optional().default(false)
  },
  (args) => listThreads(args)
);

registerTool(
  "claude_thread_archive",
  "Archive or unarchive a bridge conversation handle without deleting Claude's underlying session store.",
  {
    thread_id: z.string().min(1),
    archived: z.boolean().optional().default(true)
  },
  (args) => archiveThread(args)
);

registerTool(
  "claude_peek",
  "Return a bounded delta of model-visible Claude activity after a caller-owned cursor. It never returns the cumulative report or final answer.",
  {
    run_id: z.string().min(1),
    limit: z.number().int().positive().max(CLAUDE_WIRE_LIMITS.maxObserveEvents).optional(),
    cursor: z.number().int().nonnegative().optional()
  },
  (args) => peekRun(args.run_id, { limit: args.limit, cursor: args.cursor })
);

registerTool(
  "claude_observe",
  "Observe a long Claude run through the same bounded cursor delta as claude_peek. Use only when progress evidence is needed while one wait remains active.",
  {
    run_id: z.string().min(1),
    limit: z.number().int().positive().max(CLAUDE_WIRE_LIMITS.maxObserveEvents).optional(),
    cursor: z.number().int().nonnegative().optional()
  },
  (args) => peekRun(args.run_id, { limit: args.limit, cursor: args.cursor })
);

registerTool(
  "claude_wait",
  "Wait for terminal state and return only a compact control envelope. Prefer one long wait; timeoutMs stops waiting, not Claude, and never emits the cumulative report.",
  {
    run_id: z.string().min(1),
    timeoutMs: z.number().int().positive().optional()
  },
  (args) => waitRun(args.run_id, { timeoutMs: args.timeoutMs })
);

registerTool(
  "claude_kill",
  "Stop only the saved/fingerprinted Claude process for run_id; never broad-kill Claude processes by name.",
  {
    run_id: z.string().min(1)
  },
  (args) => killRun(args.run_id)
);

registerTool(
  "claude_result",
  "Return a compact current/final acceptance packet with status, model, warnings, write-scope status, and report/output file handles. It never emits Claude's answer.",
  {
    run_id: z.string().min(1)
  },
  (args) => resultRun(args.run_id)
);

registerTool(
  "claude_relay",
  "Read one bounded chunk of the terminal Claude answer. Pass next_cursor to continue; each Codex consumer owns its cursor independently.",
  {
    run_id: z.string().min(1),
    cursor: z.number().int().nonnegative().optional().default(0),
    maxChars: z
      .number()
      .int()
      .positive()
      .max(CLAUDE_WIRE_LIMITS.maxRelayChars)
      .optional()
      .default(CLAUDE_WIRE_LIMITS.relayChars)
  },
  (args) => relayRun(args.run_id, { cursor: args.cursor, maxChars: args.maxChars })
);

registerTool("claude_profiles", "List available Claude bridge profiles and real CLI flags.", {}, () => profiles());

registerTool(
  "claude_doctor",
  "Check Claude CLI compatibility and live authentication readiness without changing config or auth state.",
  {},
  () => doctor()
);

registerTool(
  "claude_discover_skills",
  "Discover likely Claude skill/plugin roots without writing to them.",
  {
    cwd: z.string().optional()
  },
  (args) => discoverSkills(args)
);

registerTool(
  "claude_audit_skill",
  "Run Claude in skill-audit mode and mark whether structured tool-stream evidence proves the target path was read.",
  {
    skillPath: z.string().min(1),
    prompt: z.string().optional(),
    cwd: z.string().optional(),
    timeoutMs: z.number().int().positive().optional()
  },
  (args) => auditSkill(args)
);

registerTool(
  "claude_cleanup_runs",
  "List or delete old repo-local Claude bridge run logs. Dry-run by default.",
  {
    olderThanDays: z.number().int().positive().optional().default(14),
    confirm: z.boolean().optional().default(false)
  },
  (args) => cleanupRuns(args)
);

const transport = new StdioServerTransport();
exitOnClosedStdio();
await server.connect(transport);
