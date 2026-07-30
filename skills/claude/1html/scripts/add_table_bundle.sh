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

if [[ -d "$target" && -f "$target/index.html" ]]; then
  artifact_dir="$(cd "$target" && pwd)"
else
  artifact_dir="$project_root/_workspace/HTML_artifacts/$target"
fi

if [[ ! -f "$artifact_dir/index.html" ]]; then
  echo "artifact index not found: $artifact_dir/index.html" >&2
  exit 1
fi

mkdir -p "$artifact_dir/assets"
cp "$bundle_dir/assets/artifact-table.js" \
  "$artifact_dir/assets/artifact-table.js"

printf 'artifact=%s\n' "$artifact_dir"
printf 'asset=%s\n' "$artifact_dir/assets/artifact-table.js"
printf 'reference=%s\n' "$skill_dir/references/data-tables.md"
printf '%s\n' 'index-script=<script defer src="assets/artifact-table.js"></script>'
printf '%s\n' 'page-script=<script defer src="../assets/artifact-table.js"></script>'
