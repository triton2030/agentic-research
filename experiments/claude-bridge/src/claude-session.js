import { randomUUID } from "node:crypto";
import { z } from "zod";
import { assertSdkSubscriptionEvidence, prepareClaudeRequest } from "./claude-policy.js";
import { ClaudeAskError, compactClaudeAskError, formatClaudeResult, isClaudeSessionId } from "./claude-result.js";
import { claudeRuntimeWarning, startClaudeSdkSession } from "./claude-sdk.js";

const DEFAULT_TURN_TIMEOUT_MS = 29 * 60 * 1000;
const DEFAULT_STALLED_AFTER_MS = 2 * 60 * 1000;
const DEFAULT_STEER_SETTLE_MS = 10_000;
const ACTIVE_STATES = new Set(["starting", "thinking", "tool", "subagent", "retrying", "steering", "requires_action"]);
const WAITABLE_STATES = new Set([...ACTIVE_STATES, "closing"]);
const SENDABLE_STATES = new Set(["idle", "failed", "timed_out"]);
const EVENT_LIMIT = 64;
const MESSAGE_LIMIT = 4;

const promptSchema = z.string().min(1).max(60_000);
const sessionIdSchema = z.string().uuid();

const sessionOperationFields = {
  open_fresh: {
    allowed: new Set(["op", "prompt", "profile", "effort", "cwd"]),
    required: ["prompt", "profile", "cwd"]
  },
  open_resume: {
    allowed: new Set(["op", "prompt", "cwd", "session_id"]),
    required: ["prompt", "cwd", "session_id"]
  },
  send: {
    allowed: new Set(["op", "prompt", "session_id"]),
    required: ["prompt", "session_id"]
  },
  steer: {
    allowed: new Set(["op", "prompt", "session_id"]),
    required: ["prompt", "session_id"]
  },
  stop: {
    allowed: new Set(["op", "session_id"]),
    required: ["session_id"]
  }
};

// Keep one MCP-visible object schema. The MCP SDK currently erases the
// properties of a top-level Zod discriminated union during JSON Schema export.
export const claudeSessionInputSchema = z.object({
  op: z.enum(["open_fresh", "open_resume", "send", "steer", "stop"])
    .describe("Session operation."),
  prompt: promptSchema.optional()
    .describe("Advisor task or follow-up; required except for stop."),
  profile: z.enum(["opus_advisor", "fable_advisor"]).optional()
    .describe("Fresh-session model profile."),
  effort: z.enum(["xhigh", "max"]).optional()
    .describe("Fresh-session effort; defaults to xhigh."),
  cwd: z.string().min(1).optional()
    .describe("Existing working directory for open operations."),
  session_id: sessionIdSchema.optional()
    .describe("Native Claude session UUID for every operation except open_fresh.")
}).strict().superRefine((request, context) => {
  const contract = sessionOperationFields[request.op];
  for (const field of contract.required) {
    if (request[field] === undefined) {
      context.addIssue({
        code: "custom",
        message: `${field} is required for ${request.op}.`,
        path: [field]
      });
    }
  }
  for (const field of Object.keys(request)) {
    if (!contract.allowed.has(field)) {
      context.addIssue({
        code: "custom",
        message: `${field} is not accepted for ${request.op}.`,
        path: [field]
      });
    }
  }
});

export const claudeObserveInputSchema = z.object({
  session_id: sessionIdSchema,
  detail: z.enum(["summary", "activity", "conversation", "diagnostic"]).default("summary"),
  cursor: z.number().int().nonnegative().optional(),
  wait_ms: z.number().int().min(0).max(20_000).default(0),
  limit: z.number().int().min(1).max(20).default(8),
  max_chars: z.number().int().min(200).max(12_000).default(4_000)
}).strict();

function bound(value, maxChars) {
  const text = String(value ?? "").replace(/\s+/gu, " ").trim();
  if (text.length <= maxChars) return text;
  return `${text.slice(0, Math.max(0, maxChars - 16))}...[truncated]`;
}

function invalidInput(name, parsed) {
  const issue = parsed.error.issues[0];
  const field = issue?.path?.join(".") || "request";
  return new ClaudeAskError("invalid_request", `${name} has invalid ${field}: ${issue?.message || "invalid value"}.`);
}

