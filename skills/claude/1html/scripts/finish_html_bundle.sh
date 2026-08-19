#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s [--legacy] <artifact-name> [project-root]\n' "$0" >&2
  exit 2
}

legacy=()
while [[ "${1:-}" == --* ]]; do
  case "$1" in
    --legacy)
      legacy=(--legacy)
      ;;
    *)
      usage
      ;;
  esac
  shift
done
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
audit_script="$script_dir/audit_html_style.py"
catalog_script="$script_dir/rebuild_html_catalog.sh"
artifacts_root="$project_root/_workspace/HTML_artifacts"
target="$artifacts_root/$artifact_name"

if [ -e "$artifacts_root/_catalog" ] && [ "$target" -ef "$artifacts_root/_catalog" ]; then
  printf 'Error: catalog is not an artifact target: %s\n' "$target" >&2
  exit 2
fi

if [ ! -f "$target/index.html" ]; then
  printf 'Error: artifact index.html not found: %s\n' "$target/index.html" >&2
  exit 1
fi

PYTHONDONTWRITEBYTECODE=1 python3 "$audit_script" \
  --check-bundle "${legacy[@]}" "$target"
"$catalog_script" "$project_root" >/dev/null

printf 'artifact=%s\n' "$target/index.html"
printf 'catalog=%s\n' "$artifacts_root/index.html"
