#!/usr/bin/env bash
# ensure-ops.sh — creates and verifies the universal `_ops` project contour.
#
# Default: safe bootstrap + sync (`--init --sync`).
# Modes:
#   --init     create missing owner files and the minimal bootstrap plan
#   --sync     materialize `_ops/plans/phase-NN-<slug>/done/` from PROJECT-PLAN
#   --check    report drift only; write nothing; exit non-zero on drift
#   --dry-run  show what would change; write nothing
#
# Contract:
#   - Creates only `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`,
#     `_ops/learnings.md`, and `_ops/plans/phase-NN-<slug>/done/`.
#   - Does not create task files.
#   - Does not create `_ops/inbox`, numbered docs, side docs, or trackers.
#   - Warns about root `ops/` / `plans/` legacy surfaces, never deletes them.

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

OPS="_ops"
PLAN="$OPS/PROJECT-PLAN.md"
INTERVIEW="$OPS/INTERVIEW.md"
LEARNINGS="$OPS/learnings.md"
PLANS="$OPS/plans"

DO_INIT=0
DO_SYNC=0
CHECK=0
DRY_RUN=0

usage() {
  cat <<'EOF'
usage: ensure-ops.sh [--init] [--sync] [--check] [--dry-run]

No args is equivalent to: --init --sync
EOF
}

if [[ $# -eq 0 ]]; then
  DO_INIT=1
  DO_SYNC=1
fi

for arg in "$@"; do
  case "$arg" in
    --init) DO_INIT=1 ;;
    --sync) DO_SYNC=1 ;;
    --check) CHECK=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ensure-ops: unknown arg: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ $CHECK -eq 1 ]]; then
  DO_INIT=0
  DO_SYNC=0
fi

if [[ $DRY_RUN -eq 1 && $DO_INIT -eq 0 && $DO_SYNC -eq 0 && $CHECK -eq 0 ]]; then
  DO_INIT=1
  DO_SYNC=1
fi

WRITE=1
if [[ $CHECK -eq 1 || $DRY_RUN -eq 1 ]]; then
  WRITE=0
fi

DRIFT=0

say_create() {
  local path="$1"
  if [[ $WRITE -eq 1 ]]; then
    echo "+ $path"
  else
    echo "would create: $path"
  fi
}

say_remove() {
  local path="$1"
  if [[ $WRITE -eq 1 ]]; then
    echo "- $path"
  else
    echo "would remove: $path"
  fi
}

mark_drift() {
  DRIFT=1
}

write_if_missing() {
  local path="$1"
  local content="$2"
  if [[ -e "$path" ]]; then
    return 0
  fi
  mark_drift
  say_create "$path"
  if [[ $WRITE -eq 1 ]]; then
    mkdir -p "$(dirname "$path")"
    printf "%s" "$content" > "$path"
  fi
}

mkdir_if_missing() {
  local path="$1"
  if [[ -d "$path" ]]; then
    return 0
  fi
  mark_drift
  say_create "$path"
  if [[ $WRITE -eq 1 ]]; then
    mkdir -p "$path"
  fi
}

warn_legacy_surfaces() {
  if [[ -d "ops" ]]; then
    echo "! legacy surface detected: ops/ (read as evidence only; canonical owner is _ops/)" >&2
  fi
  if [[ -d "plans" ]]; then
    echo "! legacy surface detected: plans/ (read as evidence only; canonical owner is _ops/)" >&2
  fi
}

bootstrap_plan_content() {
  cat <<'EOF'
## Goal
Сформировать ясную траекторию проекта.

## Approach & Why
Сначала собираем горячий `_ops`-контур, чтобы стратегия, предпочтения, learnings и task-файлы не расходились по разным местам. Дальше `main-strategy` уточняет Goal и Stages под реальный проект.

## Stages

### 1. Сформировать траекторию проекта [~]
- Что делаем: уточняем Goal, подход и крупные фазы проекта.
- Зачем сейчас: без этой карты `system-architect` и `task-planner` будут фабриковать контекст.
EOF
}

interview_content() {
  cat <<'EOF'
# Interview

_Пока durable preferences не зафиксированы._
EOF
}

learnings_content() {
  cat <<'EOF'
# Learnings

_Пока дельт реальность-vs-план/интервью нет._
EOF
}

