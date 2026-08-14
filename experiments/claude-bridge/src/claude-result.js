const MAX_RESULT_CHARS = 12000;
const MAX_ERROR_CHARS = 2000;
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu;

export class ClaudeAskError extends Error {
  constructor(code, message, details = {}) {
    super(boundText(message, MAX_ERROR_CHARS).text);
    this.name = "ClaudeAskError";
    this.code = code;
    this.details = details;
  }
}

function boundText(value, maxChars) {
  const text = String(value ?? "");
  if (text.length <= maxChars) return { text, truncated: false };
  const marker = `\n...[${text.length - maxChars} chars omitted]...\n`;
  const available = Math.max(0, maxChars - marker.length);
  const head = Math.ceil(available / 2);
  const tail = Math.floor(available / 2);
  return { text: `${text.slice(0, head)}${marker}${tail ? text.slice(-tail) : ""}`, truncated: true };
}

export function compactTail(value, maxChars = MAX_ERROR_CHARS) {
  const text = String(value ?? "").replace(/\s+/gu, " ").trim();
  return text.length <= maxChars ? text : `...${text.slice(-(maxChars - 3))}`;
}

export function isClaudeSessionId(value) {
  return UUID_PATTERN.test(String(value || ""));
}

/** Validate SDK evidence and create the only public success packet. */
export function formatClaudeResult(raw, launch) {
  if (!raw.result || raw.result.subtype !== "success" || raw.result.is_error) {
    const result = raw.result;
    const errors = Array.isArray(result?.errors) ? result.errors.join(" ") : "SDK query ended without success.";
    const sessionId = isClaudeSessionId(result?.session_id) ? result.session_id : undefined;
    const details = {
      ...(sessionId ? { session_id: sessionId, resumable: true } : {}),
      ...(Number.isFinite(result?.duration_ms) ? { duration_ms: result.duration_ms } : {}),
      ...(Number.isInteger(result?.num_turns) ? { num_turns: result.num_turns } : {}),
      ...(typeof result?.terminal_reason === "string" ? { terminal_reason: result.terminal_reason } : {}),
      ...(typeof result?.subtype === "string" ? { subtype: result.subtype } : {})
    };
    if (result?.subtype === "error_max_turns") {
      throw new ClaudeAskError("max_turns", compactTail(errors || "Claude reached its turn limit."), details);
    }
    throw new ClaudeAskError("claude_sdk_result", compactTail(errors), details);
  }
  if (
    typeof raw.result.terminal_reason === "string" &&
    raw.result.terminal_reason !== "completed"
  ) {
    const sessionId = isClaudeSessionId(raw.result.session_id) ? raw.result.session_id : undefined;
    throw new ClaudeAskError(
      "incomplete_result",
      `Claude returned success before the requested work completed: ${raw.result.terminal_reason}.`,
      {
        ...(sessionId ? { session_id: sessionId, resumable: true } : {}),
        ...(Number.isFinite(raw.result.duration_ms) ? { duration_ms: raw.result.duration_ms } : {}),
        terminal_reason: raw.result.terminal_reason,
        subtype: raw.result.subtype
      }
    );
  }
  if (!isClaudeSessionId(raw.result.session_id)) {
    throw new ClaudeAskError("missing_session", "Claude SDK result did not include a native session UUID.");
  }

  const resolvedModel = raw.primaryModels.at(-1) || raw.init?.model;
  if (!resolvedModel) throw new ClaudeAskError("missing_model", "Claude SDK did not identify the session model.");

  const bounded = boundText(raw.result.result, MAX_RESULT_CHARS);
  const requestedModel = launch.sessionId ? null : launch.profile.requestedModel;
  const requestedEffort = launch.sessionId ? null : launch.profile.effort;
  const warnings = [];
  if (launch.stripped.length) warnings.push(`environment_overrides_stripped:${launch.stripped.toSorted().join(",")}`);
  if (raw.primaryModels.length > 1) warnings.push(`model_history:${raw.primaryModels.join("->")}`);
  if (!launch.sessionId && !resolvedModel.toLowerCase().includes(launch.profile.model)) {
    warnings.push(`model_resolution_mismatch:requested=${launch.profile.model},resolved=${resolvedModel}`);
  }
  if (launch.sessionId) warnings.push("resume_session_owns_model");
  for (const warning of raw.runtimeWarnings || []) {
    const compact = boundText(warning, 240).text;
    if (compact && !warnings.includes(compact)) warnings.push(compact);
  }
  const deniedTools = [...new Set(
    (raw.result.permission_denials || [])
      .map((denial) => boundText(denial?.tool_name, 80).text)
      .filter(Boolean)
  )];
  if (deniedTools.length) {
    const warning = `permission_denied:${deniedTools.join(",")}`;
    if (!warnings.includes(warning)) warnings.push(warning);
  }
  if (bounded.truncated) warnings.push(`result_truncated_at:${MAX_RESULT_CHARS}`);

  return {
    text: bounded.text,
    session_id: raw.result.session_id,
    requested_model: requestedModel,
    requested_effort: requestedEffort,
    resolved_model: resolvedModel,
    duration_ms: raw.result.duration_ms,
    warnings: warnings.slice(0, 8)
  };
}

export function compactClaudeAskError(error) {
  const known = error instanceof ClaudeAskError;
  const details = known ? error.details : {};
  return {
    code: known ? error.code : "internal_error",
    message: compactTail(error?.message || "Claude request failed."),
    ...(details.session_id ? { session_id: details.session_id } : {}),
    ...(details.duration_ms !== undefined ? { duration_ms: details.duration_ms } : {}),
    ...(details.num_turns !== undefined ? { num_turns: details.num_turns } : {}),
    ...(details.terminal_reason ? { terminal_reason: compactTail(details.terminal_reason, 200) } : {}),
    ...(details.subtype ? { subtype: compactTail(details.subtype, 100) } : {}),
    ...(details.resumable !== undefined ? { resumable: Boolean(details.resumable) } : {})
  };
}
