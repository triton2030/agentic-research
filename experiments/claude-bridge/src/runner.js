import { spawn, spawnSync } from "node:child_process";
import { createHash, randomUUID } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { getProfile, listProfiles, MODEL } from "./profiles.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const BRIDGE_ROOT = path.resolve(__dirname, "..");
export const RUNS_DIR = path.resolve(process.env.CLAUDE_BRIDGE_RUNS_DIR || path.join(BRIDGE_ROOT, "runs"));
export const THREADS_FILE = path.join(RUNS_DIR, "dialog-threads.jsonl");
export const THREAD_LEASES_DIR = path.join(RUNS_DIR, "thread-leases");
export const DEFAULT_CLEANUP_DAYS = 14;

const activeRuns = new Map();
const TERMINAL_STATUSES = new Set(["completed", "failed", "killed", "orphaned"]);
const WAITABLE_STATUSES = new Set(["running", "running_orphaned", "killing"]);
const GUARDED_WRITE_ENFORCEMENT = "prompt_boundary_plus_git_and_filesystem_postflight";

function isTerminalStatus(status) {
  return TERMINAL_STATUSES.has(status);
}

function isManagedRun(run) {
  return !isTerminalStatus(run.status) && (Boolean(run.child) || Boolean(run.managed));
}