function visibleTerminal(terminal, diagnostic = false) {
  if (!terminal) return null;
  if (terminal.kind === "success") {
    return {
      kind: "success",
      duration_ms: terminal.duration_ms,
      ...(terminal.num_turns !== undefined ? { num_turns: terminal.num_turns } : {})
    };
  }
  const error = terminal.error;
  return {
    kind: terminal.kind,
    code: error.code,
    ...(error.resumable !== undefined ? { resumable: error.resumable } : {}),
    ...(error.duration_ms !== undefined ? { duration_ms: error.duration_ms } : {}),
    ...(diagnostic ? { message: bound(error.message, 800) } : {})
  };
}

function sleep(ms) {
  return new Promise((resolve) => {
    const timer = setTimeout(resolve, ms);
    timer.unref?.();
  });
}

function waitWithSignal(promise, signal) {
  if (!signal) return promise;
  if (signal.aborted) return Promise.reject(signal.reason || new Error("Request cancelled."));
  return new Promise((resolve, reject) => {
    const onAbort = () => reject(signal.reason || new Error("Request cancelled."));
    signal.addEventListener("abort", onAbort, { once: true });
    Promise.resolve(promise).then(
      (value) => {
        signal.removeEventListener("abort", onAbort);
        resolve(value);
      },
      (error) => {
        signal.removeEventListener("abort", onAbort);
        reject(error);
      }
    );
  });
}

function createRecord(launch, now) {
  return {
    activeTool: null,
    backgroundTasks: new Map(),
    closing: false,
    closingTarget: null,
    cursor: 0,
    cwd: launch.cwd,
    direction: "Starting Claude advisor",
    engine: null,
    events: [],
    lastActivityAt: now(),
    messages: [],
    operation: 0,
    requestedEffort: launch.sessionId ? null : launch.profile.effort,
    requestedModel: launch.sessionId ? null : launch.profile.requestedModel,
    resolvedModel: null,
    sessionId: launch.sessionId || null,
    state: "starting",
    terminal: null,
    thinkingTokens: null,
    turnDone: null,
    turnTimer: null,
    turnToken: null,
    warnings: launch.stripped.length
      ? [`environment_overrides_stripped:${launch.stripped.toSorted().join(",")}`]
      : [],
    waiters: new Set()
  };
}

/**
 * Process-local execution adapter keyed by native Claude session UUID.
 * Native transcript persistence belongs to Claude; this registry is disposable.
 */
