import { spawn } from "node:child_process";

// Hard caps prevent runaway subprocess output from exhausting MCP server memory
// or model context. 5 MB is enough for the largest known tool outputs
// (md_audit ≈ 100 KB, md_orient ≈ 50 KB, md_refactor_candidates ≈ 30 KB) with
// ~50x safety margin. Past this we truncate with an envelope so the consumer
// sees what happened instead of a silent cut.
const DEFAULT_MAX_STDOUT_BYTES = 5 * 1024 * 1024;
const DEFAULT_MAX_STDERR_BYTES = 1 * 1024 * 1024;

export class SpawnError extends Error {
  constructor(message, { code, stderr, stdout, kind } = {}) {
    super(message);
    this.name = "SpawnError";
    this.code = code;
    this.stderr = stderr;
    this.stdout = stdout;
    this.kind = kind;
  }
}

function appendWithCap(chunks, currentBytes, chunk, maxBytes) {
  // Streaming append that stops accumulating after maxBytes. Caller still
  // sees the first portion plus an explicit truncation marker via assemble().
  if (currentBytes >= maxBytes) {
    return { currentBytes, dropped: chunks.dropped + chunk.length };
  }
  const remaining = maxBytes - currentBytes;
  if (chunk.length <= remaining) {
    chunks.head.push(chunk);
    return { currentBytes: currentBytes + chunk.length, dropped: chunks.dropped };
  }
  chunks.head.push(chunk.subarray(0, remaining));
  chunks.dropped += chunk.length - remaining;
  return { currentBytes: maxBytes, dropped: chunks.dropped };
}

function makeCappedSink(maxBytes) {
  const state = { head: [], dropped: 0 };
  let currentBytes = 0;
  return {
    feed(chunk) {
      const out = appendWithCap(state, currentBytes, chunk, maxBytes);
      currentBytes = out.currentBytes;
      state.dropped = out.dropped;
    },
    assemble() {
      const text = Buffer.concat(state.head).toString("utf8");
      if (state.dropped === 0) return text;
      const marker = `\n\n[TRUNCATED: ${state.dropped} more bytes elided — output exceeded ${maxBytes} byte cap]`;
      return text + marker;
    },
    droppedBytes() { return state.dropped; }
  };
}

function killSubprocessGroup(child, signal = "SIGKILL") {
  if (process.platform !== "win32" && child.pid) {
    try {
      process.kill(-child.pid, signal);
      return;
    } catch {
      // Fall back to the direct child below when process-group kill is not
      // available or the child exited between timeout and signal delivery.
    }
  }
  try {
    child.kill(signal);
  } catch {
    // The close/error handlers below still settle the promise.
  }
}

export function spawnPython(scriptPath, args, {
  timeoutMs = 60_000,
  env,
  cwd,
  maxStdoutBytes = DEFAULT_MAX_STDOUT_BYTES,
  maxStderrBytes = DEFAULT_MAX_STDERR_BYTES
} = {}) {
  return new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(scriptPath, args, {
      env: { ...process.env, ...(env || {}) },
      cwd,
      detached: process.platform !== "win32",
      stdio: ["ignore", "pipe", "pipe"]
    });

    const stdoutSink = makeCappedSink(maxStdoutBytes);
    const stderrSink = makeCappedSink(maxStderrBytes);
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      killSubprocessGroup(child);
    }, timeoutMs);

    child.stdout.on("data", (chunk) => stdoutSink.feed(chunk));
    child.stderr.on("data", (chunk) => stderrSink.feed(chunk));

    child.on("error", (error) => {
      clearTimeout(timer);
      rejectPromise(new SpawnError(`spawn failed: ${error.message}`, { kind: "spawn_error" }));
    });

    child.on("close", (code) => {
      clearTimeout(timer);
      const stdout = stdoutSink.assemble();
      const stderr = stderrSink.assemble();
      if (timedOut) {
        rejectPromise(
          new SpawnError(`timeout after ${timeoutMs}ms`, { code, stdout, stderr, kind: "timeout" })
        );
        return;
      }
      resolvePromise({
        code: code ?? -1,
        stdout,
        stderr,
        truncated: stdoutSink.droppedBytes() > 0 || stderrSink.droppedBytes() > 0,
        stdout_dropped_bytes: stdoutSink.droppedBytes(),
        stderr_dropped_bytes: stderrSink.droppedBytes()
      });
    });
  });
}

export function tryParseJson(text) {
  if (!text || !text.trim()) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}
