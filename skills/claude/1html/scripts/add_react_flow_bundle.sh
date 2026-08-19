#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <artifact-name-or-directory> [project-root]" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
skill_dir="$(cd "$script_dir/.." && pwd -P)"
bundle_dir="$skill_dir/assets/react-flow"
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
  if [[ ! -d "$project_root" ]]; then
    echo "project root not found: $project_root" >&2
    exit 1
  fi
  project_root="$(cd "$project_root" && pwd -P)"
  artifact_dir="$project_root/_workspace/HTML_artifacts/$target"
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
  check react-flow "$artifact_dir" >/dev/null
mkdir -p "$artifact_dir/lib/licenses" "$artifact_dir/assets"
cp "$bundle_dir/lib/react-flow.vendor.js" "$artifact_dir/lib/react-flow.vendor.js"
cp "$bundle_dir/lib/react-flow.css" "$artifact_dir/lib/react-flow.css"
cp "$bundle_dir/lib/REACT_FLOW_THIRD_PARTY_NOTICES.txt" \
  "$artifact_dir/lib/REACT_FLOW_THIRD_PARTY_NOTICES.txt"
cp "$bundle_dir/lib/licenses/"*.txt "$artifact_dir/lib/licenses/"
cp "$bundle_dir/assets/react-flow-theme.css" \
  "$artifact_dir/assets/react-flow-theme.css"
cp "$bundle_dir/assets/react-flow-init.js" "$artifact_dir/assets/react-flow-init.js"
PYTHONDONTWRITEBYTECODE=1 python3 "$script_dir/wire_addon.py" \
  apply react-flow "$artifact_dir" >/dev/null

printf 'artifact=%s\n' "$artifact_dir"
printf 'reference=%s\n' "$skill_dir/references/react-flow.md"
printf 'wired=active-pages\n'
