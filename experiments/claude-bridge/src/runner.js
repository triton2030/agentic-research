import { spawn, spawnSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { getProfile, listProfiles, MODEL } from "./profiles.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const BRIDGE_ROOT = path.resolve(__dirname, "..");
export const RUNS_DIR = path.join(BRIDGE_ROOT, "runs");
export const DEFAULT_CLEANUP_DAYS = 14;

const activeRuns = new Map();
const TERMINAL_STATUSES = new Set(["completed", "failed", "killed", "orphaned"]);
const WAITABLE_STATUSES = new Set(["running", "running_orphaned", "killing"]);

function isTerminalStatus(status) {
  return TERMINAL_STATUSES.has(status);
}

function isManagedRun(run) {
  return !isTerminalStatus(run.status) && (Boolean(run.child) || Boolean(run.managed));
}

function markTerminal(run) {
  run.child = null;
  run.managed = false;
  activeRuns.delete(run.runId);
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function nowIsoForPath() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function shortText(value, max = 600) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  return text.length > max ? `${text.slice(0, max - 3)}...` : text;
}

function safeRead(file, fallback = "") {
  try {
    return fs.existsSync(file) ? fs.readFileSync(file, "utf8") : fallback;
  } catch {
    return fallback;
  }
}

function trimText(value, limit = 4000) {
  if (!value || value.length <= limit) return value || "";
  return `${value.slice(0, limit)}\n...[truncated]`;
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function jsonLine(file, value) {
  const event =
    value && typeof value === "object" && !Array.isArray(value)
      ? { observed_at: new Date().toISOString(), ...value }
      : value;
  fs.appendFileSync(file, `${JSON.stringify(event)}\n`);
}

function safeReadJson(file, fallback = null) {
  try {
    if (!fs.existsSync(file)) return fallback;
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return fallback;
  }
}

function writeJsonAtomic(file, value) {
  const tmp = `${file}.${process.pid}.${randomUUID().slice(0, 8)}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(value, null, 2));
  fs.renameSync(tmp, file);
}

function readJsonLines(file) {
  if (!fs.existsSync(file)) return [];
  return fs
    .readFileSync(file, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return { type: "unparsed", raw: line };
      }
    });
}

function readRunEvents(run) {
  const recordedEvents = readJsonLines(run.eventsFile);
  if (!run.useTmux) return recordedEvents;
  const stdoutEvents = safeRead(run.stdoutFile)
    .split(/\r?\n/u)
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return { type: "stdout", raw: line };
      }
    });
  const stderrEvents = safeRead(run.stderrFile)
    .split(/\r?\n/u)
    .filter(Boolean)
    .map((line) => ({ type: "stderr", raw: line }));
  return [...recordedEvents, ...stdoutEvents, ...stderrEvents];
}

function filesForLogDir(logDir) {
  return {
    prompt: path.join(logDir, "prompt.txt"),
    profile: path.join(logDir, "profile.json"),
    command: path.join(logDir, "command.json"),
    script: path.join(logDir, "run.sh"),
    events: path.join(logDir, "events.ndjson"),
    stdout: path.join(logDir, "stdout.log"),
    stderr: path.join(logDir, "stderr.log"),
    tmuxPane: path.join(logDir, "tmux-pane.log"),
    debug: path.join(logDir, "debug.log"),
    report: path.join(logDir, "report.json"),
    state: path.join(logDir, "state.json"),
    exitCode: path.join(logDir, "exit-code.txt")
  };
}

function resolveClaudeCommand() {
  const localNativeClaude = path.join(os.homedir(), ".local", "bin", "claude");
  const configured =
    process.env.CLAUDE_BRIDGE_CLAUDE_BIN ||
    (fs.existsSync(localNativeClaude) ? localNativeClaude : "claude");
  if (configured.endsWith(".js") || configured.endsWith(".mjs")) {
    return { command: process.execPath, prefixArgs: [configured] };
  }
  return { command: configured, prefixArgs: [] };
}

function commandSummary(command, args) {
  return [command, ...args].map((part) => {
    if (/[\s"']/u.test(part)) return JSON.stringify(part);
    return part;
  });
}

function scopedRunEnvAssignments(runId, runEnv = {}) {
  const allowed = new Set([
    "CLAUDE_CODE_DISABLE_AUTO_MEMORY",
    "MCP_TIMEOUT",
    "MAX_MCP_OUTPUT_TOKENS"
  ]);
  const assignments = [`CLAUDE_BRIDGE_RUN_ID=${shellQuote(runId)}`];
  for (const [name, value] of Object.entries(runEnv)) {
    if (value === undefined) continue;
    if (/^FAKE_CLAUDE_/u.test(name) || allowed.has(name)) {
      assignments.push(`${name}=${shellQuote(value)}`);
    }
  }
  return assignments;
}

function stripClaudeApiCredentials(runEnv) {
  delete runEnv.ANTHROPIC_API_KEY;
  delete runEnv.CLAUDE_API_KEY;
  return runEnv;
}

function tmuxVersion() {
  try {
    const result = spawnSync("tmux", ["-V"], { encoding: "utf8" });
    if (result.status !== 0) return null;
    return (result.stdout || result.stderr).trim() || "unknown";
  } catch {
    return null;
  }
}

function tmuxHasSession(session) {
  if (!session) return false;
  const result = spawnSync("tmux", ["has-session", "-t", session], { encoding: "utf8" });
  return result.status === 0;
}

function tmuxSignal(channel) {
  if (!channel) return false;
  const result = spawnSync("tmux", ["wait-for", "-S", channel], { encoding: "utf8" });
  return result.status === 0;
}

function tmuxWait(channel, timeoutMs) {
  if (!channel) return { status: 1, error: "missing channel" };
  const result = spawnSync("tmux", ["wait-for", channel], {
    encoding: "utf8",
    timeout: timeoutMs
  });
  return {
    status: result.status,
    signal: result.signal,
    error: result.error?.code || result.error?.message || null,
    stdout: result.stdout || "",
    stderr: result.stderr || ""
  };
}

function tmuxCapturePane(run) {
  if (!run.useTmux || !run.tmuxTarget || !tmuxHasSession(run.tmuxSession)) {
    return { available: false, text: "", source: "tmux capture-pane" };
  }
  const result = spawnSync("tmux", ["capture-pane", "-p", "-t", run.tmuxTarget, "-S", "-200"], {
    encoding: "utf8"
  });
  if (result.status !== 0) {
    return {
      available: false,
      text: "",
      source: "tmux capture-pane",
      error: shortText(result.stderr || result.stdout || "capture-pane failed", 400)
    };
  }
  return {
    available: true,
    text: trimText((result.stdout || "").trim(), 4000),
    source: "tmux capture-pane"
  };
}

function claudeHelpText() {
  const { command, prefixArgs } = resolveClaudeCommand();
  const help = spawnSync(command, [...prefixArgs, "--help"], { encoding: "utf8" });
  return `${help.stdout || ""}\n${help.stderr || ""}`;
}

function cliJsonValue(value) {
  return typeof value === "string" ? value : JSON.stringify(value);
}

function assertSupportedOptions(options) {
  const requestedFlags = [
    ["maxTurns", "--max-turns"],
    ["systemPromptFile", "--system-prompt-file"],
    ["appendSystemPromptFile", "--append-system-prompt-file"],
    ["permissionPromptTool", "--permission-prompt-tool"],
    ["permissionMode", "--permission-mode"],
    ["jsonSchema", "--json-schema"],
    ["agent", "--agent"],
    ["agents", "--agents"],
    ["pluginUrl", "--plugin-url"],
    ["allowDangerouslySkipPermissions", "--allow-dangerously-skip-permissions"],
    ["brief", "--brief"],
    ["file", "--file"],
    ["inputFormat", "--input-format"],
    ["replayUserMessages", "--replay-user-messages"]
  ].filter(([key]) => options[key] !== undefined && options[key] !== false);

  if (!requestedFlags.length) return;

  const helpText = claudeHelpText();
  const missing = requestedFlags.map(([, flag]) => flag).filter((flag) => !helpText.includes(flag));
  if (missing.length) {
    throw new Error(
      `Installed claude does not advertise required option(s): ${missing.join(", ")}. ` +
        "Run `npm run doctor` in experiments/claude-bridge to compare official docs with this local CLI."
    );
  }
}

function buildArgs({
  prompt,
  profileName,
  debugFile,
  extraArgs = [],
  appendSystemPrompt,
  appendSystemPromptFile,
  systemPrompt,
  systemPromptFile,
  maxBudgetUsd,
  maxTurns,
  fallbackModel,
  sessionId,
  resume,
  forkSession,
  name,
  noSessionPersistence,
  mcpConfig,
  strictMcpConfig,
  permissionPromptTool,
  permissionMode,
  jsonSchema,
  agent,
  agents,
  settings,
  settingSources,
  tools,
  allowedTools,
  disallowedTools,
  addDir,
  pluginDir,
  pluginUrl,
  allowDangerouslySkipPermissions,
  brief,
  file,
  inputFormat,
  replayUserMessages
}) {
  const profile = getProfile(profileName);
  const args = [...profile.flags, "--debug-file", debugFile];

  if (appendSystemPrompt) {
    args.push("--append-system-prompt", appendSystemPrompt);
  }
  if (appendSystemPromptFile) {
    args.push("--append-system-prompt-file", appendSystemPromptFile);
  }
  if (systemPrompt) {
    args.push("--system-prompt", systemPrompt);
  }
  if (systemPromptFile) {
    args.push("--system-prompt-file", systemPromptFile);
  }
  if (maxBudgetUsd) {
    args.push("--max-budget-usd", String(maxBudgetUsd));
  }
  if (maxTurns) {
    args.push("--max-turns", String(maxTurns));
  }
  if (fallbackModel) {
    args.push("--fallback-model", fallbackModel);
  }
  if (sessionId) {
    args.push("--session-id", sessionId);
  }
  if (name) {
    args.push("--name", name);
  }
  if (resume) {
    args.push("--resume");
    if (resume !== true) args.push(String(resume));
  }
  if (forkSession) {
    args.push("--fork-session");
  }
  if (noSessionPersistence) {
    args.push("--no-session-persistence");
  }
  for (const value of [].concat(mcpConfig || [])) {
    args.push("--mcp-config", value);
  }
  if (strictMcpConfig) {
    args.push("--strict-mcp-config");
  }
  if (permissionPromptTool) {
    args.push("--permission-prompt-tool", permissionPromptTool);
  }
  if (permissionMode) {
    args.push("--permission-mode", permissionMode);
  }
  if (jsonSchema) {
    args.push("--json-schema", cliJsonValue(jsonSchema));
  }
  if (agent) {
    args.push("--agent", agent);
  }
  if (agents) {
    args.push("--agents", cliJsonValue(agents));
  }
  if (settings) {
    args.push("--settings", settings);
  }
  if (settingSources) {
    args.push("--setting-sources", Array.isArray(settingSources) ? settingSources.join(",") : settingSources);
  }
  if (tools) {
    args.push("--tools", Array.isArray(tools) ? tools.join(",") : tools);
  }
  for (const value of [].concat(allowedTools || [])) {
    args.push("--allowedTools", value);
  }
  for (const value of [].concat(disallowedTools || [])) {
    args.push("--disallowedTools", value);
  }
  for (const value of [].concat(addDir || [])) {
    args.push("--add-dir", value);
  }
  for (const value of [].concat(pluginDir || [])) {
    args.push("--plugin-dir", value);
  }
  for (const value of [].concat(pluginUrl || [])) {
    args.push("--plugin-url", value);
  }
  if (allowDangerouslySkipPermissions) {
    args.push("--allow-dangerously-skip-permissions");
  }
  if (brief) {
    args.push("--brief");
  }
  const fileSpecs = [].concat(file || []).filter(Boolean);
  if (fileSpecs.length) {
    args.push("--file", ...fileSpecs);
  }
  if (inputFormat) {
    args.push("--input-format", inputFormat);
  }
  if (replayUserMessages) {
    args.push("--replay-user-messages");
  }
  args.push(...extraArgs);
  args.push("-p", prompt);
  return args.filter((value) => value !== "");
}

function extractEventText(event) {
  if (!event) return "";
  if (typeof event === "string") return event.trim();
  if (Array.isArray(event)) {
    return event.map((item) => extractEventText(item)).filter(Boolean).join(" ");
  }
  if (typeof event !== "object") return "";

  if (event.event && typeof event.event === "object") {
    const nested = extractEventText(event.event);
    if (nested) return nested;
  }
  if (typeof event.delta?.text === "string" && event.delta.text.trim()) {
    return event.delta.text.trim();
  }
  if (typeof event.content_block?.text === "string" && event.content_block.text.trim()) {
    return event.content_block.text.trim();
  }

  const content = event.content;
  if (Array.isArray(content)) {
    const text = content
      .map((item) => {
        if (typeof item === "string") return item;
        if (item?.type === "text" && typeof item.text === "string") return item.text;
        return extractEventText(item);
      })
      .filter(Boolean)
      .join(" ");
    if (text.trim()) return text.trim();
  }

  const messageContent = event.message?.content;
  if (Array.isArray(messageContent) || typeof messageContent === "string") {
    const text = extractEventText(messageContent);
    if (text) return text;
  }

  const candidates = [event.text, event.message, event.delta, event.result, event.raw, event.error];
  for (const candidate of candidates) {
    if (typeof candidate === "string" && candidate.trim()) {
      return candidate.trim();
    }
  }
  return "";
}

function eventMentionsPath(event, targetPath) {
  if (!targetPath) return false;
  const haystack = JSON.stringify(event);
  const normalizedTarget = path.resolve(targetPath);
  return haystack.includes(normalizedTarget) || haystack.includes(targetPath);
}

function toolNameFromEvent(event) {
  return event.name || event.tool_name || event.toolName || event.message?.name || event.message?.tool_name || null;
}

function normalizeEvent(event) {
  const core = event.event && typeof event.event === "object" ? event.event : event;
  const type = String(core.type || event.type || "").toLowerCase();
  const outerType = String(event.type || "").toLowerCase();
  const name = toolNameFromEvent(core) || toolNameFromEvent(event);
  const text = shortText(extractEventText(event), 500);

  if (type.includes("rate") || outerType.includes("rate")) {
    return { kind: "rate_limit", text: text || "rate limit event" };
  }
  if (type.includes("error") || outerType === "stderr" || core.error || event.error) {
    return { kind: "error", text: text || "error event" };
  }
  if (type.includes("tool_use") || type.includes("tool_call") || name) {
    return {
      kind: "tool_use",
      tool_name: name || "tool",
      file_path: core.input?.file_path || event.input?.file_path || core.file_path || event.file_path || core.path || event.path || null,
      text: text || `${name || "tool"} called`
    };
  }
  if (type.includes("tool_result")) {
    return { kind: "tool_result", text: text || "tool result" };
  }
  if (type.includes("result")) {
    return { kind: "result", text: text || "run result" };
  }
  if (text && /assistant|message|delta|content|stdout/u.test(type)) {
    return { kind: "assistant_text", text };
  }
  if (text && outerType === "stdout") {
    return { kind: "assistant_text", text };
  }
  if (event.session_id || event.sessionId) {
    return {
      kind: "session",
      text: `session ${event.session_id || event.sessionId}`,
      session_id: event.session_id || event.sessionId
    };
  }
  return null;
}

function summarizeMilestones(events, limit = 12, { cursor = 0, includeSessions = true } = {}) {
  const seenSessions = new Set();
  const milestones = [];
  const startIndex = Math.max(0, Number(cursor) || 0);
  for (const [eventIndex, event] of events.entries()) {
    if (eventIndex < startIndex) continue;
    const normalized = normalizeEvent(event);
    if (!normalized || (!normalized.text && !normalized.tool_name && !normalized.session_id)) continue;
    if (normalized.kind === "session") {
      if (!includeSessions) continue;
      if (seenSessions.has(normalized.session_id)) continue;
      seenSessions.add(normalized.session_id);
    }
    milestones.push({ ...normalized, event_index: eventIndex });
  }
  return milestones.slice(-limit);
}

function isInside(candidate, root) {
  if (!candidate || !root) return false;
  const resolvedCandidate = path.resolve(candidate);
  const resolvedRoot = path.resolve(root);
  return resolvedCandidate === resolvedRoot || resolvedCandidate.startsWith(`${resolvedRoot}${path.sep}`);
}

function collectPathStrings(value, output = []) {
  if (typeof value === "string") {
    const maybePaths = value.match(/(?:\/Users\/[^\s"'`{}[\],)]+|~\/[^\s"'`{}[\],)]+)/g) || [];
    output.push(...maybePaths.map((item) => item.replace(/^~/u, os.homedir())));
    return output;
  }
  if (Array.isArray(value)) {
    for (const item of value) collectPathStrings(item, output);
    return output;
  }
  if (value && typeof value === "object") {
    for (const item of Object.values(value)) collectPathStrings(item, output);
  }
  return output;
}