export function createClaudeSessionAdapter(options = {}) {
  const prepare = options.prepareRequest || prepareClaudeRequest;
  const startSession = options.startSession || startClaudeSdkSession;
  const now = options.now || Date.now;
  const maxSessions = options.maxSessions ?? 4;
  const maxRetained = options.maxRetained ?? 32;
  const stalledAfterMs = options.stalledAfterMs ?? DEFAULT_STALLED_AFTER_MS;
  const turnTimeoutMs = options.turnTimeoutMs ?? DEFAULT_TURN_TIMEOUT_MS;
  const steerSettleMs = options.steerSettleMs ?? DEFAULT_STEER_SETTLE_MS;
  const closeTimeoutMs = options.closeTimeoutMs ?? 5_000;
  const records = new Map();
  const pendingOpenRecords = new Set();
  const reservedSessionIds = new Set();
  const untrackedClosing = new Set();
  let shuttingDown = false;

  function notify(record) {
    for (const resolve of record.waiters) resolve();
    record.waiters.clear();
  }

  function update(record, patch = {}, event = null) {
    Object.assign(record, patch);
    record.cursor += 1;
    record.lastActivityAt = now();
    if (event) {
      record.events.push({
        cursor: record.cursor,
        at_ms: record.lastActivityAt,
        type: event.type,
        summary: bound(event.summary, 220)
      });
      if (record.events.length > EVENT_LIMIT) record.events.splice(0, record.events.length - EVENT_LIMIT);
    }
    notify(record);
  }

  function rememberMessage(record, role, text) {
    record.messages.push({
      cursor: record.cursor + 1,
      role,
      text: bound(text, 4_000)
    });
    if (record.messages.length > MESSAGE_LIMIT) {
      record.messages.splice(0, record.messages.length - MESSAGE_LIMIT);
    }
  }

  function addWarning(record, warning) {
    const compact = bound(warning, 240);
    if (record.warnings.includes(compact)) return;
    record.warnings.push(compact);
    if (record.warnings.length > 16) record.warnings.splice(0, record.warnings.length - 16);
  }

  function taskCount(record) {
    return [...record.backgroundTasks.values()]
      .filter((task) => ["pending", "running", "paused"].includes(task.status)).length;
  }

  function observeMessage(record, message) {
    const runtimeWarning = claudeRuntimeWarning(message);
    if (runtimeWarning) addWarning(record, runtimeWarning);
    if (message.type === "system" && message.subtype === "init") {
      record.backgroundTasks.clear();
      update(record, {
        resolvedModel: message.model || record.resolvedModel,
        sessionId: message.session_id || record.sessionId,
        state: record.state === "starting" ? "thinking" : record.state,
        direction: "Claude session initialized"
      }, { type: "phase", summary: "Claude session initialized" });
      return;
    }
    if (message.type === "system" && message.subtype === "session_state_changed") {
      const state = message.state === "running"
        ? "thinking"
        : message.state === "idle"
          ? "idle"
          : "requires_action";
      update(record, {
        activeTool: state === "idle" ? null : record.activeTool,
        state,
        direction: state === "idle"
          ? "Claude is ready for a follow-up"
          : state === "requires_action"
            ? "Claude requires user or permission action"
            : "Claude is working"
      }, { type: "phase", summary: `Claude session ${message.state}` });
      return;
    }
    if (message.type === "system" && message.subtype === "status") {
      const compacting = message.status === "compacting";
      update(record, {
        state: compacting ? "thinking" : record.state,
        direction: compacting ? "Claude is compacting its native context" : record.direction
      }, compacting ? { type: "phase", summary: "Claude is compacting its native context" } : null);
      return;
    }
    if (message.type === "system" && message.subtype === "thinking_tokens") {
      update(record, {
        state: "thinking",
        thinkingTokens: Number.isFinite(message.estimated_tokens) ? message.estimated_tokens : record.thinkingTokens,
        direction: "Claude is reasoning"
      });
      return;
    }
    if (message.type === "tool_progress") {
      const isSubagent = Boolean(message.task_id || message.subagent_type);
      const changedTool = record.activeTool !== message.tool_name;
      const retry = message.subagent_retry;
      update(record, {
        activeTool: bound(message.tool_name || "tool", 100),
        state: retry ? "retrying" : isSubagent ? "subagent" : "tool",
        direction: retry
          ? `Claude subagent retry ${retry.attempt}/${retry.max_retries}`
          : isSubagent
            ? `Claude subagent is using ${bound(message.tool_name || "a tool", 80)}`
            : `Claude is using ${bound(message.tool_name || "a tool", 80)}`
      }, retry
        ? { type: "retry", summary: `Subagent retry ${retry.attempt}/${retry.max_retries}` }
        : changedTool && !message.heartbeat
          ? { type: "tool", summary: `Using ${message.tool_name || "tool"}` }
          : null);
      return;
    }
    if (message.type === "system" && message.subtype === "task_started") {
      record.backgroundTasks.set(message.task_id, { status: "running" });
      const summary = bound(message.description || `${message.subagent_type || "Claude"} subagent started`, 220);
      update(record, {
        state: "subagent",
        direction: summary
      }, { type: "subagent", summary });
      return;
    }
    if (message.type === "system" && message.subtype === "background_tasks_changed") {
      record.backgroundTasks.clear();
      for (const task of message.tasks || []) {
        record.backgroundTasks.set(task.task_id, { status: "running" });
      }
      const count = taskCount(record);
      const taskStateEnded = !count && record.state === "subagent";
      update(record, {
        state: count ? "subagent" : taskStateEnded ? "thinking" : record.state,
        direction: count
          ? `${count} Claude background task${count === 1 ? "" : "s"} running`
          : taskStateEnded
            ? "Claude is working"
            : record.direction
      }, { type: "subagent", summary: `${count} background tasks running` });
      return;
    }
    if (message.type === "system" && message.subtype === "task_progress") {
      record.backgroundTasks.set(message.task_id, { status: "running" });
      const summary = bound(message.summary || message.description || "Claude subagent is working", 220);
      update(record, {
        activeTool: message.last_tool_name ? bound(message.last_tool_name, 100) : record.activeTool,
        state: "subagent",
        direction: summary
      }, message.summary ? { type: "subagent", summary } : null);
      return;
    }
    if (message.type === "system" && message.subtype === "task_updated") {
      const previous = record.backgroundTasks.get(message.task_id) || {};
      const next = { ...previous, ...message.patch };
      if (["completed", "failed", "killed"].includes(next.status)) record.backgroundTasks.delete(message.task_id);
      else record.backgroundTasks.set(message.task_id, next);
      update(record, {
        state: taskCount(record) ? "subagent" : record.state,
        direction: taskCount(record) ? record.direction : "Claude is working"
      });
      return;
    }
    if (message.type === "system" && message.subtype === "task_notification") {
      record.backgroundTasks.delete(message.task_id);
      update(record, {
        state: taskCount(record) ? "subagent" : "thinking",
        direction: `Claude subagent ${message.status}`
      }, { type: "subagent", summary: `Subagent ${message.status}` });
      return;
    }
    if (message.type === "system" && message.subtype === "api_retry") {
      update(record, {
        state: "retrying",
        direction: `Claude API retry ${message.attempt}/${message.max_retries}`
      }, { type: "retry", summary: `API retry ${message.attempt}/${message.max_retries}` });
      return;
    }
    if (message.type === "rate_limit_event") {
      update(
        record,
        runtimeWarning ? { direction: "Claude reported a subscription limit signal" } : {},
        runtimeWarning ? { type: "limit", summary: runtimeWarning } : null
      );
      return;
    }
    if (message.type === "system" && message.subtype === "permission_denied") {
      const toolName = bound(message.tool_name || "tool", 80);
      update(record, {
        direction: `Claude tool permission denied: ${toolName}`
      }, { type: "permission", summary: `Permission denied for ${toolName}` });
      return;
    }
    if (message.type === "system" && message.subtype === "model_refusal_fallback") {
      const original = bound(message.original_model || "unknown", 80);
      const fallback = bound(message.fallback_model || "unknown", 80);
      update(record, {
        state: "retrying",
        direction: `Claude is retrying a refusal with ${fallback}`
      }, { type: "model", summary: `Model refusal fallback ${original} -> ${fallback}` });
      return;
    }
    if (message.type === "assistant") {
      if (message.error) {
        update(record, {
          state: message.error === "rate_limit" || message.error === "overloaded" ? "retrying" : "thinking",
          direction: `Claude reported ${bound(message.error, 80)}`
        }, { type: "model", summary: `Claude reported ${message.error}` });
        return;
      }
      const toolNames = (message.message?.content || [])
        .filter((block) => block?.type === "tool_use" && typeof block.name === "string")
        .map((block) => bound(block.name, 80));
      if (toolNames.length) {
        const activeTool = bound(toolNames.join(", "), 100);
        const isSubagent = message.parent_tool_use_id !== null;
        const changedTool = record.activeTool !== activeTool;
        update(record, {
          activeTool,
          state: isSubagent ? "subagent" : "tool",
          direction: isSubagent
            ? `Claude subagent is using ${activeTool}`
            : `Claude is using ${activeTool}`
        }, changedTool ? { type: "tool", summary: `Using ${activeTool}` } : null);
        return;
      }
    }
    update(record);
  }

  function baseSnapshot(record, cursor) {
    const age = Math.max(0, now() - record.lastActivityAt);
    return {
      session_id: record.sessionId,
      state: record.state,
      cursor: record.cursor,
      changed: cursor === undefined || record.cursor > cursor,
      last_activity_age_ms: age,
      direction: bound(record.direction, 240),
      active_tool: record.activeTool,
      thinking_tokens: record.thinkingTokens,
      background_tasks: taskCount(record),
      possibly_stalled: WAITABLE_STATES.has(record.state) && age >= stalledAfterMs,
      requested_model: record.requestedModel,
      requested_effort: record.requestedEffort,
      resolved_model: record.resolvedModel,
      terminal: visibleTerminal(record.terminal),
      warnings: record.warnings.slice(-8),
      events: [],
      messages: []
    };
  }

  function snapshot(record, request) {
    const packet = baseSnapshot(record, request.cursor);
    if (request.detail === "activity") {
      const eligible = request.cursor === undefined
        ? record.events
        : record.events.filter((event) => event.cursor > request.cursor);
      packet.events = eligible.slice(-request.limit);
    } else if (request.detail === "conversation") {
      const eligible = request.cursor === undefined
        ? record.messages
        : record.messages.filter((message) => message.cursor > request.cursor);
      let remaining = request.max_chars;
      const selected = [];
      const candidates = eligible.slice(-request.limit);
      for (let index = candidates.length - 1; index >= 0 && remaining > 0; index -= 1) {
        const message = candidates[index];
        const text = bound(message.text, remaining);
        remaining = Math.max(0, remaining - text.length);
        if (text) selected.push({ cursor: message.cursor, role: message.role, text });
      }
      packet.messages = selected.reverse();
    } else if (request.detail === "diagnostic") {
      packet.diagnostic = {
        engine: record.engine ? "open" : "closed",
        queue_depth: 0,
        terminal: visibleTerminal(record.terminal, true),
        retained_events: record.events.length,
        retained_messages: record.messages.length
      };
    }
    return packet;
  }

  async function waitForChange(record, cursor, waitMs, signal) {
    if (!waitMs || cursor === undefined || record.cursor > cursor || !WAITABLE_STATES.has(record.state)) return;
    let resolveWait;
    const changed = new Promise((resolve) => {
      resolveWait = resolve;
      record.waiters.add(resolve);
    });
    try {
      await waitWithSignal(Promise.race([changed, sleep(waitMs)]), signal);
    } finally {
      record.waiters.delete(resolveWait);
    }
  }

  function clearTurn(record, token) {
    if (record.turnToken !== token) return false;
    clearTimeout(record.turnTimer);
    record.turnTimer = null;
    record.turnToken = null;
    record.turnDone = null;
    return true;
  }

  async function stopEngine(record, reason, settledState = "closed") {
    const engine = record.engine;
    if (!engine) {
      record.closing = false;
      return true;
    }
    record.closing = true;
    record.closingTarget = settledState;
    record.turnToken = null;
    clearTimeout(record.turnTimer);
    record.turnTimer = null;
    record.turnDone = null;
    const finished = Promise.resolve(engine.stop(reason)).then(
      () => true,
      (error) => {
        addWarning(record, `cleanup_failed:${bound(error?.message || error, 160)}`);
        return false;
      }
    );
    const released = finished.then((clean) => {
      if (!clean || record.engine !== engine) return clean;
      record.engine = null;
      record.closing = false;
      if (record.state === "closing") {
        update(record, {
          direction: settledState === "closed"
            ? "Claude session stopped; native history remains resumable"
            : "Claude process cleanup finished",
          state: settledState
        }, { type: "phase", summary: "Claude process cleanup finished" });
      }
      return true;
    });
    const clean = await Promise.race([
      released,
      sleep(closeTimeoutMs).then(() => false)
    ]);
    if (!clean && record.engine === engine) {
      addWarning(record, "cleanup_still_pending");
      update(record, {
        direction: "Claude process cleanup is still pending",
        state: "closing"
      }, { type: "phase", summary: "Claude process cleanup is still pending" });
    }
    return clean;
  }

  function settleTurn(record, completion, launch, token) {
    const done = (async () => {
      try {
        const raw = await completion;
        if (!clearTurn(record, token)) return;
        const result = formatClaudeResult(raw, launch);
        for (const warning of result.warnings) addWarning(record, warning);
        rememberMessage(record, "assistant", result.text);
        update(record, {
          activeTool: null,
          direction: "Claude finished and is ready for a follow-up",
          resolvedModel: result.resolved_model,
          state: "idle",
          terminal: {
            duration_ms: result.duration_ms,
            kind: "success",
            num_turns: raw.result?.num_turns
          },
          thinkingTokens: null
        }, { type: "result", summary: "Claude finished the turn" });
      } catch (error) {
        if (!clearTurn(record, token)) return;
        const compact = compactClaudeAskError(error);
        const timedOut = compact.code === "timeout";
        update(record, {
          activeTool: null,
          direction: timedOut ? "Claude turn timed out; the native session can be resumed" : "Claude turn failed",
          state: timedOut ? "timed_out" : "failed",
          terminal: { error: compact, kind: timedOut ? "timeout" : "error" },
          thinkingTokens: null
        }, { type: "error", summary: `${compact.code}: ${compact.message}` });
      }
    })();
    record.turnDone = done;
    return done;
  }

  function beginTurn(record, engine, prompt, launch, priority = "now") {
    if (record.turnToken) throw new ClaudeAskError("session_busy", "Claude session already has an active turn.");
    const token = randomUUID();
    record.turnToken = token;
    rememberMessage(record, "user", prompt);
    update(record, {
      activeTool: null,
      direction: "Claude accepted the task",
      state: "thinking",
      terminal: null,
      thinkingTokens: null
    }, { type: "phase", summary: "Claude accepted a task" });
    let turn;
    try {
      turn = engine.send(prompt, { priority });
    } catch (error) {
      record.turnToken = null;
      update(record, {
        direction: "Claude process could not accept the task",
        state: "failed",
        terminal: {
          error: {
            code: "claude_sdk_error",
            message: bound(error?.message || error, 800),
            resumable: Boolean(record.sessionId),
            ...(record.sessionId ? { session_id: record.sessionId } : {})
          },
          kind: "error"
        }
      }, { type: "error", summary: "Claude process rejected the task" });
      throw error;
    }
    const timer = setTimeout(() => {
      if (record.turnToken !== token) return;
      record.turnToken = null;
      record.turnDone = null;
      record.turnTimer = null;
      record.operation += 1;
      update(record, {
        activeTool: null,
        direction: "Claude turn timed out; stopping its native process",
        state: "closing",
        terminal: {
          error: {
            code: "timeout",
            message: "Claude turn exceeded its timeout.",
            resumable: true,
            session_id: record.sessionId
          },
          kind: "timeout"
        },
        thinkingTokens: null
      }, { type: "error", summary: "Claude turn timed out" });
      void stopEngine(record, new Error("Claude session turn timed out."), "timed_out");
    }, turnTimeoutMs);
    timer.unref?.();
    record.turnTimer = timer;
    settleTurn(record, turn.completion, launch, token);
  }

  function trimRecords() {
    if (records.size <= maxRetained) return;
    const removable = [...records.values()]
      .filter((record) => !record.engine && !ACTIVE_STATES.has(record.state))
      .sort((left, right) => left.lastActivityAt - right.lastActivityAt);
    while (records.size > maxRetained && removable.length) {
      const record = removable.shift();
      records.delete(record.sessionId);
    }
  }

  function activeEngineCount() {
    const liveRecords = new Set([...pendingOpenRecords, ...untrackedClosing]);
    for (const record of records.values()) {
      if (record.engine) liveRecords.add(record);
    }
    return liveRecords.size;
  }

  async function startRecord(launch, prompt, signal, existingRecord = null) {
    if (shuttingDown) throw new ClaudeAskError("server_stopping", "Claude bridge is shutting down.");
    if (signal?.aborted) throw new ClaudeAskError("cancelled", "Claude session open was cancelled.");
    const record = existingRecord || createRecord(launch, now);
    if (activeEngineCount() >= maxSessions) {
      throw new ClaudeAskError("session_capacity", `Claude bridge already has ${maxSessions} live sessions; stop one first.`);
    }
    pendingOpenRecords.add(record);
    const controller = new AbortController();
    let engine;
    try {
      engine = startSession(launch, {
        abortController: controller,
        validateInit: assertSdkSubscriptionEvidence,
        onMessage: (message) => observeMessage(record, message),
        onTerminal: ({ error, lastRaw }) => {
          if (record.engine !== engine) return;
          record.engine = null;
          const wasClosing = record.closing;
          const closingTarget = record.closingTarget || "closed";
          record.closing = false;
          if (wasClosing) {
            update(record, {
              direction: closingTarget === "closed"
                ? "Claude session stopped; native history remains resumable"
                : "Claude process cleanup finished",
              state: closingTarget
            }, { type: "phase", summary: "Claude process cleanup finished" });
            return;
          }
          if (record.state === "closed" || record.state === "timed_out") return;
          if (error && !lastRaw?.result && !record.turnToken) {
            update(record, {
              direction: "Claude process ended; resume can reopen the native session",
              state: "failed",
              terminal: {
                error: {
                  code: "claude_sdk_error",
                  message: bound(error.message || error, 800),
                  resumable: Boolean(record.sessionId),
                  ...(record.sessionId ? { session_id: record.sessionId } : {})
                },
                kind: "error"
              }
            }, { type: "error", summary: "Claude process ended" });
          }
        }
      });
      record.engine = engine;
      // Claude Code emits native init only after the first streaming message.
      // Subscription auth was already proven in this exact sanitized process
      // environment; reservations/capacity are held before this dispatch.
      beginTurn(record, engine, prompt, launch);
      const { init } = await waitWithSignal(engine.ready, signal);
      assertSdkSubscriptionEvidence(init);
      if (!isClaudeSessionId(init.session_id)) {
        throw new ClaudeAskError("missing_session", "Claude SDK init did not include a native session UUID.");
      }
      if (launch.sessionId && init.session_id !== launch.sessionId) {
        throw new ClaudeAskError(
          "session_mismatch",
          `Claude resumed ${init.session_id}, not requested session ${launch.sessionId}.`
        );
      }
      const occupied = records.get(init.session_id);
      if (occupied && occupied !== record && occupied.engine) {
        throw new ClaudeAskError("session_already_active", "That native Claude session is already active.");
      }
      if (occupied && occupied !== record) records.delete(init.session_id);
      record.sessionId = init.session_id;
      record.resolvedModel = init.model || record.resolvedModel;
      records.set(record.sessionId, record);
      trimRecords();
      return record;
    } catch (error) {
      record.turnToken = null;
      clearTimeout(record.turnTimer);
      record.turnTimer = null;
      if (engine) {
        const cleaned = await stopEngine(record, error, "failed");
        if (!cleaned) {
          untrackedClosing.add(record);
          void Promise.resolve(engine.completion).then(
            () => untrackedClosing.delete(record),
            () => untrackedClosing.delete(record)
          );
        }
      }
      if (record.sessionId && records.get(record.sessionId) === record && !existingRecord) {
        records.delete(record.sessionId);
      }
      if (signal?.aborted) throw new ClaudeAskError("cancelled", "Claude session open was cancelled.");
      if (error instanceof ClaudeAskError) throw error;
      throw new ClaudeAskError("claude_sdk_error", bound(error?.message || error, 1_000));
    } finally {
      pendingOpenRecords.delete(record);
    }
  }

  async function prepareAndStart(request, signal, existingRecord = null) {
    const launch = await prepare({
      cwd: request.cwd,
      prompt: request.prompt,
      ...(request.profile ? { profile: request.profile } : {}),
      ...(request.effort ? { effort: request.effort } : {}),
      ...(request.session_id ? { session_id: request.session_id } : {})
    }, { signal });
    if (signal?.aborted) throw new ClaudeAskError("cancelled", "Claude session open was cancelled.");
    return startRecord(launch, request.prompt, signal, existingRecord);
  }

  async function ensureEngine(record, prompt, signal, operation) {
    if (signal?.aborted) throw new ClaudeAskError("cancelled", "Claude session command was cancelled.");
    if (record.closing) throw new ClaudeAskError("session_closing", "Claude session process cleanup is still pending.");
    if (record.engine) {
      const launch = {
        cwd: record.cwd,
        env: {},
        executable: null,
        profile: null,
        prompt,
        sessionId: record.sessionId,
        stripped: []
      };
      beginTurn(record, record.engine, prompt, launch);
      return;
    }
    if (reservedSessionIds.has(record.sessionId)) {
      throw new ClaudeAskError("session_already_active", "That native Claude session is already opening.");
    }
    update(record, {
      direction: "Reopening the native Claude session",
      state: "starting"
    }, { type: "phase", summary: "Reopening native session" });
    reservedSessionIds.add(record.sessionId);
    try {
      const launchRequest = { cwd: record.cwd, prompt, session_id: record.sessionId };
      const launch = await prepare(launchRequest, { signal });
      if (record.operation !== operation || record.state === "closed") {
        throw new ClaudeAskError("cancelled", "Claude session operation was superseded.");
      }
      await startRecord(launch, prompt, signal, record);
      if (record.operation !== operation || record.state === "closed") {
        await stopEngine(record, new Error("Claude session operation was superseded."));
        throw new ClaudeAskError("cancelled", "Claude session operation was superseded.");
      }
    } catch (error) {
      if (record.operation === operation && record.state !== "closed") {
        const compact = compactClaudeAskError(error);
        update(record, {
          direction: "Claude native session could not be reopened",
          state: "failed",
          terminal: { error: compact, kind: "error" }
        }, { type: "error", summary: `${compact.code}: ${compact.message}` });
      }
      throw error;
    } finally {
      reservedSessionIds.delete(record.sessionId);
    }
  }

  async function command(input, signal) {
    const parsed = claudeSessionInputSchema.safeParse(input);
    if (!parsed.success) throw invalidInput("claude_session", parsed);
    const request = parsed.data;
    if (signal?.aborted) throw new ClaudeAskError("cancelled", "Claude session command was cancelled.");

    if (request.op === "open_fresh") {
      const record = await prepareAndStart(request, signal);
      return { accepted_op: request.op, ...baseSnapshot(record) };
    }
    if (request.op === "open_resume") {
      const active = records.get(request.session_id);
      if (active?.engine || ACTIVE_STATES.has(active?.state) || reservedSessionIds.has(request.session_id)) {
        throw new ClaudeAskError("session_already_active", "That native Claude session is already active or opening.");
      }
      reservedSessionIds.add(request.session_id);
      try {
        const record = await prepareAndStart(request, signal);
        return { accepted_op: request.op, ...baseSnapshot(record) };
      } finally {
        reservedSessionIds.delete(request.session_id);
      }
    }

    const record = records.get(request.session_id);
    if (!record) {
      throw new ClaudeAskError(
        "session_not_active",
        "No process-local lease exists for that session_id; use open_resume with cwd and a prompt."
      );
    }
    if (request.op === "stop") {
      record.operation += 1;
      record.turnToken = null;
      const cleaned = await stopEngine(record, new Error("Claude session stopped by caller."), "closed");
      if (cleaned) {
        update(record, {
          activeTool: null,
          direction: "Claude session stopped; native history remains resumable",
          state: "closed",
          terminal: null,
          thinkingTokens: null
        }, { type: "phase", summary: "Claude session stopped" });
      }
      trimRecords();
      return { accepted_op: request.op, ...baseSnapshot(record) };
    }
    if (request.op === "send") {
      if (!SENDABLE_STATES.has(record.state)) {
        throw new ClaudeAskError("session_busy", "Use steer for an active Claude turn, or wait until it becomes idle.");
      }
      const operation = ++record.operation;
      await ensureEngine(record, request.prompt, signal, operation);
      return { accepted_op: request.op, ...baseSnapshot(record) };
    }

    if (!ACTIVE_STATES.has(record.state) || !record.engine || !record.turnDone) {
      throw new ClaudeAskError("session_not_running", "Claude steer requires an active turn.");
    }
    const previousTurn = record.turnDone;
    const previousEngine = record.engine;
    const operation = ++record.operation;
    update(record, {
      direction: "Interrupting Claude before applying correction",
      state: "steering"
    }, { type: "steer", summary: "Interrupting current turn" });
    let receipt;
    try {
      receipt = await waitWithSignal(previousEngine.interrupt(), signal);
    } catch (error) {
      if (signal?.aborted) throw new ClaudeAskError("cancelled", "Claude steer was cancelled after interrupt.");
      addWarning(record, `interrupt_failed:${bound(error?.message || error, 160)}`);
    }
    const settled = await waitWithSignal(Promise.race([
      previousTurn.then(() => true),
      sleep(steerSettleMs).then(() => false)
    ]), signal).catch((error) => {
      if (signal?.aborted) throw new ClaudeAskError("cancelled", "Claude steer was cancelled after interrupt.");
      throw error;
    });
    const stillQueued = receipt?.still_queued || [];
    if (!settled || stillQueued.length || record.engine !== previousEngine) {
      addWarning(
        record,
        !settled ? "steer_forced_native_resume" : stillQueued.length ? `interrupt_queue_survived:${stillQueued.length}` : "process_ended_during_steer"
      );
      record.turnToken = null;
      const cleaned = await stopEngine(record, new Error("Claude steer reopened the native session."), "failed");
      if (!cleaned) {
        throw new ClaudeAskError("session_closing", "Claude interrupt did not settle; process cleanup is still pending.");
      }
    }
    if (record.operation !== operation || record.state === "closed") {
      throw new ClaudeAskError("cancelled", "Claude steer was superseded.");
    }
    await ensureEngine(record, request.prompt, signal, operation);
    return { accepted_op: request.op, ...baseSnapshot(record) };
  }

  async function observe(input, signal) {
    const parsed = claudeObserveInputSchema.safeParse(input);
    if (!parsed.success) throw invalidInput("claude_observe", parsed);
    const request = parsed.data;
    const record = records.get(request.session_id);
    if (!record) {
      throw new ClaudeAskError(
        "session_not_active",
        "No process-local lease exists for that session_id; use open_resume to continue native history."
      );
    }
    try {
      await waitForChange(record, request.cursor, request.wait_ms, signal);
    } catch (error) {
      if (signal?.aborted) throw new ClaudeAskError("cancelled", "Claude observation wait was cancelled.");
      throw error;
    }
    return snapshot(record, request);
  }

  return {
    command,
    observe,
    async shutdown() {
      shuttingDown = true;
      await Promise.allSettled([...records.values()].map(async (record) => {
        record.operation += 1;
        record.turnToken = null;
        const cleaned = await stopEngine(record, new Error("Claude bridge server stopped."), "closed");
        if (cleaned) {
          update(record, {
            activeTool: null,
            direction: "Claude bridge server stopped",
            state: "closed",
            thinkingTokens: null
          });
        }
      }));
      await Promise.allSettled([...untrackedClosing].map((record) => (
        Promise.race([record.engine?.completion || Promise.resolve(), sleep(closeTimeoutMs)])
      )));
    },
    /** @internal Deterministic acceptance seam. */
    inspect(sessionId) {
      return records.get(sessionId);
    }
  };
}
