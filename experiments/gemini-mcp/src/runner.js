import { execFile, spawn, spawnSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import fs from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(__dirname, "..");
export const RUNS_DIR = path.join(ROOT, "runs");
export const DEFAULT_MODEL = "gemini-3.1-pro-preview";
export const DEFAULT_ANTIGRAVITY_MODEL = "gemini-3.5-flash";
export const DEFAULT_ANTIGRAVITY_MODEL_LABEL = "Gemini 3.5 Flash (High)";
export const DEFAULT_THINKING_LEVEL = "high";
export const THINKING_LEVELS = ["minimal", "low", "medium", "high"];
export const BACKENDS = ["auto", "cli", "antigravity"];
export const APPROVAL_MODES = ["default", "auto_edit", "yolo", "plan"];
export const DEFAULT_CLI_TIMEOUT_MS = 50000;
export const DEFAULT_CLEANUP_DAYS = 14;
const PREFERRED_GEMINI_CLI_PATH = "/Users/triton/.local/bin/gemini";
const PREFERRED_ANTIGRAVITY_CLI_PATH = "/Users/triton/.local/bin/agy";
const execFileAsync = promisify(execFile);
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

function jsonLine(file, value) {
  const event =
    value && typeof value === "object" && !Array.isArray(value)
      ? { observed_at: new Date().toISOString(), ...value }
      : value;
  fs.appendFileSync(file, `${JSON.stringify(event)}\n`);
}

function safeRead(file, fallback = "") {
  try {
    return fs.existsSync(file) ? fs.readFileSync(file, "utf8") : fallback;
  } catch {
    return fallback;
  }
}

function safeReadJson(file, fallback = null) {
  try {
    return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : fallback;
  } catch {
    return fallback;
  }
}

function writeJsonAtomic(file, value) {
  const tmp = `${file}.${process.pid}.${randomUUID().slice(0, 8)}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(value, null, 2));
  fs.renameSync(tmp, file);
}

function listFromValue(value) {
  if (!value) return [];
  const values = Array.isArray(value) ? value : String(value).split(",");
  return values.map((item) => String(item).trim()).filter(Boolean);
}

function shortText(value, max = 600) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  return text.length > max ? `${text.slice(0, max - 3)}...` : text;
}

function trimText(value, limit = 4000) {
  if (!value || value.length <= limit) return value || "";
  return `${value.slice(0, limit)}\n...[truncated]`;
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function commandSummary(command, args) {
  return [command, ...args].map((part) => {
    if (/[\s"']/u.test(part)) return JSON.stringify(part);
    return part;
  });
}

function accountCliEnv() {
  const env = { ...process.env };
  delete env.GEMINI_API_KEY;
  delete env.GOOGLE_API_KEY;
  delete env.GOOGLE_APPLICATION_CREDENTIALS;
  delete env.GOOGLE_GENAI_USE_VERTEXAI;
  delete env.GOOGLE_CLOUD_PROJECT;
  delete env.GOOGLE_CLOUD_LOCATION;
  return env;
}

function envFlag(name) {
  return ["1", "true", "yes"].includes((process.env[name] || "").trim().toLowerCase());
}

function requestedBackend() {
  const backend = process.env.GEMINI_MCP_BACKEND || "auto";
  if (!BACKENDS.includes(backend)) {
    throw new Error(`GEMINI_MCP_BACKEND must be one of: ${BACKENDS.join(", ")}.`);
  }
  return backend;
}

function defaultGeminiCliCommand() {
  if (process.env.GEMINI_CLI_PATH) return process.env.GEMINI_CLI_PATH;
  if (fs.existsSync(PREFERRED_GEMINI_CLI_PATH)) return PREFERRED_GEMINI_CLI_PATH;
  return "gemini";
}

function defaultAntigravityCliCommand() {
  if (process.env.ANTIGRAVITY_CLI_PATH) return process.env.ANTIGRAVITY_CLI_PATH;
  if (fs.existsSync(PREFERRED_ANTIGRAVITY_CLI_PATH)) return PREFERRED_ANTIGRAVITY_CLI_PATH;
  return "agy";
}

function geminiCliConfig() {
  return {
    command: defaultGeminiCliCommand(),
    preferredCommand: PREFERRED_GEMINI_CLI_PATH,
    preferredCommandPresent: fs.existsSync(PREFERRED_GEMINI_CLI_PATH),
    oauthFilePresent: fs.existsSync(path.join(homedir(), ".gemini", "oauth_creds.json"))
  };
}

function antigravityCliConfig() {
  return {
    command: defaultAntigravityCliCommand(),
    preferredCommand: PREFERRED_ANTIGRAVITY_CLI_PATH,
    preferredCommandPresent: fs.existsSync(PREFERRED_ANTIGRAVITY_CLI_PATH),
    appDataDirPresent: fs.existsSync(path.join(homedir(), ".gemini", "antigravity-cli")),
    projectConfigDirPresent: fs.existsSync(path.join(process.cwd(), ".antigravitycli"))
  };
}

export async function geminiCliVersion(command = geminiCliConfig().command) {
  try {
    const { stdout } = await execFileAsync(command, ["--version"], { timeout: 5000 });
    return stdout.trim() || "unknown";
  } catch {
    return null;
  }
}

export async function antigravityCliVersion(command = antigravityCliConfig().command) {
  try {
    const { stdout } = await execFileAsync(command, ["--version"], { timeout: 5000 });
    return stdout.trim() || "unknown";
  } catch {
    return null;
  }
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

function inferBackend() {
  const requested = requestedBackend();
  const cli = geminiCliConfig();
  const antigravity = antigravityCliConfig();
  const hasAntigravityCli = Boolean(antigravity.preferredCommandPresent || antigravity.appDataDirPresent);

  if (requested === "cli") return "gemini-cli";
  if (requested === "antigravity") return "antigravity-cli";
  if (hasAntigravityCli && antigravity.appDataDirPresent) return "antigravity-cli";
  if (cli.oauthFilePresent) return "gemini-cli";
  return null;
}

function defaultModel() {
  return process.env.GEMINI_MODEL || DEFAULT_MODEL;
}

function defaultAntigravityModel() {
  return process.env.GEMINI_MODEL || DEFAULT_ANTIGRAVITY_MODEL;
}

function defaultAntigravityModelLabel() {
  return process.env.ANTIGRAVITY_MODEL_LABEL || DEFAULT_ANTIGRAVITY_MODEL_LABEL;
}

function defaultThinkingLevel() {
  return process.env.GEMINI_THINKING_LEVEL || DEFAULT_THINKING_LEVEL;
}

function defaultCliApprovalMode() {
  const value = process.env.GEMINI_CLI_APPROVAL_MODE || "yolo";
  if (!APPROVAL_MODES.includes(value)) {
    throw new Error(`GEMINI_CLI_APPROVAL_MODE must be one of: ${APPROVAL_MODES.join(", ")}.`);
  }
  return value;
}

function defaultCliIncludeDirectories() {
  return listFromValue(process.env.GEMINI_CLI_INCLUDE_DIRECTORIES);
}

function defaultCliTimeoutMs() {
  const raw = process.env.GEMINI_CLI_TIMEOUT_MS;
  if (!raw) return DEFAULT_CLI_TIMEOUT_MS;
  const value = Number(raw);
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error("GEMINI_CLI_TIMEOUT_MS must be a positive integer.");
  }
  return value;
}

function validateThinkingLevel(value) {
  if (!THINKING_LEVELS.includes(value)) {
    throw new Error(`thinkingLevel must be one of: ${THINKING_LEVELS.join(", ")}.`);
  }
  return value;
}

function summarizeCliStderr(stderr) {
  const value = stderr.trim();
  if (!value) return null;
  const firstLine = value.split(/\r?\n/u).find(Boolean);
  const status = value.match(/"status":\s*"([^"]+)"/u)?.[1];
  const message = value.match(/"message":\s*"([^"]+)"/u)?.[1];
  return trimText(
    [firstLine, status && `status=${status}`, message && `message=${message}`]
      .filter(Boolean)
      .join(" | "),
    600
  );
}

function buildCliPrompt(prompt, systemInstruction) {
  if (!systemInstruction) return prompt;
  return `System instruction:\n${systemInstruction}\n\nUser prompt:\n${prompt}`;
}

function parseCliResponse(stdout) {
  const text = stdout.trim();
  if (!text) return "";
  const jsonStart = text.lastIndexOf("\n{");
  const candidate = jsonStart >= 0 ? text.slice(jsonStart + 1) : text;
  try {
    const parsed = JSON.parse(candidate);
    if (typeof parsed.response === "string") return parsed.response;
  } catch {
    // Fall through to plain text output.
  }
  return text;
}

function requireNonEmptyText(text, source) {
  if (!text || !text.trim()) {
    throw new Error(
      `${source} returned empty text. Treat this as a failed Gemini call and recover instead of accepting success.`
    );
  }
  return text;
}

function selectedCliOptions({
  prompt,
  model,
  systemInstruction,
  thinkingLevel,
  temperature,
  maxOutputTokens,
  cwd,
  includeDirectories,
  approvalMode,
  timeoutMs
}) {
  const selectedThinkingLevel = validateThinkingLevel(thinkingLevel || defaultThinkingLevel());
  const selectedApprovalMode = approvalMode || defaultCliApprovalMode();
  if (!APPROVAL_MODES.includes(selectedApprovalMode)) {
    throw new Error(`approvalMode must be one of: ${APPROVAL_MODES.join(", ")}.`);
  }
  const unsupported = [];
  if (temperature !== undefined) unsupported.push("temperature");
  if (maxOutputTokens !== undefined) unsupported.push("maxOutputTokens");
  unsupported.push("thinkingLevel");

  return {
    model: model || defaultModel(),
    thinkingLevel: selectedThinkingLevel,
    cwd: cwd || process.cwd(),
    includeDirectories: [...defaultCliIncludeDirectories(), ...listFromValue(includeDirectories)],
    approvalMode: selectedApprovalMode,
    timeoutMs: timeoutMs || defaultCliTimeoutMs(),
    prompt: buildCliPrompt(prompt, systemInstruction),
    warnings: [`Gemini CLI backend does not expose first-class MCP controls for: ${unsupported.join(", ")}.`]
  };
}

function buildCliArgs(options) {
  const args = [
    "-m",
    options.model,
    "-p",
    options.prompt,
    "--skip-trust",
    "--approval-mode",
    options.approvalMode,
    "--output-format",
    "json"
  ];
  for (const directory of options.includeDirectories) {
    args.push("--include-directories", directory);
  }
  return args;
}

function goDuration(timeoutMs) {
  return `${timeoutMs}ms`;
}

function selectedAntigravityOptions({
  prompt,
  model,
  systemInstruction,
  thinkingLevel,
  temperature,
  maxOutputTokens,
  cwd,
  includeDirectories,
  approvalMode,
  timeoutMs
}) {
  const selectedThinkingLevel = validateThinkingLevel(thinkingLevel || defaultThinkingLevel());
  const unsupported = ["model", "thinkingLevel"];
  if (temperature !== undefined) unsupported.push("temperature");
  if (maxOutputTokens !== undefined) unsupported.push("maxOutputTokens");
  if (approvalMode && !APPROVAL_MODES.includes(approvalMode)) {
    throw new Error(`approvalMode must be one of: ${APPROVAL_MODES.join(", ")}.`);
  }
  const skipPermissions = approvalMode === "yolo" || envFlag("ANTIGRAVITY_CLI_SKIP_PERMISSIONS");
  const selectedCwd = cwd || process.cwd();
  const selectedIncludeDirectories = [
    ...defaultCliIncludeDirectories(),
    ...listFromValue(includeDirectories)
  ];
  if (skipPermissions) {
    if (!path.isAbsolute(selectedCwd)) {
      throw new Error("Antigravity approvalMode=yolo requires an absolute cwd for the allowed write folder.");
    }
    if (!selectedIncludeDirectories.length) {
      throw new Error(
        "Antigravity approvalMode=yolo requires includeDirectories to name the allowed write folder."
      );
    }
    for (const directory of selectedIncludeDirectories) {
      if (!path.isAbsolute(directory)) {
        throw new Error(
          "Antigravity approvalMode=yolo requires absolute includeDirectories for allowed write folders."
        );
      }
    }
  }

  return {
    model: model || defaultAntigravityModel(),
    modelLabel: defaultAntigravityModelLabel(),
    thinkingLevel: selectedThinkingLevel,
    cwd: selectedCwd,
    includeDirectories: selectedIncludeDirectories,
    approvalMode: approvalMode || null,
    skipPermissions,
    timeoutMs: timeoutMs || defaultCliTimeoutMs(),
    prompt: buildCliPrompt(prompt, systemInstruction),
    warnings: [
      `Antigravity CLI uses its configured model picker; MCP cannot set first-class controls for: ${unsupported.join(", ")}.`
    ]
  };
}

function buildAntigravityArgs(options) {
  const args = [
    "-p",
    options.prompt,
    "--print-timeout",
    goDuration(options.timeoutMs)
  ];
  for (const directory of options.includeDirectories) {
    args.push("--add-dir", directory);
  }
  if (envFlag("ANTIGRAVITY_CLI_SANDBOX")) args.push("--sandbox");
  if (options.skipPermissions) {
    args.push("--dangerously-skip-permissions");
  }
  return args;
}

function scopedRunEnvAssignments(runId) {
  const assignments = [`GEMINI_MCP_RUN_ID=${shellQuote(runId)}`];
  for (const [name, value] of Object.entries(process.env)) {
    if (/^FAKE_GEMINI_/u.test(name) && value !== undefined) {
      assignments.push(`${name}=${shellQuote(value)}`);
    }
  }
  return assignments;
}

function spawnCollect(command, args, { cwd, timeoutMs, maxBuffer = 1024 * 1024 * 8 }) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      env: accountCliEnv(),
      stdio: ["ignore", "pipe", "pipe"]
    });
    let stdout = "";
    let stderr = "";
    let settled = false;
    let terminatingReason = null;
    let killTimer = null;

    const finish = (error, result) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      clearTimeout(killTimer);
      if (error) reject(error);
      else resolve(result);
    };

    const terminateWithError = (message) => {
      if (settled || terminatingReason) return;
      terminatingReason = message;
      child.kill("SIGTERM");
      killTimer = setTimeout(() => {
        child.kill("SIGKILL");
      }, 2000);
    };

    const timer = setTimeout(() => {
      terminateWithError(`${commandSummary(command, args).join(" ")} timed out after ${timeoutMs}ms.`);
    }, timeoutMs);

    child.stdout.on("data", (chunk) => {
      stdout += chunk;
      if (stdout.length + stderr.length > maxBuffer) {
        terminateWithError(`${commandSummary(command, args).join(" ")} exceeded output buffer.`);
      }
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
      if (stdout.length + stderr.length > maxBuffer) {
        terminateWithError(`${commandSummary(command, args).join(" ")} exceeded output buffer.`);
      }
    });
    child.on("error", finish);
    child.on("close", (code, signal) => {
      if (terminatingReason) {
        const error = new Error(terminatingReason);
        error.code = code;
        error.signal = signal;
        error.stdout = stdout;
        error.stderr = stderr;
        finish(error);
        return;
      }
      if (code === 0) {
        finish(null, { stdout, stderr });
        return;
      }
      const details = stderr.trim() || stdout.trim() || `exit=${code ?? "null"} signal=${signal ?? "null"}`;
      const error = new Error(`${commandSummary(command, args).join(" ")} failed: ${shortText(details, 800)}`);
      error.code = code;
      error.signal = signal;
      error.stdout = stdout;
      error.stderr = stderr;
      finish(error);
    });
  });
}

export async function geminiStatus() {
  const cli = geminiCliConfig();
  const antigravity = antigravityCliConfig();
  const tmux = tmuxVersion();
  const effectiveBackend = inferBackend();
  return {
    ok: true,
    requested_backend: requestedBackend(),
    effective_backend: effectiveBackend,
    available_auth: {
      account_cli_env_sanitized: true,
      gemini_cli_command: cli.command,
      gemini_cli_preferred_command: cli.preferredCommand,
      gemini_cli_preferred_command_present: cli.preferredCommandPresent,
      gemini_cli_version: await geminiCliVersion(cli.command),
      gemini_cli_oauth_file_present: cli.oauthFilePresent,
      antigravity_cli_command: antigravity.command,
      antigravity_cli_preferred_command: antigravity.preferredCommand,
      antigravity_cli_preferred_command_present: antigravity.preferredCommandPresent,
      antigravity_cli_version: await antigravityCliVersion(antigravity.command),
      antigravity_cli_app_data_present: antigravity.appDataDirPresent,
      antigravity_cli_project_config_present: antigravity.projectConfigDirPresent
    },
    default_model: effectiveBackend === "antigravity-cli" ? defaultAntigravityModel() : defaultModel(),
    default_antigravity_model_label: defaultAntigravityModelLabel(),
    default_thinking_level: validateThinkingLevel(defaultThinkingLevel()),
    default_cli_approval_mode: defaultCliApprovalMode(),
    default_cli_include_directories: defaultCliIncludeDirectories(),
    default_cli_timeout_ms: defaultCliTimeoutMs(),
    tmux: {
      available: Boolean(tmux),
      version: tmux
    },
    node: process.version
  };
}

async function askViaAntigravityCli(args) {
  const cli = antigravityCliConfig();
  const cliVersion = await antigravityCliVersion(cli.command);
  if (!cliVersion) {
    throw new Error(
      `Antigravity CLI is not runnable at ${cli.command}. Run gemini_status and set ANTIGRAVITY_CLI_PATH before retrying.`
    );
  }
  const options = selectedAntigravityOptions(args);
  const cliArgs = buildAntigravityArgs(options);
  const { stdout, stderr } = await spawnCollect(cli.command, cliArgs, {
    timeoutMs: options.timeoutMs + 5000,
    cwd: options.cwd
  });
  const text = requireNonEmptyText(stdout.trim(), "Antigravity CLI");
  return {
    backend: "antigravity-cli",
    authMode: "antigravity-oauth",
    model: options.model,
    modelLabel: options.modelLabel,
    thinkingLevel: options.thinkingLevel,
    cliCommand: cli.command,
    cliVersion,
    cwd: options.cwd,
    includeDirectories: options.includeDirectories,
    approvalMode: options.approvalMode,
    skipPermissions: options.skipPermissions,
    timeoutMs: options.timeoutMs,
    text,
    usageMetadata: null,
    warnings: [
      ...options.warnings,
      ...(options.skipPermissions
        ? ["Antigravity CLI permission prompts are bypassed for this call. Use only with explicit user approval and constrained cwd/includeDirectories."]
        : []),
      ...(summarizeCliStderr(stderr) ? [`antigravity stderr: ${summarizeCliStderr(stderr)}`] : [])
    ]
  };
}

async function askViaCli(args) {
  const cli = geminiCliConfig();
  const cliVersion = await geminiCliVersion(cli.command);
  if (!cliVersion) {
    throw new Error(
      `Gemini CLI is not runnable at ${cli.command}. Run gemini_status and set GEMINI_CLI_PATH before retrying.`
    );
  }
  const options = selectedCliOptions(args);
  const cliArgs = buildCliArgs(options);
  const { stdout, stderr } = await execFileAsync(cli.command, cliArgs, {
    maxBuffer: 1024 * 1024 * 8,
    timeout: options.timeoutMs,
    cwd: options.cwd,
    env: accountCliEnv()
  });
  const text = requireNonEmptyText(parseCliResponse(stdout), "Gemini CLI");
  return {
    backend: "gemini-cli",
    authMode: "gemini-cli-oauth",
    model: options.model,
    thinkingLevel: options.thinkingLevel,
    cliCommand: cli.command,
    cliVersion,
    cwd: options.cwd,
    approvalMode: options.approvalMode,
    includeDirectories: options.includeDirectories,
    timeoutMs: options.timeoutMs,
    text,
    usageMetadata: null,
    warnings: [
      ...options.warnings,
      ...(summarizeCliStderr(stderr) ? [`gemini stderr: ${summarizeCliStderr(stderr)}`] : [])
    ]
  };
}

export async function askGemini(args) {
  const backend = inferBackend();
  if (!backend) {
    throw new Error(
      "No account-backed Gemini backend is available. Use GEMINI_MCP_BACKEND=antigravity with an authenticated Antigravity CLI, or GEMINI_MCP_BACKEND=cli with an authenticated Gemini CLI."
    );
  }
  if (backend === "antigravity-cli") return askViaAntigravityCli(args);
  if (backend === "gemini-cli") return askViaCli(args);
  throw new Error(`Unsupported Gemini backend: ${backend}.`);
}

function filesForLogDir(logDir) {
  return {
    prompt: path.join(logDir, "prompt.txt"),
    command: path.join(logDir, "command.json"),
    script: path.join(logDir, "run.sh"),
    events: path.join(logDir, "events.ndjson"),
    stdout: path.join(logDir, "stdout.log"),
    stderr: path.join(logDir, "stderr.log"),
    tmuxPane: path.join(logDir, "tmux-pane.log"),
    finalOutput: path.join(logDir, "final-output.md"),
    report: path.join(logDir, "report.json"),
    state: path.join(logDir, "state.json"),
    exitCode: path.join(logDir, "exit-code.txt")
  };
}

function runFiles(run) {
  return {
    prompt: run.promptFile,
    command: run.commandFile,
    script: run.scriptFile,
    events: run.eventsFile,
    stdout: run.stdoutFile,
    stderr: run.stderrFile,
    tmux_pane: run.tmuxPaneFile || null,
    final_output: run.finalOutputFile || null,
    report: run.reportFile,
    state: run.stateFile,
    exit_code: run.exitCodeFile
  };
}

function writeState(run) {
  const state = {
    run_id: run.runId,
    backend: run.backend,
    model: run.model,
    thinking_level: run.thinkingLevel,
    cwd: run.cwd,
    pid: run.child?.pid ?? run.pid ?? null,
    process_group_pid: run.processGroupPid ?? run.child?.pid ?? run.pid ?? null,
    status: run.status,
    exit_code: run.exitCode ?? null,
    signal: run.signal ?? null,
    started_at: run.startedAt,
    updated_at: new Date().toISOString(),
    command: run.commandSummary,
    log_dir: run.logDir,
    files: runFiles(run),
    managed: isManagedRun(run),
    orphan_reason: run.orphanReason || null,
    use_tmux: run.useTmux,
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
  const fingerprints = [run.scriptFile, run.logDir, run.runId].filter(Boolean);
  const rows = processGroupRows(processGroupPid);
  if (rows.length) {
    const matched = rows.some((row) => fingerprints.some((value) => row.args.includes(value)));
    return {
      alive: true,
      matched,
      args: rows.map((row) => row.args).join("\n"),
      processGroupPid,
      pids: rows.map((row) => row.pid)
    };
  }

  const args = pidArgs(run.pid);
  if (!args) return { alive: false, matched: false, args: "", processGroupPid, pids: [] };
  const matched = fingerprints.some((value) => args.includes(value));
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
    run.orphanReason = "Saved PID is alive, but ps args do not contain this run script or directory fingerprint.";
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
    backend: state.backend || "gemini-cli",
    model: state.model || DEFAULT_MODEL,
    thinkingLevel: state.thinking_level || DEFAULT_THINKING_LEVEL,
    cwd: state.cwd || process.cwd(),
    logDir,
    promptFile: files.prompt,
    commandFile: files.command,
    scriptFile: files.script,
    eventsFile: files.events,
    stdoutFile: files.stdout,
    stderrFile: files.stderr,
    tmuxPaneFile: files.tmux_pane || files.tmuxPane || path.join(logDir, "tmux-pane.log"),
    finalOutputFile: files.final_output || files.finalOutput || path.join(logDir, "final-output.md"),
    reportFile: files.report,
    stateFile: files.state || path.join(logDir, "state.json"),
    exitCodeFile: files.exit_code || files.exitCode || path.join(logDir, "exit-code.txt"),
    commandSummary: state.command || [],
    status: state.status || "completed_unknown",
    exitCode: state.exit_code ?? null,
    signal: state.signal ?? null,
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

function finalOutputDetails(run, max = 8000) {
  const stdout = safeRead(run.stdoutFile);
  const text = parseCliResponse(stdout);
  if (text) {
    const truncated = text.length > max;
    return {
      text: truncated ? `${text.slice(0, max - 3)}...` : text,
      full_text: text,
      source: "stdout",
      truncated,
      full_text_chars: text.length
    };
  }
  const stderr = safeRead(run.stderrFile);
  if (stderr.trim()) {
    const textFromStderr = trimText(stderr.trim(), max);
    return {
      text: textFromStderr,
      full_text: stderr.trim(),
      source: "stderr",
      truncated: textFromStderr.length < stderr.trim().length,
      full_text_chars: stderr.trim().length
    };
  }
  return { text: "", full_text: "", source: null, truncated: false, full_text_chars: 0 };
}

function milestonesFromLogs(run, limit = 12, cursor = 0) {
  const events = [];
  let index = 0;
  for (const raw of safeRead(run.stdoutFile).split(/\r?\n/u).filter(Boolean)) {
    if (index >= cursor) events.push({ kind: "stdout", text: shortText(raw, 500), event_index: index });
    index += 1;
  }
  for (const raw of safeRead(run.stderrFile).split(/\r?\n/u).filter(Boolean)) {
    if (index >= cursor) events.push({ kind: "stderr", text: shortText(raw, 500), event_index: index });
    index += 1;
  }
  return {
    milestones: events.slice(-limit),
    nextCursor: index
  };
}

function elapsedSeconds(startedAt) {
  const started = Date.parse(startedAt || "");
  if (!Number.isFinite(started)) return null;
  return Math.max(0, Math.round((Date.now() - started) / 1000));
}

function countLines(file) {
  return safeRead(file).split(/\r?\n/u).filter(Boolean).length;
}

function activitySummary(run, { limit = 12, cursor = 0 } = {}) {
  const { milestones, nextCursor } = milestonesFromLogs(run, limit, cursor);
  const allMilestones = milestonesFromLogs(run, 200, 0).milestones;
  const toolLike = allMilestones
    .filter((event) => /tool|read|write|edit|bash|shell|file|grep|rg|search|run|command|apply|patch/iu.test(event.text))
    .slice(-limit);
  const tmux = tmuxCapturePane(run);
  const lastOutput = allMilestones.at(-1)?.text || tmux.text || "";
  return {
    elapsed_seconds: elapsedSeconds(run.startedAt),
    stdout_line_count: countLines(run.stdoutFile),
    stderr_line_count: countLines(run.stderrFile),
    next_cursor: nextCursor,
    recent_log_trace: milestones,
    tool_like_log_trace: toolLike,
    tmux_capture_available: tmux.available,
    last_output: shortText(lastOutput, 900),
    note: "Observable trace only: CLI logs, tmux pane capture, warnings, and model-visible output. Private chain-of-thought is not exposed.",
    stop_hint: WAITABLE_STATUSES.has(run.status)
      ? "Use gemini_kill for this run_id if the trajectory is wrong or the run should stop."
      : "Run is terminal; no kill is needed unless a saved process or tmux session is still alive."
  };
}

function detectWarnings(run) {
  const warnings = [];
  const stderr = safeRead(run.stderrFile).trim();
  if (stderr) warnings.push({ type: "stderr", detail: summarizeCliStderr(stderr) || shortText(stderr, 600) });
  const finalOutput = finalOutputDetails(run);
  if (["completed", "failed"].includes(run.status) && !finalOutput.text) {
    warnings.push({ type: "empty_text", detail: "Gemini CLI produced no parseable text." });
  }
  if (run.useTmux && !tmuxVersion()) {
    warnings.push({ type: "tmux_missing", detail: "Run requested tmux but tmux is not available." });
  }
  return warnings;
}

function writeFinalOutputFile(run, fullText) {
  if (!run.finalOutputFile || !fullText) return null;
  fs.writeFileSync(run.finalOutputFile, fullText);
  return run.finalOutputFile;
}

function buildChatRelay(run) {
  const finalOutput = finalOutputDetails(run);
  const fullTextFile = writeFinalOutputFile(run, finalOutput.full_text);
  return {
    text: finalOutput.text,
    markdown: finalOutput.text ? `Gemini:\n${finalOutput.text}` : "",
    source: finalOutput.source,
    truncated: finalOutput.truncated,
    full_text_chars: finalOutput.full_text_chars,
    full_text_file: fullTextFile,
    instruction: "Relay this text to the user in chat when the user needs Gemini's answer."
  };
}

function buildReport(run) {
  const { milestones } = milestonesFromLogs(run);
  const finalOutput = finalOutputDetails(run, 1200);
  const chatRelay = buildChatRelay(run);
  const activity = activitySummary(run);
  const warnings = detectWarnings(run);
  return {
    run_id: run.runId,
    backend: run.backend,
    model: run.model,
    thinking_level: run.thinkingLevel,
    cwd: run.cwd,
    pid: run.child?.pid ?? run.pid ?? null,
    status: run.status,
    managed: isManagedRun(run),
    orphan_reason: run.orphanReason || null,
    exit_code: run.exitCode ?? null,
    signal: run.signal ?? null,
    log_dir: run.logDir,
    command: run.commandSummary,
    use_tmux: run.useTmux,
    tmux_session: run.tmuxSession || null,
    tmux_target: run.tmuxTarget || null,
    tmux_start_channel: run.tmuxStartChannel || null,
    tmux_go_channel: run.tmuxGoChannel || null,
    tmux_done_channel: run.tmuxDoneChannel || null,
    warnings,
    activity,
    milestones,
    events: milestones,
    chat_relay: chatRelay,
    final_output_summary: finalOutput.text,
    agent_behavior: {
      role: "controlled_external_gemini",
      control_surface: run.useTmux ? "tmux_managed_run" : "managed_process",
      observable_trace: {
        available: true,
        activity_note: activity.note,
        recent_log_count: activity.recent_log_trace.length,
        tool_like_log_count: activity.tool_like_log_trace.length,
        tmux_capture_available: activity.tmux_capture_available
      },
      relay: {
        source: chatRelay.source,
        truncated: chatRelay.truncated,
        full_text_chars: chatRelay.full_text_chars,
        full_text_file: chatRelay.full_text_file
      },
      tail: {
        status: run.status,
        terminal: isTerminalStatus(run.status),
        cleanup_needed: WAITABLE_STATUSES.has(run.status),
        tmux_session: run.tmuxSession || null
      },
      warnings_count: warnings.length
    },
    files: runFiles(run)
  };
}

function writeReport(run) {
  const report = buildReport(run);
  writeJsonAtomic(run.reportFile, report);
  return report;
}

function writeRunScript(files, run, cliCommand, args) {
  const commandLine = [
    "env",
    ...scopedRunEnvAssignments(run.runId),
    shellQuote(cliCommand),
    ...args.map(shellQuote)
  ].join(" ");
  const lines = run.useTmux
    ? [
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
      ]
    : [
        "#!/bin/sh",
        `cd ${shellQuote(run.cwd)} || exit 127`,
        "set +e",
        [
          commandLine,
          `> ${shellQuote(files.stdout)}`,
          `2> ${shellQuote(files.stderr)}`
        ].join(" "),
        "code=$?",
        `printf "%s" "$code" > ${shellQuote(files.exitCode)}`,
        "exit \"$code\""
      ];
  fs.writeFileSync(files.script, `${lines.join("\n")}\n`, { mode: 0o700 });
}

export async function startRun(args = {}) {
  if (!args.prompt || !String(args.prompt).trim()) {
    throw new Error("gemini_run requires a non-empty prompt.");
  }
  const backend = inferBackend();
  if (!["gemini-cli", "antigravity-cli"].includes(backend)) {
    throw new Error(
      "gemini_run requires an authenticated Gemini CLI or Antigravity CLI backend."
    );
  }
  const cli = backend === "antigravity-cli" ? antigravityCliConfig() : geminiCliConfig();
  const cliVersion =
    backend === "antigravity-cli"
      ? await antigravityCliVersion(cli.command)
      : await geminiCliVersion(cli.command);
  if (!cliVersion) {
    throw new Error(
      `${backend === "antigravity-cli" ? "Antigravity CLI" : "Gemini CLI"} is not runnable at ${cli.command}. Run gemini_status and set the matching CLI path before retrying.`
    );
  }
  const options = backend === "antigravity-cli" ? selectedAntigravityOptions(args) : selectedCliOptions(args);
  const cliArgs = backend === "antigravity-cli" ? buildAntigravityArgs(options) : buildCliArgs(options);
  const useTmux = Boolean(args.useTmux || args.tmuxMode);
  if (useTmux && !tmuxVersion()) {
    throw new Error("tmux mode requested, but tmux is not available. Install tmux or run without useTmux.");
  }

  ensureDir(RUNS_DIR);
  const runId = `${nowIsoForPath()}-${randomUUID().slice(0, 8)}`;
  const logDir = path.join(RUNS_DIR, runId);
  ensureDir(logDir);
  const files = filesForLogDir(logDir);
  const tmuxSession = useTmux ? `gemini-mcp-${runId.replace(/[^A-Za-z0-9_-]/gu, "-")}` : null;
  const tmuxTarget = useTmux ? `${tmuxSession}:0.0` : null;
  const tmuxStartChannel = useTmux ? `${tmuxSession}-ready` : null;
  const tmuxGoChannel = useTmux ? `${tmuxSession}-go` : null;
  const tmuxDoneChannel = useTmux ? `${tmuxSession}-done` : null;
  const command = useTmux ? "tmux" : "/bin/sh";
  const commandArgs = useTmux
    ? ["new-session", "-d", "-s", tmuxSession, "/bin/bash", files.script]
    : [files.script];

  const run = {
    runId,
    backend,
    model: options.model,
    thinkingLevel: options.thinkingLevel,
    cwd: options.cwd,
    logDir,
    promptFile: files.prompt,
    commandFile: files.command,
    scriptFile: files.script,
    eventsFile: files.events,
    stdoutFile: files.stdout,
    stderrFile: files.stderr,
    tmuxPaneFile: files.tmuxPane,
    finalOutputFile: files.finalOutput,
    reportFile: files.report,
    stateFile: files.state,
    exitCodeFile: files.exitCode,
    commandSummary: commandSummary(command, commandArgs),
    status: "running",
    exitCode: null,
    signal: null,
    startedAt: new Date().toISOString(),
    pid: null,
    processGroupPid: null,
    child: null,
    managed: true,
    orphanReason: null,
    useTmux,
    tmuxSession,
    tmuxTarget,
    tmuxStartChannel,
    tmuxGoChannel,
    tmuxDoneChannel
  };
  fs.writeFileSync(files.prompt, String(args.prompt));
  fs.writeFileSync(files.events, "");
  writeRunScript(files, run, cli.command, cliArgs);
  fs.writeFileSync(
    files.command,
    JSON.stringify(
      {
        command,
        args: commandArgs,
        summary: run.commandSummary,
        cli_command: cli.command,
        cli_version: cliVersion,
        cli_args: cliArgs,
        cwd: options.cwd,
        use_tmux: useTmux,
        tmux_session: tmuxSession,
        tmux_target: tmuxTarget,
        tmux_start_channel: tmuxStartChannel,
        tmux_go_channel: tmuxGoChannel,
        tmux_done_channel: tmuxDoneChannel,
        timeout_ms: options.timeoutMs,
        approval_mode: options.approvalMode,
        include_directories: options.includeDirectories,
        warnings: options.warnings
      },
      null,
      2
    )
  );

  if (useTmux) {
    const result = spawnSync(command, commandArgs, { encoding: "utf8", env: accountCliEnv() });
    if (result.status !== 0) {
      run.status = "failed";
      fs.appendFileSync(files.stderr, result.stderr || result.stdout || "tmux start failed\n");
      writeState(run);
      writeReport(run);
      throw new Error(`tmux failed to start Gemini run: ${shortText(result.stderr || result.stdout, 600)}`);
    }
    const ready = tmuxWait(tmuxStartChannel, 5000);
    if (ready.status !== 0) {
      spawnSync("tmux", ["kill-session", "-t", tmuxSession], { encoding: "utf8" });
      run.status = "failed";
      fs.appendFileSync(files.stderr, ready.stderr || ready.error || "tmux pane did not reach ready channel\n");
      writeState(run);
      writeReport(run);
      throw new Error(`tmux Gemini run did not reach ready channel: ${shortText(ready.stderr || ready.error || "", 600)}`);
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
      fs.appendFileSync(files.stderr, "tmux failed to signal Gemini run start\n");
      writeState(run);
      writeReport(run);
      throw new Error("tmux failed to signal Gemini run start.");
    }
    run.pid = null;
    run.managed = false;
    jsonLine(files.events, { type: "tmux_start", session: tmuxSession, target: tmuxTarget });
    jsonLine(files.events, { type: "tmux_pipe_pane", file: files.tmuxPane });
    writeState(run);
    writeReport(run);
  } else {
    const child = spawn(command, commandArgs, {
      cwd: options.cwd,
      env: accountCliEnv(),
      detached: true,
      stdio: ["ignore", "ignore", "ignore"]
    });
    run.child = child;
    run.pid = child.pid;
    run.processGroupPid = child.pid;
    const commandRecord = safeReadJson(files.command, {});
    commandRecord.process_group_pid = run.processGroupPid;
    writeJsonAtomic(files.command, commandRecord);
    activeRuns.set(runId, run);
    writeState(run);
    child.on("error", (error) => {
      run.status = "failed";
      run.orphanReason = error.message;
      jsonLine(files.events, { type: "process_error", error: error.message });
      markTerminal(run);
      writeState(run);
      writeReport(run);
    });
    child.on("close", (code, signal) => {
      const diskStatus = safeReadJson(run.stateFile, {})?.status;
      run.exitCode = code;
      run.signal = signal;
      run.status = run.status === "killing" || diskStatus === "killing" ? "killed" : code === 0 ? "completed" : "failed";
      run.orphanReason = null;
      markTerminal(run);
      writeState(run);
      writeReport(run);
    });
    writeReport(run);
  }

  return {
    run_id: runId,
    pid: run.pid,
    backend,
    model: options.model,
    thinking_level: options.thinkingLevel,
    cwd: options.cwd,
    log_dir: logDir,
    status: run.status,
    use_tmux: useTmux,
    tmux_session: tmuxSession,
    tmux_target: tmuxTarget
  };
}

export function getRun(runId) {
  const active = activeRuns.get(runId);
  if (active) return active.useTmux ? refreshTmuxRun(active) : active;
  const logDir = path.join(RUNS_DIR, runId);
  const files = filesForLogDir(logDir);
  if (fs.existsSync(files.state)) {
    return refreshInactiveRun(buildRunFromState(runId, logDir, safeReadJson(files.state, {})));
  }
  if (fs.existsSync(files.report)) {
    return buildRunFromState(runId, logDir, safeReadJson(files.report, {}));
  }
  throw new Error(`Unknown run_id: ${runId}`);
}

export function peekRun(runId, { limit = 12, cursor = 0 } = {}) {
  const run = getRun(runId);
  const { milestones, nextCursor } = milestonesFromLogs(run, limit, cursor);
  const relayText = milestones
    .filter((event) => ["stdout", "stderr"].includes(event.kind))
    .map((event) => event.text)
    .filter(Boolean)
    .join("\n");
  return {
    run_id: runId,
    status: run.status,
    managed: Boolean(run.child) || Boolean(run.managed),
    orphan_reason: run.orphanReason || null,
    cursor: Math.max(0, Number(cursor) || 0),
    next_cursor: nextCursor,
    milestones: milestonesFromLogs(run, limit, 0).milestones,
    relay_updates: milestones,
    chat_relay: {
      text: relayText,
      markdown: relayText ? `Gemini update:\n${relayText}` : "",
      source: "peek",
      truncated: relayText.endsWith("..."),
      next_cursor: nextCursor,
      instruction: "Relay this update in chat instead of raw logs when observing a Gemini run."
    },
    tmux_capture: tmuxCapturePane(run),
    activity: activitySummary(run, { limit, cursor }),
    warnings: detectWarnings(run),
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
        ? match.error || "PID is alive, but ps args do not contain this run script or directory fingerprint."
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
  return writeReport(getRun(runId));
}

export function cleanupRuns({ olderThanDays = DEFAULT_CLEANUP_DAYS, confirm = false } = {}) {
  ensureDir(RUNS_DIR);
  const cutoff = Date.now() - olderThanDays * 24 * 60 * 60 * 1000;
  const candidates = fs
    .readdirSync(RUNS_DIR, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => {
      const runId = entry.name;
      const logDir = path.join(RUNS_DIR, runId);
      const stat = fs.statSync(logDir);
      return { run_id: runId, log_dir: logDir, mtime_ms: stat.mtimeMs };
    })
    .filter((entry) => entry.mtime_ms < cutoff);
  if (confirm) {
    for (const candidate of candidates) {
      fs.rmSync(candidate.log_dir, { recursive: true, force: true });
    }
  }
  return {
    dry_run: !confirm,
    older_than_days: olderThanDays,
    candidates
  };
}