function detectWarnings(events, cwd) {
  const warnings = [];
  const milestones = summarizeMilestones(events, events.length || 1);
  const texts = milestones
    .filter((event) => event.kind !== "session")
    .map((event) => event.text)
    .filter(Boolean);
  const counts = new Map();
  for (const text of texts) {
    const key = shortText(text, 180);
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  for (const [text, count] of counts) {
    if (count >= 3 && text.length > 30) {
      warnings.push({ type: "possible_loop", detail: text, count });
    }
  }

  const errorText = texts.find((text) => /stuck|loop|cannot|permission|denied|failed|error|wrong/iu.test(text));
  if (errorText) {
    warnings.push({ type: "possible_wrong_direction_or_error", detail: shortText(errorText, 240) });
  }

  const allowedRoots = [cwd, path.join(os.homedir(), ".claude"), path.join(os.homedir(), ".codex")];
  const observedPaths = [...new Set(events.flatMap((event) => collectPathStrings(event)))];
  const outside = observedPaths.filter((candidate) => !allowedRoots.some((root) => isInside(candidate, root)));
  if (outside.length) {
    warnings.push({
      type: "boundary_suspicion",
      detail: "Claude mentioned or used paths outside cwd, ~/.claude, and ~/.codex.",
      paths: outside.slice(0, 20)
    });
  }

  return warnings;
}

function eventObservedAt(event) {
  return event?.observed_at || event?.timestamp || event?.time || event?.created_at || null;
}

function elapsedSeconds(startedAt) {
  const started = Date.parse(startedAt || "");
  if (!Number.isFinite(started)) return null;
  return Math.max(0, Math.round((Date.now() - started) / 1000));
}

function toolTraceFromEvent(event, eventIndex) {
  const normalized = normalizeEvent(event);
  if (!normalized || !["tool_use", "tool_result"].includes(normalized.kind)) return null;
  const core = event.event && typeof event.event === "object" ? event.event : event;
  const input = core.input || event.input || core.tool_input || event.tool_input || {};
  const command = input.command || input.cmd || null;
  const filePath =
    normalized.file_path ||
    input.file_path ||
    input.path ||
    input.absolute_path ||
    core.file_path ||
    core.path ||
    event.file_path ||
    event.path ||
    null;
  return {
    event_index: eventIndex,
    observed_at: eventObservedAt(event),
    kind: normalized.kind,
    tool_name: normalized.tool_name || core.name || event.name || null,
    file_path: filePath,
    command: command ? shortText(command, 500) : null,
    text: shortText(normalized.text || extractEventText(event), 500)
  };
}

function activitySummary(events, run, { limit = 12, cursor = 0 } = {}) {
  const startIndex = Math.max(0, Number(cursor) || 0);
  const tmux = tmuxCapturePane(run);
  const tool_trace = events
    .map((event, eventIndex) => toolTraceFromEvent(event, eventIndex))
    .filter(Boolean);
  const recent_tool_trace = tool_trace.filter((event) => event.event_index >= startIndex).slice(-limit);
  const counts = {};
  for (const event of events) {
    const normalized = normalizeEvent(event);
    if (!normalized?.kind) continue;
    counts[normalized.kind] = (counts[normalized.kind] || 0) + 1;
  }
  const recent_text = summarizeMilestones(events, limit, { cursor: startIndex, includeSessions: false })
    .filter((event) => ["assistant_text", "result", "error", "rate_limit"].includes(event.kind))
    .map((event) => ({
      event_index: event.event_index,
      kind: event.kind,
      text: shortText(event.text, 700)
    }));
  const recentPaths = [
    ...new Set(
      [
        ...recent_tool_trace.map((event) => event.file_path).filter(Boolean),
        ...events.slice(-50).flatMap((event) => collectPathStrings(event))
      ].filter(Boolean)
    )
  ].slice(-20);
  return {
    elapsed_seconds: elapsedSeconds(run.startedAt),
    event_count: events.length,
    last_event_at: [...events].reverse().map(eventObservedAt).find(Boolean) || null,
    counts,
    recent_tool_trace,
    recent_paths: recentPaths,
    recent_text,
    tmux_capture_available: tmux.available,
    last_tmux_output: shortText(tmux.text, 900),
    note: "Observable trace only: tool calls, files, logs, warnings, and model-visible updates. Private chain-of-thought is not exposed.",
    stop_hint: WAITABLE_STATUSES.has(run.status)
      ? "Use claude_kill for this run_id if the trajectory is wrong or the run should stop."
      : "Run is terminal; no kill is needed unless a fingerprint-matched process still appears in result."
  };
}

function finalOutputDetails(events, max = 8000) {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const event = events[index];
    const core = event.event && typeof event.event === "object" ? event.event : event;
    const type = String(core.type || event.type || "").toLowerCase();
    if (!type.includes("result")) continue;
    const text = extractEventText(event);
    if (text) {
      const truncated = text.length > max;
      return {
        text: truncated ? `${text.slice(0, max - 3)}...` : text,
        source: "result",
        truncated,
        event_index: index
      };
    }
  }

  for (let index = events.length - 1; index >= 0; index -= 1) {
    const event = events[index];
    const normalized = normalizeEvent(event);
    if (normalized?.kind !== "assistant_text") continue;
    const text = extractEventText(event);
    if (text) {
      const truncated = text.length > max;
      return {
        text: truncated ? `${text.slice(0, max - 3)}...` : text,
        source: "assistant_text",
        truncated,
        event_index: index
      };
    }
  }

  return {
    text: "",
    source: null,
    truncated: false,
    event_index: null
  };
}

