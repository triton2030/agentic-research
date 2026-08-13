#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  run-clean-design-agent.sh --run-dir DIR --questions FILE [options]

Runs one clean Codex reviewer for each ready question in manifest.json.
There is no lens multiplication and no aggregate reviewer.

Options:
  --run-dir DIR     Existing run directory with manifest.json.
  --questions FILE  Clean reviewer contract.
  --model NAME      Codex model. Default: gpt-5.6-sol.
  --effort LEVEL    Reasoning effort. Default: high.
  --parallel N      Maximum concurrent reviewers. Default: 3.
  --dry-run         Build prompts and print task/image mapping without Codex.
  -h, --help        Show this help.
USAGE
}

die() {
  printf 'run-clean-design-agent: %s\n' "$*" >&2
  exit 2
}

RUN_DIR=""
QUESTIONS=""
MODEL="${DESIGN_REVIEW_MODEL:-gpt-5.6-sol}"
EFFORT="${DESIGN_REVIEW_EFFORT:-high}"
PARALLEL="3"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-dir) RUN_DIR="${2:-}"; shift 2 ;;
    --questions) QUESTIONS="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --effort) EFFORT="${2:-}"; shift 2 ;;
    --parallel) PARALLEL="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ -n "$RUN_DIR" ]] || die "--run-dir is required"
[[ -n "$QUESTIONS" ]] || die "--questions is required"
[[ -d "$RUN_DIR" ]] || die "run-dir not found: $RUN_DIR"
[[ -f "$QUESTIONS" ]] || die "questions file not found: $QUESTIONS"
[[ "$PARALLEL" =~ ^[0-9]+$ && "$PARALLEL" -gt 0 ]] || die "--parallel must be a positive integer"
command -v codex >/dev/null 2>&1 || die "codex CLI not found"

RUN_DIR="$(cd "$RUN_DIR" && pwd)"
QUESTIONS="$(cd "$(dirname "$QUESTIONS")" && pwd)/$(basename "$QUESTIONS")"
AUTH_SOURCE="${CODEX_AUTH_JSON:-${CODEX_HOME:-$HOME/.codex}/auth.json}"
[[ -f "$AUTH_SOURCE" ]] || die "Codex auth file not found: $AUTH_SOURCE"

TASK_INDEX="$("$SCRIPT_DIR/prepare-design-review-tasks.mjs"   --run-dir "$RUN_DIR"   --questions "$QUESTIONS")"

if [[ "$DRY_RUN" == "1" ]]; then
  printf '[run-clean-design-agent] dry-run task index: %s\n' "$TASK_INDEX"
  node -e '
    const fs = require("fs");
    const index = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
    for (const task of index.tasks) {
      console.log([task.id, task.evidenceIds.join(","), task.images.join(",")].join("\t"));
    }
  ' "$TASK_INDEX"
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
  local image
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

status_name() {
  printf '%s.status' "$(printf '%s' "$1" | sed 's/[^A-Za-z0-9_.-]/_/g')"
}

run_task() {
  local task_id="$1"
  local prompt="$2"
  local output="$3"
  local log="$4"
  shift 4
  local images=("$@")
  local status_file
  local exit_code=0
  status_file="$STATUS_DIR/$(status_name "$task_id")"

  set +e
  run_clean_codex "$prompt" "$output" "$log" "${images[@]}"
  exit_code="$?"
  set -e
  printf '%s\n' "$exit_code" > "${status_file}.tmp"
  mv "${status_file}.tmp" "$status_file"
  return "$exit_code"
}