function markTerminal(run) {
  stopWriteObservation(run);
  if (run.writeScope && !run.writeScope.final_evaluation) {
    run.writeScope.final_evaluation = evaluateWriteScope(run.writeScope);
  }
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
    finalOutput: path.join(logDir, "final-output.md"),
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

const CLAUDE_AUTH_OVERRIDE_ENV = [
  "ANTHROPIC_AUTH_TOKEN",
  "ANTHROPIC_API_KEY",
  "ANTHROPIC_BASE_URL",
  "CLAUDE_API_KEY",
  "CLAUDE_CODE_OAUTH_TOKEN",
  "CLAUDE_CODE_USE_BEDROCK",
  "CLAUDE_CODE_USE_VERTEX",
  "CLAUDE_CODE_USE_FOUNDRY"
];

const CLAUDE_MODEL_OVERRIDE_ENV = [
  "ANTHROPIC_DEFAULT_FABLE_MODEL",
  "ANTHROPIC_DEFAULT_OPUS_MODEL",
  "ANTHROPIC_DEFAULT_SONNET_MODEL",
  "ANTHROPIC_DEFAULT_HAIKU_MODEL",
  "CLAUDE_CODE_SUBAGENT_MODEL"
];

function stripClaudeAuthOverrides(runEnv) {
  for (const name of CLAUDE_AUTH_OVERRIDE_ENV) delete runEnv[name];
  return runEnv;
}

function stripClaudeModelOverrides(runEnv) {
  for (const name of CLAUDE_MODEL_OVERRIDE_ENV) delete runEnv[name];
  return runEnv;
}

function objectHasApiKeyHelper(value) {
  if (!value || typeof value !== "object") return false;
  return Object.entries(value).some(
    ([key, child]) => (key === "apiKeyHelper" && Boolean(child)) || objectHasApiKeyHelper(child)
  );
}

function settingsHasApiKeyHelper(raw) {
  if (!String(raw || "").trim()) return false;
  try {
    return objectHasApiKeyHelper(JSON.parse(raw));
  } catch {
    return /["']apiKeyHelper["']\s*:/u.test(String(raw));
  }
}

function settingsDocuments(cwd = process.cwd(), explicitSettings) {
  const candidates = new Set([
    path.join(os.homedir(), ".claude", "settings.json"),
    path.join(os.homedir(), ".claude", "settings.local.json"),
    path.join(cwd, ".claude", "settings.json"),
    path.join(cwd, ".claude", "settings.local.json"),
    "/Library/Application Support/ClaudeCode/managed-settings.json"
  ]);
  try {
    const root = gitWorktreeRoot(cwd);
    candidates.add(path.join(root, ".claude", "settings.json"));
    candidates.add(path.join(root, ".claude", "settings.local.json"));
  } catch {
    // Non-Git cwd still uses the direct project candidates above.
  }
  const documents = [];
  for (const file of candidates) {
    if (fs.existsSync(file)) documents.push({ source: file, content: safeRead(file) });
  }
  if (explicitSettings) {
    const raw = String(explicitSettings).trim();
    const file = raw.startsWith("{") ? null : path.resolve(cwd, raw);
    const content = file && fs.existsSync(file) ? safeRead(file) : raw;
    documents.push({ source: file || "<inline --settings>", content });
  }
  return [...new Map(documents.map((document) => [document.source, document])).values()];
}

function apiKeyHelperSources(cwd = process.cwd(), explicitSettings) {
  return settingsDocuments(cwd, explicitSettings)
    .filter(({ content }) => settingsHasApiKeyHelper(content))
    .map(({ source }) => source);
}

function objectKeysPresent(value, keys, found = new Set()) {
  if (!value || typeof value !== "object") return found;
  for (const [key, child] of Object.entries(value)) {
    if (keys.has(key) && child !== undefined && child !== null && child !== "") found.add(key);
    objectKeysPresent(child, keys, found);
  }
  return found;
}

function settingsOverrideKeys(raw, names) {
  const keys = new Set(names);
  try {
    return [...objectKeysPresent(JSON.parse(raw), keys)].sort();
  } catch {
    return names.filter((name) => new RegExp(`["']${name}["']\\s*:`, "u").test(String(raw))).sort();
  }
}

function settingsOverrideSources(cwd, explicitSettings, names) {
  return settingsDocuments(cwd, explicitSettings)
    .map(({ source, content }) => ({ source, keys: settingsOverrideKeys(content, names) }))
    .filter(({ keys }) => keys.length > 0);
}

function bridgeAuthStatus({ cwd = process.cwd(), env = {} } = {}) {
  const { command, prefixArgs } = resolveClaudeCommand();
  const probeEnv = { ...process.env, ...env };
  const strippedEnv = CLAUDE_AUTH_OVERRIDE_ENV.filter((name) => probeEnv[name] !== undefined);
  const result = spawnSync(command, [...prefixArgs, "auth", "status"], {
    cwd,
    encoding: "utf8",
    env: stripClaudeAuthOverrides(probeEnv)
  });
  let status;
  try {
    status = JSON.parse(result.stdout || result.stderr || "{}");
  } catch {
    status = {
      loggedIn: false,
      error: shortText(result.stdout || result.stderr || "unparseable auth status")
    };
  }
  const subscriptionReady =
    status.loggedIn === true &&
    status.authMethod === "claude.ai" &&
    status.apiProvider === "firstParty" &&
    Boolean(status.subscriptionType);
  return { result, status, subscriptionReady, strippedEnv };
}

function assertSubscriptionBilling(options = {}) {
  const cwd = options.cwd || process.cwd();
  const helpers = apiKeyHelperSources(cwd, options.settings);
  const settingsAuthOverrides = settingsOverrideSources(cwd, options.settings, CLAUDE_AUTH_OVERRIDE_ENV);
  const settingsModelOverrides = settingsOverrideSources(cwd, options.settings, CLAUDE_MODEL_OVERRIDE_ENV);
  if (helpers.length) {
    throw new Error(
      `Subscription-only Claude bridge refuses apiKeyHelper settings: ${helpers.join(", ")}. ` +
        "Remove the helper before using this bridge."
    );
  }
  if (settingsAuthOverrides.length) {
    throw new Error(
      `Subscription-only Claude bridge refuses auth/provider overrides in settings: ` +
        settingsAuthOverrides.map(({ source, keys }) => `${source} (${keys.join(", ")})`).join("; ")
    );
  }
  if (settingsModelOverrides.length) {
    throw new Error(
      `Claude bridge refuses model alias redirects in settings: ` +
        settingsModelOverrides.map(({ source, keys }) => `${source} (${keys.join(", ")})`).join("; ")
    );
  }
  const auth = bridgeAuthStatus({ cwd, env: options.env || {} });
  if (!auth.subscriptionReady) {
    throw new Error(
      `Subscription-only Claude bridge requires Claude.ai plan OAuth; active auth is ` +
        `${auth.status.authMethod || "none"}/${auth.status.apiProvider || "none"}/${auth.status.subscriptionType || "none"}. ` +
        "Run `claude auth login` without --console."
    );
  }
  return {
    mode: "subscription_oauth",
    auth_method: auth.status.authMethod,
    api_provider: auth.status.apiProvider || null,
    subscription_type: auth.status.subscriptionType,
    auth_env_overrides_stripped: auth.strippedEnv,
    api_key_helper_sources: [],
    settings_auth_override_sources: [],
    settings_model_override_sources: []
  };
}

function gitOutput(cwd, args) {
  const result = spawnSync("git", args, { cwd, encoding: "buffer" });
  if (result.status !== 0) {
    throw new Error(`Git write-scope check failed: ${shortText(result.stderr?.toString() || result.stdout?.toString(), 600)}`);
  }
  return result.stdout;
}

function gitWorktreeRoot(cwd) {
  return gitOutput(cwd, ["rev-parse", "--show-toplevel"]).toString("utf8").trim();
}

function gitWorkspaceContext(cwd) {
  try {
    const worktreeRoot = fs.realpathSync(gitWorktreeRoot(cwd));
    const commonDirRaw = gitOutput(cwd, ["rev-parse", "--git-common-dir"]).toString("utf8").trim();
    const commonDir = fs.realpathSync(path.resolve(worktreeRoot, commonDirRaw));
    const head = gitOutput(cwd, ["rev-parse", "HEAD"]).toString("utf8").trim();
    const branchResult = spawnSync("git", ["symbolic-ref", "--quiet", "--short", "HEAD"], {
      cwd,
      encoding: "utf8"
    });
    const branch = branchResult.status === 0 ? branchResult.stdout.trim() : null;
    return {
      kind: "git",
      worktree_root: worktreeRoot,
      common_dir: commonDir,
      branch,
      head,
      ref: branch || `detached:${head}`
    };
  } catch {
    return { kind: "directory", worktree_root: path.resolve(cwd), common_dir: null, branch: null, head: null, ref: null };
  }
}

function assertThreadWorkspace(thread, cwd) {
  const requestedCwd = path.resolve(cwd || thread.cwd);
  if (path.resolve(thread.cwd) !== requestedCwd) {
    throw new Error(
      `Claude thread ${thread.thread_id} belongs to cwd ${thread.cwd}, not ${requestedCwd}. Start a new thread for another worktree.`
    );
  }
  const expected = thread.workspace;
  const current = gitWorkspaceContext(requestedCwd);
  if (expected?.common_dir && current.common_dir !== expected.common_dir) {
    throw new Error(`Claude thread ${thread.thread_id} belongs to a different Git project/worktree family.`);
  }
  if (expected?.worktree_root && current.worktree_root !== expected.worktree_root) {
    throw new Error(`Claude thread ${thread.thread_id} belongs to worktree ${expected.worktree_root}.`);
  }
  if (expected?.ref && current.ref !== expected.ref) {
    throw new Error(
      `Claude thread ${thread.thread_id} belongs to Git ref ${expected.ref}, but cwd is now ${current.ref || "unknown"}. Start a new branch-specific thread.`
    );
  }
  return { cwd: requestedCwd, workspace: current };
}

function parsePorcelainZ(buffer) {
  const records = buffer.toString("utf8").split("\0");
  const entries = [];
  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (!record) continue;
    const status = record.slice(0, 2);
    const file = record.slice(3);
    entries.push({ status, file });
    if (/[RC]/u.test(status) && records[index + 1]) {
      entries.push({ status: `${status}:source`, file: records[index + 1] });
      index += 1;
    }
  }
  return entries;
}

function fileFingerprint(root, relativeFile) {
  const absoluteFile = path.join(root, relativeFile);
  try {
    const stat = fs.lstatSync(absoluteFile);
    if (stat.isSymbolicLink()) return `symlink:${fs.readlinkSync(absoluteFile)}`;
    if (!stat.isFile()) return `type:${stat.mode}:${stat.size}:${stat.mtimeMs}:${stat.ctimeMs}`;
    return `file:${createHash("sha256").update(fs.readFileSync(absoluteFile)).digest("hex")}`;
  } catch (error) {
    if (error?.code === "ENOENT") return "missing";
    return `error:${error?.code || error?.message || "unknown"}`;
  }
}

function gitDirtySnapshot(root) {
  const entries = parsePorcelainZ(
    gitOutput(root, ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored=matching"])
  );
  const relativeRunsDir = path.relative(root, RUNS_DIR).split(path.sep).join("/").replace(/\/$/u, "");
  const visibleEntries = entries.filter(({ file }) => {
    if (!relativeRunsDir || relativeRunsDir.startsWith("..") || path.isAbsolute(relativeRunsDir)) return true;
    const normalizedFile = file.replace(/\/$/u, "");
    return normalizedFile !== relativeRunsDir && !normalizedFile.startsWith(`${relativeRunsDir}/`);
  });
  return Object.fromEntries(
    visibleEntries.map(({ status, file }) => [file, { status, fingerprint: fileFingerprint(root, file) }])
  );
}

function normalizeWriteFiles(cwd, writeFiles) {
  const root = fs.realpathSync(gitWorktreeRoot(cwd));
  const resolvedCwd = fs.realpathSync(cwd);
  const files = [...new Set([].concat(writeFiles || []).map((file) => String(file).trim()).filter(Boolean))];
  if (!files.length) {
    throw new Error("The worker profile requires writeFiles with one or more exact project-relative file paths.");
  }
  const normalized = files.map((file) => {
    if (path.isAbsolute(file)) {
      throw new Error(`writeFiles entries must be relative to cwd, not absolute: ${file}`);
    }
    const absolute = path.resolve(resolvedCwd, file);
    const relativeToRoot = path.relative(root, absolute);
    if (!relativeToRoot || relativeToRoot.startsWith("..") || path.isAbsolute(relativeToRoot)) {
      throw new Error(`writeFiles entry must resolve to a file inside the Git worktree: ${file}`);
    }
    let cursor = root;
    for (const segment of relativeToRoot.split(path.sep)) {
      cursor = path.join(cursor, segment);
      try {
        if (fs.lstatSync(cursor).isSymbolicLink()) {
          throw new Error(`Worker write scope cannot contain symlinks: ${file}`);
        }
      } catch (error) {
        if (error?.code !== "ENOENT") throw error;
      }
    }
    return relativeToRoot.split(path.sep).join("/");
  });
  const baseline = gitDirtySnapshot(root);
  const dirtyOverlap = normalized.filter((file) => baseline[file]);
  if (dirtyOverlap.length) {
    throw new Error(
      `Worker write scope overlaps pre-existing dirty files: ${dirtyOverlap.join(", ")}. ` +
        "Preserve the user's edits and use a clean target or an explicitly unrestricted profile."
    );
  }
  return {
    mode: "guarded",
    root,
    allowed_files: normalized,
    baseline,
    baseline_head: gitOutput(root, ["rev-parse", "HEAD"]).toString("utf8").trim(),
    observed_files: [],
    observation_complete: false,
    observation_error: null
  };
}

function snapshotGitFootprint(cwd, mode = "unrestricted_observation") {
  try {
    const root = fs.realpathSync(gitWorktreeRoot(cwd));
    return {
      mode,
      root,
      allowed_files: null,
      baseline: gitDirtySnapshot(root),
      baseline_head: gitOutput(root, ["rev-parse", "HEAD"]).toString("utf8").trim()
    };
  } catch (error) {
    return {
      mode,
      root: null,
      allowed_files: null,
      baseline: null,
      baseline_head: null,
      baseline_error: error.message
    };
  }
}

function gitChangedBetween(root, beforeHead, afterHead) {
  if (!beforeHead || !afterHead || beforeHead === afterHead) return [];
  return gitOutput(root, ["diff", "--name-only", "-z", `${beforeHead}..${afterHead}`])
    .toString("utf8")
    .split("\0")
    .filter(Boolean);
}

function isTransientClaudeAtomicWrite(file, allowedFiles, root) {
  if (fs.existsSync(path.join(root, file))) return false;
  return allowedFiles.some((allowedFile) => {
    const prefix = `${allowedFile}.tmp.`;
    if (!file.startsWith(prefix)) return false;
    return /^\d+\.[0-9a-f]{8,}$/iu.test(file.slice(prefix.length));
  });
}

function terminalWriteScopeUnknown(writeScope) {
  const readOnly = writeScope?.mode === "read_only_observation";
  const guarded = writeScope?.mode === "guarded";
  return {
    status: "unknown",
    enforcement: guarded
      ? GUARDED_WRITE_ENFORCEMENT
      : readOnly
        ? "read_only_git_footprint_observation"
        : "unrestricted_git_footprint_observation",
    allowed_files: writeScope?.allowed_files || null,
    error: "Terminal run has no frozen write-scope report from its completion window.",
    note: "Current worktree state cannot reconstruct historical write-scope evidence."
  };
}

function evaluateWriteScope(writeScope) {
  if (!writeScope) return null;
  if (!writeScope.root || !writeScope.baseline) {
    const readOnly = writeScope.mode === "read_only_observation";
    return {
      status: "unknown",
      enforcement: readOnly ? "read_only_git_footprint_observation" : "unrestricted_git_footprint_observation",
      error: writeScope.baseline_error || "No Git baseline is available.",
      note: readOnly
        ? "The read-only run's persistent Git footprint could not be isolated."
        : "Unrestricted execution was allowed, but its persistent file footprint could not be isolated."
    };
  }
  try {
    const current = gitDirtySnapshot(writeScope.root);
    const currentHead = gitOutput(writeScope.root, ["rev-parse", "HEAD"]).toString("utf8").trim();
    const candidates = new Set([...Object.keys(writeScope.baseline), ...Object.keys(current)]);
    const changedFiles = [...candidates].filter((file) => {
      const before = writeScope.baseline[file];
      const after = current[file];
      return before?.status !== after?.status || before?.fingerprint !== after?.fingerprint;
    });
    for (const file of gitChangedBetween(writeScope.root, writeScope.baseline_head, currentHead)) {
      changedFiles.push(file);
    }
    const guarded = writeScope.mode === "guarded";
    const readOnly = writeScope.mode === "read_only_observation";
    const allowed = new Set(writeScope.allowed_files || []);
    const observedFiles = (writeScope.observed_files || []).filter(
      (file) => !guarded || !isTransientClaudeAtomicWrite(file, writeScope.allowed_files, writeScope.root)
    );
    const uniqueChanged = [...new Set([...changedFiles, ...observedFiles])].sort();
    const outOfScope = guarded ? uniqueChanged.filter((file) => !allowed.has(file)) : [];
    const headChanged = writeScope.baseline_head !== currentHead;
    const symlinkFiles = guarded
      ? writeScope.allowed_files.filter((file) => {
          try {
            return fs.lstatSync(path.join(writeScope.root, file)).isSymbolicLink();
          } catch {
            return false;
          }
        })
      : [];
    const violations = guarded
      ? [
          ...(outOfScope.length ? ["out_of_scope_files"] : []),
          ...(headChanged ? ["git_head_changed"] : []),
          ...(symlinkFiles.length ? ["allowed_path_became_symlink"] : [])
        ]
      : readOnly
        ? [
            ...(uniqueChanged.length ? ["persistent_files_changed"] : []),
            ...(headChanged ? ["git_head_changed"] : [])
          ]
        : [];
    if (guarded && writeScope.observation_complete !== true) {
      return {
        status: "unknown",
        enforcement: GUARDED_WRITE_ENFORCEMENT,
        worktree_root: writeScope.root,
        allowed_files: writeScope.allowed_files,
        changed_files: uniqueChanged,
        out_of_scope_files: outOfScope,
        head_changed: headChanged,
        symlink_files: symlinkFiles,
        violations,
        error: writeScope.observation_error || "Filesystem observation did not reach a complete terminal handoff.",
        note: "The guarded worker footprint cannot be proven after observation loss."
      };
    }
    return {
      status: guarded || readOnly ? (violations.length ? "failed" : "passed") : "observed",
      enforcement: guarded
        ? GUARDED_WRITE_ENFORCEMENT
        : readOnly
          ? "read_only_git_footprint_observation"
          : "unrestricted_git_footprint_observation",
      worktree_root: writeScope.root,
      allowed_files: writeScope.allowed_files || null,
      changed_files: uniqueChanged,
      out_of_scope_files: outOfScope,
      head_changed: headChanged,
      symlink_files: symlinkFiles,
      violations,
      attribution: readOnly ? "unknown_shared_worktree" : guarded ? "claude_worker_run" : "unrestricted_run_window",
      note: "Postflight detection covers the persistent Git-worktree footprint; it does not sandbox Claude, prove no temporary write, or observe external-service mutations."
    };
  } catch (error) {
    return {
      status: "unknown",
      enforcement: GUARDED_WRITE_ENFORCEMENT,
      allowed_files: writeScope.allowed_files,
      error: error.message,
      note: "Postflight detection could not prove the final write footprint."
    };
  }
}

function startWriteObservation(run) {
  const scope = run.writeScope;
  if (scope?.mode !== "guarded") return;
  if (run.useTmux) {
    scope.observation_error = "Guarded filesystem observation is unavailable for tmux worker runs.";
    return;
  }
  const ignoredPrefixes = [".git"];
  const relativeRunsDir = path.relative(scope.root, RUNS_DIR).split(path.sep).join("/");
  if (relativeRunsDir && !relativeRunsDir.startsWith("..") && !path.isAbsolute(relativeRunsDir)) {
    ignoredPrefixes.push(relativeRunsDir);
  }
  try {
    run.writeWatcher = fs.watch(scope.root, { recursive: true }, (_eventType, filename) => {
      if (!filename) {
        scope.observation_error = "Filesystem watcher emitted an event without a path.";
        return;
      }
      const relativeFile = String(filename).split(path.sep).join("/");
      if (ignoredPrefixes.some((prefix) => relativeFile === prefix || relativeFile.startsWith(`${prefix}/`))) return;
      if (!scope.observed_files.includes(relativeFile)) scope.observed_files.push(relativeFile);
    });
    run.writeWatcher.on("error", (error) => {
      scope.observation_error = error.message;
    });
  } catch (error) {
    scope.observation_error = error.message;
  }
}

function stopWriteObservation(run) {
  if (!run.writeWatcher) return;
  run.writeWatcher.close();
  run.writeWatcher = null;
  run.writeScope.observation_complete = !run.writeScope.observation_error;
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

const HIDDEN_FLAG_PROBES = new Map([
  ["--max-turns", ["--max-turns", "1"]],
  ["--system-prompt-file", ["--system-prompt-file", os.devNull]],
  ["--append-system-prompt-file", ["--append-system-prompt-file", os.devNull]],
  ["--permission-prompt-tool", ["--permission-prompt-tool", "claude_bridge_parser_probe"]],
  ["--append-subagent-system-prompt", ["--append-subagent-system-prompt", "claude_bridge_parser_probe"]]
]);

function probeHiddenClaudeFlag(flag) {
  const probeArgs = HIDDEN_FLAG_PROBES.get(flag);
  if (!probeArgs) {
    return { supported: false, evidence: "not_advertised_or_probeable" };
  }
  const { command, prefixArgs } = resolveClaudeCommand();
  const probe = spawnSync(command, [...prefixArgs, ...probeArgs, "auth", "status"], {
    encoding: "utf8",
    env: stripClaudeAuthOverrides({ ...process.env })
  });
  const output = `${probe.stdout || ""}\n${probe.stderr || ""}`;
  const parserRejected = /(?:unknown|invalid|unrecognized) (?:option|argument)/iu.test(output);
  return {
    supported: !probe.error && !parserRejected,
    evidence: !probe.error && !parserRejected ? "parser_probe" : "parser_rejected",
    status_code: probe.status,
    error: probe.error?.code || probe.error?.message || (parserRejected ? shortText(output, 300) : null)
  };
}

function claudeFlagCapability(flag, helpText) {
  if (helpText.includes(flag)) {
    return { supported: true, evidence: "advertised" };
  }
  return probeHiddenClaudeFlag(flag);
}

function cliJsonValue(value) {
  return typeof value === "string" ? value : JSON.stringify(value);
}

function setFlagValue(flags, flag, value) {
  if (value === undefined || value === null || value === "") return flags;
  const next = [...flags];
  const index = next.indexOf(flag);
  if (index === -1) {
    next.unshift(flag, String(value));
  } else {
    next.splice(index, 2, flag, String(value));
  }
  return next;
}

function flagValue(flags, flag, fallback = null) {
  const index = flags.indexOf(flag);
  return index === -1 ? fallback : flags[index + 1] ?? fallback;
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
    ["replayUserMessages", "--replay-user-messages"],
    ["appendSubagentSystemPrompt", "--append-subagent-system-prompt"],
    ["forwardSubagentText", "--forward-subagent-text"],
    ["safeMode", "--safe-mode"]
  ].filter(([key]) => options[key] !== undefined && options[key] !== false);

  if (!requestedFlags.length) return;

  const helpText = claudeHelpText();
  const missing = requestedFlags
    .map(([, flag]) => ({ flag, capability: claudeFlagCapability(flag, helpText) }))
    .filter(({ capability }) => !capability.supported);
  if (missing.length) {
    throw new Error(
      `Installed claude does not support required option(s): ${missing.map(({ flag }) => flag).join(", ")}. ` +
        "The bridge checked live help plus non-spending parser probes; run `npm run doctor` for evidence."
    );
  }
}

function parsedAgentDefinitions(agents) {
  if (agents === undefined || agents === null) return null;
  if (typeof agents === "string") {
    try {
      return JSON.parse(agents);
    } catch {
      throw new Error("agents must be valid inspectable JSON for a named bridge profile.");
    }
  }
  return agents;
}

function agentToolNames(value) {
  return [].concat(value || []).flatMap((item) => String(item).split(",")).map((item) => item.trim()).filter(Boolean);
}

function assertAgentDefinitions(profileName, profileConfig, options) {
  if (profileName === "unrestricted") return;
  if (options.agent !== undefined) {
    throw new Error(
      `Profile ${profileName} cannot load an opaque --agent definition. Pass inspectable agents JSON or use unrestricted.`
    );
  }
  if (options.agents === undefined) return;

  const definitions = parsedAgentDefinitions(options.agents);
  if (!definitions || Array.isArray(definitions) || typeof definitions !== "object") {
    throw new Error("agents must be an object keyed by subagent name.");
  }

  const profileModel = options.model || flagValue(profileConfig.flags, "--model", MODEL);
  const profileEffort = options.effort || flagValue(profileConfig.flags, "--effort", null);
  const profilePermission = flagValue(profileConfig.flags, "--permission-mode", null);
  const writeCapable = new Set(["Bash", "Edit", "Write", "NotebookEdit"]);
  for (const [name, definition] of Object.entries(definitions)) {
    if (!definition || Array.isArray(definition) || typeof definition !== "object") {
      throw new Error(`Agent ${name} must be an object definition.`);
    }
    const forbiddenConfig = ["hooks", "mcpServers"].filter((key) => definition[key] !== undefined);
    if (forbiddenConfig.length) {
      throw new Error(
        `Agent ${name} cannot set ${forbiddenConfig.join(", ")} inside named profile ${profileName}; use audited project config or unrestricted.`
      );
    }
    if (definition.permissionMode !== undefined && definition.permissionMode !== profilePermission) {
      throw new Error(
        `Agent ${name} cannot override permissionMode=${profilePermission || "none"} in profile ${profileName}.`
      );
    }
    if (definition.model !== undefined && !["inherit", profileModel].includes(definition.model)) {
      throw new Error(`Agent ${name} cannot override model=${profileModel} in profile ${profileName}.`);
    }
    if (definition.effort !== undefined && definition.effort !== profileEffort) {
      throw new Error(`Agent ${name} cannot override effort=${profileEffort || "none"} in profile ${profileName}.`);
    }
    if (profileName !== "worker") {
      const unsafeTools = agentToolNames(definition.tools).filter((tool) => writeCapable.has(tool));
      if (unsafeTools.length) {
        throw new Error(`Read-only agent ${name} cannot enable write-capable tools: ${unsafeTools.join(", ")}.`);
      }
    }
  }
}

function assertProfileInvariants(profileName, profileConfig, options) {
  const profileModel = flagValue(profileConfig.flags, "--model", MODEL);
  const profileEffort = flagValue(profileConfig.flags, "--effort", null);
  const profilePermission = flagValue(profileConfig.flags, "--permission-mode", null);
  const isUnrestricted = profileName === "unrestricted";
  const acceptsBoundedCapabilityOverride = ["advisor", "worker"].includes(profileName);
  const extraArgs = [].concat(options.extraArgs || []);
  const reservedExtraFlags = new Set([
    "--model",
    "--effort",
    "--permission-mode",
    "--dangerously-skip-permissions",
    "--allow-dangerously-skip-permissions",
    "--allowedTools",
    "--disallowedTools",
    "--tools"
  ]);
  const reservedOverrides = extraArgs.filter((value) => reservedExtraFlags.has(String(value).split("=")[0]));
  if (reservedOverrides.length) {
    throw new Error(`extraArgs cannot override bridge-owned controls: ${[...new Set(reservedOverrides)].join(", ")}`);
  }
  if (extraArgs.length) {
    throw new Error("extraArgs is disabled; use a typed bridge option so command and report stay identical.");
  }
  if (acceptsBoundedCapabilityOverride && options.model !== undefined && !["opus", "fable"].includes(options.model)) {
    throw new Error(`Profile ${profileName} allows only moving model aliases opus or fable.`);
  }
  if (!isUnrestricted && !acceptsBoundedCapabilityOverride && options.model !== undefined && options.model !== profileModel) {
    throw new Error(`Profile ${profileName} fixes model=${profileModel}; use unrestricted for a model override.`);
  }
  if (!isUnrestricted && !acceptsBoundedCapabilityOverride && options.effort !== undefined && options.effort !== profileEffort) {
    throw new Error(`Profile ${profileName} fixes effort=${profileEffort}; use unrestricted for an effort override.`);
  }
  if (!isUnrestricted && options.fallbackModel !== undefined) {
    throw new Error(`Profile ${profileName} does not allow silent model fallback; start a fresh explicit thread instead.`);
  }
  if (!isUnrestricted && options.permissionMode !== undefined && options.permissionMode !== profilePermission) {
    throw new Error(`Profile ${profileName} fixes permissionMode=${profilePermission || "none"}.`);
  }
  if (isUnrestricted && options.permissionMode !== undefined) {
    throw new Error("Profile unrestricted fixes permission bypass; do not add a second permission mode.");
  }
  if (!isUnrestricted && options.allowDangerouslySkipPermissions) {
    throw new Error(`Profile ${profileName} cannot enable permission bypass.`);
  }
  assertAgentDefinitions(profileName, profileConfig, options);
}

function buildArgs({
  prompt,
  profileName,
  debugFile,
  extraArgs = [],
  model,
  effort,
  appendSystemPrompt,
  appendSubagentSystemPrompt,
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
  forwardSubagentText,
  safeMode
}) {
  const profile = getProfile(profileName);
  let args = [...profile.flags];
  args = setFlagValue(args, "--model", model);
  args = setFlagValue(args, "--effort", effort);
  args.push("--debug-file", debugFile);

  if (appendSystemPrompt) {
    args.push("--append-system-prompt", appendSystemPrompt);
  }
  if (appendSubagentSystemPrompt) {
    args.push("--append-subagent-system-prompt", appendSubagentSystemPrompt);
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
    args = setFlagValue(args, "--permission-mode", permissionMode);
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
  const profileDisallowedTools = String(flagValue(args, "--disallowedTools", ""))
    .split(",")
    .filter(Boolean);
  const requestedDisallowedTools = [].concat(disallowedTools || []).flatMap((value) => String(value).split(","));
  const mergedDisallowedTools = [...new Set([...profileDisallowedTools, ...requestedDisallowedTools].filter(Boolean))];
  if (mergedDisallowedTools.length) {
    args = setFlagValue(args, "--disallowedTools", mergedDisallowedTools.join(","));
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
  if (forwardSubagentText) {
    args.push("--forward-subagent-text");
  }
  if (safeMode) {
    args.push("--safe-mode");
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

function toolBlocksFromEvent(event) {
  const core = event.event && typeof event.event === "object" ? event.event : event;
  const blocks = [
    core,
    core.content_block,
    ...(Array.isArray(core.content) ? core.content : []),
    ...(Array.isArray(core.message?.content) ? core.message.content : [])
  ];
  return blocks.filter((block) => {
    const type = String(block?.type || "").toLowerCase();
    return type.includes("tool_use") || type.includes("tool_call") || type.includes("tool_result");
  });
}

function normalizeEvent(event) {
  const core = event.event && typeof event.event === "object" ? event.event : event;
  const type = String(core.type || event.type || "").toLowerCase();
  const outerType = String(event.type || "").toLowerCase();
  const toolBlock = toolBlocksFromEvent(event)[0];
  const toolType = String(toolBlock?.type || "").toLowerCase();
  const name = toolNameFromEvent(toolBlock || {}) || toolNameFromEvent(core) || toolNameFromEvent(event);
  const text = shortText(extractEventText(event), 500);

  if (type.includes("rate") || outerType.includes("rate")) {
    return { kind: "rate_limit", text: text || "rate limit event" };
  }
  if (type.includes("error") || outerType === "stderr" || core.error || event.error) {
    return { kind: "error", text: text || "error event" };
  }
  const isToolUse =
    toolType.includes("tool_use") ||
    toolType.includes("tool_call") ||
    type.includes("tool_use") ||
    type.includes("tool_call") ||
    Boolean(name);
  if (isToolUse) {
    const input = toolBlock?.input || core.input || event.input || {};
    return {
      kind: "tool_use",
      tool_name: name || "tool",
      file_path: input.file_path || input.path || core.file_path || event.file_path || core.path || event.path || null,
      text: text || `${name || "tool"} called`
    };
  }
  if (toolType.includes("tool_result") || type.includes("tool_result")) {
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
  const authText = texts.find((text) => /authenticate|oauth session expired|not logged in/iu.test(text));
  if (authText) {
    warnings.push({ type: "authentication_failed", detail: shortText(authText, 240) });
  }
  const refusalText = texts.find((text) => /stop_reason.?refusal|request (?:was )?refused|safety classifier/iu.test(text));
  if (refusalText) {
    warnings.push({
      type: "model_refusal",
      detail: shortText(refusalText, 240),
      recovery: "Start a fresh Opus advisor thread; do not treat a continued Fable thread as an independent fallback."
    });
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

function toolTracesFromEvent(event, eventIndex) {
  const toolBlocks = toolBlocksFromEvent(event);
  if (toolBlocks.length) {
    return toolBlocks.map((toolBlock) => {
      const toolType = String(toolBlock.type || "").toLowerCase();
      const kind = toolType.includes("tool_result") ? "tool_result" : "tool_use";
      const input = toolBlock.input || toolBlock.tool_input || {};
      const command = input.command || input.cmd || null;
      return {
        event_index: eventIndex,
        observed_at: eventObservedAt(event),
        kind,
        tool_name: kind === "tool_use" ? toolNameFromEvent(toolBlock) || "tool" : null,
        file_path:
          input.file_path ||
          input.path ||
          input.absolute_path ||
          toolBlock.file_path ||
          toolBlock.path ||
          null,
        command: command ? shortText(command, 500) : null,
        text:
          shortText(extractEventText(toolBlock), 500) ||
          (kind === "tool_use" ? `${toolNameFromEvent(toolBlock) || "tool"} called` : "tool result")
      };
    });
  }
  const normalized = normalizeEvent(event);
  if (!normalized || !["tool_use", "tool_result"].includes(normalized.kind)) return [];
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
  return [
    {
      event_index: eventIndex,
      observed_at: eventObservedAt(event),
      kind: normalized.kind,
      tool_name: normalized.tool_name || core.name || event.name || null,
      file_path: filePath,
      command: command ? shortText(command, 500) : null,
      text: shortText(normalized.text || extractEventText(event), 500)
    }
  ];
}

function activitySummary(events, run, { limit = 12, cursor = 0 } = {}) {
  const startIndex = Math.max(0, Number(cursor) || 0);
  const tmux = tmuxCapturePane(run);
  const tool_trace = events
    .flatMap((event, eventIndex) => toolTracesFromEvent(event, eventIndex));
  const recent_tool_trace = tool_trace.filter((event) => event.event_index >= startIndex).slice(-limit);
  const counts = {};
  for (const event of events) {
    const toolBlocks = toolBlocksFromEvent(event);
    if (toolBlocks.length) {
      for (const toolBlock of toolBlocks) {
        const kind = String(toolBlock.type || "").toLowerCase().includes("tool_result") ? "tool_result" : "tool_use";
        counts[kind] = (counts[kind] || 0) + 1;
      }
      continue;
    }
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
        full_text: text,
        source: "result",
        truncated,
        full_text_chars: text.length,
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
        full_text: text,
        source: "assistant_text",
        truncated,
        full_text_chars: text.length,
        event_index: index
      };
    }
  }

  return {
    text: "",
    full_text: "",
    source: null,
    truncated: false,
    full_text_chars: 0,
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

function writeFinalOutputFile(run, fullText) {
  if (!run.finalOutputFile || !fullText) return null;
  fs.writeFileSync(run.finalOutputFile, fullText);
  return run.finalOutputFile;
}

function buildFinalChatRelay(events, run) {
  const finalOutput = finalOutputDetails(events);
  const fullTextFile = writeFinalOutputFile(run, finalOutput.full_text);
  return {
    text: finalOutput.text,
    markdown: finalOutput.text ? `Claude:\n${finalOutput.text}` : "",
    source: finalOutput.source,
    truncated: finalOutput.truncated,
    full_text_chars: finalOutput.full_text_chars,
    full_text_file: fullTextFile,
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
    final_output: run.finalOutputFile || null,
    report: run.reportFile,
    state: run.stateFile,
    exit_code: run.exitCodeFile || null
  };
}

function runtimeFactsFromEvents(events) {
  let sessionId = null;
  const primaryModels = [];
  const usageModels = new Set();
  for (const event of events) {
    const core = event?.event && typeof event.event === "object" ? event.event : event;
    sessionId = sessionId || core?.session_id || core?.sessionId || null;
    for (const model of Object.keys(core?.modelUsage || event?.modelUsage || {})) usageModels.add(model);
    const candidate =
      core?.model ||
      core?.model_id ||
      core?.modelId ||
      core?.message?.model ||
      null;
    if (!candidate || candidate === "<synthetic>") continue;
    const parentToolUseId = event?.parent_tool_use_id || core?.parent_tool_use_id || null;
    if (parentToolUseId) continue;
    if (primaryModels.at(-1) !== candidate) primaryModels.push(candidate);
  }
  return {
    sessionId,
    initialResolvedModel: primaryModels[0] || null,
    resolvedModel: primaryModels.at(-1) || null,
    resolvedModelHistory: primaryModels,
    modelSwitchObserved: primaryModels.length > 1,
    modelUsageModels: [...usageModels].sort()
  };
}

function refreshRunRuntimeFacts(run, events) {
  const facts = runtimeFactsFromEvents(events);
  if (facts.sessionId) {
    run.sessionId = facts.sessionId;
    run.sessionObserved = true;
  }
  if (facts.resolvedModel) run.resolvedModel = facts.resolvedModel;
  run.initialResolvedModel = facts.initialResolvedModel;
  run.resolvedModelHistory = facts.resolvedModelHistory;
  run.modelSwitchObserved = facts.modelSwitchObserved;
  run.modelUsageModels = facts.modelUsageModels;
  return run;
}

function writeState(run) {
  const state = {
    run_id: run.runId,
    profile: run.profileName,
    model: run.model || MODEL,
    initial_resolved_model: run.initialResolvedModel || null,
    resolved_model: run.resolvedModel || null,
    resolved_model_history: run.resolvedModelHistory || [],
    model_switch_observed: run.modelSwitchObserved === true,
    model_usage_models: run.modelUsageModels || [],
    model_env_overrides_stripped: run.modelEnvOverridesStripped || [],
    effort: run.effort || null,
    topic: run.topic || null,
    session_persistence: run.sessionPersistence !== false,
    auto_memory: run.autoMemory !== false,
    billing: run.billing || null,
    cwd: run.cwd,
    pid: run.child?.pid ?? run.pid ?? null,
    process_group_pid: run.processGroupPid ?? run.child?.pid ?? run.pid ?? null,
    status: run.status,
    exit_code: run.exitCode ?? null,
    signal: run.signal ?? null,
    session_id: run.sessionId ?? null,
    session_observed: run.sessionObserved === true,
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
    tmux_done_channel: run.tmuxDoneChannel || null,
    write_scope: run.writeScope || null
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
      if (run.writeScope) delete run.writeScope.final_evaluation;
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
  const startedAtMs = Date.parse(run.startedAt || "");
  const inStartupGrace =
    run.status !== "killing" && Number.isFinite(startedAtMs) && Date.now() - startedAtMs < 2_000;
  if (match.alive && match.matched) {
    run.status = run.status === "killing" ? "killing" : "running_orphaned";
    run.orphanReason =
      run.status === "killing"
        ? "Kill was requested; process group is still alive and fingerprint matches this run."
        : "Process group is alive and fingerprint matches this run, but current MCP server does not own the child handle.";
  } else if (inStartupGrace) {
    run.status = run.status === "killing" ? "killing" : "running_orphaned";
    run.orphanReason = "Run is inside startup grace; process fingerprint is not stable yet.";
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
    model: state.model || MODEL,
    initialResolvedModel: state.initial_resolved_model || null,
    resolvedModel: state.resolved_model || null,
    resolvedModelHistory: state.resolved_model_history || [],
    modelSwitchObserved: state.model_switch_observed === true,
    modelUsageModels: state.model_usage_models || [],
    modelEnvOverridesStripped: state.model_env_overrides_stripped || [],
    effort: state.effort || null,
    topic: state.topic || null,
    sessionPersistence: state.session_persistence !== false,
    autoMemory: state.auto_memory !== false,
    billing: state.billing || null,
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
    finalOutputFile: files.final_output || files.finalOutput || path.join(logDir, "final-output.md"),
    reportFile: files.report,
    stateFile: files.state || path.join(logDir, "state.json"),
    exitCodeFile: files.exit_code || files.exitCode || path.join(logDir, "exit-code.txt"),
    commandSummary: state.command || [],
    status: state.status || "completed_unknown",
    exitCode: state.exit_code ?? null,
    signal: state.signal ?? null,
    sessionId: state.session_id ?? null,
    sessionObserved: state.session_observed === true,
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
    tmuxDoneChannel: state.tmux_done_channel || null,
    writeScope: state.write_scope || null
  };
}

function buildRunFromLegacyReport(runId, logDir, report) {
  const files = report.files || filesForLogDir(logDir);
  const status = report.status && report.status !== "running" ? report.status : "completed_unknown";
  return {
    runId,
    profileName: report.profile || "unknown",
    model: report.model || MODEL,
    initialResolvedModel: report.initial_resolved_model || null,
    resolvedModel: report.resolved_model || null,
    resolvedModelHistory: report.resolved_model_history || [],
    modelSwitchObserved: report.model_switch_observed === true,
    modelUsageModels: report.model_usage_models || [],
    modelEnvOverridesStripped: report.model_env_overrides_stripped || [],
    effort: report.effort || null,
    topic: report.topic || null,
    sessionPersistence: report.session_persistence !== false,
    autoMemory: report.auto_memory !== false,
    billing: report.billing || null,
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
    finalOutputFile: files.final_output || files.finalOutput || path.join(logDir, "final-output.md"),
    reportFile: files.report || path.join(logDir, "report.json"),
    stateFile: files.state || path.join(logDir, "state.json"),
    exitCodeFile: files.exit_code || files.exitCode || path.join(logDir, "exit-code.txt"),
    commandSummary: report.command || [],
    status,
    exitCode: report.exit_code ?? null,
    signal: report.signal ?? null,
    sessionId: report.session_id ?? null,
    sessionObserved: report.session_observed === true,
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
    tmuxDoneChannel: report.tmux_done_channel || null,
    writeScope: report.write_scope ? { final_evaluation: report.write_scope } : null
  };
}

function buildReport(run) {
  const events = readRunEvents(run);
  refreshRunRuntimeFacts(run, events);
  const warnings = detectWarnings(events, run.cwd);
  const milestones = summarizeMilestones(events);
  const activity = activitySummary(events, run);
  const chatRelay = buildFinalChatRelay(events, run);
  const writeScope = isTerminalStatus(run.status)
    ? run.writeScope?.final_evaluation || (run.writeScope ? terminalWriteScopeUnknown(run.writeScope) : null)
    : run.writeScope
      ? {
          status: "pending",
          enforcement:
            run.writeScope.mode === "guarded"
              ? GUARDED_WRITE_ENFORCEMENT
              : run.writeScope.mode === "read_only_observation"
                ? "read_only_git_footprint_observation"
                : "unrestricted_git_footprint_observation",
          allowed_files: run.writeScope.allowed_files
        }
      : null;
  if (writeScope?.status === "failed") {
    const details = [
      writeScope.out_of_scope_files?.length
        ? `out-of-scope files: ${writeScope.out_of_scope_files.join(", ")}`
        : null,
      writeScope.head_changed ? "Git HEAD changed" : null,
      writeScope.symlink_files?.length
        ? `allowed paths became symlinks: ${writeScope.symlink_files.join(", ")}`
        : null
    ].filter(Boolean);
    const readOnlyViolation = writeScope.enforcement === "read_only_git_footprint_observation";
    warnings.push({
      kind: readOnlyViolation ? "read_only_footprint_changed" : "write_scope_violation",
      detail: readOnlyViolation
        ? `The shared Git worktree changed during Claude's read-only run: ${(writeScope.changed_files || []).join(", ") || "HEAD changed"}. Attribution is unknown; another concurrent agent may be responsible.`
        : `Claude worker violated its authorized scope (${details.join("; ")}).`,
      recovery: "Inspect the working tree. Do not revert user changes automatically; repair or restore only with explicit authorization."
    });
  } else if (writeScope?.status === "unknown") {
    const readOnlyUnknown = writeScope.enforcement === "read_only_git_footprint_observation";
    warnings.push({
      kind: readOnlyUnknown ? "read_only_footprint_unknown" : "write_scope_unknown",
      detail: writeScope.error || "The final Git footprint could not be proven.",
      recovery: "Inspect git status and diff before accepting the result."
    });
  }
  if (run.modelSwitchObserved) {
    warnings.push({
      kind: "model_switch_observed",
      detail: `Claude's primary model changed during this run: ${(run.resolvedModelHistory || []).join(" -> ")}.`,
      recovery: "Treat the final answer as produced by the last resolved model and preserve the switch as routing evidence."
    });
  }

  return {
    run_id: run.runId,
    profile: run.profileName,
    model: run.model || MODEL,
    initial_resolved_model: run.initialResolvedModel || null,
    resolved_model: run.resolvedModel || null,
    resolved_model_history: run.resolvedModelHistory || [],
    model_switch_observed: run.modelSwitchObserved === true,
    model_usage_models: run.modelUsageModels || [],
    model_env_overrides_stripped: run.modelEnvOverridesStripped || [],
    effort: run.effort || null,
    topic: run.topic || null,
    session_persistence: run.sessionPersistence !== false,
    auto_memory: run.autoMemory !== false,
    billing: run.billing || null,
    write_scope: writeScope,
    cwd: run.cwd,
    pid: run.child?.pid ?? run.pid ?? null,
    status: run.status,
    managed: isManagedRun(run),
    orphan_reason: run.orphanReason || null,
    exit_code: run.exitCode ?? null,
    signal: run.signal ?? null,
    session_id: run.sessionId ?? null,
    session_observed: run.sessionObserved === true,
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
    chat_relay: chatRelay,
    final_output_summary: finalOutputSummary(events),
    agent_behavior: {
      role: "controlled_external_claude",
      control_surface: run.useTmux ? "tmux_managed_run" : "managed_process",
      observable_trace: {
        available: true,
        activity_note: activity.note,
        recent_tool_trace_count: activity.recent_tool_trace.length,
        recent_path_count: activity.recent_paths.length,
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
      warnings_count: warnings.length,
      write_scope_status: writeScope?.status || null
    },
    files: runFiles(run)
  };
}

function writeReport(run) {
  const report = buildReport(run);
  writeState(run);
  writeJsonAtomic(run.reportFile, report);
  return report;
}

function writeRunScript(files, run, command, args, runEnv) {
  const commandLine = [
    "env",
    ...[...CLAUDE_AUTH_OVERRIDE_ENV, ...CLAUDE_MODEL_OVERRIDE_ENV].flatMap((name) => ["-u", name]),
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
    profile = "advisor",
    cwd = process.cwd(),
    title,
    topic,
    extraArgs,
    model,
    effort,
    appendSystemPrompt,
    appendSubagentSystemPrompt,
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
    forwardSubagentText,
    safeMode,
    writeFiles,
    useTmux,
    tmuxMode
  } = options || {};

  if (!prompt || !String(prompt).trim()) {
    throw new Error("claude_run requires a non-empty prompt.");
  }
  const billing = assertSubscriptionBilling({ ...options, cwd });
  assertSupportedOptions(
    profile === "unrestricted"
      ? options
      : { ...options, appendSubagentSystemPrompt: appendSubagentSystemPrompt || "bridge-owned boundary" }
  );

  const profileConfig = getProfile(profile);
  if (profileConfig.unsupported) {
    throw new Error(`Profile ${profile} is marked unsupported.`);
  }
  assertProfileInvariants(profile, profileConfig, options);
  const profilePermissionMode = flagValue(profileConfig.flags, "--permission-mode");
  const effectivePermissionMode = permissionMode || profilePermissionMode;
  const bypassRequested =
    profileConfig.flags.includes("--dangerously-skip-permissions") ||
    allowDangerouslySkipPermissions ||
    effectivePermissionMode === "bypassPermissions";
  if (["plan", "manual", "default"].includes(effectivePermissionMode) && bypassRequested) {
    throw new Error(`Conflicting permission controls: ${effectivePermissionMode} cannot be combined with permission bypass.`);
  }
  if (resume && sessionId) {
    throw new Error("Use either resume or sessionId, not both.");
  }
  if (writeFiles !== undefined && profile !== "worker") {
    throw new Error("writeFiles is available only with the worker profile.");
  }
  const writeScope =
    profile === "worker"
      ? normalizeWriteFiles(cwd, writeFiles)
      : profile === "unrestricted"
        ? snapshotGitFootprint(cwd)
        : snapshotGitFootprint(cwd, "read_only_observation");
  const workerBoundary = writeScope?.mode === "guarded"
    ? [
        "Authorized write scope:",
        ...writeScope.allowed_files.map((file) => `- ${file}`),
        "Modify only those exact files. Preserve all pre-existing changes. Do not commit, reset, rebase, stash, or change Git configuration.",
        "If the task requires any other file, stop and report the missing authorization instead of writing it."
      ].join("\n")
    : null;
  const effectiveAppendSystemPrompt = [appendSystemPrompt, workerBoundary].filter(Boolean).join("\n\n") || undefined;
  const subagentBoundary =
    profile === "unrestricted"
      ? null
      : profile === "worker"
        ? workerBoundary
        : "This bridge run is read-only. Do not use Bash, Edit, Write, NotebookEdit, hooks, or external write actions. Return evidence to the lead without changing state.";
  const effectiveAppendSubagentSystemPrompt = [appendSubagentSystemPrompt, subagentBoundary]
    .filter(Boolean)
    .join("\n\n") || undefined;

  const requestedModel = model || flagValue(profileConfig.flags, "--model", MODEL);
  const requestedEffort = effort || flagValue(profileConfig.flags, "--effort", null);
  const cliSessionId = sessionId || (!resume && !noSessionPersistence ? randomUUID() : null);
  const requestedSessionId = cliSessionId || (typeof resume === "string" && !forkSession ? resume : null);
  const threadTopic = String(topic || name || title || String(prompt).slice(0, 80)).trim();

  ensureDir(RUNS_DIR);
  const runId = `${nowIsoForPath()}-${randomUUID().slice(0, 8)}`;
  const logDir = path.join(RUNS_DIR, runId);
  ensureDir(logDir);
  const files = filesForLogDir(logDir);

  fs.writeFileSync(files.prompt, String(prompt));
  fs.writeFileSync(
    files.profile,
    JSON.stringify(
      { name: profile, ...profileConfig, requested_model: requestedModel, requested_effort: requestedEffort },
      null,
      2
    )
  );

  const { command, prefixArgs } = resolveClaudeCommand();
  const runEnv = {
    ...process.env,
    CLAUDE_BRIDGE_RUN_ID: runId,
    ...(profileConfig.env || {}),
    ...(options.env || {})
  };
  const modelEnvOverridesStripped = CLAUDE_MODEL_OVERRIDE_ENV.filter((name) => runEnv[name] !== undefined);
  stripClaudeAuthOverrides(runEnv);
  stripClaudeModelOverrides(runEnv);
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
      model: requestedModel,
      effort: requestedEffort,
      appendSystemPrompt: effectiveAppendSystemPrompt,
      appendSubagentSystemPrompt: effectiveAppendSubagentSystemPrompt,
      appendSystemPromptFile,
      systemPrompt,
      systemPromptFile,
      maxBudgetUsd,
      maxTurns,
      fallbackModel,
      sessionId: cliSessionId,
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
      forwardSubagentText,
      safeMode
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
    model: requestedModel,
    initialResolvedModel: null,
    resolvedModel: null,
    resolvedModelHistory: [],
    modelSwitchObserved: false,
    modelUsageModels: [],
    modelEnvOverridesStripped,
    effort: requestedEffort,
    topic: threadTopic,
    sessionPersistence: !noSessionPersistence,
    autoMemory: !options.disableAutoMemory && profile !== "no-memory",
    billing,
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
    finalOutputFile: files.finalOutput,
    reportFile: files.report,
    stateFile: files.state,
    exitCodeFile: files.exitCode,
    commandSummary: summary,
    status: "running",
    exitCode: null,
    signal: null,
    sessionId: requestedSessionId,
    sessionObserved: false,
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
    tmuxDoneChannel,
    writeScope
  };

  startWriteObservation(run);

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
        topic: threadTopic,
        requested_model: requestedModel,
        requested_effort: requestedEffort,
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
          subscription_billing_guard: billing,
          model_env_overrides_stripped: modelEnvOverridesStripped
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
      model: requestedModel,
      effort: requestedEffort,
      topic: threadTopic,
      session_id: requestedSessionId,
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
        if (event.session_id || event.sessionId) {
          run.sessionId = event.session_id || event.sessionId;
          run.sessionObserved = true;
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
    model: requestedModel,
    effort: requestedEffort,
    topic: threadTopic,
    session_id: requestedSessionId,
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
    const run = refreshInactiveRun(buildRunFromState(runId, logDir, safeReadJson(files.state, {})));
    if (
      isTerminalStatus(run.status) &&
      run.writeScope &&
      !run.writeScope.final_evaluation &&
      fs.existsSync(files.report)
    ) {
      const savedWriteScope = safeReadJson(files.report, {})?.write_scope;
      if (savedWriteScope?.status && savedWriteScope.status !== "pending") {
        run.writeScope.final_evaluation = savedWriteScope;
      }
    }
    if (isTerminalStatus(run.status) && run.writeScope && !run.writeScope.final_evaluation) {
      run.writeScope.final_evaluation = terminalWriteScopeUnknown(run.writeScope);
    }
    return run;
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

function appendThreadEvent(event) {
  ensureDir(RUNS_DIR);
  jsonLine(THREADS_FILE, event);
}

function threadLeaseFile(threadId) {
  return path.join(THREAD_LEASES_DIR, `${String(threadId).replace(/[^A-Za-z0-9_-]/gu, "-")}.json`);
}

function acquireThreadLease(threadId) {
  ensureDir(THREAD_LEASES_DIR);
  const file = threadLeaseFile(threadId);
  const token = randomUUID();
  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      const descriptor = fs.openSync(file, "wx", 0o600);
      fs.writeFileSync(
        descriptor,
        JSON.stringify({ thread_id: threadId, token, owner_pid: process.pid, acquired_at: new Date().toISOString() })
      );
      fs.closeSync(descriptor);
      return { file, token };
    } catch (error) {
      if (error?.code !== "EEXIST") throw error;
      const existing = safeReadJson(file, {});
      const acquiredAt = Date.parse(existing.acquired_at || "");
      const fileAge = (() => {
        try {
          return Date.now() - fs.statSync(file).mtimeMs;
        } catch {
          return Number.POSITIVE_INFINITY;
        }
      })();
      const fresh =
        (Number.isFinite(acquiredAt) && Date.now() - acquiredAt < 30_000) || fileAge < 30_000;
      if (fresh) {
        throw new Error(`Claude thread ${threadId} is being claimed by another bridge process.`);
      }
      fs.rmSync(file, { force: true });
    }
  }
  throw new Error(`Could not acquire Claude thread lease: ${threadId}`);
}

function releaseThreadLease(lease) {
  if (!lease?.file) return;
  const existing = safeReadJson(lease.file, {});
  if (existing.token === lease.token) fs.rmSync(lease.file, { force: true });
}

function foldThreads() {
  const threads = new Map();
  for (const event of readJsonLines(THREADS_FILE)) {
    const threadId = event.thread_id;
    if (!threadId) continue;
    const previous = threads.get(threadId) || {
      thread_id: threadId,
      topic: null,
      cwd: null,
      workspace: null,
      profile: "advisor",
      model: MODEL,
      effort: null,
      created_at: event.observed_at || null,
      last_active_at: event.observed_at || null,
      last_run_id: null,
      run_ids: [],
      turns: 0,
      archived: false
    };
    if (event.type === "start") {
      previous.topic = event.topic || previous.topic;
      previous.cwd = event.cwd || previous.cwd;
      previous.workspace = event.workspace || previous.workspace;
      previous.profile = event.profile || previous.profile;
      previous.model = event.model || previous.model;
      previous.effort = event.effort || previous.effort;
      previous.created_at = event.observed_at || previous.created_at;
      previous.archived = false;
    }
    if (event.type === "start" || event.type === "send") {
      previous.last_run_id = event.run_id || previous.last_run_id;
      if (event.run_id && !previous.run_ids.includes(event.run_id)) previous.run_ids.push(event.run_id);
      previous.last_active_at = event.observed_at || previous.last_active_at;
      previous.turns += 1;
      previous.profile = event.profile || previous.profile;
      previous.model = event.model || previous.model;
      previous.effort = event.effort || previous.effort;
    }
    if (event.type === "archive") previous.archived = true;
    if (event.type === "unarchive") previous.archived = false;
    threads.set(threadId, previous);
  }
  return threads;
}

function requireThread(threadId) {
  const thread = foldThreads().get(threadId);
  if (!thread) throw new Error(`Unknown Claude thread_id: ${threadId}`);
  return thread;
}

export function listThreads({ cwd, includeArchived = false } = {}) {
  const expectedCwd = cwd ? path.resolve(cwd) : null;
  const threads = [...foldThreads().values()]
    .filter((thread) => includeArchived || !thread.archived)
    .filter((thread) => !expectedCwd || path.resolve(thread.cwd || "") === expectedCwd)
    .map((thread) => {
      const reports = thread.run_ids.map((runId) => {
        try {
          return resultRun(runId);
        } catch {
          return null;
        }
      });
      const run = reports.at(-1) || null;
      const currentWorkspace = gitWorkspaceContext(thread.cwd);
      const hasReadySession = reports.some(
        (report) => report?.status === "completed" && report?.session_observed === true
      );
      const lastBusy = WAITABLE_STATUSES.has(run?.status);
      const workspaceMatch =
        !thread.workspace ||
        (thread.workspace.worktree_root === currentWorkspace.worktree_root &&
          thread.workspace.ref === currentWorkspace.ref);
      const lifecycle = lastBusy
        ? "busy"
        : hasReadySession
          ? run?.status === "completed"
            ? "ready"
            : "ready_with_failed_last_turn"
          : run
            ? "failed"
            : "unknown";
      return {
        ...thread,
        last_status: run?.status || "unknown",
        lifecycle,
        current_workspace: currentWorkspace,
        workspace_match: workspaceMatch,
        session_observed: run?.session_observed === true,
        resolved_model: run?.resolved_model || null,
        resumable: !thread.archived && hasReadySession && !lastBusy && workspaceMatch,
        last_output_file: run?.files?.final_output || null
      };
    })
    .sort((left, right) => String(right.last_active_at).localeCompare(String(left.last_active_at)));
  return { registry: THREADS_FILE, count: threads.length, threads };
}

export function startThread({ prompt, topic, cwd = process.cwd(), profile = "advisor", ...options } = {}) {
  if (!topic || !String(topic).trim()) {
    throw new Error("claude_thread_start requires a non-empty topic.");
  }
  if (options.noSessionPersistence) {
    throw new Error("Persistent Claude threads cannot use noSessionPersistence.");
  }
  const started = startRun({
    ...options,
    prompt,
    topic: String(topic).trim(),
    name: options.name || String(topic).trim(),
    cwd,
    profile,
    noSessionPersistence: false
  });
  appendThreadEvent({
    type: "start",
    thread_id: started.session_id,
    topic: started.topic,
    cwd: started.cwd,
    workspace: gitWorkspaceContext(started.cwd),
    profile: started.profile,
    model: started.model,
    effort: started.effort,
    run_id: started.run_id
  });
  return { ...started, thread_id: started.session_id };
}

export function sendThread({ thread_id: threadId, prompt, cwd, profile, model, effort, ...options } = {}) {
  const lease = acquireThreadLease(threadId);
  try {
    const thread = requireThread(threadId);
    if (thread.archived) throw new Error(`Claude thread ${threadId} is archived.`);
    const threadWorkspace = assertThreadWorkspace(thread, cwd || thread.cwd);
    const status = listThreads({ includeArchived: true }).threads.find(
      (candidate) => candidate.thread_id === threadId
    );
    if (status?.lifecycle === "busy") {
      throw new Error(`Claude thread ${threadId} already has a live turn (${status.last_run_id}).`);
    }
    if (!status?.resumable) {
      throw new Error(`Claude thread ${threadId} has no completed, stream-observed session to resume.`);
    }
    if (profile !== undefined && profile !== thread.profile) {
      throw new Error(
        `Claude thread ${threadId} is bound to profile=${thread.profile}; start a fresh thread for profile=${profile}.`
      );
    }
    if (model !== undefined && model !== thread.model) {
      throw new Error(
        `Claude thread ${threadId} is bound to model=${thread.model}; start a fresh thread for model=${model}.`
      );
    }
    if (effort !== undefined && effort !== thread.effort) {
      throw new Error(
        `Claude thread ${threadId} is bound to effort=${thread.effort}; start a fresh thread for effort=${effort}.`
      );
    }
    const started = startRun({
      ...options,
      prompt,
      topic: thread.topic,
      cwd: threadWorkspace.cwd,
      profile: thread.profile,
      model: thread.model,
      effort: thread.effort,
      resume: threadId,
      noSessionPersistence: false
    });
    appendThreadEvent({
      type: "send",
      thread_id: threadId,
      topic: thread.topic,
      cwd: started.cwd,
      workspace: threadWorkspace.workspace,
      profile: started.profile,
      model: started.model,
      effort: started.effort,
      run_id: started.run_id
    });
    return { ...started, thread_id: threadId };
  } finally {
    releaseThreadLease(lease);
  }
}

export function archiveThread({ thread_id: threadId, archived = true } = {}) {
  const lease = acquireThreadLease(threadId);
  try {
    requireThread(threadId);
    const status = listThreads({ includeArchived: true }).threads.find(
      (candidate) => candidate.thread_id === threadId
    );
    if (status?.lifecycle === "busy") {
      throw new Error(`Claude thread ${threadId} has a live turn and cannot change archive state.`);
    }
    appendThreadEvent({ type: archived ? "archive" : "unarchive", thread_id: threadId });
    return { thread_id: threadId, archived };
  } finally {
    releaseThreadLease(lease);
  }
}

export function doctor() {
  const { command, prefixArgs } = resolveClaudeCommand();
  const version = spawnSync(command, [...prefixArgs, "--version"], { encoding: "utf8" });
  const help = spawnSync(command, [...prefixArgs, "--help"], { encoding: "utf8" });
  const auth = bridgeAuthStatus();
  const npm = spawnSync("npm", ["--version"], { encoding: "utf8" });
  const node = process.version;
  const helpText = `${help.stdout || ""}\n${help.stderr || ""}`;
  const authStatus = auth.status;
  const helperSources = apiKeyHelperSources(process.cwd());
  const settingsAuthOverrides = settingsOverrideSources(process.cwd(), undefined, CLAUDE_AUTH_OVERRIDE_ENV);
  const settingsModelOverrides = settingsOverrideSources(process.cwd(), undefined, CLAUDE_MODEL_OVERRIDE_ENV);
  const modelEnvOverrides = CLAUDE_MODEL_OVERRIDE_ENV.filter((name) => process.env[name] !== undefined);
  const requiredFlags = [
    "--model",
    "--effort",
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
    "--name",
    "--session-id",
    "--resume",
    "--safe-mode",
    "--forward-subagent-text",
    "--append-subagent-system-prompt"
  ];
  const coreFlags = [
    "--model",
    "--effort",
    "--output-format",
    "--debug-file",
    "--permission-mode",
    "--disallowedTools",
    "--verbose",
    "--include-partial-messages",
    "--include-hook-events",
    "--session-id",
    "--resume"
  ];
  const cliCompatible =
    version.status === 0 && help.status === 0 && coreFlags.every((flag) => helpText.includes(flag));
  const authenticated = authStatus.loggedIn === true;
  const subscriptionReady =
    auth.subscriptionReady && helperSources.length === 0 && settingsAuthOverrides.length === 0;
  const runtimeReady = cliCompatible && subscriptionReady && settingsModelOverrides.length === 0;
  const flagCapabilities = Object.fromEntries(
    requiredFlags.map((flag) => [flag, claudeFlagCapability(flag, helpText)])
  );
  return {
    ok: runtimeReady,
    cli_compatible: cliCompatible,
    ready_for_live_runs: runtimeReady,
    claude_command: commandSummary(command, prefixArgs),
    claude_version: shortText(version.stdout || version.stderr),
    auth: {
      logged_in: authenticated,
      method: authStatus.authMethod || null,
      provider: authStatus.apiProvider || null,
      subscription_type: authStatus.subscriptionType || null,
      status_code: auth.result.status,
      error: authStatus.error || null
    },
    billing: {
      mode: subscriptionReady ? "subscription_oauth" : "not_subscription_safe",
      auth_env_overrides_stripped: auth.strippedEnv,
      api_key_helper_sources: helperSources,
      settings_auth_override_sources: settingsAuthOverrides
    },
    node,
    npm_version: shortText(npm.stdout || npm.stderr),
    stream_json_supported: helpText.includes("stream-json"),
    opus_requested_by_profiles: MODEL,
    model_aliases: {
      fable: helpText.includes("fable"),
      opus: helpText.includes("opus"),
      sonnet: helpText.includes("sonnet")
    },
    model_env_overrides_stripped_on_run: modelEnvOverrides,
    settings_model_override_sources: settingsModelOverrides,
    flags: Object.fromEntries(requiredFlags.map((flag) => [flag, flagCapabilities[flag].supported])),
    flag_evidence: Object.fromEntries(requiredFlags.map((flag) => [flag, flagCapabilities[flag].evidence])),
    mcp_server: "stdio",
    note: "Read-only readiness check. ok requires CLI compatibility plus Claude.ai subscription OAuth after stripping higher-precedence API, gateway, cloud, and token environments. Live runs also strip model-family and subagent alias redirects; hidden documented flags use non-spending parser probes."
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

function toolEventFacts(event, eventIndex) {
  const core = event?.event && typeof event.event === "object" ? event.event : event;
  const contentSources = [core?.content, core?.message?.content];
  if (core !== event) contentSources.push(event?.message?.content);
  const contentBlocks = contentSources
    .flatMap((content) => (Array.isArray(content) ? content : []))
    .filter((block) => block && typeof block === "object" && /tool_(?:use|result)/iu.test(String(block.type || "")));
  return [core, ...contentBlocks].map((source) => {
    const type = String(source?.type || "").toLowerCase();
    const name = String(toolNameFromEvent(source) || "").toLowerCase();
    const input = source?.input || source?.tool_input || {};
    const filePath = input.file_path || input.path || source?.file_path || source?.path || null;
    return {
      event,
      block: source,
      event_index: eventIndex,
      type,
      name,
      file_path: filePath,
      tool_use_id: source?.tool_use_id || null,
      id: source?.id || null,
      is_error: source?.is_error === true || Boolean(source?.error),
      text: extractEventText(source) || extractEventText(event)
    };
  });
}

function strictStreamToolEvidence(events, targetPath) {
  const facts = events.flatMap(toolEventFacts);
  const uses = facts.filter(
    (fact) =>
      (fact.type.includes("tool_use") || fact.type.includes("tool_call")) &&
      fact.name === "read" &&
      fact.file_path &&
      path.resolve(fact.file_path) === path.resolve(targetPath)
  );
  const successful = [];
  for (const use of uses) {
    const result = facts.find(
      (fact) =>
        fact.event_index > use.event_index &&
        fact.type.includes("tool_result") &&
        ((use.id && fact.tool_use_id === use.id) || (!use.id && eventMentionsPath(fact.event, targetPath)))
    );
    if (!result) continue;
    const knownFailure = result.is_error || /\b(?:enoent|permission denied|read failed)\b/iu.test(result.text);
    if (!knownFailure) successful.push({ tool_use: use.event, tool_result: result.event });
  }
  return { attempts: uses, successful };
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
  let report = await waitRun(started.run_id, { timeoutMs });
  if (report.timed_out) {
    killRun(started.run_id);
    report = await waitRun(started.run_id, { timeoutMs: 10000 });
    if (!isTerminalStatus(report.status)) {
      killRun(started.run_id);
      report = await waitRun(started.run_id, { timeoutMs: 10000 });
    }
    const tailTerminal = isTerminalStatus(report.status);
    const audit = {
      evidence: "timed_out",
      reason: tailTerminal
        ? "Skill audit exceeded its timeout and the managed Claude run reached a terminal state after kill."
        : "Skill audit exceeded its timeout; kill was requested, but terminal process-tail evidence is still missing.",
      tail_terminal: tailTerminal,
      target_path: resolvedSkillPath,
      run: report,
      matching_events: []
    };
    fs.writeFileSync(path.join(started.log_dir, "skill-audit.json"), JSON.stringify(audit, null, 2));
    return audit;
  }
  const events = readJsonLines(report.files.events);
  const streamEvidence = strictStreamToolEvidence(events, resolvedSkillPath);
  const toolEvidence = streamEvidence.successful;
  const selfReportOnly =
    events.some((event) => eventMentionsPath(event, resolvedSkillPath)) &&
    toolEvidence.length === 0 &&
    streamEvidence.attempts.length === 0;
  const evidence = toolEvidence.length ? "passed" : selfReportOnly ? "unknown" : "failed";
  const audit = {
    evidence,
    reason:
      evidence === "passed"
        ? "Structured stream evidence pairs an exact-path Read call with a successful tool result."
        : evidence === "unknown"
          ? "The target path appears only in message-like output, not structured tool evidence."
          : streamEvidence.attempts.length
            ? "An exact-path Read was attempted, but no successful paired tool result proved the file was read."
            : "No exact-path Read call with a successful paired tool result was observed.",
    target_path: resolvedSkillPath,
    run: report,
    matching_events: toolEvidence.slice(0, 10),
    read_attempts: streamEvidence.attempts.slice(0, 10).map((attempt) => attempt.event)
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
  const skippedActive = [];
  const skippedUnknown = [];

  for (const entry of entries) {
    const runId = entry.name;
    const runDir = path.join(RUNS_DIR, runId);
    const stateFile = path.join(runDir, "state.json");
    const reportFile = path.join(runDir, "report.json");
    const state = safeReadJson(stateFile, null);
    const legacyReport = safeReadJson(reportFile, null);
    const stat = fs.statSync(runDir);
    const startedAtMs = state?.started_at ? Date.parse(state.started_at) : Number.NaN;
    const ageBaseMs = Number.isFinite(startedAtMs) ? startedAtMs : stat.mtimeMs;
    if (ageBaseMs > cutoffMs) continue;
    const ageDays = Math.floor((Date.now() - ageBaseMs) / (24 * 60 * 60 * 1000));
    if (fs.existsSync(stateFile) && !state) {
      skippedUnknown.push({ run_id: runId, path: runDir, age_days: ageDays, reason: "corrupt state.json" });
      continue;
    }
    if (!state && fs.existsSync(reportFile) && !legacyReport) {
      skippedUnknown.push({ run_id: runId, path: runDir, age_days: ageDays, reason: "corrupt report.json" });
      continue;
    }
    if (!state && !fs.existsSync(reportFile)) {
      skippedUnknown.push({ run_id: runId, path: runDir, age_days: ageDays, reason: "missing state and report" });
      continue;
    }
    let refreshed;
    try {
      refreshed = resultRun(runId);
    } catch (error) {
      skippedUnknown.push({ run_id: runId, path: runDir, age_days: ageDays, reason: error.message });
      continue;
    }
    if (WAITABLE_STATUSES.has(refreshed.status)) {
      skippedActive.push({ run_id: runId, path: runDir, age_days: ageDays, status: refreshed.status });
      continue;
    }
    if (!TERMINAL_STATUSES.has(refreshed.status)) {
      skippedUnknown.push({
        run_id: runId,
        path: runDir,
        age_days: ageDays,
        reason: `unproven terminal status: ${refreshed.status || "unknown"}`
      });
      continue;
    }
    candidates.push({
      run_id: runId,
      path: runDir,
      age_days: ageDays,
      status: refreshed.status || state?.status || "unknown"
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
    candidates,
    skipped_active: skippedActive,
    skipped_unknown: skippedUnknown
  };
}
