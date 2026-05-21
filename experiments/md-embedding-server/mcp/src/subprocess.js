import { spawn } from "node:child_process";

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

export function spawnPython(scriptPath, args, { timeoutMs = 60_000, env, cwd } = {}) {
  return new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(scriptPath, args, {
      env: { ...process.env, ...(env || {}) },
      cwd,
      stdio: ["ignore", "pipe", "pipe"]
    });

    let stdout = "";
    let stderr = "";
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGKILL");
    }, timeoutMs);

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString("utf8");
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString("utf8");
    });

    child.on("error", (error) => {
      clearTimeout(timer);
      rejectPromise(new SpawnError(`spawn failed: ${error.message}`, { kind: "spawn_error" }));
    });

    child.on("close", (code) => {
      clearTimeout(timer);
      if (timedOut) {
        rejectPromise(
          new SpawnError(`timeout after ${timeoutMs}ms`, { code, stdout, stderr, kind: "timeout" })
        );
        return;
      }
      resolvePromise({ code: code ?? -1, stdout, stderr });
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
