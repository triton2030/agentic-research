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
  ""|"."|".."|"_catalog"|*/*)
    printf 'Error: artifact name must be one directory name: %s\n' "$artifact_name" >&2
    exit 2
    ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
scaffold_dir="$(cd "$script_dir/../assets/scaffold" && pwd)"
catalog_script="$script_dir/rebuild_html_catalog.sh"
finish_script="$script_dir/finish_html_bundle.sh"
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

created_target=0
rollback_created_target() {
  status="$1"
  trap - ERR INT TERM
  if [ "$created_target" -eq 1 ] \
    && [ "$(dirname "$target")" = "$artifacts_root" ]; then
    rm -rf -- "$target"
  fi
  exit "$status"
}
trap 'rollback_created_target $?' ERR
trap 'rollback_created_target 130' INT
trap 'rollback_created_target 143' TERM

mkdir -p "$artifacts_root" "$target"
created_target=1
cp -R "$scaffold_dir"/. "$target"/
"$catalog_script" "$project_root" >/dev/null
trap - ERR INT TERM

printf 'artifact=%s\n' "$target/index.html"
printf 'catalog=%s\n' "$artifacts_root/index.html"
printf 'finish-command='
printf '%q ' "$finish_script" "$artifact_name" "$project_root"
printf '\n'