function finalOutputSummary(events) {
  return finalOutputDetails(events, 1200).text;
}

function relayTextFromMilestones(milestones, max = 4000) {
  const lines = [];
  for (const event of milestones) {
    if (!["assistant_text", "result", "error"].includes(event.kind)) continue;
    const text = shortText(event.text, 1000);
    if (!text || lines.at(-1) === text) continue;
    lines.push(text);
  }
  const text = lines.join("\n");
  return text.length > max ? `${text.slice(0, max - 3)}...` : text;
}

function buildFinalChatRelay(events) {
  const finalOutput = finalOutputDetails(events);
  return {
    text: finalOutput.text,
    markdown: finalOutput.text ? `Claude:\n${finalOutput.text}` : "",
    source: finalOutput.source,
    truncated: finalOutput.truncated,
    event_index: finalOutput.event_index,
    instruction: "Relay this text to the user in chat when the user needs Claude's answer."
  };
}

function buildPeekChatRelay(milestones, nextCursor) {
  const text = relayTextFromMilestones(milestones);
  return {
    text,
    markdown: text ? `Claude update:\n${text}` : "",
    source: "peek",
    truncated: text.endsWith("..."),
    next_cursor: nextCursor,
    instruction: "Relay this update in chat instead of raw stream-json when observing a Claude run."
  };
}

