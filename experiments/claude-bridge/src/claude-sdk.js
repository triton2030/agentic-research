import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { ClaudeAskError, claudeSdkResultError } from "./claude-result.js";

export const CLAUDE_SDK_VERSION = JSON.parse(readFileSync(
  new URL("./package.json", import.meta.resolve("@anthropic-ai/claude-agent-sdk")), "utf8"
)).version;

const CLIENT_APP = "claude-bridge/2.0";
const MAX_TURNS = 48;
const DEFAULT_INTERRUPT_GRACE_MS = 5_000;
const TERMINAL_COMMAND_STATES = new Set(["cancelled", "completed", "discarded"]);

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, reject, resolve };
}

function collectModel(models, value) {
  if (typeof value !== "string" || !value || value === "<synthetic>") return;
  if (models.at(-1) !== value) models.push(value);
}

/** Reduce one raw SDK event to the bridge's compact warning vocabulary. */
export function claudeRuntimeWarning(message) {
  let warning = null;
  if (message.type === "rate_limit_event") {
    const info = message.rate_limit_info || {};
    if (info.errorCode === "credits_required") warning = "subscription_credits_required";
    else if (info.isUsingOverage || info.overageInUse) warning = "subscription_overage_in_use";
    else if (info.status === "rejected") warning = `subscription_rate_limit:${info.rateLimitType || "unknown"}`;
    else if (info.status === "allowed_warning") warning = `subscription_rate_limit_warning:${info.rateLimitType || "unknown"}`;
  } else if (message.type === "system" && message.subtype === "permission_denied") {
    warning = `permission_denied:${message.tool_name || "tool"}`;
  } else if (message.type === "system" && message.subtype === "model_refusal_fallback") {
    warning = [
      "model_refusal_fallback",
      message.original_model || "unknown",
      message.fallback_model || "unknown",
      message.api_refusal_category || "uncategorized"
    ].join(":");
  }
  return warning;
}

/** Keep actionable subscription facts, never account/payment data or raw events. */
export function claudeRateLimit(message) {
  if (message.type !== "rate_limit_event") return null;
  const info = message.rate_limit_info || {};
  if (!["allowed", "allowed_warning", "rejected"].includes(info.status)) return null;
  const result = { status: info.status };
  for (const [source, target] of [
    ["resetsAt", "resets_at"], ["overageResetsAt", "overage_resets_at"],
    ["utilization", "utilization"]
  ]) {
    if (Number.isFinite(info[source]) && info[source] >= 0) result[target] = info[source];
  }
  for (const [source, target] of [
    ["rateLimitType", "rate_limit_type"], ["overageStatus", "overage_status"],
    ["overageDisabledReason", "overage_disabled_reason"], ["errorCode", "error_code"]
  ]) {
    if (typeof info[source] === "string" && /^[a-z0-9_]{1,64}$/u.test(info[source])) {
      result[target] = info[source];
    }
  }
  if (typeof info.overageEnabled === "boolean") result.overage_enabled = info.overageEnabled;
  if (typeof info.isUsingOverage === "boolean" || typeof info.overageInUse === "boolean") {
    result.is_using_overage = info.isUsingOverage === true || info.overageInUse === true;
  }
  return result;
}

function contextSummary(usage) {
  if (![usage?.totalTokens, usage?.maxTokens, usage?.percentage]
    .every((value) => Number.isFinite(value) && value >= 0) || usage.maxTokens === 0) return null;
  return {
    used_tokens: usage.totalTokens,
    max_tokens: usage.maxTokens,
    used_percent: usage.percentage,
    estimated: true
  };
}

function collectRuntimeWarning(warnings, message) {
  const warning = claudeRuntimeWarning(message);
  if (warning && !warnings.includes(warning)) warnings.push(warning);
}

/** Small owned AsyncIterable: SDK close does not close the caller's input stream. */
export class AsyncMailbox {
  #closed = false;
  #queue = [];
  #waiters = [];

