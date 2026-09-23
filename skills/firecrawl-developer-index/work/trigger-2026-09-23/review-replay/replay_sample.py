import json, os, re, glob, time, random, collections
BASE = os.path.expanduser("~/.claude/projects/-Users-triton-Documents-GitHub-agentic-research")
code_file = re.compile(r"\.(py|js|mjs|cjs|ts|tsx|sh|rb|go|rs|java|kt|swift|php|pl|lua)$")
bash_re = re.compile(r"\b(python3?|node|ruby|perl)\s+(-\s*<<|-[ce]\s)|cat\s*>+\s*\S+\.(py|js|mjs|ts|sh|rb)\b")
cut = time.time() - 21 * 86400
def events(path, src):
    out = []
    for line in open(path, errors="replace"):
        try: d = json.loads(line)
        except Exception: continue
        if d.get("type") != "assistant": continue
        for c in (d.get("message", {}) or {}).get("content", []) or []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                out.append((d.get("timestamp", ""), src, c.get("name"), c.get("input") or {}))
    return out
firsts = []
for main in sorted(glob.glob(f"{BASE}/*.jsonl")):
    if os.path.getmtime(main) < cut: continue
    sid = os.path.basename(main)[:-6]
    ev = events(main, "main")
    for sub in glob.glob(f"{BASE}/{sid}/subagents/*.jsonl"): ev += events(sub, "sub")
    ev.sort(key=lambda e: e[0]); touched = set()
    for ts, src, name, inp in ev:
        fp = inp.get("file_path", "") if isinstance(inp, dict) else ""
        chk = (name == "Skill" and "firecrawl-developer-index" in str(inp.get("skill", ""))) or (name == "Bash" and "firecrawl developer" in str(inp.get("command", "")))
        code = (name == "Write" and code_file.search(fp or "") and fp not in touched) or (name == "Bash" and bash_re.search(str(inp.get("command", ""))))
        if name in ("Read", "Write", "Edit", "MultiEdit") and fp: touched.add(fp)
        if chk or code:
            if code and not chk:
                cmd = str(inp.get("command", "")) or fp
                m = bash_re.search(cmd) if name == "Bash" else None
                seg = cmd[max(0, m.start() - 60): m.start() + 260] if m else cmd[:300]
                firsts.append((sid[:8], src, name, seg.replace("\n", "⏎")))
            break
random.seed(7)
for x in random.sample(firsts, 25):
    print(x[0], x[1], x[2], "|", x[3][:320]); print()