wait_for_one() {
  local index
  local status_file
  local exit_code
  while true; do
    for index in "${!pids[@]}"; do
      status_file="$STATUS_DIR/$(status_name "${task_ids[$index]}")"
      if [[ ! -f "$status_file" ]]; then
        continue
      fi
      exit_code="$(cat "$status_file")"
      wait "${pids[$index]}" >/dev/null 2>&1 || true
      if [[ "$exit_code" != "0" ]]; then
        failures=$((failures + 1))
        printf '[run-clean-design-agent] failed task=%s log=%s\n'           "${task_ids[$index]}" "${logs[$index]}" >&2
      else
        printf '[run-clean-design-agent] done task=%s\n' "${task_ids[$index]}"
      fi
      unset 'pids[index]'
      unset 'task_ids[index]'
      unset 'logs[index]'
      pids=("${pids[@]}")
      task_ids=("${task_ids[@]}")
      logs=("${logs[@]}")
      active=$((active - 1))
      return
    done
    sleep 0.2
  done
}

STATUS_DIR="$RUN_DIR/reviewers/.status"
mkdir -p "$STATUS_DIR"
find "$STATUS_DIR" -type f -name '*.status' -delete

active=0
failures=0
pids=()
task_ids=()
logs=()

while IFS=$'\t' read -r task_id prompt output log images_json; do
  images=()
  while IFS= read -r image; do
    [[ -n "$image" ]] && images+=("$image")
  done < <(node -e 'for (const item of JSON.parse(process.argv[1])) console.log(item)' "$images_json")

  printf '[run-clean-design-agent] start task=%s images=%s\n' "$task_id" "${#images[@]}"
  run_task "$task_id" "$prompt" "$output" "$log" "${images[@]}" &
  pids+=("$!")
  task_ids+=("$task_id")
  logs+=("$log")
  active=$((active + 1))
  if [[ "$active" -ge "$PARALLEL" ]]; then
    wait_for_one
  fi
done < <(node -e '
  const fs = require("fs");
  const index = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
  for (const task of index.tasks) {
    console.log([task.id, task.prompt, task.output, task.log, JSON.stringify(task.images)].join("\t"));
  }
' "$TASK_INDEX")

while [[ "$active" -gt 0 ]]; do
  wait_for_one
done

final_failures="$(
node - "$TASK_INDEX" "$STATUS_DIR" <<'NODE'
const fs = require("fs");
const path = require("path");
const [indexPath, statusDir] = process.argv.slice(2);
const index = JSON.parse(fs.readFileSync(indexPath, "utf8"));
for (const task of index.tasks) {
  const name = task.id.replace(/[^A-Za-z0-9_.-]/g, "_") + ".status";
  const statusPath = path.join(statusDir, name);
  const exitCode = fs.existsSync(statusPath) ? Number(fs.readFileSync(statusPath, "utf8").trim()) : null;
  task.exitCode = exitCode;
  task.status = exitCode === 0 && fs.existsSync(task.output) ? "done" : "failed";
}
fs.writeFileSync(indexPath, JSON.stringify(index, null, 2) + "\n");
const summary = {
  version: 1,
  generatedAt: new Date().toISOString(),
  tasks: index.tasks.map(({ id, evidenceIds, output, log, status, exitCode }) => ({
    id,
    evidenceIds,
    output,
    log,
    status,
    exitCode,
  })),
};
fs.writeFileSync(path.join(path.dirname(indexPath), "summary.json"), JSON.stringify(summary, null, 2) + "\n");
console.log(summary.tasks.filter((task) => task.status === "failed").length);
NODE
)"

if [[ "$final_failures" -gt 0 ]]; then
  printf '[run-clean-design-agent] %s reviewer task(s) failed or produced no output\n' +    "$final_failures" >&2
  node -e '
    const fs = require("fs");
    const index = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
    for (const task of index.tasks.filter((item) => item.status === "failed")) {
      console.error([
        "task=" + task.id,
        "output=" + task.output,
        "log=" + task.log,
        "exit=" + task.exitCode,
      ].join(" "));
    }
  ' "$TASK_INDEX"
  exit 1
fi

printf '[run-clean-design-agent] reviews complete: %s\n' "$RUN_DIR/reviewers"
printf '[run-clean-design-agent] root must now re-open exact pixels and adjudicate every candidate\n'