  push(value) {
    if (this.#closed) throw new Error("Claude input mailbox is closed.");
    const waiter = this.#waiters.shift();
    if (waiter) waiter({ done: false, value });
    else this.#queue.push(value);
  }

  close() {
    if (this.#closed) return;
    this.#closed = true;
    for (const waiter of this.#waiters.splice(0)) waiter({ done: true, value: undefined });
  }

  next() {
    if (this.#queue.length) return Promise.resolve({ done: false, value: this.#queue.shift() });
    if (this.#closed) return Promise.resolve({ done: true, value: undefined });
    return new Promise((resolve) => this.#waiters.push(resolve));
  }

  return() {
    this.close();
    return Promise.resolve({ done: true, value: undefined });
  }

  [Symbol.asyncIterator]() {
    return this;
  }
}

function queryOptions(launch, options) {
  const isResume = Boolean(launch.sessionId);
  return {
    abortController: options.abortController,
    additionalDirectories: ["/"],
    agentProgressSummaries: true,
    allowDangerouslySkipPermissions: true,
    cwd: launch.cwd,
    env: {
      ...launch.env,
      CLAUDE_AGENT_SDK_CLIENT_APP: CLIENT_APP,
      CLAUDE_CODE_DISABLE_AUTO_MEMORY: "1",
      CLAUDE_CODE_STARTUP_FAILURE_RESULTS: "1"
    },
    forwardSubagentText: false,
    includeHookEvents: false,
    includePartialMessages: false,
    maxTurns: MAX_TURNS,
    mcpServers: {},
    pathToClaudeCodeExecutable: launch.executable,
    permissionMode: "bypassPermissions",
    persistSession: true,
    resume: launch.sessionId || undefined,
    settingSources: [],
    settings: {
      allowedMcpServers: [],
      autoMemoryEnabled: false,
      disableAllHooks: true,
      disableBundledSkills: true,
      disableClaudeAiConnectors: true,
      disableWorkflows: true,
      enableArtifact: false
    },
    skills: [],
    spawnClaudeCodeProcess: options.spawnClaudeCodeProcess,
    strictMcpConfig: true,
    // Native Claude behavior; the caller supplies the task and its write scope.
    // Re-render on resume instead of inheriting a previous custom advisor prompt.
    systemPrompt: { type: "preset", preset: "claude_code", snapshot: false },
    tools: { type: "preset", preset: "claude_code" },
    verbatimPrompts: true,
    ...(!isResume ? { effort: launch.profile.effort, model: launch.profile.model } : {})
  };
}

function userMessage(prompt, priority) {
  return {
    type: "user",
    message: { role: "user", content: prompt },
    parent_tool_use_id: null,
    priority,
    uuid: randomUUID()
  };
}

/**
 * Own one supported streaming Agent SDK Query.
 *
 * Exactly one bridge turn may be active at once. Results resolve the turn but
 * do not stop the output pump, so the same native process can accept follow-ups.
 */
export function startClaudeSdkSession(launch, options = {}) {
  const queryFactory = options.queryFactory || query;
  const abortController = options.abortController || new AbortController();
  const mailbox = new AsyncMailbox();
  const initReady = deferred();
  let init = null;
  let currentTurn = null;
  let lastRaw = null;
  let terminalError = null;
  let stopping = false;
  let terminated = false;
  let contextRequest = null;

  const handle = queryFactory({
    prompt: mailbox,
    options: queryOptions(launch, {
      ...options,
      abortController
    })
  });
  const emit = (message) => {
    try {
      options.onMessage?.(message);
    } catch {
      // Observation must never be able to terminate the Claude process.
    }
  };

  const settleCurrentTurn = () => {
    if (!currentTurn?.raw || !currentTurn.completed) return;
    currentTurn.resolve(currentTurn.raw);
    currentTurn = null;
  };

  const completion = (async () => {
    try {
      for await (const message of handle) {
        if (message.type === "system" && message.subtype === "init") {
          try {
            options.validateInit?.(message);
          } catch (error) {
            if (!abortController.signal.aborted) abortController.abort(error);
            handle.close?.();
            throw error;
          }
        }
        emit(message);
        if (currentTurn) collectRuntimeWarning(currentTurn.runtimeWarnings, message);
        const rateLimit = claudeRateLimit(message);
        if (currentTurn && rateLimit) {
          currentTurn.rateLimit = rateLimit;
          if (currentTurn.raw) currentTurn.raw.rateLimit = rateLimit;
        }
        if (message.type === "system" && message.subtype === "init") {
          init = message;
          initReady.resolve(message);
          if (currentTurn) collectModel(currentTurn.primaryModels, message.model);
          continue;
        }
        if (message.type === "assistant" && message.parent_tool_use_id === null && currentTurn) {
          collectModel(currentTurn.primaryModels, message.message?.model);
          continue;
        }
        if (message.type === "result") {
          if (
            currentTurn &&
            message.user_message_uuid &&
            message.user_message_uuid !== currentTurn.uuid
          ) {
            continue;
          }
          const raw = {
            init,
            result: message,
            primaryModels: currentTurn?.primaryModels || [],
            runtimeWarnings: currentTurn?.runtimeWarnings || [],
            rateLimit: currentTurn?.rateLimit || null,
            runtime: {
              sdk_version: CLAUDE_SDK_VERSION,
              claude_code_version: typeof init?.claude_code_version === "string"
                ? init.claude_code_version.slice(0, 80) : null
            },
            usageModels: Object.keys(message.modelUsage || {}),
            iteratorError: null
          };
          lastRaw = raw;
          if (currentTurn) {
            currentTurn.raw = raw;
            settleCurrentTurn();
          }
          if (!init) throw claudeSdkResultError(raw);
          continue;
        }
        if (
          message.type === "system" &&
          message.subtype === "session_state_changed" &&
          message.state === "idle" &&
          currentTurn
        ) {
          currentTurn.completed = true;
          settleCurrentTurn();
          continue;
        }
        // Claude Code emits a terminal lifecycle after result in streaming mode.
        // The installed SDK declaration still omits this top-level message type.
        if (
          message.type === "command_lifecycle" &&
          TERMINAL_COMMAND_STATES.has(message.state) &&
          message.command_uuid === currentTurn?.uuid
        ) {
          currentTurn.completed = true;
          settleCurrentTurn();
        }
      }
    } catch (error) {
      terminalError = error;
      if (lastRaw) lastRaw.iteratorError = error;
      if (currentTurn) {
        if (currentTurn.raw) currentTurn.resolve(currentTurn.raw);
        else currentTurn.reject(error);
        currentTurn = null;
      }
    } finally {
      terminated = true;
      if (!init) initReady.reject(terminalError || new Error("Claude SDK ended before initialization."));
      if (currentTurn) {
        if (currentTurn.raw) currentTurn.resolve(currentTurn.raw);
        else currentTurn.reject(terminalError || new Error("Claude SDK ended before returning a result."));
        currentTurn = null;
      }
      options.onTerminal?.({ error: terminalError, lastRaw });
    }
    return { error: terminalError, init, lastRaw };
  })();

  const ready = initReady.promise.then((initMessage) => ({ control: null, init: initMessage }));

  return {
    abortController,
    completion,
    ready,
    send(prompt, { priority = "now" } = {}) {
      if (stopping || terminated) throw new Error("Claude SDK session is not accepting turns.");
      if (currentTurn) throw new Error("Claude SDK session already has an active turn.");
      const turn = deferred();
      const message = userMessage(prompt, priority);
      currentTurn = {
        ...turn,
        completed: false,
        primaryModels: [],
        rateLimit: null,
        raw: null,
        runtimeWarnings: [],
        uuid: message.uuid
      };
      if (init) collectModel(currentTurn.primaryModels, init.model);
      mailbox.push(message);
      return { completion: turn.promise, uuid: message.uuid };
    },
    async interrupt(options) {
      if (stopping) return undefined;
      return handle.interrupt?.(options);
    },
    getContextUsage() {
      if (stopping || terminated || !init || !handle.getContextUsage) return Promise.resolve(null);
      // Repeated observations share a slow native request instead of queuing probes.
      if (!contextRequest) {
        contextRequest = Promise.resolve().then(() => handle.getContextUsage({ detail: "summary" }))
          .then(contextSummary).finally(() => { contextRequest = null; });
      }
      return contextRequest;
    },
    closeInput() {
      mailbox.close();
    },
    async stop(reason) {
      if (stopping) return completion;
      stopping = true;
      mailbox.close();
      if (reason && !abortController.signal.aborted) abortController.abort(reason);
      handle.close?.();
      return completion;
    }
  };
}

function gracefulCancellation(engine, signal, graceMs, messageUuid, onEvent) {
  let hardStopTimer = null;
  const emit = (event) => {
    try {
      onEvent?.(Object.freeze({ message_uuid: messageUuid, ...event }));
    } catch {
      // Cancellation observation must never change process ownership.
    }
  };
  const interrupt = () => {
    if (hardStopTimer) return;
    const reason = signal.reason || new Error("Claude request was cancelled.");
    hardStopTimer = setTimeout(() => {
      emit({ type: "hard_abort" });
      void engine.stop(reason).catch(() => {});
    }, graceMs);
    hardStopTimer.unref?.();
    void Promise.resolve(engine.interrupt({ cancelQueued: true })).then(
      (receipt) => emit({ receipt: receipt ?? null, type: "native_interrupt" }),
      () => emit({ type: "interrupt_error" })
    );
  };
  if (signal?.aborted) interrupt();
  else signal?.addEventListener("abort", interrupt, { once: true });
  return {
    close() {
      signal?.removeEventListener("abort", interrupt);
      if (hardStopTimer) clearTimeout(hardStopTimer);
    }
  };
}

/** Execute one native Claude turn through the shared streaming engine. */
export async function runClaudeSdk(launch, options = {}) {
  const engine = startClaudeSdkSession(launch, options);
  let cancellation = null;
  try {
    // Pinned Claude Code does not emit system/init until streaming input begins.
    // The exact-environment auth preflight already ran; validate SDK evidence
    // immediately after init and abort before waiting for the model result.
    const turn = engine.send(launch.prompt);
    cancellation = gracefulCancellation(
      engine,
      options.signal,
      options.interruptGraceMs ?? DEFAULT_INTERRUPT_GRACE_MS,
      turn.uuid,
      options.onCancellationEvent
    );
    void turn.completion.catch(() => {});
    let ready;
    try {
      ready = await engine.ready;
    } catch (error) {
      if (error instanceof ClaudeAskError) throw error;
      options.validateInit?.(null);
      throw error;
    }
    options.validateInit?.(ready.init);
    const raw = await turn.completion;
    await engine.stop();
    await engine.completion;
    return raw;
  } finally {
    cancellation?.close();
    const reason = options.signal?.aborted
      ? undefined
      : new Error("Claude one-shot query closed.");
    await engine.stop(reason).catch(() => {});
  }
}
