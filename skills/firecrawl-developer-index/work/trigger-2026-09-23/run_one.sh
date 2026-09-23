#!/bin/bash
# usage: run_one.sh VARIANT SCENARIO REP
R=/tmp/reuse-probe; V=$1; S=$2; N=$3
W=$R/work/$V/$S-$N; rm -rf "$W"; mkdir -p "$W" "$R/out/$V"; cp -R "$R/templates/$S/." "$W/"
P=$(grep "^$S	" $R/prompts.tsv | cut -f2)
cd "$W" && printf '%s' "$P" | "/Users/triton/Library/Application Support/Claude/claude-code/2.1.280/claude.app/Contents/MacOS/claude" -p --model claude-opus-5-5 --output-format stream-json --verbose \
  --max-turns 12 --no-session-persistence --permission-mode bypassPermissions \
  --disallowedTools "Bash,Monitor,WebFetch,WebSearch,Agent" \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  > "$R/out/$V/$S-$N.jsonl" 2> "$R/out/$V/$S-$N.err"
echo "done $V $S $N exit=$?"
