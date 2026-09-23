#!/usr/bin/env python3
"""PreToolUse: once per session, stop the first new-code write until the reuse check has happened."""
import json, os, re, sys

data = json.load(sys.stdin)
tool = data.get("tool_name", "")
inp = data.get("tool_input") or {}
marker = os.path.join("/tmp/reuse-hook", data.get("session_id", "none"))
os.makedirs(os.path.dirname(marker), exist_ok=True)
if os.path.exists(marker):
    sys.exit(0)

checked = (tool == "Skill" and "firecrawl-developer-index" in str(inp.get("skill", ""))) or (
    tool == "Bash" and "firecrawl developer" in inp.get("command", ""))
code_file = re.compile(r"\.(py|js|mjs|cjs|ts|tsx|sh|rb|go|rs|java|kt|swift|php|pl|lua)$")
writes_code = (tool == "Write" and code_file.search(inp.get("file_path", "")) and not os.path.exists(inp.get("file_path", ""))) or (
    tool == "Bash" and re.search(r"\b(python3?|node|ruby|perl)\s+(-\s*<<|-[ce]\s)|cat\s*>+\s*\S+\.(py|js|mjs|ts|sh|rb)\b", inp.get("command", "")))
if not (checked or writes_code):
    sys.exit(0)
open(marker, "w").close()
if checked:
    sys.exit(0)
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Before writing new code, even a quick script, check firecrawl-developer-index for a package to install, an upgrade, or the documented way. If nothing fits, retry this call."}}))
