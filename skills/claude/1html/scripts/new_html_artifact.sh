#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s <artifact-slug> [project-root]\n' "$0" >&2
  exit 2
}

copy_once() {
  local source="$1"
  local target="$2"
  [ -e "$target" ] || cp "$source" "$target"
}

[ "$#" -ge 1 ] && [ "$#" -le 2 ] || usage

artifact_slug="$1"
project_root="${2:-$PWD}"

case "$artifact_slug" in
  ""|"."|".."|"index"|_*|*[!a-z0-9-]*|-*|*-)
    printf 'Error: artifact slug must use lowercase letters, digits and inner hyphens: %s\n' "$artifact_slug" >&2
    exit 2
    ;;
esac

if [ ! -d "$project_root" ]; then
  printf 'Error: project root is not a directory: %s\n' "$project_root" >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
zone_source="$skill_dir/assets/zone"
base_source="$skill_dir/assets/base"
artifacts_root="$project_root/_workspace/HTML_artifacts"
shared_assets="$artifacts_root/assets/shared"
shared_lib="$artifacts_root/lib"
target_html="$artifacts_root/$artifact_slug.html"
target_css="$artifacts_root/assets/$artifact_slug.css"
zone_template_html="$artifacts_root/_template.html"
zone_template_css="$artifacts_root/assets/_template.css"

if [ -e "$target_html" ] || [ -e "$target_css" ]; then
  printf 'Error: artifact already exists: %s\n' "$target_html" >&2
  exit 1
fi

mkdir -p "$shared_assets" "$shared_lib/licenses"

for file in \
  THIRD_PARTY_NOTICES.txt \
  alpine.js \
  daisyui-themes.css \
  daisyui.css \
  lucide.min.js \
  tailwind.js; do
  copy_once "$base_source/lib/$file" "$shared_lib/$file"
done
for license in "$base_source/lib/licenses"/*.txt; do
  copy_once "$license" "$shared_lib/licenses/$(basename "$license")"
done

if [ ! -e "$shared_assets/components.css" ]; then
  cp "$zone_source/components.css" "$shared_assets/components.css"
fi

copy_once "$skill_dir/assets/table/assets/artifact-table.js" \
  "$shared_assets/artifact-table.js"

copy_once "$skill_dir/assets/mermaid/lib/mermaid.min.js" \
  "$shared_lib/mermaid.min.js"
copy_once "$skill_dir/assets/mermaid/lib/mermaid-layout-elk.iife.min.js" \
  "$shared_lib/mermaid-layout-elk.iife.min.js"
copy_once "$skill_dir/assets/mermaid/lib/panzoom.min.js" \
  "$shared_lib/panzoom.min.js"
copy_once "$skill_dir/assets/mermaid/lib/MERMAID_THIRD_PARTY_NOTICES.txt" \
  "$shared_lib/MERMAID_THIRD_PARTY_NOTICES.txt"
for license in "$skill_dir/assets/mermaid/lib/licenses"/*.txt; do
  copy_once "$license" "$shared_lib/licenses/$(basename "$license")"
done
for asset in "$skill_dir/assets/mermaid/assets"/*; do
  copy_once "$asset" "$shared_assets/$(basename "$asset")"
done

copy_once "$skill_dir/assets/echarts/lib/echarts.min.js" \
  "$shared_lib/echarts.min.js"
copy_once "$skill_dir/assets/echarts/lib/LICENSE" "$shared_lib/ECHARTS_LICENSE"
copy_once "$skill_dir/assets/echarts/lib/NOTICE" "$shared_lib/ECHARTS_NOTICE"
copy_once "$skill_dir/assets/echarts/lib/ECHARTS_THIRD_PARTY_NOTICES.txt" \
  "$shared_lib/ECHARTS_THIRD_PARTY_NOTICES.txt"
copy_once "$skill_dir/assets/echarts/lib/licenses/LICENSE-d3" \
  "$shared_lib/licenses/ECHARTS_LICENSE-d3"
copy_once "$skill_dir/assets/echarts/assets/echarts-init.js" \
  "$shared_assets/echarts-init.js"

copy_once "$skill_dir/assets/react-flow/lib/react-flow.vendor.js" \
  "$shared_lib/react-flow.vendor.js"
copy_once "$skill_dir/assets/react-flow/lib/react-flow.css" \
  "$shared_lib/react-flow.css"
copy_once "$skill_dir/assets/react-flow/lib/REACT_FLOW_THIRD_PARTY_NOTICES.txt" \
  "$shared_lib/REACT_FLOW_THIRD_PARTY_NOTICES.txt"
for license in "$skill_dir/assets/react-flow/lib/licenses"/*.txt; do
  copy_once "$license" "$shared_lib/licenses/$(basename "$license")"
done
copy_once "$skill_dir/assets/react-flow/assets/react-flow-theme.css" \
  "$shared_assets/react-flow-theme.css"
copy_once "$skill_dir/assets/react-flow/assets/react-flow-init.js" \
  "$shared_assets/react-flow-init.js"

cp "$skill_dir/assets/catalog/theme.css" "$shared_assets/catalog-theme.css"
cp "$skill_dir/assets/catalog/catalog.css" "$shared_assets/catalog.css"

if [ ! -e "$artifacts_root/AGENTS.md" ]; then
  cp "$zone_source/AGENTS.md" "$artifacts_root/AGENTS.md"
fi
if [ ! -e "$artifacts_root/CLAUDE.md" ]; then
  cp "$zone_source/CLAUDE.md" "$artifacts_root/CLAUDE.md"
fi
if [ ! -e "$artifacts_root/COMPONENTS.md" ]; then
  cp "$zone_source/COMPONENTS.md" "$artifacts_root/COMPONENTS.md"
fi
if [ ! -e "$zone_template_html" ]; then
  cp "$zone_source/page.template.html" "$zone_template_html"
fi
if [ ! -e "$zone_template_css" ]; then
  cp "$zone_source/page.template.css" "$zone_template_css"
fi

sed "s/__ARTIFACT_SLUG__/$artifact_slug/g" \
  "$zone_template_html" >"$target_html"
cp "$zone_template_css" "$target_css"

"$script_dir/rebuild_html_catalog.sh" "$project_root" >/dev/null

printf 'artifact=%s\n' "$target_html"
printf 'catalog=%s\n' "$artifacts_root/index.html"
