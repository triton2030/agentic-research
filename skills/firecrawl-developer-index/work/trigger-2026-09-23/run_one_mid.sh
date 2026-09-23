#!/bin/bash
# usage: run_one_mid.sh VARIANT SCENARIO REP  (Bash allowed, installs and network fetchers denied)
R=/tmp/reuse-probe; V=$1; S=$2; N=$3
W=$R/work/$V/$S-$N; rm -rf "$W"; mkdir -p "$W" "$R/out/$V"; cp -R "$R/templates/$S/." "$W/"
P=$(grep "^$S	" $R/prompts.tsv | cut -f2)
cd "$W" && printf '%s' "$P" | "/Users/triton/Library/Application Support/Claude/claude-code/2.1.280/claude.app/Contents/MacOS/claude" -p --model claude-opus-5-5 --output-format stream-json --verbose \
  --max-turns 16 --no-session-persistence --permission-mode bypassPermissions \
  --disallowedTools "Monitor,WebFetch,WebSearch,Agent,Bash(npm install:*),Bash(npm i:*),Bash(npm add:*),Bash(npx:*),Bash(pnpm:*),Bash(yarn:*),Bash(pip install:*),Bash(pip3 install:*),Bash(python3 -m pip:*),Bash(uv:*),Bash(uvx:*),Bash(brew:*),Bash(curl:*),Bash(wget:*),Bash(git push:*),Bash(gh:*)" \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  > "$R/out/$V/$S-$N.jsonl" 2> "$R/out/$V/$S-$N.err"
echo "done $V $S $N exit=$?"
