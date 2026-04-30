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

function textResult(value) {
  return {
    content: [
      {
        type: "text",
        text: typeof value === "string" ? value : JSON.stringify(value, null, 2)
      }
    ]
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
        return textResult({
          error: error instanceof Error ? error.message : String(error)
        });
      }
    }
  );
}

registerTool(
  "claude_run",
  "Start a Claude Code run with a named bridge profile. Returns run_id, pid, profile, cwd, and log_dir.",
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
    settings: z.string().optional(),
    settingSources: z.union([z.string(), z.array(z.string())]).optional(),
    tools: z.union([z.string(), z.array(z.string())]).optional(),
    allowedTools: z.union([z.string(), z.array(z.string())]).optional(),
    disallowedTools: z.union([z.string(), z.array(z.string())]).optional(),
    addDir: z.union([z.string(), z.array(z.string())]).optional(),
    pluginDir: z.union([z.string(), z.array(z.string())]).optional(),
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
  "Return recent milestone-like events and warnings for a running or completed Claude run.",
  {
    run_id: z.string().min(1),
    limit: z.number().int().positive().max(50).optional(),
    cursor: z.number().int().nonnegative().optional()
  },
  (args) => peekRun(args.run_id, { limit: args.limit, cursor: args.cursor })
);

registerTool(
  "claude_wait",
  "Wait for a Claude run to finish and return a compact run report.",
  {
    run_id: z.string().min(1),
    timeoutMs: z.number().int().positive().optional()
  },
  (args) => waitRun(args.run_id, { timeoutMs: args.timeoutMs })
);

registerTool(
  "claude_kill",
  "Stop a running Claude process.",
  {
    run_id: z.string().min(1)
  },
  (args) => killRun(args.run_id)
);

registerTool(
  "claude_result",
  "Return the current or final report and log file locations for a Claude run.",
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
await server.connect(transport);