function runFiles(run) {
  return {
    prompt: run.promptFile,
    profile: run.profileFile,
    command: run.commandFile,
    script: run.scriptFile || null,
    events: run.eventsFile,
    stdout: run.stdoutFile,
    stderr: run.stderrFile,
    tmux_pane: run.tmuxPaneFile || null,
    debug: run.debugFile,
    report: run.reportFile,
    state: run.stateFile,
    exit_code: run.exitCodeFile || null
  };
}

function writeState(run) {
  const state = {
    run_id: run.runId,
    profile: run.profileName,
    model: MODEL,
    cwd: run.cwd,
    pid: run.child?.pid ?? run.pid ?? null,
    process_group_pid: run.processGroupPid ?? run.child?.pid ?? run.pid ?? null,
    status: run.status,
    exit_code: run.exitCode ?? null,
    signal: run.signal ?? null,
    session_id: run.sessionId ?? null,
    started_at: run.startedAt,
    updated_at: new Date().toISOString(),
    command: run.commandSummary,
    log_dir: run.logDir,
    files: runFiles(run),
    orphan_reason: run.orphanReason || null,
    use_tmux: run.useTmux || false,
    tmux_session: run.tmuxSession || null,
    tmux_target: run.tmuxTarget || null,
    tmux_start_channel: run.tmuxStartChannel || null,
    tmux_go_channel: run.tmuxGoChannel || null,
    tmux_done_channel: run.tmuxDoneChannel || null
  };
  writeJsonAtomic(run.stateFile, state);
  return state;
}

function pidArgs(pid) {
  if (!pid) return "";
  const result = spawnSync("ps", ["-p", String(pid), "-o", "args="], { encoding: "utf8" });
  if (result.status !== 0) return "";
  return result.stdout.trim();
}

function processGroupRows(processGroupPid) {
  if (!processGroupPid) return [];
  const result = spawnSync("ps", ["-axo", "pid=,pgid=,args="], { encoding: "utf8" });
  if (result.status !== 0) return [];
  return result.stdout
    .split(/\r?\n/u)
    .map((line) => line.match(/^\s*(\d+)\s+(\d+)\s+(.+)$/u))
    .filter(Boolean)
    .map((match) => ({
      pid: Number(match[1]),
      pgid: Number(match[2]),
      args: match[3]
    }))
    .filter((row) => row.pgid === Number(processGroupPid));
}

function processMatchesRun(run) {
  const processGroupPid = run.processGroupPid ?? run.pid;
  const fingerprints = [run.debugFile, run.logDir, run.runId].filter(Boolean);
  const rows = processGroupRows(processGroupPid);
  if (rows.length) {
    const matched = rows.some((row) => fingerprints.some((fingerprint) => row.args.includes(fingerprint)));
    return {
      alive: true,
      matched,
      args: rows.map((row) => row.args).join("\n"),
      processGroupPid,
      pids: rows.map((row) => row.pid)
    };
  }

  const args = pidArgs(run.pid);
  if (!args) {
    return { alive: false, matched: false, args: "", processGroupPid, pids: [] };
  }
  const matched = fingerprints.some((fingerprint) => args.includes(fingerprint));
  return { alive: true, matched, args, processGroupPid, pids: [run.pid].filter(Boolean) };
}

function signalProcessGroup(run, signal = "SIGTERM") {
  const match = processMatchesRun(run);
  if (!match.alive || !match.matched || !match.processGroupPid) return { ...match, signaled: false };
  return signalMatchedProcessGroup(match, signal);
}

function signalMatchedProcessGroup(match, signal = "SIGTERM") {
  if (!match.alive || !match.matched || !match.processGroupPid) return { ...match, signaled: false };
  try {
    process.kill(-Number(match.processGroupPid), signal);
    return { ...match, signaled: true };
  } catch (error) {
    return { ...match, signaled: false, error: error.message };
  }
}

function refreshTmuxRun(run) {
  if (!run.useTmux || !WAITABLE_STATUSES.has(run.status)) return run;
  if (fs.existsSync(run.exitCodeFile)) {
    const code = Number(safeRead(run.exitCodeFile, "1").trim());
    run.exitCode = Number.isInteger(code) ? code : 1;
    run.status = run.status === "killing" ? "killed" : run.exitCode === 0 ? "completed" : "failed";
    markTerminal(run);
    run.orphanReason = null;
    writeState(run);
    writeReport(run);
    return run;
  }
  if (tmuxHasSession(run.tmuxSession)) {
    run.status = run.status === "killing" ? "killing" : "running_orphaned";
    run.managed = false;
    run.orphanReason =
      run.status === "killing"
        ? "Kill was requested; tmux session is still alive."
        : "tmux session is alive, but this MCP server does not own a child handle.";
  } else {
    run.status = run.status === "killing" ? "killed" : "orphaned";
    markTerminal(run);
    run.orphanReason =
      run.status === "killed"
        ? "Kill was requested and tmux session is no longer alive."
        : "tmux session is gone and no exit-code.txt was recorded.";
  }
  writeState(run);
  writeReport(run);
  return run;
}

function refreshInactiveRun(run) {
  if (run.useTmux) return refreshTmuxRun(run);
  if (["completed", "failed", "killed"].includes(run.status)) {
    const match = processMatchesRun(run);
    if (match.alive && match.matched) {
      run.status = run.status === "killed" ? "killing" : "running_orphaned";
      run.orphanReason =
        run.status === "killing"
          ? "Run recorded killed status, but its fingerprint-matched process group still has live members."
          : "Run recorded terminal status, but its fingerprint-matched process group still has live members.";
      writeState(run);
      writeReport(run);
    }
    return run;
  }
  if (!WAITABLE_STATUSES.has(run.status)) return run;
  const match = processMatchesRun(run);
  run.managed = false;
  if (match.alive && match.matched) {
    run.status = run.status === "killing" ? "killing" : "running_orphaned";
    run.orphanReason =
      run.status === "killing"
        ? "Kill was requested; process group is still alive and fingerprint matches this run."
        : "Process group is alive and fingerprint matches this run, but current MCP server does not own the child handle.";
  } else if (match.alive) {
    run.status = "orphaned";
    markTerminal(run);
    run.orphanReason = "Saved PID is alive, but ps args do not contain this run directory or debug.log fingerprint.";
  } else {
    run.status = run.status === "killing" ? "killed" : "orphaned";
    markTerminal(run);
    run.orphanReason =
      run.status === "killed"
        ? "Kill was requested and saved process group is no longer alive."
        : "Saved PID is not alive; previous MCP server likely exited before recording completion.";
  }
  writeState(run);
  writeReport(run);
  return run;
}

