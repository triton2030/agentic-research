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
    const errors = Array.isArray(raw.result?.errors) ? raw.result.errors.join(" ") : "SDK query ended without success.";
    throw new ClaudeAskError("claude_sdk_result", compactTail(errors));
  }
  if (!isClaudeSessionId(raw.result.session_id)) {
    throw new ClaudeAskError("missing_session", "Claude SDK result did not include a native session UUID.");
  }

  const resolvedModel = raw.primaryModels.at(-1) || raw.init.model;
  if (!resolvedModel) throw new ClaudeAskError("missing_model", "Claude SDK did not identify the session model.");

  const bounded = boundText(raw.result.result, MAX_RESULT_CHARS);
  const requestedModel = launch.sessionId ? null : launch.profile.model;
  const warnings = [];
  if (launch.stripped.length) warnings.push(`environment_overrides_stripped:${launch.stripped.toSorted().join(",")}`);
  if (raw.primaryModels.length > 1) warnings.push(`model_history:${raw.primaryModels.join("->")}`);
  if (requestedModel && !resolvedModel.toLowerCase().includes(requestedModel)) {
    warnings.push(`model_resolution_mismatch:requested=${requestedModel},resolved=${resolvedModel}`);
  }
  if (launch.sessionId) warnings.push("resume_session_owns_model");
  if (bounded.truncated) warnings.push(`result_truncated_at:${MAX_RESULT_CHARS}`);

  return {
    text: bounded.text,
    session_id: raw.result.session_id,
    requested_model: requestedModel,
    resolved_model: resolvedModel,
    duration_ms: raw.result.duration_ms,
    warnings: warnings.slice(0, 8)
  };
}

export function compactClaudeAskError(error) {
  const known = error instanceof ClaudeAskError;
  return {
    code: known ? error.code : "internal_error",
    message: compactTail(error?.message || "Claude request failed."),
    ...(known && error.details.duration_ms !== undefined ? { duration_ms: error.details.duration_ms } : {})
  };
}
