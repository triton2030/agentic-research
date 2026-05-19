#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import {
  auditSkill,
  cleanupRuns,
  discoverSkills,
  doctor,
  killRun,
  peekRun,
  profiles,
  resultRun,
  startRun,
  waitRun
} from "./runner.js";

const server = new McpServer({
  name: "claude-bridge-control",
  version: "0.1.0"
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
  "Start a controlled Claude Code run. Use useTmux for long human-observable terminal sessions. Returns run_id, saved pid/session, profile, cwd, and log_dir for later observe/peek/wait/result/kill.",
  {
    prompt: z.string().min(1),
    profile: z.string().optional().default("normal"),
    cwd: z.string().optional(),
    title: z.string().optional(),
    appendSystemPrompt: z.string().optional(),
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
    permissionMode: z.enum(["acceptEdits", "auto", "bypassPermissions", "default", "dontAsk", "plan"]).optional(),
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
    allowDangerouslySkipPermissions: z.boolean().optional(),
    brief: z.boolean().optional(),
    file: z.union([z.string(), z.array(z.string())]).optional(),
    inputFormat: z.enum(["text", "stream-json"]).optional(),
    replayUserMessages: z.boolean().optional(),
    useTmux: z.boolean().optional(),
    tmuxMode: z.boolean().optional(),
    disableAutoMemory: z.boolean().optional(),
    mcpTimeout: z.number().int().positive().optional(),
    maxMcpOutputTokens: z.number().int().positive().optional(),
    env: z.record(z.string(), z.string()).optional(),
    extraArgs: z.array(z.string()).optional()
  },
  (args) => startRun(args)
);

registerTool(
  "claude_peek",
  "Observe a Claude run without stopping it: recent milestones, warnings, relay updates, and cursor for evidence/timeouts.",
  {
    run_id: z.string().min(1),
    limit: z.number().int().positive().max(50).optional(),
    cursor: z.number().int().nonnegative().optional()
  },
  (args) => peekRun(args.run_id, { limit: args.limit, cursor: args.cursor })
);

registerTool(
  "claude_observe",
  "Observe a long Claude run: elapsed time, recent tool/file/command trace, model-visible updates, warnings, cursor, and stop hint.",
  {
    run_id: z.string().min(1),
    limit: z.number().int().positive().max(50).optional(),
    cursor: z.number().int().nonnegative().optional()
  },
  (args) => peekRun(args.run_id, { limit: args.limit, cursor: args.cursor })
);

registerTool(
  "claude_wait",
  "Wait for a Claude run report. timeoutMs stops waiting, not the live Claude process; use peek/result/kill if not terminal.",
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
  "Return current/final Claude report, relay/log files, status, and tail-check evidence for deciding whether the run is terminal.",
  {
    run_id: z.string().min(1)
  },
  (args) => resultRun(args.run_id)
);

registerTool("claude_profiles", "List available Claude bridge profiles and real CLI flags.", {}, () => profiles());

registerTool("claude_doctor", "Check local Claude/Node/npm support without registering global MCP config.", {}, () => doctor());

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
  "Run Claude in skill-audit mode and mark whether tool/debug/stream evidence proves the target path was read.",
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