function buildRunFromState(runId, logDir, state) {
  const files = state.files || filesForLogDir(logDir);
  return {
    runId,
    profileName: state.profile || "unknown",
    cwd: state.cwd || process.cwd(),
    logDir,
    promptFile: files.prompt,
    profileFile: files.profile,
    commandFile: files.command,
    scriptFile: files.script,
    eventsFile: files.events,
    stdoutFile: files.stdout,
    stderrFile: files.stderr,
    tmuxPaneFile: files.tmux_pane || files.tmuxPane || path.join(logDir, "tmux-pane.log"),
    debugFile: files.debug,
    reportFile: files.report,
    stateFile: files.state || path.join(logDir, "state.json"),
    exitCodeFile: files.exit_code || files.exitCode || path.join(logDir, "exit-code.txt"),
    commandSummary: state.command || [],
    status: state.status || "completed_unknown",
    exitCode: state.exit_code ?? null,
    signal: state.signal ?? null,
    sessionId: state.session_id ?? null,
    startedAt: state.started_at || null,
    pid: state.pid ?? null,
    processGroupPid: state.process_group_pid ?? state.pid ?? null,
    child: null,
    managed: false,
    orphanReason: state.orphan_reason || null,
    useTmux: Boolean(state.use_tmux),
    tmuxSession: state.tmux_session || null,
    tmuxTarget: state.tmux_target || null,
    tmuxStartChannel: state.tmux_start_channel || null,
    tmuxGoChannel: state.tmux_go_channel || null,
    tmuxDoneChannel: state.tmux_done_channel || null
  };
}

function buildRunFromLegacyReport(runId, logDir, report) {
  const files = report.files || filesForLogDir(logDir);
  const status = report.status && report.status !== "running" ? report.status : "completed_unknown";
  return {
    runId,
    profileName: report.profile || "unknown",
    cwd: report.cwd || process.cwd(),
    logDir,
    promptFile: files.prompt,
    profileFile: files.profile,
    commandFile: files.command,
    scriptFile: files.script || path.join(logDir, "run.sh"),
    eventsFile: files.events,
    stdoutFile: files.stdout,
    stderrFile: files.stderr,
    tmuxPaneFile: files.tmux_pane || files.tmuxPane || path.join(logDir, "tmux-pane.log"),
    debugFile: files.debug,
    reportFile: files.report || path.join(logDir, "report.json"),
    stateFile: files.state || path.join(logDir, "state.json"),
    exitCodeFile: files.exit_code || files.exitCode || path.join(logDir, "exit-code.txt"),
    commandSummary: report.command || [],
    status,
    exitCode: report.exit_code ?? null,
    signal: report.signal ?? null,
    sessionId: report.session_id ?? null,
    startedAt: null,
    pid: report.pid ?? null,
    processGroupPid: report.process_group_pid ?? report.pid ?? null,
    child: null,
    managed: false,
    orphanReason: status === "completed_unknown" ? "Legacy run has no durable state.json." : null,
    useTmux: Boolean(report.use_tmux),
    tmuxSession: report.tmux_session || null,
    tmuxTarget: report.tmux_target || null,
    tmuxStartChannel: report.tmux_start_channel || null,
    tmuxGoChannel: report.tmux_go_channel || null,
    tmuxDoneChannel: report.tmux_done_channel || null
  };
}

function buildReport(run) {
  const events = readRunEvents(run);
  const warnings = detectWarnings(events, run.cwd);
  const milestones = summarizeMilestones(events);
  const activity = activitySummary(events, run);

  return {
    run_id: run.runId,
    profile: run.profileName,
    model: MODEL,
    cwd: run.cwd,
    pid: run.child?.pid ?? run.pid ?? null,
    status: run.status,
    managed: isManagedRun(run),
    orphan_reason: run.orphanReason || null,
    exit_code: run.exitCode ?? null,
    signal: run.signal ?? null,
    session_id: run.sessionId ?? null,
    log_dir: run.logDir,
    command: run.commandSummary,
    use_tmux: run.useTmux || false,
    tmux_session: run.tmuxSession || null,
    tmux_target: run.tmuxTarget || null,
    tmux_capture: tmuxCapturePane(run),
    warnings,
    activity,
    milestones,
    events: milestones,
    chat_relay: buildFinalChatRelay(events),
    final_output_summary: finalOutputSummary(events),
    files: runFiles(run)
  };
}

function writeReport(run) {
  const report = buildReport(run);
  writeJsonAtomic(run.reportFile, report);
  return report;
}

function writeRunScript(files, run, command, args, runEnv) {
  const commandLine = [
    "env",
    ...scopedRunEnvAssignments(run.runId, runEnv),
    shellQuote(command),
    ...args.map(shellQuote)
  ].join(" ");
  const lines = [
    "#!/bin/bash",
    `cd ${shellQuote(run.cwd)} || exit 127`,
    "set +e",
    `stdout_pipe=${shellQuote(path.join(run.logDir, "stdout.pipe"))}`,
    `stderr_pipe=${shellQuote(path.join(run.logDir, "stderr.pipe"))}`,
    "rm -f \"$stdout_pipe\" \"$stderr_pipe\"",
    "mkfifo \"$stdout_pipe\" \"$stderr_pipe\"",
    "cleanup_pipes() { rm -f \"$stdout_pipe\" \"$stderr_pipe\"; }",
    "trap cleanup_pipes EXIT",
    `tmux wait-for -S ${shellQuote(run.tmuxStartChannel)} 2>/dev/null || true`,
    `tmux wait-for ${shellQuote(run.tmuxGoChannel)} 2>/dev/null || true`,
    `tee -a ${shellQuote(files.stdout)} < "$stdout_pipe" &`,
    "stdout_tee=$!",
    `tee -a ${shellQuote(files.stderr)} < "$stderr_pipe" >&2 &`,
    "stderr_tee=$!",
    `${commandLine} > "$stdout_pipe" 2> "$stderr_pipe"`,
    "code=$?",
    "drain_tee() {",
    "  local pid=\"$1\"",
    "  local count=0",
    "  while kill -0 \"$pid\" 2>/dev/null && [ \"$count\" -lt 20 ]; do",
    "    sleep 0.05",
    "    count=$((count + 1))",
    "  done",
    "  if kill -0 \"$pid\" 2>/dev/null; then",
    "    kill \"$pid\" 2>/dev/null || true",
    "  fi",
    "  wait \"$pid\" 2>/dev/null || true",
    "}",
    "drain_tee \"$stdout_tee\"",
    "drain_tee \"$stderr_tee\"",
    `printf "%s" "$code" > ${shellQuote(files.exitCode)}`,
    `tmux wait-for -S ${shellQuote(run.tmuxDoneChannel)} 2>/dev/null || true`,
    "exit \"$code\""
  ];
  fs.writeFileSync(files.script, `${lines.join("\n")}\n`, { mode: 0o700 });
}

