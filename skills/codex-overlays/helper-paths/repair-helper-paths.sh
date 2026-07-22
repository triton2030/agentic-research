#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  repair-helper-paths.sh --root CODEX_SKILLS_ROOT --check
  repair-helper-paths.sh --root CODEX_SKILLS_ROOT --apply

Exit codes:
  0  installed files match the repaired form
  1  --check found known pre-fix forms
  2  invalid invocation, root, or runtime dependency
  3  a guarded file or text block has unknown drift
USAGE
}

root=""
mode=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -ge 2 && -z "$root" ]] || { usage >&2; exit 2; }
      root="$2"
      shift 2
      ;;
    --check|--apply)
      [[ -z "$mode" ]] || { usage >&2; exit 2; }
      mode="$1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
done

[[ -n "$root" && -n "$mode" ]] || { usage >&2; exit 2; }
[[ -d "$root" ]] || { printf 'helper-paths: skills root not found: %s\n' "$root" >&2; exit 2; }
command -v python3 >/dev/null 2>&1 || {
  printf 'helper-paths: python3 is required\n' >&2
  exit 2
}

root="$(cd "$root" && pwd -P)"

python3 - "$mode" "$root" <<'PY'
from __future__ import annotations

import os
import stat
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Repair:
    relative_path: str
    old: str
    new: str
    occurrences: int


MODE, ROOT_ARG = sys.argv[1:]
ROOT = Path(ROOT_ARG)
CODEX_EXPR = "${CODEX_HOME:-$HOME/.codex}"


def impeccable_repair(relative_path: str, helper: str, occurrences: int) -> Repair:
    old = f"node .agents/skills/1impeccable/scripts/{helper}"
    new = f'node "{CODEX_EXPR}/skills/1impeccable/scripts/{helper}"'
    return Repair(relative_path, old, new, occurrences)


repairs = [
    impeccable_repair("1impeccable/SKILL.md", "load-context.mjs", 1),
    impeccable_repair("1impeccable/SKILL.md", "pin.mjs", 1),
    impeccable_repair("1impeccable/reference/teach.md", "load-context.mjs", 2),
    impeccable_repair("1impeccable/reference/document.md", "load-context.mjs", 2),
    impeccable_repair("1impeccable/reference/live.md", "live.mjs", 1),
    impeccable_repair("1impeccable/reference/live.md", "live-poll.mjs", 3),
    impeccable_repair("1impeccable/reference/live.md", "live-wrap.mjs", 1),
    impeccable_repair("1impeccable/reference/live.md", "live-server.mjs", 1),
    impeccable_repair("1impeccable/reference/live.md", "detect-csp.mjs", 1),
    Repair(
        "1python-dev/SKILL.md",
        "`scripts/python_quality_gate.sh <repo>`",
        f'`"{CODEX_EXPR}/skills/1python-dev/scripts/python_quality_gate.sh" <repo>`',
        2,
    ),
    Repair(
        "1diagnosing-bugs/SKILL.md",
        "10. **HITL bash script.** Last resort. If a human must click, drive _them_ with `scripts/hitl-loop.template.sh` so the loop is still structured. Captured output feeds back to you.",
        f'''10. **HITL bash script.** Last resort. If a human must click, copy the bundled
    template into the project, then edit and run the local copy so the loop is
    still structured:

    ```bash
    cp "{CODEX_EXPR}/skills/1diagnosing-bugs/scripts/hitl-loop.template.sh" ./hitl-loop.sh
    chmod +x ./hitl-loop.sh
    ```

    Captured output feeds back to you. Keep project-specific steps only in
    `./hitl-loop.sh`; do not edit the global template.''',
        1,
    ),
    Repair(
        "1diagnosing-bugs/SKILL.md",
        "- [ ] **Agent-runnable** — you can run it unattended; a human in the loop only via `scripts/hitl-loop.template.sh`.",
        """- [ ] **Agent-runnable** — you can run it unattended; a human in the loop only
  via a project-local `./hitl-loop.sh` copied from the bundled template above.""",
        1,
    ),
]

by_path: dict[str, list[Repair]] = defaultdict(list)
for repair in repairs:
    by_path[repair.relative_path].append(repair)

texts: dict[str, str] = {}
states: dict[Repair, str] = {}
errors: list[str] = []

for relative_path, file_repairs in by_path.items():
    path = ROOT / relative_path
    if not path.is_file():
        errors.append(f"missing file: {relative_path}")
        continue

    text = path.read_text(encoding="utf-8")
    texts[relative_path] = text

    for repair in file_repairs:
        old_count = text.count(repair.old)
        new_count = text.count(repair.new)
        expected = repair.occurrences
        if old_count == expected and new_count == 0:
            states[repair] = "old"
        elif old_count == 0 and new_count == expected:
            states[repair] = "new"
        else:
            errors.append(
                f"drift: {relative_path}: expected old={expected},new=0 or "
                f"old=0,new={expected}; found old={old_count},new={new_count}"
            )

if errors:
    for error in errors:
        print(f"helper-paths: {error}", file=sys.stderr)
    raise SystemExit(3)

old_repairs = [repair for repair, state in states.items() if state == "old"]

if MODE == "--check":
    if old_repairs:
        affected = sorted({repair.relative_path for repair in old_repairs})
        for relative_path in affected:
            print(f"NEEDS_APPLY {relative_path}")
        raise SystemExit(1)
    print(f"OK {len(by_path)} files repaired")
    raise SystemExit(0)

updated_texts = dict(texts)
for repair in old_repairs:
    current = updated_texts[repair.relative_path]
    replaced = current.replace(repair.old, repair.new)
    if replaced == current:
        print(
            f"helper-paths: internal replacement failure: {repair.relative_path}",
            file=sys.stderr,
        )
        raise SystemExit(3)
    updated_texts[repair.relative_path] = replaced

changed_paths: list[str] = []
for relative_path, updated in updated_texts.items():
    original = texts[relative_path]
    if updated == original:
        continue

    path = ROOT / relative_path
    original_mode = stat.S_IMODE(path.stat().st_mode)
    path.write_text(updated, encoding="utf-8")
    os.chmod(path, original_mode)
    if stat.S_IMODE(path.stat().st_mode) != original_mode:
        print(f"helper-paths: mode changed unexpectedly: {relative_path}", file=sys.stderr)
        raise SystemExit(3)
    changed_paths.append(relative_path)

for relative_path in changed_paths:
    print(f"APPLIED {relative_path}")
print(f"OK {len(by_path)} files repaired")
PY
