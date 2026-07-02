#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run-clean-design-agent.sh --run-dir DIR --questions FILE [--url URL]

Runs a clean Codex terminal design reviewer:
  - temporary CODEX_HOME
  - only ~/.codex/auth.json linked
  - OPENAI_API_KEY / CODEX_API_KEY / OPENAI_BASE_URL unset
  - neutral temporary cwd, not the reviewed project
  - --ignore-user-config --ignore-rules --ephemeral
  - screenshots attached with codex exec -i

Options:
  --run-dir DIR       Existing design-review run directory.
  --questions FILE    Markdown questions file.
  --url URL           Captured page URL, added to prompt.
  --model NAME        Codex model. Default: gpt-5.5.
  --effort LEVEL      model_reasoning_effort. Default: high.
  --max-images N      Max PNG files to attach. Default: 28.
  --out FILE          Output markdown. Default: <run-dir>/design-review.md.
  --dry-run           Write prompt and selected image list, but do not call Codex.
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
MAX_IMAGES="28"
OUT_FILE=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-dir) RUN_DIR="${2:-}"; shift 2 ;;
    --questions) QUESTIONS="${2:-}"; shift 2 ;;
    --url) URL="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --effort) EFFORT="${2:-}"; shift 2 ;;
    --max-images) MAX_IMAGES="${2:-}"; shift 2 ;;
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
[[ "$MAX_IMAGES" =~ ^[0-9]+$ ]] || die "--max-images must be a positive integer"
[[ "$MAX_IMAGES" -gt 0 ]] || die "--max-images must be > 0"
command -v codex >/dev/null 2>&1 || die "codex CLI not found"

RUN_DIR="$(cd "$RUN_DIR" && pwd)"
QUESTIONS="$(cd "$(dirname "$QUESTIONS")" && pwd)/$(basename "$QUESTIONS")"
OUT_FILE="${OUT_FILE:-$RUN_DIR/design-review.md}"
PROMPT_FILE="$RUN_DIR/agent-prompt.md"
IMAGE_LIST_FILE="$RUN_DIR/attached-images.txt"
MANIFEST_FILE="$RUN_DIR/manifest.json"
SCREENSHOT_LEDGER="$RUN_DIR/screenshots.md"

ALL_IMAGES=()
while IFS= read -r image; do
  ALL_IMAGES+=("$image")
done < <(find "$RUN_DIR" -type f -name '*.png' | sort)
if [[ "${#ALL_IMAGES[@]}" -eq 0 ]]; then
  die "no PNG screenshots found under $RUN_DIR"
fi

SELECTED_IMAGES=()
for image in "${ALL_IMAGES[@]}"; do
  SELECTED_IMAGES+=("$image")
  [[ "${#SELECTED_IMAGES[@]}" -ge "$MAX_IMAGES" ]] && break
done

printf '%s\n' "${SELECTED_IMAGES[@]}" > "$IMAGE_LIST_FILE"

manifest_text="{}"
if [[ -f "$MANIFEST_FILE" ]]; then
  manifest_text="$(cat "$MANIFEST_FILE")"
fi

ledger_text="screenshots.md not found"
if [[ -f "$SCREENSHOT_LEDGER" ]]; then
  ledger_text="$(cat "$SCREENSHOT_LEDGER")"
fi

cat > "$PROMPT_FILE" <<EOF
You are a clean visual design review agent.

You are intentionally running from a neutral cwd. Do not search for or follow
project AGENTS.md, local skills, source code, git history, or chat history.
Use only:

1. The screenshots attached to this Codex exec run.
2. The screenshot manifest and ledger pasted below.
3. The Markdown question contract pasted below.

Task:
Answer the questions in the same Markdown structure. Be direct and critical.
Ground claims in screenshot filenames, manifest ids, viewport names, or scroll
positions. If evidence is missing, say it is not checkable from screenshots.

Do not write code. Do not propose implementation details unless the design fix
requires naming the type of change. Do not praise generally. Findings first.

Captured URL: ${URL:-"(not provided)"}
Run directory: $RUN_DIR
Attached images: ${#SELECTED_IMAGES[@]} of ${#ALL_IMAGES[@]}
Output language: Russian.

<attached_images>
$(printf '%s\n' "${SELECTED_IMAGES[@]}")
</attached_images>

<questions_markdown>
$(cat "$QUESTIONS")
</questions_markdown>

<screenshot_ledger>
$ledger_text
</screenshot_ledger>

<manifest_json>
$manifest_text
</manifest_json>
EOF

if [[ "$DRY_RUN" == "1" ]]; then
  printf '[run-clean-design-agent] dry-run prompt: %s\n' "$PROMPT_FILE"
  printf '[run-clean-design-agent] selected images: %s\n' "$IMAGE_LIST_FILE"
  exit 0
fi

AUTH_SOURCE="${CODEX_AUTH_JSON:-$HOME/.codex/auth.json}"
[[ -f "$AUTH_SOURCE" ]] || die "Codex auth file not found: $AUTH_SOURCE"

CLEAN_HOME="$(mktemp -d "${TMPDIR:-/tmp}/codex-design-review-home.XXXXXX")"
CLEAN_CWD="$(mktemp -d "${TMPDIR:-/tmp}/codex-design-review-cwd.XXXXXX")"
cleanup() {
  rm -rf "$CLEAN_HOME" "$CLEAN_CWD"
}
trap cleanup EXIT

ln -s "$AUTH_SOURCE" "$CLEAN_HOME/auth.json"

cmd=(
  codex exec
  --ephemeral
  --ignore-user-config
  --ignore-rules
  --skip-git-repo-check
  --sandbox read-only
  --cd "$CLEAN_CWD"
  --add-dir "$RUN_DIR"
  --model "$MODEL"
  -c "model_reasoning_effort=\"$EFFORT\""
  --output-last-message "$OUT_FILE"
)

for image in "${SELECTED_IMAGES[@]}"; do
  cmd+=(-i "$image")
done
cmd+=(-)

(
  unset OPENAI_API_KEY
  unset CODEX_API_KEY
  unset OPENAI_BASE_URL
  export CODEX_HOME="$CLEAN_HOME"
  "${cmd[@]}" < "$PROMPT_FILE"
)

printf '[run-clean-design-agent] review written: %s\n' "$OUT_FILE"