export function startRun(options = {}) {
  const {
    prompt,
    profile = "normal",
    cwd = process.cwd(),
    title,
    extraArgs,
    appendSystemPrompt,
    appendSystemPromptFile,
    systemPrompt,
    systemPromptFile,
    maxBudgetUsd,
    maxTurns,
    fallbackModel,
    sessionId,
    resume,
    forkSession,
    name,
    noSessionPersistence,
    mcpConfig,
    strictMcpConfig,
    permissionPromptTool,
    permissionMode,
    jsonSchema,
    agent,
    agents,
    settings,
    settingSources,
    tools,
    allowedTools,
    disallowedTools,
    addDir,
    pluginDir,
    pluginUrl,
    allowDangerouslySkipPermissions,
    brief,
    file,
    inputFormat,
    replayUserMessages,
    useTmux,
    tmuxMode
  } = options || {};

  if (!prompt || !String(prompt).trim()) {
    throw new Error("claude_run requires a non-empty prompt.");
  }
  assertSupportedOptions(options);

  const profileConfig = getProfile(profile);
  if (profileConfig.unsupported) {
    throw new Error(`Profile ${profile} is marked unsupported.`);
  }

  ensureDir(RUNS_DIR);
  const runId = `${nowIsoForPath()}-${randomUUID().slice(0, 8)}`;
  const logDir = path.join(RUNS_DIR, runId);
  ensureDir(logDir);
  const files = filesForLogDir(logDir);

  fs.writeFileSync(files.prompt, String(prompt));
  fs.writeFileSync(files.profile, JSON.stringify({ name: profile, ...profileConfig }, null, 2));

  const { command, prefixArgs } = resolveClaudeCommand();
  const runEnv = {
    ...process.env,
    CLAUDE_BRIDGE_RUN_ID: runId,
    ...(profileConfig.env || {}),
    ...(options.env || {})
  };
  stripClaudeApiCredentials(runEnv);
  if (options.disableAutoMemory) {
    runEnv.CLAUDE_CODE_DISABLE_AUTO_MEMORY = "1";
  }
  if (options.mcpTimeout) {
    runEnv.MCP_TIMEOUT = String(options.mcpTimeout);
  }
  if (options.maxMcpOutputTokens) {
    runEnv.MAX_MCP_OUTPUT_TOKENS = String(options.maxMcpOutputTokens);
  }
  const claudeArgs = [
    ...prefixArgs,
    ...buildArgs({
      prompt: String(prompt),
      profileName: profile,
      debugFile: files.debug,
      extraArgs,
      appendSystemPrompt,
      appendSystemPromptFile,
      systemPrompt,
      systemPromptFile,
      maxBudgetUsd,
      maxTurns,
      fallbackModel,
      sessionId,
      resume,
      forkSession,
      name,
      noSessionPersistence,
      mcpConfig,
      strictMcpConfig,
      permissionPromptTool,
      permissionMode,
      jsonSchema,
      agent,
      agents,
      settings,
      settingSources,
      tools,
      allowedTools,
      disallowedTools,
      addDir,
      pluginDir,
      pluginUrl,
      allowDangerouslySkipPermissions,
      brief,
      file,
      inputFormat,
      replayUserMessages
    })
  ];
  const selectedUseTmux = Boolean(useTmux || tmuxMode);
  if (selectedUseTmux && !tmuxVersion()) {
    throw new Error("tmux mode requested, but tmux is not available. Install tmux or run without useTmux.");
  }
  const tmuxSession = selectedUseTmux ? `claude-bridge-${runId.replace(/[^A-Za-z0-9_-]/gu, "-")}` : null;
  const tmuxTarget = selectedUseTmux ? `${tmuxSession}:0.0` : null;
  const tmuxStartChannel = selectedUseTmux ? `${tmuxSession}-ready` : null;
  const tmuxGoChannel = selectedUseTmux ? `${tmuxSession}-go` : null;
  const tmuxDoneChannel = selectedUseTmux ? `${tmuxSession}-done` : null;
  const runCommand = selectedUseTmux ? "tmux" : command;
  const runArgs = selectedUseTmux
    ? ["new-session", "-d", "-s", tmuxSession, "/bin/bash", files.script]
    : claudeArgs;
  const summary = commandSummary(runCommand, runArgs);

  const run = {
    runId,
    profileName: profile,
    cwd,
    logDir,
    promptFile: files.prompt,
    profileFile: files.profile,
    commandFile: files.command,
    scriptFile: files.script,
    eventsFile: files.events,
    stdoutFile: files.stdout,
    stderrFile: files.stderr,
    tmuxPaneFile: files.tmuxPane,
    debugFile: files.debug,
    reportFile: files.report,
    stateFile: files.state,
    exitCodeFile: files.exitCode,
    commandSummary: summary,
    status: "running",
    exitCode: null,
    signal: null,
    sessionId: null,
    startedAt: new Date().toISOString(),
    pid: null,
    processGroupPid: null,
    child: null,
    managed: true,
    orphanReason: null,
    useTmux: selectedUseTmux,
    tmuxSession,
    tmuxTarget,
    tmuxStartChannel,
    tmuxGoChannel,
    tmuxDoneChannel
  };

  if (selectedUseTmux) {
    writeRunScript(files, run, command, claudeArgs, runEnv);
  }

  fs.writeFileSync(
    files.command,
    JSON.stringify(
      {
        command: runCommand,
        args: runArgs,
        summary,
        claude_command: command,
        claude_args: claudeArgs,
        cwd,
        title,
        use_tmux: selectedUseTmux,
        tmux_session: tmuxSession,
        tmux_target: tmuxTarget,
        tmux_start_channel: tmuxStartChannel,
        tmux_go_channel: tmuxGoChannel,
        tmux_done_channel: tmuxDoneChannel,
        env: {
          CLAUDE_CODE_DISABLE_AUTO_MEMORY: runEnv.CLAUDE_CODE_DISABLE_AUTO_MEMORY || null,
          MCP_TIMEOUT: runEnv.MCP_TIMEOUT || null,
          MAX_MCP_OUTPUT_TOKENS: runEnv.MAX_MCP_OUTPUT_TOKENS || null,
          api_key_env_stripped: true
        }
      },
      null,
      2
    )
  );

  if (selectedUseTmux) {
    const result = spawnSync(runCommand, runArgs, { encoding: "utf8" });
    if (result.status !== 0) {
      run.status = "failed";
      fs.appendFileSync(files.stderr, result.stderr || result.stdout || "tmux start failed\n");
      writeState(run);
      writeReport(run);
      throw new Error(`tmux failed to start Claude run: ${shortText(result.stderr || result.stdout, 600)}`);
    }
    const ready = tmuxWait(tmuxStartChannel, 5000);
    if (ready.status !== 0) {
      spawnSync("tmux", ["kill-session", "-t", tmuxSession], { encoding: "utf8" });
      run.status = "failed";
      fs.appendFileSync(files.stderr, ready.stderr || ready.error || "tmux pane did not reach ready channel\n");
      writeState(run);
      writeReport(run);
      throw new Error(`tmux Claude run did not reach ready channel: ${shortText(ready.stderr || ready.error || "", 600)}`);
    }
    const pipe = spawnSync(
      "tmux",
      ["pipe-pane", "-o", "-t", tmuxTarget, `cat >> ${shellQuote(files.tmuxPane)}`],
      { encoding: "utf8" }
    );
    if (pipe.status !== 0) {
      spawnSync("tmux", ["kill-session", "-t", tmuxSession], { encoding: "utf8" });
      run.status = "failed";
      fs.appendFileSync(files.stderr, pipe.stderr || pipe.stdout || "tmux pipe-pane failed\n");
      writeState(run);
      writeReport(run);
      throw new Error(`tmux pipe-pane failed: ${shortText(pipe.stderr || pipe.stdout, 600)}`);
    }
    if (!tmuxSignal(tmuxGoChannel)) {
      spawnSync("tmux", ["kill-session", "-t", tmuxSession], { encoding: "utf8" });
      run.status = "failed";
      fs.appendFileSync(files.stderr, "tmux failed to signal Claude run start\n");
      writeState(run);
      writeReport(run);
      throw new Error("tmux failed to signal Claude run start.");
    }
    run.pid = null;
    run.managed = false;
    jsonLine(files.events, { type: "tmux_start", session: tmuxSession, target: tmuxTarget });
    jsonLine(files.events, { type: "tmux_pipe_pane", file: files.tmuxPane });
    writeState(run);
    writeReport(run);
    return {
      run_id: runId,
      pid: null,
      profile,
      cwd,
      log_dir: logDir,
      status: run.status,
      use_tmux: true,
      tmux_session: tmuxSession,
      tmux_target: tmuxTarget
    };
  }

  const child = spawn(runCommand, runArgs, {
    cwd,
    env: runEnv,
    detached: true,
    stdio: ["ignore", "pipe", "pipe"]
  });
  run.child = child;
  run.pid = child.pid;
  run.processGroupPid = child.pid;
  const commandRecord = safeReadJson(files.command, {});
  commandRecord.process_group_pid = run.processGroupPid;
  writeJsonAtomic(files.command, commandRecord);
  activeRuns.set(runId, run);
  writeState(run);

  let stdoutBuffer = "";
  child.stdout.on("data", (chunk) => {
    const text = chunk.toString();
    fs.appendFileSync(files.stdout, text);
    stdoutBuffer += text;
    const lines = stdoutBuffer.split(/\r?\n/);
    stdoutBuffer = lines.pop() || "";
    for (const line of lines.filter(Boolean)) {
      try {
        const event = JSON.parse(line);
        if ((event.session_id || event.sessionId) && !run.sessionId) {
          run.sessionId = event.session_id || event.sessionId;
          writeState(run);
        }
        jsonLine(files.events, event);
      } catch {
        jsonLine(files.events, { type: "stdout", raw: line });
      }
    }
  });

  child.stderr.on("data", (chunk) => {
    const text = chunk.toString();
    fs.appendFileSync(files.stderr, text);
    for (const line of text.split(/\r?\n/).filter(Boolean)) {
      jsonLine(files.events, { type: "stderr", raw: line });
    }
  });

  child.on("error", (error) => {
    run.status = "failed";
    run.error = error.message;
    jsonLine(files.events, { type: "process_error", error: error.message });
    markTerminal(run);
    writeState(run);
    writeReport(run);
  });

  child.on("close", (code, signal) => {
    if (stdoutBuffer.trim()) {
      jsonLine(files.events, { type: "stdout", raw: stdoutBuffer.trim() });
    }
    const diskStatus = safeReadJson(run.stateFile, {})?.status;
    run.status = run.status === "killing" || diskStatus === "killing" ? "killed" : code === 0 ? "completed" : "failed";
    run.exitCode = code;
    run.signal = signal;
    run.orphanReason = null;
    markTerminal(run);
    writeState(run);
    writeReport(run);
  });

  writeReport(run);
  return {
    run_id: runId,
    pid: child.pid,
    profile,
    cwd,
    log_dir: logDir,
    status: run.status,
    use_tmux: false
  };
}

