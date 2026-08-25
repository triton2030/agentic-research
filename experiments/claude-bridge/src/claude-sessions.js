import { execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { promisify } from "node:util";
import { getSessionInfo, getSessionMessages } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import { CLAUDE_EXECUTABLE } from "./claude-policy.js";
import { ClaudeAskError, compactTail, isClaudeSessionId } from "./claude-result.js";

const execFileAsync = promisify(execFile);
const MAX_ACTIVE_SESSIONS = 20;
const DEFAULT_MESSAGE_LIMIT = 12;
const MAX_MESSAGE_LIMIT = 40;
const MAX_TITLE_CHARS = 240;
const MAX_MESSAGE_CHARS = 4000;
const MAX_CONVERSATION_CHARS = 16_000;

export const claudeSessionsInputSchema = Object.freeze({
  op: z.enum(["list_active", "read"]),
  cwd: z.string().min(1).optional(),
  session_id: z.string().uuid().optional(),
  limit: z.number().int().min(1).max(MAX_MESSAGE_LIMIT).optional()
});

const requestSchema = z.object(claudeSessionsInputSchema).strict();

function canonicalDirectory(value) {
  if (value === undefined) return undefined;
  const requested = path.resolve(value);
  try {
    const canonical = fs.realpathSync.native(requested);
    if (!fs.statSync(canonical).isDirectory()) throw new Error("not a directory");
    return canonical;
  } catch {
    throw new ClaudeAskError("invalid_cwd", `Claude cwd is unavailable: ${requested}`);
  }
}

function canonicalRequest(request) {
  const parsed = requestSchema.safeParse(request);
  if (!parsed.success) {
    const field = parsed.error.issues[0]?.path[0];
    if (field === "session_id") {
      throw new ClaudeAskError("invalid_session_id", "Claude session_id must be a UUID.");
    }
    if (field === "cwd") throw new ClaudeAskError("invalid_cwd", "Claude cwd must be a directory path.");
    throw new ClaudeAskError("invalid_request", "claude_sessions requires list_active or read.");
  }
  if (parsed.data.op === "read" && !parsed.data.session_id) {
    throw new ClaudeAskError("invalid_session_id", "claude_sessions read requires a session_id.");
  }
  if (parsed.data.op === "list_active" && parsed.data.session_id) {
    throw new ClaudeAskError("invalid_request", "claude_sessions list_active does not accept session_id.");
  }
  return {
    op: parsed.data.op,
    cwd: canonicalDirectory(parsed.data.cwd),
    sessionId: parsed.data.session_id,
    limit: parsed.data.limit ?? (
      parsed.data.op === "list_active" ? MAX_ACTIVE_SESSIONS : DEFAULT_MESSAGE_LIMIT
    )
  };
}

function boundText(value, maxChars) {
  const text = String(value ?? "").trim();
  if (text.length <= maxChars) return text;
  return `${text.slice(0, Math.max(0, maxChars - 16))}\n...[truncated]`;
}

function visibleText(entry) {
  const content = entry?.message?.content;
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content
    .filter((block) => block?.type === "text" && typeof block.text === "string")
    .map((block) => block.text)
    .join("\n");
}

function visibleMessages(entries) {
  return entries
    .filter((entry) => entry?.type === "user" || entry?.type === "assistant")
    .map((entry) => ({ role: entry.type, text: visibleText(entry) }))
    .filter((entry) => entry.text.trim());
}

function boundedConversation(messages, limit) {
  const selected = messages.slice(-limit);
  const bounded = [];
  let remaining = MAX_CONVERSATION_CHARS;
  for (const message of [...selected].reverse()) {
    if (remaining <= 0) break;
    const text = boundText(message.text, Math.min(MAX_MESSAGE_CHARS, remaining));
    if (!text) continue;
    bounded.push({ role: message.role, text });
    remaining -= text.length;
  }
  return bounded.reverse();
}

function parseActiveSessions(stdout) {
  let parsed;
  try {
    parsed = JSON.parse(stdout || "[]");
  } catch {
    throw new ClaudeAskError("sessions_probe_failed", "Claude agents returned malformed JSON.");
  }
  if (!Array.isArray(parsed)) {
    throw new ClaudeAskError("sessions_probe_failed", "Claude agents did not return a session array.");
  }
  return parsed
    .filter((entry) => isClaudeSessionId(entry?.sessionId) && typeof entry?.cwd === "string")
    .slice(0, MAX_ACTIVE_SESSIONS)
    .map((entry) => ({
      sessionId: entry.sessionId,
      name: typeof entry.name === "string" ? entry.name : null,
      kind: typeof entry.kind === "string" ? entry.kind : "unknown",
      cwd: entry.cwd,
      startedAt: Number.isFinite(entry.startedAt) && entry.startedAt >= 0 ? entry.startedAt : null
    }));
}

async function listNativeActiveSessions({ executable, cwd, signal }) {
  const args = ["agents", "--json"];
  if (cwd) args.push("--cwd", cwd);
  let stdout;
  try {
    ({ stdout } = await execFileAsync(executable, args, {
      cwd: cwd || process.cwd(),
      encoding: "utf8",
      maxBuffer: 1024 * 1024,
      signal,
      timeout: 10_000
    }));
  } catch (error) {
    if (signal?.aborted || error?.name === "AbortError") throw error;
    throw new ClaudeAskError(
      "sessions_probe_failed",
      `Claude agents failed: ${compactTail(error?.stderr || error?.message)}`
    );
  }
  return parseActiveSessions(stdout);
}

function sessionPacket(active, info) {
  return {
    session_id: active.sessionId,
    name: active.name,
    kind: active.kind,
    cwd: active.cwd,
    started_at_ms: active.startedAt,
    title: boundText(info?.customTitle || info?.summary || active.name, MAX_TITLE_CHARS) || null,
    git_branch: info?.gitBranch || null
  };
}

/** Create the read-only adapter for active native Claude sessions and visible text. */
export function createClaudeSessionsReader(options = {}) {
  const executable = options.executable || CLAUDE_EXECUTABLE;
  const listActive = options.listActive || listNativeActiveSessions;
  const readInfo = options.getSessionInfo || getSessionInfo;
  const readMessages = options.getSessionMessages || getSessionMessages;

  async function activeSessions(request, signal) {
    if (!fs.existsSync(executable)) {
      throw new ClaudeAskError("missing_claude", `Claude executable is unavailable: ${executable}`);
    }
    return listActive({ executable, cwd: request.cwd, signal });
  }

  async function readNative(active) {
    try {
      const [info, entries] = await Promise.all([
        readInfo(active.sessionId, { dir: active.cwd }),
        readMessages(active.sessionId, { dir: active.cwd })
      ]);
      return { info, messages: visibleMessages(entries) };
    } catch (error) {
      throw new ClaudeAskError(
        "session_read_failed",
        `Claude session could not be read: ${compactTail(error?.message)}`,
        { session_id: active.sessionId }
      );
    }
  }

  async function readMetadata(active) {
    try {
      return await readInfo(active.sessionId, { dir: active.cwd });
    } catch {
      return null;
    }
  }

  return {
    async read(request, signal) {
      const canonical = canonicalRequest(request);
      const active = await activeSessions(canonical, signal);

      if (canonical.op === "list_active") {
        const sessions = await Promise.all(active.slice(0, canonical.limit).map(async (entry) => {
          const info = await readMetadata(entry);
          return sessionPacket(entry, info);
        }));
        return { op: "list_active", sessions, session: null, messages: [], warnings: [] };
      }

      const selected = active.find((entry) => entry.sessionId === canonical.sessionId);
      if (!selected) {
        throw new ClaudeAskError(
          "session_not_active",
          `Claude session is not active: ${canonical.sessionId}`,
          { session_id: canonical.sessionId }
        );
      }
      const { info, messages } = await readNative(selected);
      return {
        op: "read",
        sessions: [],
        session: sessionPacket(selected, info),
        messages: boundedConversation(messages, canonical.limit),
        warnings: []
      };
    }
  };
}
