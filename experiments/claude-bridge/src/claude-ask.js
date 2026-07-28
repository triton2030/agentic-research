import { AsyncLocalStorage } from "node:async_hooks";
import { assertSdkSubscriptionEvidence, prepareClaudeRequest } from "./claude-policy.js";
import { formatClaudeResult, ClaudeAskError, compactTail } from "./claude-result.js";
import { runClaudeSdk } from "./claude-sdk.js";

// Finish with a typed bridge timeout before Codex's 30-minute MCP envelope wins.
const DEFAULT_TIMEOUT_MS = 29 * 60 * 1000;
const testDependencies = new AsyncLocalStorage();

function requestLifetime(signal, timeoutMs) {
  const controller = new AbortController();
  let stoppedBy = null;
  const cancel = () => {
    stoppedBy ||= "cancelled";
    controller.abort(signal?.reason);
  };
  if (signal?.aborted) cancel();
  else signal?.addEventListener("abort", cancel, { once: true });
  const timer = setTimeout(() => {
    stoppedBy ||= "timeout";
    controller.abort(new Error("Claude request timed out."));
  }, timeoutMs);
  timer.unref?.();
  return {
    controller,
    stoppedBy: () => stoppedBy,
    close() {
      clearTimeout(timer);
      signal?.removeEventListener("abort", cancel);
    }
  };
}

/** Run one bounded Claude advisor turn through the exact Agent SDK implementation. */
export async function askClaude(request, signal) {
  const dependencies = testDependencies.getStore() || {};
  const lifetime = requestLifetime(signal, dependencies.timeoutMs ?? DEFAULT_TIMEOUT_MS);
  try {
    if (lifetime.stoppedBy()) throw new Error("Claude request stopped before launch.");
    const launch = await prepareClaudeRequest(request, {
      authTimeoutMs: dependencies.authTimeoutMs,
      env: dependencies.env,
      executable: dependencies.executable,
      signal: lifetime.controller.signal
    });
    const raw = await runClaudeSdk(launch, {
      abortController: lifetime.controller,
      queryFactory: dependencies.queryFactory,
      spawnClaudeCodeProcess: dependencies.spawnClaudeCodeProcess,
      validateInit: assertSdkSubscriptionEvidence
    });
    assertSdkSubscriptionEvidence(raw.init);
    return formatClaudeResult(raw, launch);
  } catch (error) {
    const stoppedBy = lifetime.stoppedBy();
    if (stoppedBy === "timeout") throw new ClaudeAskError("timeout", "Claude request exceeded its timeout.");
    if (stoppedBy === "cancelled") throw new ClaudeAskError("cancelled", "Claude request was cancelled.");
    if (error instanceof ClaudeAskError) throw error;
    throw new ClaudeAskError("claude_sdk_error", compactTail(error?.message || error));
  } finally {
    lifetime.close();
  }
}

/** @internal Scope exact external-effect substitutes to one concurrent test call tree. */
export function withClaudeAskTestDependencies(dependencies, callback) {
  if (process.env.NODE_ENV !== "test") throw new Error("Claude test dependencies require NODE_ENV=test.");
  return testDependencies.run(Object.freeze({ ...dependencies }), callback);
}

export { ClaudeAskError, compactClaudeAskError } from "./claude-result.js";
