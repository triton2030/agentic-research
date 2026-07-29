#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <artifact-name-or-directory> [project-root]" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
bundle_dir="$skill_dir/assets/mermaid"
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

mkdir -p "$artifact_dir/lib/licenses" "$artifact_dir/assets"
cp "$bundle_dir/lib/mermaid.min.js" "$artifact_dir/lib/mermaid.min.js"
cp "$bundle_dir/lib/mermaid-layout-elk.iife.min.js" \
  "$artifact_dir/lib/mermaid-layout-elk.iife.min.js"
cp "$bundle_dir/lib/panzoom.min.js" "$artifact_dir/lib/panzoom.min.js"
cp "$bundle_dir/lib/MERMAID_THIRD_PARTY_NOTICES.txt" \
  "$artifact_dir/lib/MERMAID_THIRD_PARTY_NOTICES.txt"
cp "$bundle_dir/lib/licenses/mermaid.txt" "$artifact_dir/lib/licenses/mermaid.txt"
cp "$bundle_dir/lib/licenses/mermaid-layout-elk.txt" \
  "$artifact_dir/lib/licenses/mermaid-layout-elk.txt"
cp "$bundle_dir/lib/licenses/panzoom.txt" "$artifact_dir/lib/licenses/panzoom.txt"
cp "$bundle_dir/assets/diagram-viewer.css" "$artifact_dir/assets/diagram-viewer.css"
cp "$bundle_dir/assets/diagram-viewer.js" "$artifact_dir/assets/diagram-viewer.js"

printf 'artifact=%s\n' "$artifact_dir"
printf 'reference=%s\n' "$skill_dir/references/mermaid-diagrams.md"
