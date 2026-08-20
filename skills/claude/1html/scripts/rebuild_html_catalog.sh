#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s [project-root]\n' "$0" >&2
  exit 2
}

copy_once() {
  local source="$1"
  local target="$2"
  [ -e "$target" ] || cp "$source" "$target"
}

[ "$#" -le 1 ] || usage

project_root="${1:-$PWD}"

if [ ! -d "$project_root" ]; then
  printf 'Error: project root is not a directory: %s\n' "$project_root" >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
base_lib="$skill_dir/assets/base/lib"
catalog_theme="$skill_dir/assets/catalog/theme.css"
catalog_source="$skill_dir/assets/catalog/catalog.css"
catalog_builder="$script_dir/build_catalog.py"
artifacts_root="$project_root/_workspace/HTML_artifacts"
shared_assets="$artifacts_root/assets/shared"
shared_lib="$artifacts_root/lib"
catalog_index="$artifacts_root/index.html"
temporary_index="$artifacts_root/.index.html.tmp.$$"

mkdir -p "$shared_assets" "$shared_lib/licenses"
cp "$catalog_theme" "$shared_assets/catalog-theme.css"
cp "$catalog_source" "$shared_assets/catalog.css"
for file in \
  THIRD_PARTY_NOTICES.txt \
  alpine.js \
  daisyui-themes.css \
  daisyui.css \
  lucide.min.js \
  tailwind.js; do
  copy_once "$base_lib/$file" "$shared_lib/$file"
done
for license in "$base_lib/licenses"/*.txt; do
  copy_once "$license" "$shared_lib/licenses/$(basename "$license")"
done

trap 'rm -f "$temporary_index"' EXIT
PYTHONDONTWRITEBYTECODE=1 python3 "$catalog_builder" "$artifacts_root" "$temporary_index"
mv "$temporary_index" "$catalog_index"
trap - EXIT

printf '%s\n' "$catalog_index"
