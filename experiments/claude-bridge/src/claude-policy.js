import { execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { promisify } from "node:util";
import { z } from "zod";
import { ClaudeAskError, compactTail, isClaudeSessionId } from "./claude-result.js";

const execFileAsync = promisify(execFile);
export const CLAUDE_EXECUTABLE = "/Users/triton/.local/bin/claude";

const PROFILES = Object.freeze({
  opus_advisor: Object.freeze({ model: "opus", effort: "xhigh" }),
  fable_advisor: Object.freeze({ model: "fable", effort: "xhigh" })
});

export const claudeAskInputSchema = Object.freeze({
  prompt: z.string().min(1).max(60_000),
  profile: z.enum(["opus_advisor", "fable_advisor"]),
  cwd: z.string().min(1),
  session_id: z.string().uuid().optional()
});
const requestSchema = z.object(claudeAskInputSchema).strict();

// Personal-tool hygiene, not a hostile-config sandbox. Native Claude settings stay active.
const EXPLICIT_ROUTE_ENV = Object.freeze([
  "ANTHROPIC_API_KEY",
  "ANTHROPIC_AUTH_TOKEN",
  "ANTHROPIC_AWS_API_KEY",
  "ANTHROPIC_AWS_BASE_URL",
  "ANTHROPIC_BASE_URL",
  "ANTHROPIC_BEDROCK_BASE_URL",
  "ANTHROPIC_CUSTOM_HEADERS",
  "ANTHROPIC_FOUNDRY_API_KEY",
  "ANTHROPIC_FOUNDRY_AUTH_TOKEN",
  "ANTHROPIC_FOUNDRY_BASE_URL",
  "ANTHROPIC_VERTEX_BASE_URL",
  "AWS_BEARER_TOKEN_BEDROCK",
  "CLAUDE_API_KEY",
  "CLAUDE_CODE_OAUTH_REFRESH_TOKEN",
  "CLAUDE_CODE_OAUTH_SCOPES",
  "CLAUDE_CODE_OAUTH_TOKEN",
  "CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST",
  "CLAUDE_CODE_USE_ANTHROPIC_AWS",
  "CLAUDE_CODE_USE_BEDROCK",
  "CLAUDE_CODE_USE_FOUNDRY",
  "CLAUDE_CODE_USE_MANTLE",
  "CLAUDE_CODE_USE_VERTEX"
]);

function canonicalDirectory(value) {
  if (!value || !String(value).trim()) throw new ClaudeAskError("invalid_cwd", "Claude cwd is required.");
  const requested = path.resolve(String(value));
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
    if (field === "profile") throw new ClaudeAskError("unsupported_profile", "Use opus_advisor or fable_advisor.");
    if (field === "session_id") throw new ClaudeAskError("invalid_session_id", "Claude session_id must be a UUID.");
    if (field === "cwd") throw new ClaudeAskError("invalid_cwd", "Claude cwd is required.");
    throw new ClaudeAskError("invalid_request", "claude_ask requires a prompt of 1 to 60000 characters.");
  }
  if (!parsed.data.prompt.trim()) {
    throw new ClaudeAskError("invalid_request", "claude_ask requires a non-empty prompt.");
  }
  const profile = PROFILES[parsed.data.profile];
  if (parsed.data.session_id && !isClaudeSessionId(parsed.data.session_id)) {
    throw new ClaudeAskError("invalid_session_id", "Claude session_id must be a UUID.");
  }
  return {
    cwd: canonicalDirectory(parsed.data.cwd),
    profile,
    prompt: parsed.data.prompt,
    sessionId: parsed.data.session_id || null
  };
}

function sanitizedEnvironment(extraEnv) {
  const env = { ...process.env, ...extraEnv };
  const stripped = EXPLICIT_ROUTE_ENV.filter((name) => env[name] !== undefined);
  for (const name of EXPLICIT_ROUTE_ENV) delete env[name];
  return { env, stripped };
}

async function requireSubscription(executable, cwd, env, options) {
  let stdout;
  try {
    ({ stdout } = await execFileAsync(executable, ["auth", "status"], {
      cwd,
      env,
      encoding: "utf8",
      maxBuffer: 64 * 1024,
      signal: options.signal,
      timeout: options.authTimeoutMs ?? 10_000
    }));
  } catch (error) {
    if (options.signal?.aborted || error?.name === "AbortError") throw error;
    throw new ClaudeAskError("auth_probe_failed", `Claude auth status failed: ${compactTail(error?.stderr || error?.message)}`);
  }

  let status;
  try {
    status = JSON.parse(stdout || "{}");
  } catch {
    throw new ClaudeAskError("auth_probe_failed", "Claude auth status returned malformed JSON.");
  }
  if (
    status.loggedIn !== true ||
    status.authMethod !== "claude.ai" ||
    status.apiProvider !== "firstParty" ||
    !status.subscriptionType
  ) {
    throw new ClaudeAskError(
      "subscription_required",
      `Claude.ai subscription auth required; active route is ${status.authMethod || "none"}/${status.apiProvider || "none"}/${status.subscriptionType || "none"}.`
    );
  }
  return status.subscriptionType;
}

/** Validate one public request and prove subscription auth in its exact SDK environment. */
export async function prepareClaudeRequest(request, options = {}) {
  const canonical = canonicalRequest(request);
  const { env, stripped } = sanitizedEnvironment(options.env);
  const executable = options.executable || CLAUDE_EXECUTABLE;
  if (!fs.existsSync(executable)) {
    throw new ClaudeAskError("missing_claude", `Claude executable is unavailable: ${executable}`);
  }
  const subscriptionType = await requireSubscription(executable, canonical.cwd, env, options);
  return { ...canonical, env, executable, stripped, subscriptionType };
}

/** Reject SDK evidence that contradicts the already-proven subscription route. */
export function assertSdkSubscriptionEvidence(init) {
  if (!init || !["none", "oauth"].includes(init.apiKeySource)) {
    throw new ClaudeAskError(
      "sdk_subscription_required",
      `Claude SDK exposed a non-subscription credential source: ${init?.apiKeySource || "missing"}.`
    );
  }
}
