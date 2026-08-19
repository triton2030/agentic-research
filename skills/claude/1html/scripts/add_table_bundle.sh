#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <artifact-name-or-directory> [project-root]" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
bundle_dir="$skill_dir/assets/table"
target="$1"
project_root="${2:-$PWD}"

if [[ "$target" == */* ]]; then
  if [[ ! -d "$target" ]]; then
    echo "artifact directory not found: $target" >&2
    exit 1
  fi
  artifact_dir="$(cd "$target" && pwd -P)"
else
  case "$target" in
    ""|"."|".."|"_catalog")
      echo "invalid artifact slug: $target" >&2
      exit 2
      ;;
  esac
  artifact_dir="$project_root/_workspace/HTML_artifacts/$target"
fi

if [[ "$(basename "$artifact_dir")" == "_catalog" ]]; then
  echo "catalog is not an artifact target: $artifact_dir" >&2
  exit 2
fi

if [[ ! -f "$artifact_dir/index.html" ]]; then
  echo "artifact index not found: $artifact_dir/index.html" >&2
  exit 1
fi
artifact_dir="$(cd "$artifact_dir" && pwd -P)"
if [[ "$(basename "$artifact_dir")" == "_catalog" ]]; then
  echo "catalog is not an artifact target: $artifact_dir" >&2
  exit 2
fi

PYTHONDONTWRITEBYTECODE=1 python3 "$script_dir/wire_addon.py" \
  check table "$artifact_dir" >/dev/null
mkdir -p "$artifact_dir/assets"
cp "$bundle_dir/assets/artifact-table.js" \
  "$artifact_dir/assets/artifact-table.js"
PYTHONDONTWRITEBYTECODE=1 python3 "$script_dir/wire_addon.py" \
  apply table "$artifact_dir" >/dev/null

printf 'artifact=%s\n' "$artifact_dir"
printf 'asset=%s\n' "$artifact_dir/assets/artifact-table.js"
printf 'reference=%s\n' "$skill_dir/references/data-tables.md"
printf 'wired=all-live-pages\n'
