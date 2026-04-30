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

function jsonLine(file, value) {
  fs.appendFileSync(file, `${JSON.stringify(value)}\n`);
}

function safeReadJson(file, fallback = null) {
  try {
    if (!fs.existsSync(file)) return fallback;
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return fallback;
  }
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

function filesForLogDir(logDir) {
  return {
    prompt: path.join(logDir, "prompt.txt"),
    profile: path.join(logDir, "profile.json"),
    command: path.join(logDir, "command.json"),
    events: path.join(logDir, "events.ndjson"),
    stdout: path.join(logDir, "stdout.log"),
    stderr: path.join(logDir, "stderr.log"),
    debug: path.join(logDir, "debug.log"),
    report: path.join(logDir, "report.json"),
    state: path.join(logDir, "state.json")
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

function claudeHelpText() {
  const { command, prefixArgs } = resolveClaudeCommand();
  const help = spawnSync(command, [...prefixArgs, "--help"], { encoding: "utf8" });
  return `${help.stdout || ""}\n${help.stderr || ""}`;
}

function assertSupportedOptions(options) {
  const requestedFlags = [
    ["maxTurns", "--max-turns"],
    ["systemPromptFile", "--system-prompt-file"],
    ["appendSystemPromptFile", "--append-system-prompt-file"],
    ["permissionPromptTool", "--permission-prompt-tool"]
  ].filter(([key]) => options[key]);

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
  settings,
  settingSources,
  tools,
  allowedTools,
  disallowedTools,
  addDir,
  pluginDir
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
    events: run.eventsFile,
    stdout: run.stdoutFile,
    stderr: run.stderrFile,
    debug: run.debugFile,
    report: run.reportFile,
    state: run.stateFile
  };
}

function writeState(run) {
  const state = {
    run_id: run.runId,
    profile: run.profileName,
    model: MODEL,
    cwd: run.cwd,
    pid: run.child?.pid ?? run.pid ?? null,
    status: run.status,
    exit_code: run.exitCode ?? null,
    signal: run.signal ?? null,
    session_id: run.sessionId ?? null,
    started_at: run.startedAt,
    updated_at: new Date().toISOString(),
    command: run.commandSummary,
    log_dir: run.logDir,
    files: runFiles(run),
    orphan_reason: run.orphanReason || null
  };
  fs.writeFileSync(run.stateFile, JSON.stringify(state, null, 2));
  return state;
}

function pidArgs(pid) {
  if (!pid) return "";
  const result = spawnSync("ps", ["-p", String(pid), "-o", "args="], { encoding: "utf8" });
  if (result.status !== 0) return "";
  return result.stdout.trim();
}

function processMatchesRun(run) {
  const args = pidArgs(run.pid);
  if (!args) {
    return { alive: false, matched: false, args: "" };
  }
  const fingerprints = [run.debugFile, run.logDir].filter(Boolean);
  const matched = fingerprints.some((fingerprint) => args.includes(fingerprint));
  return { alive: true, matched, args };
}

function refreshInactiveRun(run) {
  if (!["running", "killing", "running_orphaned"].includes(run.status)) return run;
  const match = processMatchesRun(run);
  run.managed = false;
  if (match.alive && match.matched) {
    run.status = "running_orphaned";
    run.orphanReason = "Process is alive and fingerprint matches this run, but current MCP server does not own the child handle.";
  } else if (match.alive) {
    run.status = "orphaned";
    run.orphanReason = "Saved PID is alive, but ps args do not contain this run directory or debug.log fingerprint.";
  } else {
    run.status = "orphaned";
    run.orphanReason = "Saved PID is not alive; previous MCP server likely exited before recording completion.";
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
    eventsFile: files.events,
    stdoutFile: files.stdout,
    stderrFile: files.stderr,
    debugFile: files.debug,
    reportFile: files.report,
    stateFile: files.state || path.join(logDir, "state.json"),
    commandSummary: state.command || [],
    status: state.status || "completed_unknown",
    exitCode: state.exit_code ?? null,
    signal: state.signal ?? null,
    sessionId: state.session_id ?? null,
    startedAt: state.started_at || null,
    pid: state.pid ?? null,
    child: null,
    managed: false,
    orphanReason: state.orphan_reason || null
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
    eventsFile: files.events,
    stdoutFile: files.stdout,
    stderrFile: files.stderr,
    debugFile: files.debug,
    reportFile: files.report || path.join(logDir, "report.json"),
    stateFile: files.state || path.join(logDir, "state.json"),
    commandSummary: report.command || [],
    status,
    exitCode: report.exit_code ?? null,
    signal: report.signal ?? null,
    sessionId: report.session_id ?? null,
    startedAt: null,
    pid: report.pid ?? null,
    child: null,
    managed: false,
    orphanReason: status === "completed_unknown" ? "Legacy run has no durable state.json." : null
  };
}

function buildReport(run) {
  const events = readJsonLines(run.eventsFile);
  const warnings = detectWarnings(events, run.cwd);
  const milestones = summarizeMilestones(events);

  return {
    run_id: run.runId,
    profile: run.profileName,
    model: MODEL,
    cwd: run.cwd,
    pid: run.child?.pid ?? run.pid ?? null,
    status: run.status,
    managed: Boolean(run.child) || Boolean(run.managed),
    orphan_reason: run.orphanReason || null,
    exit_code: run.exitCode ?? null,
    signal: run.signal ?? null,
    session_id: run.sessionId ?? null,
    log_dir: run.logDir,
    command: run.commandSummary,
    warnings,
    milestones,
    events: milestones,
    chat_relay: buildFinalChatRelay(events),
    final_output_summary: finalOutputSummary(events),
    files: runFiles(run)
  };
}

function writeReport(run) {
  const report = buildReport(run);
  fs.writeFileSync(run.reportFile, JSON.stringify(report, null, 2));
  return report;
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
    settings,
    settingSources,
    tools,
    allowedTools,
    disallowedTools,
    addDir,
    pluginDir
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
    ...(profileConfig.env || {}),
    ...(options.env || {})
  };
  if (options.disableAutoMemory) {
    runEnv.CLAUDE_CODE_DISABLE_AUTO_MEMORY = "1";
  }
  if (options.mcpTimeout) {
    runEnv.MCP_TIMEOUT = String(options.mcpTimeout);
  }
  if (options.maxMcpOutputTokens) {
    runEnv.MAX_MCP_OUTPUT_TOKENS = String(options.maxMcpOutputTokens);
  }
  const args = [
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
      settings,
      settingSources,
      tools,
      allowedTools,
      disallowedTools,
      addDir,
      pluginDir
    })
  ];
  const summary = commandSummary(command, args);
  fs.writeFileSync(
    files.command,
    JSON.stringify(
      {
        command,
        args,
        summary,
        cwd,
        title,
        env: {
          CLAUDE_CODE_DISABLE_AUTO_MEMORY: runEnv.CLAUDE_CODE_DISABLE_AUTO_MEMORY || null,
          MCP_TIMEOUT: runEnv.MCP_TIMEOUT || null,
          MAX_MCP_OUTPUT_TOKENS: runEnv.MAX_MCP_OUTPUT_TOKENS || null
        }
      },
      null,
      2
    )
  );

  const run = {
    runId,
    profileName: profile,
    cwd,
    logDir,
    promptFile: files.prompt,
    profileFile: files.profile,
    commandFile: files.command,
    eventsFile: files.events,
    stdoutFile: files.stdout,
    stderrFile: files.stderr,
    debugFile: files.debug,
    reportFile: files.report,
    stateFile: files.state,
    commandSummary: summary,
    status: "running",
    exitCode: null,
    signal: null,
    sessionId: null,
    startedAt: new Date().toISOString(),
    child: null,
    managed: true,
    orphanReason: null
  };

  const child = spawn(command, args, {
    cwd,
    env: runEnv,
    stdio: ["ignore", "pipe", "pipe"]
  });
  run.child = child;
  run.pid = child.pid;
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
    writeState(run);
    writeReport(run);
  });

  child.on("close", (code, signal) => {
    if (stdoutBuffer.trim()) {
      jsonLine(files.events, { type: "stdout", raw: stdoutBuffer.trim() });
    }
    run.status = code === 0 ? "completed" : "failed";
    run.exitCode = code;
    run.signal = signal;
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
    status: run.status
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
  const events = readJsonLines(run.eventsFile);
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
    warnings: report.warnings,
    log_dir: run.logDir
  };
}

