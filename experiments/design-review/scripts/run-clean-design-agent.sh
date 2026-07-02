#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  run-clean-design-agent.sh --run-dir DIR --questions FILE [--url URL]

Runs clean Codex terminal design reviewers:
  1. one clean reviewer per planned screenshot group (2-3 images each);
  2. one clean aggregate reviewer over the group outputs.

Options:
  --run-dir DIR       Existing design-review run directory with manifest.json.
  --questions FILE    Markdown questions file.
  --url URL           Captured page URL, added to prompts.
  --model NAME        Codex model. Default: gpt-5.5.
  --effort LEVEL      model_reasoning_effort. Default: high.
  --parallel N        Group reviewers to run at once. Default: 3.
  --out FILE          Aggregate output markdown. Default: <run-dir>/design-review.md.
  --dry-run           Build prompts and selected image lists, but do not call Codex.
  -h, --help          Show this help.
USAGE
}

die() {
  printf 'run-clean-design-agent: %s\n' "$*" >&2
  exit 2
}

RUN_DIR=""
QUESTIONS=""
URL=""
MODEL="${DESIGN_REVIEW_MODEL:-gpt-5.5}"
EFFORT="${DESIGN_REVIEW_EFFORT:-high}"
PARALLEL="3"
OUT_FILE=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-dir) RUN_DIR="${2:-}"; shift 2 ;;
    --questions) QUESTIONS="${2:-}"; shift 2 ;;
    --url) URL="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --effort) EFFORT="${2:-}"; shift 2 ;;
    --parallel) PARALLEL="${2:-}"; shift 2 ;;
    --max-images) shift 2 ;; # Backward-compatible no-op; groups own image count.
    --out) OUT_FILE="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ -n "$RUN_DIR" ]] || die "--run-dir is required"
[[ -n "$QUESTIONS" ]] || die "--questions is required"
[[ -d "$RUN_DIR" ]] || die "run-dir not found: $RUN_DIR"
[[ -f "$QUESTIONS" ]] || die "questions file not found: $QUESTIONS"
[[ "$PARALLEL" =~ ^[0-9]+$ ]] || die "--parallel must be a positive integer"
[[ "$PARALLEL" -gt 0 ]] || die "--parallel must be > 0"
command -v codex >/dev/null 2>&1 || die "codex CLI not found"

RUN_DIR="$(cd "$RUN_DIR" && pwd)"
QUESTIONS="$(cd "$(dirname "$QUESTIONS")" && pwd)/$(basename "$QUESTIONS")"
OUT_FILE="${OUT_FILE:-$RUN_DIR/design-review.md}"
AUTH_SOURCE="${CODEX_AUTH_JSON:-$HOME/.codex/auth.json}"
[[ -f "$AUTH_SOURCE" ]] || die "Codex auth file not found: $AUTH_SOURCE"

GROUP_INDEX="$("$SCRIPT_DIR/prepare-design-review-groups.mjs" \
  --run-dir "$RUN_DIR" \
  --questions "$QUESTIONS" \
  ${URL:+--url "$URL"})"

if [[ "$DRY_RUN" == "1" ]]; then
  printf '[run-clean-design-agent] dry-run group index: %s\n' "$GROUP_INDEX"
  exit 0
fi

run_clean_codex() {
  local prompt_file="$1"
  local output_file="$2"
  local log_file="$3"
  shift 3
  local images=("$@")

  local clean_home
  local clean_cwd
  clean_home="$(mktemp -d "${TMPDIR:-/tmp}/codex-design-review-home.XXXXXX")"
  clean_cwd="$(mktemp -d "${TMPDIR:-/tmp}/codex-design-review-cwd.XXXXXX")"
  ln -s "$AUTH_SOURCE" "$clean_home/auth.json"

  local cmd=(
    codex exec
    --ephemeral
    --ignore-user-config
    --ignore-rules
    --skip-git-repo-check
    --sandbox read-only
    --cd "$clean_cwd"
    --add-dir "$RUN_DIR"
    --model "$MODEL"
    -c "model_reasoning_effort=\"$EFFORT\""
    --output-last-message "$output_file"
  )
  for image in "${images[@]}"; do
    cmd+=(-i "$image")
  done
  cmd+=(-)

  (
    trap 'rm -rf "$clean_home" "$clean_cwd"' EXIT
    unset OPENAI_API_KEY
    unset CODEX_API_KEY
    unset OPENAI_BASE_URL
    export CODEX_HOME="$clean_home"
    "${cmd[@]}" < "$prompt_file"
  ) >"$log_file" 2>&1
}

active=0
failures=0
pids=()

while IFS=$'\t' read -r group_id prompt output log images_json; do
  images=()
  while IFS= read -r image; do
    [[ -n "$image" ]] && images+=("$image")
  done < <(node -e 'for (const item of JSON.parse(process.argv[1])) console.log(item)' "$images_json")

  printf '[run-clean-design-agent] start group=%s images=%s\n' "$group_id" "${#images[@]}"
  run_clean_codex "$prompt" "$output" "$log" "${images[@]}" &
  pids+=("$!")
  active=$((active + 1))

  if [[ "$active" -ge "$PARALLEL" ]]; then
    if ! wait "${pids[0]}"; then
      failures=$((failures + 1))
    fi
    pids=("${pids[@]:1}")
    active=$((active - 1))
  fi
done < <(node -e '
const fs = require("fs");
const index = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
for (const group of index.groups) {
  console.log([group.id, group.prompt, group.output, group.log, JSON.stringify(group.images)].join("\t"));
}
' "$GROUP_INDEX")

for pid in "${pids[@]}"; do
  if ! wait "$pid"; then
    failures=$((failures + 1))
  fi
done

if [[ "$failures" -gt 0 ]]; then
  printf '[run-clean-design-agent] %s group reviewer(s) failed\n' "$failures" >&2
  find "$RUN_DIR/group-reviews" -name codex.log -maxdepth 3 -print >&2
  exit 1
fi

AGGREGATE_PROMPT="$("$SCRIPT_DIR/prepare-design-review-groups.mjs" \
  --aggregate \
  --run-dir "$RUN_DIR" \
  --questions "$QUESTIONS" \
  ${URL:+--url "$URL"})"

AGGREGATE_LOG="$RUN_DIR/aggregate-codex.log"
run_clean_codex "$AGGREGATE_PROMPT" "$OUT_FILE" "$AGGREGATE_LOG"

printf '[run-clean-design-agent] aggregate review written: %s\n' "$OUT_FILE"
printf '[run-clean-design-agent] group reviews: %s\n' "$RUN_DIR/group-reviews"
printf '[run-clean-design-agent] aggregate log: %s\n' "$AGGREGATE_LOG"
