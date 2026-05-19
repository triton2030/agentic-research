#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import {
  APPROVAL_MODES,
  THINKING_LEVELS,
  askGemini,
  cleanupRuns,
  geminiStatus,
  killRun,
  peekRun,
  resultRun,
  startRun,
  waitRun
} from "./runner.js";

const server = new McpServer({
  name: "gemini-mcp",
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

const askSchema = {
  prompt: z.string().min(1),
  model: z.string().min(1).optional(),
  systemInstruction: z.string().min(1).optional(),
  thinkingLevel: z.enum(THINKING_LEVELS).optional(),
  temperature: z.number().min(0).max(2).optional(),
  maxOutputTokens: z.number().int().positive().optional(),
  cwd: z.string().min(1).optional(),
  includeDirectories: z.union([z.string(), z.array(z.string())]).optional(),
  approvalMode: z.enum(APPROVAL_MODES).optional(),
  timeoutMs: z.number().int().positive().optional()
};

registerTool("gemini_status", "Report Gemini MCP configuration without making a network call.", {}, () =>
  geminiStatus()
);

registerTool(
  "gemini_ask",
  "Ask Gemini once through account-backed Antigravity CLI or legacy Gemini CLI.",
  askSchema,
  (args) => askGemini(args)
);

registerTool(
  "gemini_run",
  "Start a managed Gemini CLI or Antigravity CLI run. Returns run_id, status, log_dir, and saved process/tmux identifiers for later peek/wait/result/kill.",
  {
    ...askSchema,
    useTmux: z.boolean().optional(),
    tmuxMode: z.boolean().optional()
  },
  (args) => startRun(args)
);

registerTool(
  "gemini_peek",
  "Observe a Gemini run without stopping it: recent log milestones, relay text, activity summary, and tmux_capture when a tmux pane is alive.",
  {
    run_id: z.string().min(1),
    limit: z.number().int().positive().max(50).optional(),
    cursor: z.number().int().nonnegative().optional()
  },
  (args) => peekRun(args.run_id, { limit: args.limit, cursor: args.cursor })
);

registerTool(
  "gemini_observe",
  "Observe a long Gemini/Antigravity run: elapsed time, recent logs, tool-like trace, tmux capture, warnings, cursor, and stop hint.",
  {
    run_id: z.string().min(1),
    limit: z.number().int().positive().max(50).optional(),
    cursor: z.number().int().nonnegative().optional()
  },
  (args) => peekRun(args.run_id, { limit: args.limit, cursor: args.cursor })
);

registerTool(
  "gemini_wait",
  "Wait for a Gemini run report. timeoutMs stops waiting, not the live CLI/tmux process; use peek/result/kill if not terminal.",
  {
    run_id: z.string().min(1),
    timeoutMs: z.number().int().positive().optional()
  },
  (args) => waitRun(args.run_id, { timeoutMs: args.timeoutMs })
);

registerTool(
  "gemini_kill",
  "Stop only the saved Gemini target for run_id: fingerprinted process or saved tmux_session; never broad-kill Gemini/tmux.",
  {
    run_id: z.string().min(1)
  },
  (args) => killRun(args.run_id)
);

registerTool(
  "gemini_result",
  "Return current/final Gemini report, files, status, and tail-check evidence for deciding whether the run/session is terminal.",
  {
    run_id: z.string().min(1)
  },
  (args) => resultRun(args.run_id)
);

registerTool(
  "gemini_cleanup_runs",
  "List or delete old repo-local Gemini run logs. Dry-run by default.",
  {
    olderThanDays: z.number().int().positive().optional().default(14),
    confirm: z.boolean().optional().default(false)
  },
  (args) => cleanupRuns(args)
);

const transport = new StdioServerTransport();
exitOnClosedStdio();
await server.connect(transport);