parse_phase_list() {
  python3 - "$@" <<'PY'
import re
import sys

if len(sys.argv) > 1:
    text = open(sys.argv[1], encoding="utf-8").read()
else:
    text = sys.stdin.read()
m = re.search(r"^##\s+Stages\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
if not m:
    sys.exit(0)

body = m.group(1)
for mm in re.finditer(r"^###\s+(\d+)\.?\s+(.+?)\s*$", body, re.M):
    num = int(mm.group(1))
    name = mm.group(2)
    name = re.sub(r"\s*\[[ ~x]\]\s*$", "", name).strip()
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", "", slug, flags=re.U)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    if slug:
        print(f"phase-{num:02d}-{slug}")
PY
}

expected_phase_list() {
  if [[ ! -f "$PLAN" ]]; then
    return 1
  fi
  parse_phase_list "$PLAN"
}

is_effectively_empty_phase() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    return 0
  fi

  local entry base
  shopt -s nullglob dotglob
  for entry in "$dir"/*; do
    base="$(basename "$entry")"
    if [[ "$base" == "done" && -d "$entry" ]]; then
      if [[ -n "$(ls -A "$entry")" ]]; then
        return 1
      fi
      continue
    fi
    return 1
  done
  return 0
}

contains_expected() {
  local needle="$1"
  local item
  while IFS= read -r item; do
    [[ -z "$item" ]] && continue
    if [[ "$item" == "$needle" ]]; then
      return 0
    fi
  done <<< "$EXPECTED_LIST"
  return 1
}

warn_legacy_surfaces

if [[ $DO_INIT -eq 1 ]]; then
  mkdir_if_missing "$OPS"
  write_if_missing "$PLAN" "$(bootstrap_plan_content)"
  write_if_missing "$INTERVIEW" "$(interview_content)"
  write_if_missing "$LEARNINGS" "$(learnings_content)"
fi

if [[ $CHECK -eq 1 ]]; then
  for required in "$PLAN" "$INTERVIEW" "$LEARNINGS"; do
    if [[ ! -f "$required" ]]; then
      echo "! missing: $required" >&2
      mark_drift
    fi
  done
  DO_SYNC=1
fi

if [[ $DO_SYNC -eq 1 ]]; then
  if [[ ! -f "$PLAN" ]]; then
    if [[ $DO_INIT -eq 1 && $WRITE -eq 0 ]]; then
      EXPECTED_LIST="$(bootstrap_plan_content | parse_phase_list || true)"
    else
      echo "ensure-ops: $PLAN not found; run --init first" >&2
      mark_drift
      exit 1
    fi
  else
    EXPECTED_LIST="$(expected_phase_list || true)"
  fi
  if [[ -z "$EXPECTED_LIST" ]]; then
    echo "ensure-ops: no Stages found in $PLAN" >&2
    mark_drift
  else
    mkdir_if_missing "$PLANS"

    count=0
    while IFS= read -r phase; do
      [[ -z "$phase" ]] && continue
      mkdir_if_missing "$PLANS/$phase"
      mkdir_if_missing "$PLANS/$phase/done"
      count=$((count + 1))
    done <<< "$EXPECTED_LIST"

    shopt -s nullglob
    for dir in "$PLANS"/*/; do
      [[ -d "$dir" ]] || continue
      name="$(basename "$dir")"
      if contains_expected "$name"; then
        continue
      fi
      mark_drift
      if is_effectively_empty_phase "$dir"; then
        say_remove "$PLANS/$name"
        if [[ $WRITE -eq 1 ]]; then
          [[ -d "$dir/done" ]] && rmdir "$dir/done" 2>/dev/null || true
          rmdir "$dir"
        fi
      else
        echo "! $PLANS/$name contains files; Stage is absent from plan, remove manually if trajectory changed" >&2
      fi
    done

    echo "ensure-ops: synced $count phase folders."
  fi
fi

if [[ $CHECK -eq 1 || $DRY_RUN -eq 1 ]]; then
  if [[ $DRIFT -eq 1 ]]; then
    echo "ensure-ops: drift detected."
    exit 1
  fi
  echo "ensure-ops: no drift."
  exit 0
fi

echo "ensure-ops: ready."
