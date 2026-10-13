import json, subprocess, threading, time, uuid
T0 = time.time()
p = subprocess.Popen(["muse", "serve", "--model", "muse-wonder-1.0"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd="/tmp/muse-steer")
out = []
def reader():
    for line in p.stdout:
        out.append((time.time() - T0, line.rstrip("\n")))
threading.Thread(target=reader, daemon=True).start()
def send(obj):
    p.stdin.write(json.dumps(obj) + "\n"); p.stdin.flush()
def wait_id(i, t=20):
    end = time.time() + t
    while time.time() < end:
        for _, line in list(out):
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("id") == i: return m
        time.sleep(0.1)
    return {}
def wait_method(name, t):
    end = time.time() + t
    while time.time() < end:
        for _, line in list(out):
            if f'"method":"{name}"' in line.replace(" ", ""): return json.loads(line)
        time.sleep(0.3)
send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"clientInfo": {"name": "steer_probe", "version": "0.1"}}}); wait_id(1)
send({"jsonrpc": "2.0", "method": "initialized"}); time.sleep(0.5)
send({"jsonrpc": "2.0", "id": 2, "method": "session/start", "params": {"commandId": str(uuid.uuid7()), "workspaceRoot": "/tmp/muse-steer", "approvalMode": "allowAll"}})
r = wait_id(2); sid = ((r.get("result") or {}).get("session") or {}).get("sessionId"); print("session:", sid, "| err:", json.dumps(r.get("error"))[:300] if r.get("error") else "")
brief = "Выполни командой оболочки: sleep 25. После неё ответь ровно одним словом: АЛЬФА."
send({"jsonrpc": "2.0", "id": 3, "method": "turn/start", "params": {"commandId": str(uuid.uuid7()), "sessionId": sid, "reasoningEffort": "high", "input": [{"type": "text", "text": brief}]}})
r = wait_id(3); tid = (r.get("result") or {}).get("turnId"); print(f"[{time.time()-T0:5.1f}s] turn/start:", json.dumps(r.get("result") or r.get("error"))[:300])
time.sleep(9)
send({"jsonrpc": "2.0", "id": 4, "method": "turn/steer", "params": {"commandId": str(uuid.uuid7()), "sessionId": sid, "expectedTurnId": tid, "input": [{"type": "text", "text": "Поправка от вызывающего агента: в ответе вместо слова АЛЬФА напиши слово БЕТА."}]}})
r = wait_id(4); print(f"[{time.time()-T0:5.1f}s] turn/steer:", json.dumps(r.get("result") or r.get("error"))[:300])
done = wait_method("turn/completed", 150); print(f"[{time.time()-T0:5.1f}s] turn/completed:", json.dumps((done or {}).get("params"))[:500])
send({"jsonrpc": "2.0", "id": 5, "method": "usage/read"}); print("usage/read:", json.dumps(wait_id(5).get("result"))[:500])
texts = []
for ts, line in out:
    try: m = json.loads(line)
    except ValueError: continue
    if m.get("method") in ("item/completed",):
        item = (m.get("params") or {}).get("item") or {}
        texts.append((round(ts, 1), item.get("type") or item.get("kind"), json.dumps(item, ensure_ascii=False)[:260]))
for t in texts[-8:]: print(t)
print("methods seen:", sorted({json.loads(l).get("method") for _, l in out if '"method"' in l and json.loads(l).get("method")}))
p.stdin.close(); time.sleep(0.5); p.terminate()
print("STDERR:", p.stderr.read()[-400:])
