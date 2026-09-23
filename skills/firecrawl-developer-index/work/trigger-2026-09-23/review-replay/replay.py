#!/usr/bin/env python3
"""Replay hook.py decision logic over real owner sessions (main + subagents, merged by timestamp). Read-only."""
import json, os, re, glob, time, sys, collections
BASE = os.path.expanduser("~/.claude/projects/-Users-triton-Documents-GitHub-agentic-research")
code_file = re.compile(r"\.(py|js|mjs|cjs|ts|tsx|sh|rb|go|rs|java|kt|swift|php|pl|lua)$")
bash_re = re.compile(r"\b(python3?|node|ruby|perl)\s+(-\s*<<|-[ce]\s)|cat\s*>+\s*\S+\.(py|js|mjs|ts|sh|rb)\b")
days = float(sys.argv[1]) if len(sys.argv) > 1 else 21
cut = time.time() - days * 86400
def events(path, src):
    out = []
    for line in open(path, errors="replace"):
        try: d = json.loads(line)
        except Exception: continue
        if d.get("type") != "assistant": continue
        ts = d.get("timestamp", "")
        for c in (d.get("message", {}) or {}).get("content", []) or []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                out.append((ts, src, c.get("name"), c.get("input") or {}))
    return out
stats = collections.Counter(); firsts = []
for main in glob.glob(f"{BASE}/*.jsonl"):
    if os.path.getmtime(main) < cut: continue
    sid = os.path.basename(main)[:-6]
    ev = events(main, "main")
    for sub in glob.glob(f"{BASE}/{sid}/subagents/*.jsonl"):
        ev += events(sub, "sub")
    ev.sort(key=lambda e: e[0])
    if not ev: continue
    stats["sessions"] += 1
    touched = set(); first = None; n_code = 0; fired_skill = False
    for ts, src, name, inp in ev:
        is_checked = (name == "Skill" and "firecrawl-developer-index" in str(inp.get("skill", ""))) or (name == "Bash" and "firecrawl developer" in str(inp.get("command", "")))
        fp = inp.get("file_path", "") if isinstance(inp, dict) else ""
        is_code = (name == "Write" and code_file.search(fp or "") and fp not in touched) or (name == "Bash" and bash_re.search(str(inp.get("command", ""))))
        if name in ("Read", "Write", "Edit", "MultiEdit") and fp: touched.add(fp)
        if is_checked: fired_skill = True
        if is_code: n_code += 1
        if first is None and (is_checked or is_code):
            first = ("CHECK" if is_checked else "DENY", src, name, (str(inp.get("command", "")) or fp)[:150].replace("\n", "⏎"))
    if n_code: stats["sessions_with_code_write"] += 1
    if fired_skill: stats["sessions_skill_or_search"] += 1
    if first:
        stats["first=" + first[0]] += 1
        stats[f"first={first[0]} in {first[1]}"] += 1
        firsts.append((sid[:8], n_code, first))
    stats["code_writes_total"] += n_code
print(dict(stats))
print("code writes after the first (unguarded by once-per-session):", stats["code_writes_total"] - stats["first=DENY"])
for sid, n, f in sorted(firsts, key=lambda x: -x[1])[:60]:
    print(sid, f"code_writes={n:3d}", f[0], f[1], f[2], "|", f[3])
