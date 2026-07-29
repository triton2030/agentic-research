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
metadata_reader="$script_dir/artifact_metadata.py"
artifacts_root="$project_root/_workspace/HTML_artifacts"
catalog_runtime="$artifacts_root/_catalog"
catalog_index="$artifacts_root/index.html"
temporary_index="$artifacts_root/.index.html.tmp.$$"

html_escape() {
  LC_ALL=C sed \
    -e 's/&/\&amp;/g' \
    -e 's/</\&lt;/g' \
    -e 's/>/\&gt;/g' \
    -e 's/"/\&quot;/g' \
    -e "s/'/\&#39;/g"
}

page_word() {
  local count="$1"
  local last_two=$((count % 100))
  local last=$((count % 10))

  if [ "$last_two" -ge 11 ] && [ "$last_two" -le 14 ]; then
    printf 'страниц'
  elif [ "$last" -eq 1 ]; then
    printf 'страница'
  elif [ "$last" -ge 2 ] && [ "$last" -le 4 ]; then
    printf 'страницы'
  else
    printf 'страниц'
  fi
}

file_created_at() {
  local value

  if stat -c '%Y' "$1" >/dev/null 2>&1; then
    value="$(stat -c '%W' "$1")"
    if [ "$value" -gt 0 ]; then
      printf '%s' "$value"
    else
      stat -c '%Y' "$1"
    fi
  else
    value="$(stat -f '%B' "$1")"
    if [ "$value" -gt 0 ]; then
      printf '%s' "$value"
    else
      stat -f '%m' "$1"
    fi
  fi
}

mkdir -p "$catalog_runtime/assets" "$catalog_runtime/lib"
cp "$starter_dir/assets/theme.css" "$catalog_runtime/assets/theme.css"
cp "$catalog_source" "$catalog_runtime/assets/catalog.css"
cp -R "$starter_dir/lib"/. "$catalog_runtime/lib"/

artifact_names=()
artifact_titles=()
artifact_icons=()
artifact_created_epochs=()
artifact_count=0

