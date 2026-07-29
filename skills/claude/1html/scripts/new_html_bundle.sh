#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s <artifact-name> [project-root]\n' "$0" >&2
  exit 2
}

[ "$#" -ge 1 ] && [ "$#" -le 2 ] || usage

artifact_name="$1"
project_root="${2:-$PWD}"

case "$artifact_name" in
  ""|"."|".."|*/*)
    printf 'Error: artifact name must be one directory name: %s\n' "$artifact_name" >&2
    exit 2
    ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
starter_dir="$(cd "$script_dir/../assets/starter" && pwd)"
catalog_script="$script_dir/rebuild_html_catalog.sh"
artifacts_root="$project_root/_workspace/HTML_artifacts"
target="$artifacts_root/$artifact_name"

if [ ! -d "$project_root" ]; then
  printf 'Error: project root is not a directory: %s\n' "$project_root" >&2
  exit 1
fi

if [ -e "$target" ]; then
  printf 'Error: artifact already exists: %s\n' "$target" >&2
  exit 1
fi

mkdir -p "$artifacts_root" "$target"
cp -R "$starter_dir"/. "$target"/
"$catalog_script" "$project_root" >/dev/null

printf 'artifact=%s\n' "$target/index.html"
printf 'catalog=%s\n' "$artifacts_root/index.html"
