import json, subprocess, threading, time, uuid
p = subprocess.Popen(["muse", "serve", "--provider", "echo"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd="/tmp/muse-steer")
out = []
def reader():
    for line in p.stdout:
        out.append(line.rstrip("\n"))
threading.Thread(target=reader, daemon=True).start()
def send(obj):
    p.stdin.write(json.dumps(obj) + "\n"); p.stdin.flush()
def wait_id(i, t=8):
    end = time.time() + t
    while time.time() < end:
        for line in out:
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("id") == i: return m
        time.sleep(0.1)
send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"clientInfo": {"name": "steer_probe", "version": "0.1"}}})
print("init:", json.dumps(wait_id(1))[:120]); send({"jsonrpc": "2.0", "method": "initialized"}); time.sleep(0.5)
send({"jsonrpc": "2.0", "id": 2, "method": "session/start", "params": {"commandId": str(uuid.uuid7()), "workspaceRoot": "/tmp/muse-steer"}})
r = wait_id(2); print("session/start:", json.dumps(r)[:600])
sid = (r.get("result") or {}).get("sessionId")
send({"jsonrpc": "2.0", "id": 3, "method": "turn/start", "params": {"commandId": str(uuid.uuid7()), "sessionId": sid, "input": [{"type": "text", "text": "hello"}]}})
r = wait_id(3); print("turn/start:", json.dumps(r)[:500])
tid = (r.get("result") or {}).get("turnId")
send({"jsonrpc": "2.0", "id": 4, "method": "turn/steer", "params": {"commandId": str(uuid.uuid7()), "sessionId": sid, "expectedTurnId": tid, "input": [{"type": "text", "text": "steer text"}]}})
print("turn/steer:", json.dumps(wait_id(4))[:500])
send({"jsonrpc": "2.0", "id": 5, "method": "usage/read"})
print("usage/read:", json.dumps(wait_id(5))[:500])
time.sleep(1.5)
print("--- notifications:", [json.loads(l).get("method") for l in out if '"method"' in l][:30])
p.stdin.close(); time.sleep(0.3); p.terminate()