export function getRun(runId) {
  const active = activeRuns.get(runId);
  if (active) return active;

  const logDir = path.join(RUNS_DIR, runId);
  const files = filesForLogDir(logDir);
  if (fs.existsSync(files.state)) {
    return refreshInactiveRun(buildRunFromState(runId, logDir, safeReadJson(files.state, {})));
  }
  if (fs.existsSync(files.report)) {
    return buildRunFromLegacyReport(runId, logDir, safeReadJson(files.report, {}));
  }
  throw new Error(`Unknown run_id: ${runId}`);
}

export function peekRun(runId, { limit = 12, cursor = 0 } = {}) {
  const run = getRun(runId);
  const events = readRunEvents(run);
  const report = buildReport(run);
  const nextCursor = events.length;
  const relayUpdates = summarizeMilestones(events, limit, { cursor, includeSessions: false });
  return {
    run_id: runId,
    status: run.status,
    managed: report.managed,
    orphan_reason: report.orphan_reason,
    cursor: Math.max(0, Number(cursor) || 0),
    next_cursor: nextCursor,
    milestones: summarizeMilestones(events, limit),
    relay_updates: relayUpdates,
    chat_relay: buildPeekChatRelay(relayUpdates, nextCursor),
    activity: activitySummary(events, run, { limit, cursor }),
    tmux_capture: tmuxCapturePane(run),
    warnings: report.warnings,
    log_dir: run.logDir
  };
}

function waitForTmuxRun(runId, timeoutMs) {
  let run = getRun(runId);
  if (!WAITABLE_STATUSES.has(run.status)) return writeReport(run);
  if (fs.existsSync(run.exitCodeFile)) return writeReport(refreshTmuxRun(run));

  const wait = tmuxWait(run.tmuxDoneChannel, timeoutMs);
  run = getRun(runId);
  if (fs.existsSync(run.exitCodeFile)) return writeReport(refreshTmuxRun(run));
  if (!WAITABLE_STATUSES.has(run.status)) return writeReport(run);

  return {
    ...buildReport(run),
    status: run.status,
    timed_out: true,
    wait_error: wait.error || null
  };
}

export function waitRun(runId, { timeoutMs = 120000 } = {}) {
  const run = getRun(runId);
  if (!WAITABLE_STATUSES.has(run.status)) {
    return Promise.resolve(writeReport(run));
  }
  if (run.useTmux) {
    return Promise.resolve(waitForTmuxRun(runId, timeoutMs));
  }
  if (!run.child) {
    return Promise.resolve(writeReport(refreshInactiveRun(run)));
  }
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      resolve({ ...buildReport(run), status: run.status, timed_out: true });
    }, timeoutMs);
    run.child.once("close", () => {
      clearTimeout(timer);
      resolve(writeReport(refreshInactiveRun(run)));
    });
  });
}

export function killRun(runId) {
  const run = getRun(runId);
  if (run.useTmux) {
    if (tmuxHasSession(run.tmuxSession)) {
      const killed = spawnSync("tmux", ["kill-session", "-t", run.tmuxSession], { encoding: "utf8" });
      if (killed.status !== 0) {
        run.orphanReason = shortText(killed.stderr || killed.stdout || "tmux kill-session failed", 600);
        writeState(run);
        writeReport(run);
        return { run_id: runId, status: run.status, killed: false, reason: run.orphanReason };
      }
      run.status = "killed";
      markTerminal(run);
      run.orphanReason = "Kill sent to saved tmux session.";
      writeState(run);
      writeReport(run);
      return { run_id: runId, status: run.status, killed: true, tmux_session: run.tmuxSession };
    }
    run.status = fs.existsSync(run.exitCodeFile) ? run.status : run.status === "killing" ? "killed" : "orphaned";
    markTerminal(run);
    run.orphanReason =
      run.status === "killed" ? "tmux session is already gone after kill request." : "tmux session is not alive.";
    writeState(run);
    writeReport(run);
    return { run_id: runId, status: run.status, killed: false, reason: run.orphanReason };
  }
  if (!run.child && ["completed", "failed", "killed"].includes(run.status)) {
    const signal = run.status === "killed" ? "SIGKILL" : "SIGTERM";
    const match = processMatchesRun(run);
    if (!match.alive || !match.matched) {
      return {
        run_id: runId,
        status: run.status,
        killed: false,
        reason: match.alive ? "Process group is alive, but no run fingerprint matched." : "No live process group remains for this terminal run."
      };
    }
    run.status = "killing";
    run.orphanReason =
      signal === "SIGKILL"
        ? "Hard kill sent to fingerprint-matched process group that survived killed status."
        : "Kill sent to fingerprint-matched process group that survived terminal status.";
    writeState(run);
    writeReport(run);
    const signaled = signalMatchedProcessGroup(match, signal);
    if (!signaled.signaled) {
      run.orphanReason = signaled.error || "Failed to signal fingerprint-matched process group.";
      writeState(run);
      writeReport(run);
      return { run_id: runId, status: run.status, killed: false, reason: run.orphanReason };
    }
    return { run_id: runId, status: run.status, killed: true };
  }
  if (run.status === "running" && run.child) {
    const match = processMatchesRun(run);
    if (!match.alive || !match.matched) {
      run.orphanReason = match.error || "Process group did not match this run fingerprint.";
      writeState(run);
      writeReport(run);
      return { run_id: runId, status: run.status, killed: false, reason: run.orphanReason };
    }
    run.status = "killing";
    run.orphanReason = "Kill sent conservatively to fingerprint-matched process group.";
    writeState(run);
    writeReport(run);
    const signaled = signalMatchedProcessGroup(match);
    if (!signaled.signaled) {
      run.orphanReason = signaled.error || "Failed to signal fingerprint-matched process group.";
      writeState(run);
      writeReport(run);
      return { run_id: runId, status: run.status, killed: false, reason: run.orphanReason };
    }
    return { run_id: runId, status: run.status, killed: true };
  }

  if (["running_orphaned", "orphaned", "killing"].includes(run.status)) {
    const signal = run.status === "killing" ? "SIGKILL" : "SIGTERM";
    const match = processMatchesRun(run);
    if (!match.alive || !match.matched) {
      run.status = match.alive ? "orphaned" : run.status === "killing" ? "killed" : "orphaned";
      markTerminal(run);
      run.orphanReason = match.alive
        ? match.error || "PID is alive, but ps args do not contain this run directory or debug.log fingerprint."
        : run.status === "killed"
          ? "Kill was already requested and saved process group is not alive."
          : "Saved PID is not alive.";
      writeState(run);
      writeReport(run);
      return { run_id: runId, status: run.status, killed: false, reason: run.orphanReason };
    }
    run.status = "killing";
    run.orphanReason =
      signal === "SIGKILL"
        ? "Hard kill sent to fingerprint-matched process group after it stayed in killing."
        : "Kill sent conservatively to fingerprint-matched process group.";
    writeState(run);
    writeReport(run);
    const signaled = signalMatchedProcessGroup(match, signal);
    if (!signaled.signaled) {
      run.orphanReason = signaled.error || "Failed to signal fingerprint-matched process group.";
      writeState(run);
      writeReport(run);
      return { run_id: runId, status: run.status, killed: false, reason: run.orphanReason };
    }
    return { run_id: runId, status: run.status, killed: true };
  }

  return { run_id: runId, status: run.status, killed: false };
}

