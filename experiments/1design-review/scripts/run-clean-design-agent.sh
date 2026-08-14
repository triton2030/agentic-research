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
  --parallel N      Concurrent reviewers, 1-3. Default: 3.
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
[[ "$PARALLEL" =~ ^[1-3]$ ]] || die "--parallel must be an integer from 1 to 3"
command -v codex >/dev/null 2>&1 || die "codex CLI not found"
command -v sandbox-exec >/dev/null 2>&1 || die "sandbox-exec is required for reviewer evidence isolation"
command -v shasum >/dev/null 2>&1 || die "shasum is required for approved pixel verification"
CODEX_BIN="$(realpath "$(command -v codex)")"
CODEX_BIN_DIR="$(dirname "$CODEX_BIN")"

RUN_DIR="$(cd "$RUN_DIR" && pwd)"
QUESTIONS="$(cd "$(dirname "$QUESTIONS")" && pwd)/$(basename "$QUESTIONS")"
AUTH_SOURCE="${CODEX_AUTH_JSON:-${CODEX_HOME:-$HOME/.codex}/auth.json}"
[[ -f "$AUTH_SOURCE" ]] || die "Codex auth file not found: $AUTH_SOURCE"
AUTH_SOURCE="$(realpath "$AUTH_SOURCE")"

mkdir -p "$RUN_DIR/reviewers"
GLOBAL_LOCK_DIR="${TMPDIR:-/tmp}/codex-1design-review-${UID}.runner.lock"
LOCK_DIR="$RUN_DIR/reviewers/.runner.lock"

acquire_lock() {
  local lock_dir="$1"
  local owner=""
  if mkdir "$lock_dir" 2>/dev/null; then
    printf '%s\n' "$$" > "$lock_dir/pid"
    return
  fi
  if [[ -f "$lock_dir/pid" ]]; then
    read -r owner < "$lock_dir/pid" || true
  fi
  if [[ "$owner" =~ ^[0-9]+$ ]] && kill -0 "$owner" >/dev/null 2>&1; then
    return 1
  fi
  rm -f "$lock_dir/pid"
  rmdir "$lock_dir" >/dev/null 2>&1 || return 1
  mkdir "$lock_dir" 2>/dev/null || return 1
  printf '%s\n' "$$" > "$lock_dir/pid"
}

if ! acquire_lock "$GLOBAL_LOCK_DIR"; then
  die "another design-review queue is already running; global reviewer limit is three"
fi
if ! acquire_lock "$LOCK_DIR"; then
  rm -f "$GLOBAL_LOCK_DIR/pid"
  rmdir "$GLOBAL_LOCK_DIR" >/dev/null 2>&1 || true
  die "reviewer queue is already running for this run-dir"
