#!/usr/bin/env bash
# Generate or edit images with OpenAI GPT Image from saved briefs, in parallel.
# Usage: gen.sh NAME [NAME ...]  — reads $DIR/NAME.prompt.md, writes $DIR/NAME.$FORMAT
# Env:   DIR        default <git root or cwd>/_workspace/codex-image/<today>
#        MODEL      default gpt-image-2.5-sunburst-2026-09-08
#        QUALITY    low | medium | high (default) | xhigh | max
#        SIZE       default 2048x1152; edges multiples of 16
#        FORMAT     png (default) | webp | jpeg
#        BACKGROUND transparent | opaque
#        IMAGES     "target.png ref.png" — edit instead of generate; order = Image 1, Image 2; no spaces in paths
set -euo pipefail

MODEL=${MODEL:-gpt-image-2.5-sunburst-2026-09-08}
QUALITY=${QUALITY:-high}
SIZE=${SIZE:-2048x1152}
FORMAT=${FORMAT:-png}
BACKGROUND=${BACKGROUND:-}
IMAGES=${IMAGES:-}
DIR=${DIR:-"$(git rev-parse --show-toplevel 2>/dev/null || pwd)/_workspace/codex-image/$(date +%F)"}
KEY_FILE="$HOME/.config/openai/api-key"

[ $# -ge 1 ] || { sed -n '2,11p' "$0"; exit 2; }
[ -r "$KEY_FILE" ] || { echo "no API key at $KEY_FILE" >&2; exit 1; }

auth() { printf 'Authorization: Bearer %s\n' "$(<"$KEY_FILE")"; }

one() {
  local name=$1
  local brief="$DIR/$name.prompt.md" out="$DIR/$name.$FORMAT" json
  [ -f "$brief" ] || { echo "$name: no brief at $brief" >&2; return 1; }
  [ -e "$out" ] && { echo "$name: $out exists — use a new name" >&2; return 1; }
  json=$(mktemp)
  if [ -n "$IMAGES" ]; then
    local args=(-F "model=$MODEL" -F "size=$SIZE" -F "quality=$QUALITY" -F "output_format=$FORMAT" -F "prompt=<$brief")
    [ -n "$BACKGROUND" ] && args+=(-F "background=$BACKGROUND")
    local img
    for img in $IMAGES; do args+=(-F "image[]=@$img"); done
    curl -sS --max-time 300 https://api.openai.com/v1/images/edits -H @<(auth) "${args[@]}" > "$json" || true
  else
    jq -n --rawfile p "$brief" --arg m "$MODEL" --arg s "$SIZE" --arg q "$QUALITY" --arg f "$FORMAT" --arg b "$BACKGROUND" \
      '{model:$m, prompt:$p, size:$s, quality:$q, output_format:$f} + (if $b == "" then {} else {background:$b} end)' |
      curl -sS --max-time 300 https://api.openai.com/v1/images/generations \
        -H @<(auth) -H 'Content-Type: application/json' -d @- > "$json" || true
  fi
  if jq -e '.data[0].b64_json' "$json" >/dev/null 2>&1; then
    jq -r '.data[0].b64_json' "$json" | base64 -d > "$out"
    jq -r --arg n "$name" --arg o "$out" '.usage as $u
      | (($u.output_tokens * 30 + ($u.input_tokens_details.image_tokens // 0) * 8
          + ($u.input_tokens_details.text_tokens // 0) * 5) / 1e6) as $usd
      | "\($n): \($o)  $\(($usd * 1000 | round) / 1000)"' "$json"
    rm -f "$json"
  else
    echo "$name: ERROR $(jq -c '.error // .' "$json" 2>/dev/null | head -c 400 || head -c 400 "$json")" >&2
    rm -f "$json"
    return 1
  fi
}

mkdir -p "$DIR"
pids=()
for name in "$@"; do one "$name" & pids+=("$!"); done
rc=0
for pid in "${pids[@]}"; do wait "$pid" || rc=1; done
exit "$rc"