export function resultRun(runId) {
  const run = getRun(runId);
  return writeReport(run);
}

export function profiles() {
  return listProfiles();
}

export function doctor() {
  const { command, prefixArgs } = resolveClaudeCommand();
  const version = spawnSync(command, [...prefixArgs, "--version"], { encoding: "utf8" });
  const help = spawnSync(command, [...prefixArgs, "--help"], { encoding: "utf8" });
  const npm = spawnSync("npm", ["--version"], { encoding: "utf8" });
  const node = process.version;
  const helpText = `${help.stdout || ""}\n${help.stderr || ""}`;
  const requiredFlags = [
    "--model",
    "--dangerously-skip-permissions",
    "--output-format",
    "--include-partial-messages",
    "--include-hook-events",
    "--debug-file",
    "--disable-slash-commands",
    "--verbose",
    "--max-turns",
    "--system-prompt-file",
    "--append-system-prompt-file",
    "--permission-prompt-tool",
    "--permission-mode",
    "--json-schema",
    "--agent",
    "--agents",
    "--setting-sources",
    "--settings",
    "--strict-mcp-config",
    "--allowedTools",
    "--disallowedTools",
    "--add-dir",
    "--plugin-dir",
    "--plugin-url",
    "--allow-dangerously-skip-permissions",
    "--brief",
    "--file",
    "--input-format",
    "--replay-user-messages",
    "--fallback-model",
    "--max-budget-usd",
    "--no-session-persistence",
    "--fork-session",
    "--name"
  ];
  return {
    ok: version.status === 0 && help.status === 0,
    claude_command: commandSummary(command, prefixArgs),
    claude_version: shortText(version.stdout || version.stderr),
    node,
    npm_version: shortText(npm.stdout || npm.stderr),
    stream_json_supported: helpText.includes("stream-json"),
    opus_requested_by_profiles: MODEL,
    flags: Object.fromEntries(requiredFlags.map((flag) => [flag, helpText.includes(flag)])),
    mcp_server: "stdio",
    note: "This check is read-only and does not register global MCP config."
  };
}

export function discoverSkills({ cwd = process.cwd() } = {}) {
  const home = os.homedir();
  const candidates = [
    path.join(cwd, ".claude"),
    path.join(cwd, ".claude", "skills"),
    path.join(home, ".claude", "skills"),
    path.join(home, ".claude", "marketplaces"),
    path.join(home, ".claude", "plugins", "cache"),
    path.join(home, ".claude", "CLAUDE.md"),
    path.join(home, ".claude", "settings.json"),
    path.join(home, ".claude", "settings.local.json")
  ];
  return candidates.map((candidate) => ({
    path: candidate,
    exists: fs.existsSync(candidate),
    type: fs.existsSync(candidate) ? (fs.statSync(candidate).isDirectory() ? "directory" : "file") : "missing"
  }));
}

function strictStreamToolEvidence(events, targetPath) {
  return events.filter((event) => {
    const normalized = normalizeEvent(event);
    return (
      normalized &&
      ["tool_use", "tool_result"].includes(normalized.kind) &&
      eventMentionsPath(event, targetPath)
    );
  });
}

function strictDebugEvidence(debugFile, targetPath) {
  if (!fs.existsSync(debugFile)) return [];
  const text = fs.readFileSync(debugFile, "utf8");
  if (!text.includes(targetPath)) return [];
  if (!/(tool|read|file_path|bash)/iu.test(text)) return [];
  return [{ type: "debug", text: shortText(text, 500) }];
}

export async function auditSkill({ skillPath, prompt, cwd = process.cwd(), timeoutMs = 120000 }) {
  if (!skillPath) {
    throw new Error("claude_audit_skill requires skillPath.");
  }
  const resolvedSkillPath = path.resolve(cwd, skillPath);
  const auditPrompt = [
    prompt || "Audit this Claude skill/control file.",
    "",
    `Target path: ${resolvedSkillPath}`,
    "First read the target path with tools. Then summarize only what the file actually says."
  ].join("\n");
  const started = startRun({
    prompt: auditPrompt,
    profile: "skill-audit",
    cwd,
    title: `skill-audit ${resolvedSkillPath}`
  });
  const report = await waitRun(started.run_id, { timeoutMs });
  const events = readJsonLines(report.files.events);
  const streamEvidence = strictStreamToolEvidence(events, resolvedSkillPath);
  const debugEvidence = strictDebugEvidence(report.files.debug, resolvedSkillPath);
  const toolEvidence = [...streamEvidence, ...debugEvidence];
  const selfReportOnly =
    events.some((event) => eventMentionsPath(event, resolvedSkillPath)) && toolEvidence.length === 0;
  const evidence = toolEvidence.length ? "passed" : selfReportOnly ? "unknown" : "failed";
  const audit = {
    evidence,
    reason:
      evidence === "passed"
        ? "Tool/debug/stream evidence includes a tool-like event and the exact target path."
        : evidence === "unknown"
          ? "The target path appears only in message-like output, not strict tool/debug evidence."
          : "No strict tool/debug/stream evidence mentioned the target path.",
    target_path: resolvedSkillPath,
    run: report,
    matching_events: toolEvidence.slice(0, 10)
  };
  fs.writeFileSync(path.join(started.log_dir, "skill-audit.json"), JSON.stringify(audit, null, 2));
  return audit;
}

export function cleanupRuns({ olderThanDays = DEFAULT_CLEANUP_DAYS, confirm = false } = {}) {
  ensureDir(RUNS_DIR);
  const cutoffMs = Date.now() - Number(olderThanDays) * 24 * 60 * 60 * 1000;
  const entries = fs
    .readdirSync(RUNS_DIR, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith("_"));
  const candidates = [];

  for (const entry of entries) {
    const runId = entry.name;
    const runDir = path.join(RUNS_DIR, runId);
    const state = safeReadJson(path.join(runDir, "state.json"), {});
    const stat = fs.statSync(runDir);
    const startedAtMs = state.started_at ? Date.parse(state.started_at) : Number.NaN;
    const ageBaseMs = Number.isFinite(startedAtMs) ? startedAtMs : stat.mtimeMs;
    if (ageBaseMs > cutoffMs) continue;
    const ageDays = Math.floor((Date.now() - ageBaseMs) / (24 * 60 * 60 * 1000));
    candidates.push({
      run_id: runId,
      path: runDir,
      age_days: ageDays,
      status: state.status || "unknown"
    });
  }

  if (confirm) {
    for (const candidate of candidates) {
      fs.rmSync(candidate.path, { recursive: true, force: true });
    }
  }

  return {
    olderThanDays: Number(olderThanDays),
    dry_run: !confirm,
    deleted_count: confirm ? candidates.length : 0,
    candidates
  };
}