for artifact_dir in "$artifacts_root"/*; do
  [ -d "$artifact_dir" ] || continue
  [ "$artifact_dir" != "$catalog_runtime" ] || continue
  [ -f "$artifact_dir/index.html" ] || continue

  artifact_name="$(basename "$artifact_dir")"
  display_name="${artifact_name//[-_]/ }"
  artifact_metadata="$(python3 "$metadata_reader" "$artifact_dir/index.html")"
  IFS=$'\t' read -r artifact_title artifact_icon <<< "$artifact_metadata"
  artifact_title="${artifact_title:-$display_name}"
  artifact_created_epoch="$(file_created_at "$artifact_dir")"
  insert_index="$artifact_count"

  while [ "$insert_index" -gt 0 ]; do
    previous_index=$((insert_index - 1))
    [ "$artifact_created_epoch" -le "${artifact_created_epochs[$previous_index]}" ] && break

    artifact_names[$insert_index]="${artifact_names[$previous_index]}"
    artifact_titles[$insert_index]="${artifact_titles[$previous_index]}"
    artifact_icons[$insert_index]="${artifact_icons[$previous_index]}"
    artifact_created_epochs[$insert_index]="${artifact_created_epochs[$previous_index]}"
    insert_index="$previous_index"
  done

  artifact_names[$insert_index]="$artifact_name"
  artifact_titles[$insert_index]="$artifact_title"
  artifact_icons[$insert_index]="$artifact_icon"
  artifact_created_epochs[$insert_index]="$artifact_created_epoch"
  artifact_count=$((artifact_count + 1))
done

artifact_page_word="$(page_word "$artifact_count")"
trap 'rm -f "$temporary_index"' EXIT

{
  printf '%s\n' '<!doctype html>'
  printf '%s\n' '<html lang="ru" data-theme="editorial">'
  printf '%s\n' '<head>'
  printf '%s\n' '  <meta charset="utf-8">'
  printf '%s\n' '  <meta name="viewport" content="width=device-width, initial-scale=1">'
  printf '%s\n' '  <meta name="color-scheme" content="light">'
  printf '%s\n' '  <title>Локальные HTML-артефакты</title>'
  printf '%s\n' '  <link href="_catalog/lib/daisyui.css" rel="stylesheet">'
  printf '%s\n' '  <link href="_catalog/lib/daisyui-themes.css" rel="stylesheet">'
  printf '%s\n' '  <link href="_catalog/assets/theme.css" rel="stylesheet">'
  printf '%s\n' '  <link href="_catalog/assets/catalog.css" rel="stylesheet">'
  printf '%s\n' '  <script src="_catalog/lib/tailwind.js"></script>'
  printf '%s\n' '</head>'
  printf '%s\n' '<body class="catalog-page">'
  printf '%s\n' '  <header class="catalog-topbar">'
  printf '%s\n' '    <a class="catalog-brand" href="index.html">HTML artifacts</a>'
  printf '%s\n' '    <nav class="catalog-nav-scroll" aria-label="Навигация по артефактам">'

  if [ "$artifact_count" -gt 0 ]; then
    for ((artifact_index = 0; artifact_index < artifact_count; artifact_index++)); do
      artifact_name="${artifact_names[$artifact_index]}"
      artifact_title="${artifact_titles[$artifact_index]}"
      escaped_name="$(printf '%s' "$artifact_name" | html_escape)"
      escaped_title="$(printf '%s' "$artifact_title" | html_escape)"
      printf '      <a class="btn btn-ghost btn-sm catalog-nav-link" href="%s/index.html">%s</a>\n' \
        "$escaped_name" "$escaped_title"
    done
  fi

  printf '%s\n' '    </nav>'
  printf '    <span class="badge badge-outline">%s</span>\n' "$artifact_count"
  printf '%s\n' '  </header>'
  printf '%s\n' '  <main class="catalog-shell">'
  printf '%s\n' '    <section class="catalog-hero">'
  printf '%s\n' '      <div>'
  printf '%s\n' '        <p class="artifact-kicker">_workspace · local drafts</p>'
  printf '%s\n' '        <h1 class="catalog-title">Все HTML-артефакты проекта</h1>'
  printf '%s\n' '        <p class="catalog-lead">Одна постоянная точка входа. Каждый черновик остаётся автономной переносимой папкой.</p>'
  printf '%s\n' '      </div>'
  printf '      <span class="badge badge-success">%s %s</span>\n' \
    "$artifact_count" "$artifact_page_word"
  printf '%s\n' '    </section>'

  if [ "$artifact_count" -eq 0 ]; then
    printf '%s\n' '    <article class="card catalog-empty">'
    printf '%s\n' '      <div class="card-body">'
    printf '%s\n' '        <h2 class="card-title">Пока нет артефактов</h2>'
    printf '%s\n' '        <p>Первый созданный bundle автоматически появится здесь.</p>'
    printf '%s\n' '      </div>'
    printf '%s\n' '    </article>'
  else
    printf '%s\n' '    <section class="catalog-grid" aria-label="Все HTML-артефакты">'

    for ((artifact_index = 0; artifact_index < artifact_count; artifact_index++)); do
      artifact_name="${artifact_names[$artifact_index]}"
      artifact_title="${artifact_titles[$artifact_index]}"
      artifact_icon="${artifact_icons[$artifact_index]}"
      artifact_created_epoch="${artifact_created_epochs[$artifact_index]}"
      escaped_name="$(printf '%s' "$artifact_name" | html_escape)"
      escaped_title="$(printf '%s' "$artifact_title" | html_escape)"
      escaped_icon="$(printf '%s' "$artifact_icon" | html_escape)"
      printf '      <a class="card catalog-card" href="%s/index.html">\n' "$escaped_name"
      printf '%s\n' '        <div class="card-body">'
      printf '%s\n' '          <div>'
      printf '%s\n' '            <div class="catalog-card-meta">'
      printf '%s\n' '              <span class="badge badge-outline">HTML</span>'
      printf '              <span class="catalog-card-date" data-created-epoch="%s">сейчас</span>\n' \
        "$artifact_created_epoch"
      printf '%s\n' '            </div>'
      printf '            <h2 class="catalog-card-title mt-5">%s</h2>\n' "$escaped_title"
      printf '%s\n' '          </div>'
      if [ -n "$escaped_icon" ]; then
        printf '          <i class="catalog-card-icon" data-lucide="%s" aria-hidden="true"></i>\n' \
          "$escaped_icon"
      fi
      printf '          <span class="catalog-card-path">%s/index.html →</span>\n' "$escaped_name"
      printf '%s\n' '        </div>'
      printf '%s\n' '      </a>'
    done

  printf '%s\n' '    </section>'
  fi

  printf '%s\n' '  </main>'
  printf '%s\n' '  <script src="_catalog/lib/lucide.min.js"></script>'
  printf '%s\n' '  <script>'
  printf '%s\n' '    lucide.createIcons();'
  printf '%s\n' '    (() => {'
  printf '%s\n' '      const formatter = new Intl.RelativeTimeFormat("ru", { numeric: "auto" });'
  printf '%s\n' '      const units = ['
  printf '%s\n' '        ["year", 31536000],'
  printf '%s\n' '        ["month", 2592000],'
  printf '%s\n' '        ["week", 604800],'
  printf '%s\n' '        ["day", 86400],'
  printf '%s\n' '        ["hour", 3600],'
  printf '%s\n' '        ["minute", 60],'
  printf '%s\n' '        ["second", 1],'
  printf '%s\n' '      ];'
  printf '%s\n' '      const now = Date.now() / 1000;'
  printf '%s\n' '      document.querySelectorAll("[data-created-epoch]").forEach((element) => {'
  printf '%s\n' '        const difference = Number(element.dataset.createdEpoch) - now;'
  printf '%s\n' '        const [unit, seconds] = units.find(([, size]) => Math.abs(difference) >= size) || units.at(-1);'
  printf '%s\n' '        element.textContent = formatter.format(Math.round(difference / seconds), unit);'
  printf '%s\n' '      });'
  printf '%s\n' '    })();'
  printf '%s\n' '  </script>'
  printf '%s\n' '</body>'
  printf '%s\n' '</html>'
} > "$temporary_index"

mv "$temporary_index" "$catalog_index"
trap - EXIT

printf '%s\n' "$catalog_index"
