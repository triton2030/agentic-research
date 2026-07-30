#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s [project-root]\n' "$0" >&2
  exit 2
}

[ "$#" -le 1 ] || usage

project_root="${1:-$PWD}"

if [ ! -d "$project_root" ]; then
  printf 'Error: project root is not a directory: %s\n' "$project_root" >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
starter_dir="$skill_dir/assets/starter"
catalog_source="$skill_dir/assets/catalog/catalog.css"
catalog_builder="$script_dir/build_catalog.py"
artifacts_root="$project_root/_workspace/HTML_artifacts"
catalog_runtime="$artifacts_root/_catalog"
catalog_index="$artifacts_root/index.html"
temporary_index="$artifacts_root/.index.html.tmp.$$"

mkdir -p "$catalog_runtime/assets" "$catalog_runtime/lib"
cp "$starter_dir/assets/theme.css" "$catalog_runtime/assets/theme.css"
cp "$catalog_source" "$catalog_runtime/assets/catalog.css"
cp -R "$starter_dir/lib"/. "$catalog_runtime/lib"/

trap 'rm -f "$temporary_index"' EXIT
PYTHONDONTWRITEBYTECODE=1 python3 "$catalog_builder" "$artifacts_root" "$temporary_index"
mv "$temporary_index" "$catalog_index"
trap - EXIT

printf '%s\n' "$catalog_index"
