#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  run-clean-design-agent.sh --run-dir DIR --questions FILE [--url URL]

Runs clean Codex terminal design reviewers:
  1. multiple focused reviewers per planned screenshot group (2-3 images each);
  2. one clean aggregate reviewer over the focused outputs.

Options:
  --run-dir DIR       Existing design-review run directory with manifest.json.
  --questions FILE    Markdown questions file.
  --url URL           Captured page URL, added to prompts.
  --model NAME        Codex model. Default: gpt-5.5.
  --effort LEVEL      model_reasoning_effort. Default: high.
  --parallel N        Focused reviewers to run at once. Default: 6.
  --progress-interval N
                     Seconds between progress heartbeats. Default: 10.
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
PARALLEL="6"
PROGRESS_INTERVAL="10"
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
    --progress-interval) PROGRESS_INTERVAL="${2:-}"; shift 2 ;;
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
[[ "$PROGRESS_INTERVAL" =~ ^[0-9]+$ ]] || die "--progress-interval must be a positive integer"
[[ "$PROGRESS_INTERVAL" -gt 0 ]] || die "--progress-interval must be > 0"
command -v codex >/dev/null 2>&1 || die "codex CLI not found"

RUN_DIR="$(cd "$RUN_DIR" && pwd)"
QUESTIONS="$(cd "$(dirname "$QUESTIONS")" && pwd)/$(basename "$QUESTIONS")"
OUT_FILE="${OUT_FILE:-$RUN_DIR/design-review.md}"
AUTH_SOURCE="${CODEX_AUTH_JSON:-$HOME/.codex/auth.json}"
[[ -f "$AUTH_SOURCE" ]] || die "Codex auth file not found: $AUTH_SOURCE"

node -e '
const fs = require("fs");
const manifestPath = `${process.argv[1]}/manifest.json`;
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const failures = Array.isArray(manifest.failures) ? manifest.failures : [];
if (failures.length > 0) {
  console.error(`manifest has ${failures.length} capture failure(s); rerun capture before review`);
  process.exit(1);
}
' "$RUN_DIR" || die "manifest contains capture failures"

GROUP_INDEX="$("$SCRIPT_DIR/prepare-design-review-groups.mjs" \
  --run-dir "$RUN_DIR" \
  --questions "$QUESTIONS" \
  ${URL:+--url "$URL"})"
PROGRESS_SCRIPT="$SCRIPT_DIR/design-review-progress.mjs"
PROGRESS_MD="$("$PROGRESS_SCRIPT" init \
  --run-dir "$RUN_DIR" \
  --index "$GROUP_INDEX" \
  --parallel "$PARALLEL")"

if [[ "$DRY_RUN" == "1" ]]; then
  printf '[run-clean-design-agent] dry-run group index: %s\n' "$GROUP_INDEX"
  printf '[run-clean-design-agent] dry-run progress file: %s\n' "$PROGRESS_MD"
  exit 0
fi

progress_update() {
  "$PROGRESS_SCRIPT" "$@" --run-dir "$RUN_DIR" >/dev/null
}

progress_summary() {
  "$PROGRESS_SCRIPT" summary --run-dir "$RUN_DIR"
}

progress_heartbeat() {
  "$PROGRESS_SCRIPT" heartbeat --run-dir "$RUN_DIR" >/dev/null
  progress_summary
}

HEARTBEAT_PID=""

stop_heartbeat() {
  if [[ -n "${HEARTBEAT_PID:-}" ]]; then
    kill "$HEARTBEAT_PID" >/dev/null 2>&1 || true
    wait "$HEARTBEAT_PID" >/dev/null 2>&1 || true
    HEARTBEAT_PID=""
  fi
}

start_heartbeat() {
  (
    while true; do
      sleep "$PROGRESS_INTERVAL"
      progress_heartbeat
    done
  ) &
  HEARTBEAT_PID="$!"
}

trap stop_heartbeat EXIT

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

run_group_reviewer() {
  local group_id="$1"
  local prompt="$2"
  local output="$3"
  local log="$4"
  shift 4
  local images=("$@")
  local exit_code

  set +e
  run_clean_codex "$prompt" "$output" "$log" "${images[@]}"
  exit_code="$?"
  set -e

  if [[ "$exit_code" -eq 0 ]]; then
    progress_update group --id "$group_id" --status done --exit-code 0
    return 0
  fi

  progress_update group --id "$group_id" --status failed --exit-code "$exit_code"
  return "$exit_code"
}

active=0
failures=0
pids=()
groups=()

printf '[run-clean-design-agent] progress file: %s\n' "$PROGRESS_MD"
progress_summary
start_heartbeat

while IFS=$'\t' read -r group_id prompt output log images_json; do
  images=()
  while IFS= read -r image; do
    [[ -n "$image" ]] && images+=("$image")
  done < <(node -e 'for (const item of JSON.parse(process.argv[1])) console.log(item)' "$images_json")

  printf '[run-clean-design-agent] start group=%s images=%s\n' "$group_id" "${#images[@]}"
  run_group_reviewer "$group_id" "$prompt" "$output" "$log" "${images[@]}" &
  progress_update group --id "$group_id" --status running --pid "$!"
  pids+=("$!")
  groups+=("$group_id")
  active=$((active + 1))

  if [[ "$active" -ge "$PARALLEL" ]]; then
    if ! wait "${pids[0]}"; then
      failures=$((failures + 1))
    fi
    pids=("${pids[@]:1}")
    groups=("${groups[@]:1}")
    active=$((active - 1))
    progress_summary
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
  progress_summary
done

if [[ "$failures" -gt 0 ]]; then
  progress_update stage --stage failed
  stop_heartbeat
  progress_summary
  printf '[run-clean-design-agent] %s focused reviewer(s) failed\n' "$failures" >&2
  find "$RUN_DIR/group-reviews" -name codex.log -maxdepth 3 -print >&2
  exit 1
fi

AGGREGATE_PROMPT="$("$SCRIPT_DIR/prepare-design-review-groups.mjs" \
  --aggregate \
  --run-dir "$RUN_DIR" \
  --questions "$QUESTIONS" \
  ${URL:+--url "$URL"})"

AGGREGATE_LOG="$RUN_DIR/aggregate-codex.log"
progress_update stage --stage aggregate-review
progress_update aggregate --status running --output "$OUT_FILE" --log "$AGGREGATE_LOG"
progress_summary

if run_clean_codex "$AGGREGATE_PROMPT" "$OUT_FILE" "$AGGREGATE_LOG"; then
  progress_update aggregate --status done --exit-code 0
  progress_update stage --stage complete
else
  aggregate_exit="$?"
  progress_update aggregate --status failed --exit-code "$aggregate_exit"
  progress_update stage --stage failed
  stop_heartbeat
  progress_summary
  exit "$aggregate_exit"
fi

stop_heartbeat
progress_summary

printf '[run-clean-design-agent] aggregate review written: %s\n' "$OUT_FILE"
printf '[run-clean-design-agent] group reviews: %s\n' "$RUN_DIR/group-reviews"
printf '[run-clean-design-agent] aggregate log: %s\n' "$AGGREGATE_LOG"