export function waitRun(runId, { timeoutMs = 120000 } = {}) {
  const run = getRun(runId);
  if (run.status !== "running") {
    return Promise.resolve(writeReport(run));
  }
  if (!run.child) {
    return Promise.resolve(writeReport(refreshInactiveRun(run)));
  }
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      resolve({ ...buildReport(run), status: "running", timed_out: true });
    }, timeoutMs);
    run.child.once("close", () => {
      clearTimeout(timer);
      resolve(writeReport(run));
    });
  });
}

export function killRun(runId) {
  const run = getRun(runId);
  if (run.status === "running" && run.child) {
    run.child.kill("SIGTERM");
    run.status = "killing";
    writeState(run);
    writeReport(run);
    return { run_id: runId, status: run.status, killed: true };
  }

  if (["running_orphaned", "orphaned", "killing"].includes(run.status)) {
    const match = processMatchesRun(run);
    if (!match.alive) {
      run.status = "orphaned";
      run.orphanReason = "Saved PID is not alive.";
      writeState(run);
      writeReport(run);
      return { run_id: runId, status: run.status, killed: false, reason: run.orphanReason };
    }
    if (!match.matched) {
      run.status = "orphaned";
      run.orphanReason = "PID is alive, but ps args do not contain this run directory or debug.log fingerprint.";
      writeState(run);
      writeReport(run);
      return { run_id: runId, status: run.status, killed: false, reason: run.orphanReason };
    }
    process.kill(run.pid, "SIGTERM");
    run.status = "killing";
    run.orphanReason = "Kill sent conservatively by saved PID after fingerprint match.";
    writeState(run);
    writeReport(run);
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
    "--bare",
    "--verbose",
    "--max-turns",
    "--system-prompt-file",
    "--append-system-prompt-file",
    "--permission-prompt-tool",
    "--setting-sources",
    "--settings",
    "--strict-mcp-config",
    "--allowedTools",
    "--disallowedTools",
    "--add-dir",
    "--plugin-dir",
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