fi
pids=()
cleanup_runner() {
  local pid
  for pid in "${pids[@]}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done
  rm -f "$LOCK_DIR/pid" "$GLOBAL_LOCK_DIR/pid"
  rmdir "$LOCK_DIR" >/dev/null 2>&1 || true
  rmdir "$GLOBAL_LOCK_DIR" >/dev/null 2>&1 || true
}
trap cleanup_runner EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

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
  local expected_sha256="$4"
  shift 4
  local images=("$@")
  local clean_home
  local clean_cwd
  local staged_image
  local sandbox_profile
  local staged_output
  local escaped_clean_cwd
  local escaped_clean_home
  local escaped_codex_bin_dir

  clean_home="$(mktemp -d "${TMPDIR:-/tmp}/codex-design-review-home.XXXXXX")"
  clean_cwd="$(mktemp -d "${TMPDIR:-/tmp}/codex-design-review-cwd.XXXXXX")"
  cp "$AUTH_SOURCE" "$clean_home/auth.json"
  chmod 0600 "$clean_home/auth.json"
  staged_image="$clean_cwd/evidence.png"
  staged_output="$clean_cwd/review.md"
  cp "${images[0]}" "$staged_image"
  chmod 0444 "$staged_image"
  sandbox_profile="$clean_cwd/reviewer.sb"
  escaped_clean_cwd="$(realpath "$clean_cwd" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  escaped_clean_home="$(realpath "$clean_home" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  escaped_codex_bin_dir="$(printf '%s' "$CODEX_BIN_DIR" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  printf '%s\n' \
    '(version 1)' \
    '(deny default)' \
    '(import "system.sb")' \
    '(allow process*)' \
    '(allow network*)' \
    '(allow system-socket)' \
    '(allow user-preference-read)' \
    '(allow mach-lookup' \
    '  (global-name "com.apple.SystemConfiguration.configd")' \
    '  (global-name "com.apple.SecurityServer")' \
    '  (global-name "com.apple.CoreServices.coreservicesd"))' \
    '(allow file-read-metadata file-test-existence)' \
    '(allow file-write*' \
    "  (subpath \"$escaped_clean_cwd\")" \
    "  (subpath \"$escaped_clean_home\"))" \
    '(allow file-read* file-test-existence' \
    '  (subpath "/bin")' \
    '  (subpath "/usr")' \
    '  (subpath "/System")' \
    '  (subpath "/Library")' \
    '  (subpath "/private/etc")' \
    "  (subpath \"$escaped_codex_bin_dir\")" \
    "  (subpath \"$escaped_clean_cwd\")" \
    "  (subpath \"$escaped_clean_home\"))" > "$sandbox_profile"
  if [[ -n "${DESIGN_REVIEW_TEST_CONCURRENCY:-}" ]]; then
    local escaped_test_concurrency
    escaped_test_concurrency="$(realpath "$DESIGN_REVIEW_TEST_CONCURRENCY" | sed 's/\\/\\\\/g; s/"/\\"/g')"
    printf '(allow file-write* (subpath "%s"))\n' \
      "$escaped_test_concurrency" >> "$sandbox_profile"
  fi

  local cmd=(
    "$CODEX_BIN" exec
    --ephemeral
    --ignore-user-config
    --ignore-rules
    --skip-git-repo-check
    --sandbox danger-full-access
    --cd "$clean_cwd"
    --model "$MODEL"
    -c "model_reasoning_effort=\"$EFFORT\""
    --output-last-message "$staged_output"
  )
  cmd+=(-i "$staged_image")
  cmd+=(-)

  (
    trap 'rm -rf "$clean_home" "$clean_cwd"' EXIT
    if [[ "$(shasum -a 256 "$staged_image" | awk '{print $1}')" != "$expected_sha256" ]]; then
      printf 'run-clean-design-agent: approved PNG changed before reviewer launch\n' >&2
      exit 2
    fi
    unset OPENAI_API_KEY
    unset CODEX_API_KEY
    unset OPENAI_BASE_URL
    export CODEX_HOME="$clean_home"
    cd "$clean_cwd"
    sandbox-exec -f "$sandbox_profile" "${cmd[@]}" < "$prompt_file"
    cp "$staged_output" "$output_file"
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
  local image_sha256="$5"
  shift 5
  local images=("$@")
  local status_file
  local exit_code=0
  status_file="$STATUS_DIR/$(status_name "$task_id")"

  rm -f "$output"
  set +e
  run_clean_codex "$prompt" "$output" "$log" "$image_sha256" "${images[@]}"
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
        if ! kill -0 "${pids[$index]}" >/dev/null 2>&1; then
          wait "${pids[$index]}" >/dev/null 2>&1 || true
          printf '255\n' > "${status_file}.tmp"
          mv "${status_file}.tmp" "$status_file"
        else
          continue
        fi
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
task_ids=()
logs=()

while IFS=$'\t' read -r task_id prompt output log image_sha256 images_json; do
  images=()
  while IFS= read -r image; do
    [[ -n "$image" ]] && images+=("$image")
  done < <(node -e 'for (const item of JSON.parse(process.argv[1])) console.log(item)' "$images_json")
  [[ "${#images[@]}" == "1" ]] || die "task $task_id must have exactly one image"

  printf '[run-clean-design-agent] start task=%s images=%s\n' "$task_id" "${#images[@]}"
  run_task "$task_id" "$prompt" "$output" "$log" "$image_sha256" "${images[@]}" &
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
    console.log([task.id, task.prompt, task.output, task.log, task.imageSha256, JSON.stringify(task.images)].join("\t"));
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
  task.status =
    exitCode === 0 && fs.existsSync(task.output) && fs.statSync(task.output).size > 0
      ? "done"
      : "failed";
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
