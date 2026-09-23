#!/usr/bin/env python3
"""Summarize tool-use traces of headless runs: was firecrawl-developer-index invoked, and before the first code write?"""
import json, sys, glob, os, re
R = "/tmp/reuse-probe"
variants = sys.argv[1:] or sorted(os.listdir(f"{R}/out"))
TARGET = "firecrawl-developer-index"
for v in variants:
    files = sorted(glob.glob(f"{R}/out/{v}/*.jsonl"))
    print(f"\n=== {v} ({len(files)} runs)")
    for f in files:
        name = os.path.basename(f)[:-6]
        seq, skills, first_write, target_at, result, err = [], [], None, None, "", ""
        try:
            lines = open(f).read().splitlines()
        except Exception as e:
            print(name, "READ ERROR", e); continue
        denied = set()
        for line in lines:
            try: d = json.loads(line)
            except Exception: continue
            if d.get("type") == "user":
                for c in d.get("message", {}).get("content", []) or []:
                    if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error") and "firecrawl-developer-index" in json.dumps(c.get("content")):
                        denied.add(c.get("tool_use_id"))
        for line in lines:
            try: d = json.loads(line)
            except Exception: continue
            if d.get("type") == "assistant":
                for c in d.get("message", {}).get("content", []) or []:
                    if c.get("type") == "tool_use":
                        n = c.get("name")
                        inp = c.get("input") or {}
                        if n == "Skill":
                            sk = inp.get("skill") or inp.get("command") or json.dumps(inp)[:60]
                            skills.append(sk)
                            seq.append(f"Skill:{sk}")
                            if TARGET in str(sk) and target_at is None: target_at = len(seq)
                        else:
                            seq.append(n)
                            if n == "Bash" and "firecrawl" in str(inp.get("command","")): skills.append("bash:firecrawl")
                            if c.get("id") not in denied and (n in ("Write", "Edit", "MultiEdit") or (n == "Bash" and ("cat >" in str(inp.get("command","")) or "<<" in str(inp.get("command","")) or "python3 -c" in str(inp.get("command","")) or "python3 - " in str(inp.get("command","")))) ) and first_write is None:
                                first_write = len(seq)
            if d.get("type") == "result":
                result = (d.get("result") or "")[:160].replace("\n", " ")
                err = d.get("subtype", "")
        fired = target_at is not None
        before = fired and (first_write is None or target_at < first_write)
        verdict = "FIRED-before-code" if before else ("FIRED-late" if fired else "no")
        print(f"{name:14} {verdict:18} skills={skills} tools={len(seq)} end={err}")
    print()
