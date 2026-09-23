import json, os, re, glob, time, sys, collections, random
code_file = re.compile(r"\.(py|js|mjs|cjs|ts|tsx|sh|rb|go|rs|java|kt|swift|php|pl|lua)$")
bash_re = re.compile(r"\b(python3?|node|ruby|perl)\s+(-\s*<<|-[ce]\s)|cat\s*>+\s*\S+\.(py|js|mjs|ts|sh|rb)\b")
# narrowed detector (candidate): interpreter heredoc/script >= 6 lines, or script file written via heredoc/tee, not a stdin pipe formatter
code_file2 = re.compile(r"\.(py|js|jsx|mjs|cjs|ts|tsx|sh|bash|zsh|rb|go|rs|java|kt|swift|php|pl|lua)$")
heredoc_interp = re.compile(r"\b(python3?|node|ruby|perl)\s+(-\s*)?<<-?\s*['\"]?(\w+)")
file_heredoc = re.compile(r"(cat|tee)\b[^\n|;&]*\S+\.(py|js|jsx|mjs|ts|tsx|sh|bash|rb)\b[^\n]*<<|(cat|tee)\b[^\n]*<<[^\n]*>\s*\S+\.(py|js|jsx|mjs|ts|tsx|sh|bash|rb)\b")
inline_c = re.compile(r"(?<!\|\s)(?<!\|)\b(python3?|node)\s+-[ce]\s+(['\"])(.*?)\2", re.S)
def narrow(cmd):
    m = heredoc_interp.search(cmd)
    if m:
        body = cmd[m.end():].split("\n" + m.group(3), 1)[0]
        if body.count("\n") >= 6: return True
    if file_heredoc.search(cmd): return True
    for m in inline_c.finditer(cmd):
        pre = cmd[:m.start()].rstrip()
        if pre.endswith("|"): continue
        if m.group(3).count("\n") >= 6: return True
    return False
cut = time.time() - 21 * 86400
def is_prompt(d):
    if d.get("type") != "user" or d.get("isMeta"): return False
    c = (d.get("message") or {}).get("content")
    txt = c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict) and x.get("type") == "text")
    if not txt or any(isinstance(x, dict) and x.get("type") == "tool_result" for x in (c if isinstance(c, list) else [])): return False
    t = txt.lstrip()
    return not (t.startswith("Base directory for this skill") or t.startswith("<system-reminder>") or t.startswith("Caveat:") or t.startswith("<command-") or t.startswith("<local-command") or t.startswith("<task-notification") or t.startswith("[Request interrupted"))
def load(path, src):
    out = []
    for line in open(path, errors="replace"):
        try: d = json.loads(line)
        except Exception: continue
        ts = d.get("timestamp", "")
        if src == "main" and is_prompt(d): out.append((ts, src, "PROMPT", {}))
        if d.get("type") == "assistant":
            for c in (d.get("message") or {}).get("content", []) or []:
                if isinstance(c, dict) and c.get("type") == "tool_use": out.append((ts, src, c.get("name"), c.get("input") or {}))
    return out
res = collections.Counter(); samples = []
for proj in sys.argv[1:]:
    B = os.path.expanduser("~/.claude/projects/" + proj)
    for main in glob.glob(B + "/*.jsonl"):
        if os.path.getmtime(main) < cut: continue
        sid = os.path.basename(main)[:-6]
        ev = load(main, "main")
        for sub in glob.glob(f"{B}/{sid}/subagents/*.jsonl"): ev += load(sub, "sub")
        ev.sort(key=lambda e: e[0])
        res["sessions"] += 1
        touched = set(); armed_v0 = True; armed_v1 = True; armed_v2 = True; prompts = 0
        for ts, src, name, inp in ev:
            if name == "PROMPT":
                prompts += 1; armed_v1 = True; armed_v2 = True; continue
            fp = inp.get("file_path", "") if isinstance(inp, dict) else ""
            cmd = str(inp.get("command", "")) if isinstance(inp, dict) else ""
            chk = (name == "Skill" and "firecrawl-developer-index" in str(inp.get("skill", ""))) or (name == "Bash" and "firecrawl developer" in cmd)
            new_file = name == "Write" and fp and fp not in touched
            c0 = (new_file and code_file.search(fp)) or (name == "Bash" and bash_re.search(cmd))
            c2 = (new_file and code_file2.search(fp)) or (name == "Bash" and narrow(cmd))
            if name in ("Read", "Write", "Edit", "MultiEdit") and fp: touched.add(fp)
            if src == "sub": c2 = False  # candidate: main thread only
            if armed_v0 and (chk or c0):
                armed_v0 = False
                if c0 and not chk: res["v0_denies"] += 1
            if armed_v1 and (chk or c0):
                armed_v1 = False
                if c0 and not chk: res["v1_denies"] += 1
            if armed_v2 and (chk or c2):
                armed_v2 = False
                if c2 and not chk:
                    res["v2_denies"] += 1; samples.append((sid[:8], (cmd or fp)[:260].replace("\n", "⏎")))
        res["prompts"] += prompts
print(dict(res))
random.seed(3)
for s in random.sample(samples, min(15, len(samples))): print(s[0], "|", s[1]); print()
