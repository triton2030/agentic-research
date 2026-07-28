import { randomUUID } from "node:crypto";
import { query } from "@anthropic-ai/claude-agent-sdk";

const CLIENT_APP = "claude-bridge/2.0";
const MAX_TURNS = 24;
const ADVISOR_INSTRUCTION = [
  "Act as an independent advisor.",
  "Investigate and read whatever evidence is necessary, but do not modify files, run state-changing commands, or take external actions.",
  "Return compact, decision-useful answers to the user's tasks."
].join(" ");

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, reject, resolve };
}

function advisorTask(prompt) {
  return `<task>\n${prompt}\n</task>`;
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
    cwd: launch.cwd,
    env: { ...launch.env, CLAUDE_AGENT_SDK_CLIENT_APP: CLIENT_APP },
    forwardSubagentText: false,
    includeHookEvents: false,
    includePartialMessages: false,
    maxTurns: MAX_TURNS,
    pathToClaudeCodeExecutable: launch.executable,
    persistSession: true,
    resume: launch.sessionId || undefined,
    spawnClaudeCodeProcess: options.spawnClaudeCodeProcess,
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: ADVISOR_INSTRUCTION
    },
    ...(!isResume ? { effort: launch.profile.effort, model: launch.profile.model } : {})
  };
}

function userMessage(prompt, priority) {
  return {
    type: "user",
    message: { role: "user", content: advisorTask(prompt) },
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
            usageModels: Object.keys(message.modelUsage || {}),
            iteratorError: null
          };
          lastRaw = raw;
          if (currentTurn) {
            currentTurn.raw = raw;
            settleCurrentTurn();
          }
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
        // Claude Code 2.1.219 emits this runtime event after result in streaming
        // mode even though the pinned SDK declaration omits it.
        if (
          message.type === "command_lifecycle" &&
          message.state === "completed" &&
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
        raw: null,
        runtimeWarnings: [],
        uuid: message.uuid
      };
      if (init) collectModel(currentTurn.primaryModels, init.model);
      mailbox.push(message);
      return { completion: turn.promise, uuid: message.uuid };
    },
    async interrupt() {
      if (stopping) return undefined;
      return handle.interrupt?.();
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

/** Execute one native Claude turn through the shared streaming engine. */
export async function runClaudeSdk(launch, options = {}) {
  const engine = startClaudeSdkSession(launch, options);
  try {
    // Pinned Claude Code does not emit system/init until streaming input begins.
    // The exact-environment auth preflight already ran; validate SDK evidence
    // immediately after init and abort before waiting for the model result.
    const turn = engine.send(launch.prompt);
    void turn.completion.catch(() => {});
    engine.closeInput();
    let ready;
    try {
      ready = await engine.ready;
    } catch (error) {
      if (error?.code === "sdk_subscription_required") throw error;
      options.validateInit?.(null);
      throw error;
    }
    options.validateInit?.(ready.init);
    const raw = await turn.completion;
    await engine.stop();
    await engine.completion;
    return raw;
  } finally {
    await engine.stop(new Error("Claude one-shot query closed.")).catch(() => {});
  }
}
