#!/usr/bin/env python3
"""Show what is left on the owner's outside-agent subscriptions: Codex, Google
(Gemini and Claude inside Antigravity) and Meta (Muse).

Codex and Google are read for free. Muse reports its usage only after a model
turn in the same process, so its check spends one minimal request; skip it
with --only. Nothing here consumes a Codex rate-limit reset credit.
"""
import argparse
import datetime
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid

SOURCES = ("codex", "google", "muse")


def when(seconds):
    return datetime.datetime.fromtimestamp(seconds).strftime("%Y-%m-%d %H:%M")


class JsonRpc:
    """Line-delimited JSON-RPC over a child's stdin and stdout."""

    def __init__(self, command, cwd):
        self.proc = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, text=True)
        self.lines = []
        threading.Thread(target=lambda: [self.lines.append(line) for line in self.proc.stdout], daemon=True).start()

    def send(self, message):
        self.proc.stdin.write(json.dumps({"jsonrpc": "2.0", **message}) + "\n")
        self.proc.stdin.flush()

    def wait(self, match, timeout):
        end = time.time() + timeout
        while time.time() < end:
            for line in list(self.lines):
                try:
                    message = json.loads(line)
                except ValueError:
                    continue
                if match(message):
                    return message
            time.sleep(0.2)
        return None

    def call(self, request_id, method, params=None, timeout=30):
        self.send({"id": request_id, "method": method, **({"params": params} if params else {})})
        reply = self.wait(lambda m: m.get("id") == request_id, timeout)
        if reply is None:
            raise RuntimeError(f"{method}: no reply in {timeout}s")
        if "error" in reply:
            raise RuntimeError(f"{method}: {reply['error']}")
        return reply.get("result") or {}

    def close(self):
        self.proc.terminate()


def codex():
    binary = shutil.which("codex")
    if not binary:
        return ["codex: the codex CLI is not in PATH"]
    rpc = JsonRpc([binary, "app-server"], tempfile.gettempdir())
    try:
        rpc.call(1, "initialize", {"clientInfo": {"name": "limits_check", "version": "1"}})
        rpc.send({"method": "initialized"})
        limits = rpc.call(2, "account/rateLimits/read")
    finally:
        rpc.close()
    block = limits.get("rateLimits") or {}
    rows = []
    for name in ("primary", "secondary"):
        window = block.get(name)
        if window:
            span = "неделя" if window.get("windowDurationMins") == 10080 else f"{window.get('windowDurationMins')} мин"
            rows.append(f"codex · {span}: израсходовано {window['usedPercent']}%, сброс {when(window['resetsAt'])}")
    credits = block.get("credits") or {}
    if credits.get("hasCredits"):
        rows.append(f"codex · кредиты: {float(credits.get('balance') or 0):.0f}")
    resets = [c for c in (limits.get("rateLimitResetCredits") or {}).get("credits", []) if c.get("status") == "available"]
    if resets:
        soonest = min(c["expiresAt"] for c in resets)
        rows.append(f"codex · бесплатных сбросов лимита: {len(resets)}, ближайший сгорает {when(soonest)}")
    return rows or ["codex: limits came back empty"]


def google():
    if not shutil.which("agy"):
        return ["google: agy (Antigravity CLI) is not in PATH"]
    done = subprocess.run(["agy", "-p", "/usage"], capture_output=True, text=True, timeout=120,
                          cwd=tempfile.gettempdir())
    rows = []
    for line in done.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 4 and parts[2].endswith("%"):
            group, span, left, reset = parts
            span = "неделя" if "Weekly" in span else "5 часов"
            stamp = datetime.datetime.fromisoformat(reset.replace("Z", "+00:00")).astimezone()
            rows.append(f"google · {group} · {span}: осталось {left}, сброс {stamp:%Y-%m-%d %H:%M}")
    return rows or [f"google: no usage lines; agy said: {(done.stdout + done.stderr).strip()[:300]}"]


def muse():
    if not shutil.which("muse"):
        return ["muse: the muse CLI is not in PATH"]
    workdir = tempfile.mkdtemp(prefix="muse-limits-")
    rpc = JsonRpc(["muse", "serve"], workdir)
    try:
        rpc.call(1, "initialize", {"clientInfo": {"name": "limits_check", "version": "1"}})
        rpc.send({"method": "initialized"})
        session = rpc.call(2, "session/start", {"commandId": str(uuid.uuid7()), "workspaceRoot": workdir,
                                               "approvalMode": "allowAll", "modelId": "muse-wonder-1.0"})
        session_id = (session.get("session") or {}).get("sessionId")
        rpc.call(3, "turn/start", {"commandId": str(uuid.uuid7()), "sessionId": session_id, "reasoningEffort": "minimal",
                                   "input": [{"type": "text", "text": "Reply with one word: ok. Call no tools."}]})
        if rpc.wait(lambda m: m.get("method") == "turn/completed", 120) is None:
            return ["muse: the probe turn did not complete in 120s"]
        usage = rpc.call(4, "usage/read").get("usage")
    finally:
        rpc.close()
    if not usage:
        return ["muse: usage/read came back empty"]
    rows = []
    for key, span in (("window", None), ("weekly", "неделя")):
        block = usage.get(key)
        if block:
            label = span or f"{block.get('windowDurationMins')} мин"
            rows.append(f"muse · {label}: израсходовано {block['usedPercent']}%, сброс {when(block['resetsAtMs'] / 1000)}")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", default=",".join(SOURCES), help="comma-separated subset of: " + ", ".join(SOURCES))
    chosen = [s.strip() for s in parser.parse_args().only.split(",") if s.strip()]
    unknown = [s for s in chosen if s not in SOURCES]
    if unknown:
        sys.exit(f"[limits] unknown source: {', '.join(unknown)}")
    checks = {"codex": codex, "google": google, "muse": muse}
    for name in chosen:
        try:
            rows = checks[name]()
        except Exception as error:  # one failed source must not hide the others
            rows = [f"{name}: check failed — {error}"]
        print("\n".join(rows), flush=True)


if __name__ == "__main__":
    main()
