import re, json
# logic copied verbatim from work/trigger-2026-09-23/hook.py (no marker side effects)
code_file = re.compile(r"\.(py|js|mjs|cjs|ts|tsx|sh|rb|go|rs|java|kt|swift|php|pl|lua)$")
bash_re = r"\b(python3?|node|ruby|perl)\s+(-\s*<<|-[ce]\s)|cat\s*>+\s*\S+\.(py|js|mjs|ts|sh|rb)\b"
def checked(tool, inp):
    return (tool == "Skill" and "firecrawl-developer-index" in str(inp.get("skill", ""))) or (tool == "Bash" and "firecrawl developer" in inp.get("command", ""))
def writes(tool, inp, exists=False):
    return bool((tool == "Write" and code_file.search(inp.get("file_path", "")) and not exists) or (tool == "Bash" and re.search(bash_re, inp.get("command", ""))))
cases = [
 ("Bash", "python3 - <<'EOF'\nprint(1)\nEOF", "inline heredoc (dash)"),
 ("Bash", "python3 <<'EOF'\nprint(1)\nEOF", "inline heredoc (no dash)"),
 ("Bash", "cat <<'EOF' > check.py\nprint(1)\nEOF", "heredoc to file, redirect after"),
 ("Bash", "cat > check.py <<'EOF'\nprint(1)\nEOF", "heredoc to file, redirect first"),
 ("Bash", "python3 -c \"import yaml,sys; print(yaml.__version__)\"", "trivial version one-liner"),
 ("Bash", "node -e \"console.log(require('./package.json').version)\"", "trivial node one-liner"),
 ("Bash", "gh api repos/x/y | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"name\"])'", "json field extraction"),
 ("Bash", "python3 -X utf8 -c 'print(1)'", "flag before -c"),
 ("Bash", "uv run python -c 'import x'", "uv run python -c"),
 ("Bash", "awk '/^BEGIN:VCARD/{t=0} /^TEL/{t=1} /^END:VCARD/{if(!t)print fn}' contacts.vcf", "awk program"),
 ("Bash", "grep -o '](.*)' *.md | while IFS=: read f l m; do [ -e \"$m\" ] || echo $f; done", "shell loop checker"),
 ("Bash", "perl -ne 'print if /TEL/' contacts.vcf", "perl -ne"),
 ("Bash", "tee fix.sh <<'EOF'\necho hi\nEOF", "tee heredoc to file"),
 ("Bash", "python3 -m pytest -q", "run tests"),
 ("Write", "/repo/src/NewButton.jsx", "new .jsx file"),
 ("Write", "/repo/scripts/check.py", "new .py file"),
 ("Write", "/repo/tools/check.bash", "new .bash file"),
 ("Edit", "/repo/src/schedule.js", "Edit existing file (not in matcher)"),
]
for tool, arg, label in cases:
    inp = {"command": arg} if tool == "Bash" else {"file_path": arg}
    matched_by_matcher = tool in ("Write", "Bash", "Skill")
    print(f"{'DENY' if matched_by_matcher and writes(tool, inp) else 'pass':5} | {label}")
