#!/usr/bin/env bash
set -euo pipefail

export PYTHONDONTWRITEBYTECODE=1

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
scaffold_dir="$skill_dir/assets/scaffold"
audit_script="$script_dir/audit_html_style.py"
tmp_root="$(mktemp -d /tmp/1html-contract.XXXXXX)"
pass_count=0
trap 'rm -rf -- "$tmp_root"' EXIT

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

pass() {
  pass_count=$((pass_count + 1))
}

expect_pass() {
  label="$1"
  shift
  if ! "$@" >"$tmp_root/output" 2>&1; then
    cat "$tmp_root/output" >&2
    fail "$label"
  fi
  pass
}

expect_fail() {
  label="$1"
  needle="$2"
  shift 2
  if "$@" >"$tmp_root/output" 2>&1; then
    cat "$tmp_root/output" >&2
    fail "$label unexpectedly passed"
  fi
  if ! grep -Fq "$needle" "$tmp_root/output"; then
    cat "$tmp_root/output" >&2
    fail "$label did not report $needle"
  fi
  pass
}

audit_bundle() {
  python3 "$audit_script" --check-bundle "$1"
}

audit_legacy() {
  python3 "$audit_script" --check-bundle --legacy "$1"
}

make_project() {
  name="$1"
  project="$tmp_root/$name"
  mkdir -p "$project"
  cp -R "$scaffold_dir"/. "$project"/
  printf '%s\n' "$project"
}

write_narrative() {
  target="$1"
  cat >"$target/index.html" <<'HTML'
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self' data: blob:; connect-src 'none'; font-src 'self' data:; frame-src 'self'; img-src 'self' data: blob:; media-src 'self' data: blob:; object-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; worker-src 'self' blob:">
  <title>Свободный отчёт</title>
  <link href="assets/local.css" rel="stylesheet">
</head>
<body>
  <main class="essay">
    <h1>Короткий ответ</h1>
    <article class="custom-card"><p>Разметка и ритм принадлежат артефакту.</p></article>
  </main>
</body>
</html>
HTML
  cat >"$target/assets/local.css" <<'CSS'
:root { --color-primary: rebeccapurple; --radius-box: 0; }
body { margin: 0; font-family: Georgia, serif; }
.custom-card { padding: 3rem; border-radius: 0; background: #fff4cc; }
.card, .navbar { border-radius: 0; }
CSS
}

write_dashboard() {
  target="$1"
  cat >"$target/index.html" <<'HTML'
<!doctype html>
<html lang="ru" data-theme="night-lab">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self' data: blob:; connect-src 'none'; font-src 'self' data:; frame-src 'self'; img-src 'self' data: blob:; media-src 'self' data: blob:; object-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; worker-src 'self' blob:">
  <meta name="artifact-title" content="Экспериментальная панель">
  <title>Панель</title>
  <style>
    body { margin: 0; background: #090b10; color: #e7fbff; }
    main { min-height: 100vh; display: grid; place-items: center; }
  </style>
</head>
<body>
  <main aria-label="Экспериментальная панель">
    <canvas width="800" height="450"></canvas>
  </main>
</body>
</html>
HTML
}

write_react_flow_page() {
  target="$1"
  cat >"$target/index.html" <<'HTML'
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self' data: blob:; connect-src 'none'; font-src 'self' data:; frame-src 'self'; img-src 'self' data: blob:; media-src 'self' data: blob:; object-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; worker-src 'self' blob:">
  <title>Поток заказа</title>
  <link href="assets/local.css" rel="stylesheet">
</head>
<body>
  <main>
    <h1>Поток заказа</h1>
    <p>Вход проходит проверку и переходит в работу.</p>
    <template id="node-intake">
      <article><h2>Вход</h2><details><summary>Поля</summary><p>Состав и срок.</p></details></article>
    </template>
    <div data-react-flow="order-flow" aria-label="Поток данных заказа"></div>
    <script type="application/json" id="order-flow">
    {
      "nodes": [
        {"id":"intake","template":"node-intake","position":{"x":0,"y":0}},
        {"id":"work","label":"Работа","position":{"x":520,"y":40}}
      ],
      "edges": [
        {"id":"intake-work","source":"intake","target":"work","label":"проверено","type":"dataFlow"}
      ]
    }
    </script>
  </main>
</body>
</html>
HTML
}

write_echarts_page() {
  target="$1"
  cat >"$target/index.html" <<'HTML'
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self' data: blob:; connect-src 'none'; font-src 'self' data:; frame-src 'self'; img-src 'self' data: blob:; media-src 'self' data: blob:; object-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; worker-src 'self' blob:">
  <meta name="artifact-title" content="Продажи по каналу">
  <title>Продажи по каналу</title>
  <link href="assets/local.css" rel="stylesheet">
</head>
<body>
  <main>
    <h1>Продажи по каналу</h1>
    <figure>
      <div data-echart="sales-option" aria-labelledby="sales-summary" style="height: 24rem"></div>
      <figcaption id="sales-summary">Розница лидирует: 82 заказа.</figcaption>
    </figure>
    <script type="application/json" id="sales-option">
    {
      "xAxis": {"type":"value"},
      "yAxis": {"type":"category","data":["Сайт","Розница"]},
      "series": [{"type":"bar","data":[44,82]}]
    }
    </script>
  </main>
</body>
</html>
HTML
}

narrative="$(make_project narrative)"
write_narrative "$narrative"
expect_pass "independent narrative design" audit_bundle "$narrative"

dashboard="$(make_project dashboard)"
write_dashboard "$dashboard"
expect_pass "independent fullscreen dashboard" audit_bundle "$dashboard"

if rg -q 'data-theme|artifact-(shell|project|hero|card|rail|footer)|\bcard\b|theme\.css|project\.js|pages\.js' \
  "$scaffold_dir/index.html"; then
  fail "blank scaffold contains visual composition"
fi
pass

if find "$scaffold_dir" -type f -name '*template*' -o -name '_template.html' | grep -q .; then
  fail "scaffold still ships a page template"
fi
pass

if [[ -e "$skill_dir/assets/starter" ]]; then
  fail "legacy starter directory still exists"
fi
pass

if rg -q -- '--allow-theme-change' "$script_dir/finish_html_bundle.sh"; then
  fail "visual exception flag still exists"
fi
pass

untouched="$(make_project untouched)"
expect_fail "untouched scaffold" "[PLACEHOLDER]" audit_bundle "$untouched"

empty="$(make_project empty)"
cat >"$empty/index.html" <<'HTML'
<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="artifact-title" content="Пусто"><title>Пусто</title></head><body><main></main></body></html>
HTML
expect_fail "empty main" "[EMPTY_PAGE]" audit_bundle "$empty"

no_main="$(make_project no-main)"
cat >"$no_main/index.html" <<'HTML'
<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Нет main</title></head><body><h1>Нет main</h1></body></html>
HTML
expect_fail "missing semantic main" "[PAGE_MAIN]" audit_bundle "$no_main"

fragment="$(make_project html-fragment)"
cat >"$fragment/index.html" <<'HTML'
<main><h1>Фрагмент</h1><p>Не автономный документ.</p></main>
HTML
expect_fail "HTML fragment is not a portable document" "[PAGE_DOCTYPE]" \
  audit_bundle "$fragment"

no_viewport="$(make_project no-viewport)"
write_narrative "$no_viewport"
perl -0pi -e 's#  <meta name="viewport"[^>]*>\n##' "$no_viewport/index.html"
expect_fail "mobile viewport is required" "[PAGE_VIEWPORT]" \
  audit_bundle "$no_viewport"

no_csp="$(make_project no-csp)"
write_narrative "$no_csp"
perl -0pi -e 's#  <meta http-equiv="Content-Security-Policy"[^>]*>\n##' \
  "$no_csp/index.html"
expect_fail "local-only CSP is required" "[PAGE_CSP]" audit_bundle "$no_csp"

two_main="$(make_project two-main)"
cat >"$two_main/index.html" <<'HTML'
<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Два main</title></head><body><main><h1>Один</h1></main><main>Два</main></body></html>
HTML
expect_fail "duplicate main" "[PAGE_MAIN]" audit_bundle "$two_main"

two_h1="$(make_project two-h1)"
cat >"$two_h1/index.html" <<'HTML'
<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Два h1</title></head><body><main><h1>Один</h1><h1>Два</h1></main></body></html>
HTML
expect_fail "duplicate h1" "[PAGE_HEADING]" audit_bundle "$two_h1"

canvas="$(make_project canvas)"
write_dashboard "$canvas"
expect_pass "canvas with artifact title needs no h1" audit_bundle "$canvas"

malformed="$(make_project malformed)"
write_narrative "$malformed"
perl -0pi -e 's#</article>##' "$malformed/index.html"
expect_fail "unclosed element" "[TAG_NESTING]" audit_bundle "$malformed"

self_closing_script="$(make_project self-closing-script)"
write_narrative "$self_closing_script"
perl -0pi -e 's#</body>#<script defer src="lib/alpine.js" /></body>#' \
  "$self_closing_script/index.html"
expect_fail "self-closing script is invalid HTML" "[TAG_NESTING]" \
  audit_bundle "$self_closing_script"

self_closing_div="$(make_project self-closing-div)"
write_narrative "$self_closing_div"
perl -0pi -e 's#</main>#<div /></main>#' "$self_closing_div/index.html"
expect_fail "self-closing div is invalid HTML" "[TAG_NESTING]" \
  audit_bundle "$self_closing_div"

plain_card="$(make_project plain-card)"
write_narrative "$plain_card"
perl -0pi -e 's#custom-card#card#' "$plain_card/index.html"
expect_fail "bare Daisy card is blocked" "[DAISY_STRUCTURE]" \
  audit_bundle "$plain_card"

structured_card="$(make_project structured-card)"
write_narrative "$structured_card"
perl -0pi -e 's#class="custom-card"#class="card"><div class="card-body"#; s#</article>#</div></article>#' \
  "$structured_card/index.html"
expect_pass "Daisy card with direct body passes" audit_bundle "$structured_card"

media_card="$(make_project media-card)"
write_narrative "$media_card"
perl -0pi -e 's#<article class="custom-card"><p>[^<]+</p></article>#<article class="card"><figure><svg aria-label="Обложка"></svg></figure></article>#' \
  "$media_card/index.html"
expect_pass "media-only Daisy card needs no card-body" audit_bundle "$media_card"

accidental_hero="$(make_project accidental-hero)"
write_narrative "$accidental_hero"
perl -0pi -e 's#class="essay"#class="hero"#' "$accidental_hero/index.html"
expect_fail "accidental Daisy hero collision is blocked" "[DAISY_STRUCTURE]" \
  audit_bundle "$accidental_hero"

inline_style="$(make_project inline-style)"
write_narrative "$inline_style"
perl -0pi -e 's#<main class="essay">#<main class="essay" style="padding: 7vw">#' \
  "$inline_style/index.html"
expect_pass "inline style remains design freedom" audit_bundle "$inline_style"

multi="$(make_project multi-page)"
write_narrative "$multi"
mkdir -p "$multi/pages"
cat >"$multi/pages/detail.html" <<'HTML'
<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'self' data: blob:; connect-src 'none'; font-src 'self' data:; frame-src 'self'; img-src 'self' data: blob:; media-src 'self' data: blob:; object-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; worker-src 'self' blob:"><title>Деталь</title><link href="../assets/local.css" rel="stylesheet"></head><body><main><h1>Другой экран</h1><a href="../index.html">К отчёту</a></main></body></html>
HTML
expect_pass "multi-page bundle needs no navigation template" audit_bundle "$multi"

nested="$(make_project nested-page)"
write_narrative "$nested"
mkdir -p "$nested/pages/deep"
cp "$nested/index.html" "$nested/pages/deep/detail.html"
expect_fail "nested page topology" "[PAGE_TOPOLOGY]" audit_bundle "$nested"

uppercase="$(make_project uppercase-page)"
write_narrative "$uppercase"
mkdir -p "$uppercase/pages"
cp "$uppercase/index.html" "$uppercase/pages/BAD.HTML"
expect_fail "uppercase page topology" "[PAGE_TOPOLOGY]" audit_bundle "$uppercase"

existing_resource="$(make_project existing-resource)"
write_narrative "$existing_resource"
printf 'image' >"$existing_resource/assets/pixel.png"
perl -0pi -e 's#</main>#<img src="assets/pixel.png" alt="Пиксель"></main>#' \
  "$existing_resource/index.html"
expect_pass "existing local image" audit_bundle "$existing_resource"

missing_resource="$(make_project missing-resource)"
write_narrative "$missing_resource"
perl -0pi -e 's#</main>#<img src="assets/missing.png" alt="Нет"></main>#' \
  "$missing_resource/index.html"
expect_fail "missing image" "[RESOURCE_LINK]" audit_bundle "$missing_resource"

remote_resource="$(make_project remote-resource)"
write_narrative "$remote_resource"
perl -0pi -e 's#</main>#<iframe src="https://example.com"></iframe></main>#' \
  "$remote_resource/index.html"
expect_fail "remote iframe" "[RESOURCE_LINK]" audit_bundle "$remote_resource"

escape_resource="$(make_project escape-resource)"
write_narrative "$escape_resource"
perl -0pi -e 's#</main>#<img src="../outside.png" alt="Нет"></main>#' \
  "$escape_resource/index.html"
expect_fail "escaping image" "[RESOURCE_LINK]" audit_bundle "$escape_resource"

srcset_resource="$(make_project srcset-resource)"
write_narrative "$srcset_resource"
perl -0pi -e 's#</main>#<img srcset="assets/a.png 1x, assets/b.png 2x" alt="Нет"></main>#' \
  "$srcset_resource/index.html"
expect_fail "missing srcset candidates" "[RESOURCE_LINK]" audit_bundle "$srcset_resource"

base_page="$(make_project base-page)"
write_narrative "$base_page"
perl -0pi -e 's#<head>#<head><base href="./">#' "$base_page/index.html"
expect_fail "base element" "[RESOURCE_LINK]" audit_bundle "$base_page"

anchor_page="$(make_project anchor-page)"
write_narrative "$anchor_page"
perl -0pi -e 's~</main>~<a href="#missing">Нет</a></main>~' "$anchor_page/index.html"
expect_fail "dead local anchor" "[RESOURCE_LINK]" audit_bundle "$anchor_page"

external_link="$(make_project external-link)"
write_narrative "$external_link"
perl -0pi -e 's#</main>#<a href="https://example.com">Источник</a></main>#' \
  "$external_link/index.html"
expect_pass "external navigation link" audit_bundle "$external_link"

css_local="$(make_project css-local)"
write_narrative "$css_local"
printf 'font' >"$css_local/assets/type.woff2"
printf '.essay { background: url("type.woff2"); }\n' >"$css_local/assets/local.css"
expect_pass "existing CSS url" audit_bundle "$css_local"

css_missing="$(make_project css-missing)"
write_narrative "$css_missing"
printf '.essay { background: url("missing.png"); }\n' >"$css_missing/assets/local.css"
expect_fail "missing CSS url" "[RESOURCE_LINK]" audit_bundle "$css_missing"

css_remote="$(make_project css-remote)"
write_narrative "$css_remote"
printf '.essay { background: url("https://example.com/a.png"); }\n' >"$css_remote/assets/local.css"
expect_fail "remote CSS url" "[RESOURCE_LINK]" audit_bundle "$css_remote"

css_escape="$(make_project css-escape)"
write_narrative "$css_escape"
printf '.essay { background: url("../../outside.png"); }\n' >"$css_escape/assets/local.css"
expect_fail "escaping CSS url" "[RESOURCE_LINK]" audit_bundle "$css_escape"

css_data="$(make_project css-data)"
write_narrative "$css_data"
printf '.essay { mask: url("data:image/svg+xml,<svg></svg>"); filter: url("#fx"); }\n' >"$css_data/assets/local.css"
expect_pass "data and fragment CSS urls" audit_bundle "$css_data"

css_import="$(make_project css-import)"
write_narrative "$css_import"
printf '@import "other.css";\n' >"$css_import/assets/local.css"
expect_fail "CSS import remains explicit" "[RESOURCE_LINK]" audit_bundle "$css_import"

inline_css_remote="$(make_project inline-css-remote)"
write_narrative "$inline_css_remote"
perl -0pi -e 's#</head>#<style>.essay { background: url("https://example.com/a.png"); }</style></head>#' \
  "$inline_css_remote/index.html"
expect_fail "remote URL in style block is blocked" "[RESOURCE_LINK]" \
  audit_bundle "$inline_css_remote"

inline_attr_remote="$(make_project inline-attribute-remote)"
write_narrative "$inline_attr_remote"
perl -0pi -e 's#class="essay"#class="essay" style="background:url(https://example.com/a.png)"#' \
  "$inline_attr_remote/index.html"
expect_fail "remote URL in style attribute is blocked" "[RESOURCE_LINK]" \
  audit_bundle "$inline_attr_remote"

inline_fetch="$(make_project inline-fetch)"
write_narrative "$inline_fetch"
perl -0pi -e 's#</body>#<script>fetch("https://example.com/data.json")</script></body>#' \
  "$inline_fetch/index.html"
expect_fail "network fetch is blocked" "[SCRIPT_PORTABILITY]" \
  audit_bundle "$inline_fetch"

module_script="$(make_project module-script)"
write_narrative "$module_script"
perl -0pi -e 's#</body>#<script type="module">const ready = true;</script></body>#' \
  "$module_script/index.html"
expect_fail "module script is not direct-file portable" "[SCRIPT_PORTABILITY]" \
  audit_bundle "$module_script"

local_fetch="$(make_project local-fetch)"
write_narrative "$local_fetch"
printf 'fetch("https://example.com/data.json");\n' >"$local_fetch/assets/local.js"
perl -0pi -e 's#</body>#<script src="assets/local.js"></script></body>#' \
  "$local_fetch/index.html"
expect_fail "network route in authored JS is blocked" "[SCRIPT_PORTABILITY]" \
  audit_bundle "$local_fetch"

missing_marker="$(make_project missing-marker)"
write_narrative "$missing_marker"
rm "$missing_marker/.1html-bundle-version"
expect_fail "missing marker requires legacy" "[BUNDLE_VERSION]" audit_bundle "$missing_marker"
expect_pass "explicit legacy accepts pre-marker" audit_legacy "$missing_marker"

previous_marker="$(make_project previous-marker)"
write_narrative "$previous_marker"
printf '2026-08-19.1\n' >"$previous_marker/.1html-bundle-version"
perl -0pi -e 's#</main>#<div data-react-flow="old-schema">Старый runtime</div></main>#' \
  "$previous_marker/index.html"
expect_fail "previous marker requires legacy" "[BUNDLE_VERSION]" audit_bundle "$previous_marker"
expect_pass "explicit legacy accepts previous generation" audit_legacy "$previous_marker"

current_legacy="$(make_project current-legacy)"
write_narrative "$current_legacy"
expect_fail "current marker rejects legacy" "[BUNDLE_VERSION]" audit_legacy "$current_legacy"

vendor_change="$(make_project vendor-change)"
write_narrative "$vendor_change"
printf '\n/* changed */\n' >>"$vendor_change/lib/daisyui.css"
expect_fail "vendored runtime is immutable" "[OWNER_DIVERGENCE]" audit_bundle "$vendor_change"

vendor_missing="$(make_project vendor-missing)"
write_narrative "$vendor_missing"
rm "$vendor_missing/lib/THIRD_PARTY_NOTICES.txt"
expect_fail "vendor notice is required" "[SHARED_ASSET]" audit_bundle "$vendor_missing"

author_change="$(make_project author-change)"
write_narrative "$author_change"
printf '\nbody { container-type: inline-size; }\n' >>"$author_change/assets/local.css"
expect_pass "authored CSS is not byte locked" audit_bundle "$author_change"

table_missing="$(make_project table-missing)"
write_narrative "$table_missing"
perl -0pi -e 's#<main class="essay">#<main class="essay" x-data="artifactTable([])">#' \
  "$table_missing/index.html"
expect_fail "active table requires helper wiring" "[DEPENDENCY_WIRING]" audit_bundle "$table_missing"

table_ready="$(make_project table-ready)"
write_narrative "$table_ready"
perl -0pi -e 's#<main class="essay">#<main class="essay" x-data="artifactTable([])">#; s#</head>#  <script defer src="lib/alpine.js"></script>\n</head>#' \
  "$table_ready/index.html"
expect_pass "table helper wires design-free page" \
  "$script_dir/add_table_bundle.sh" "$table_ready"
expect_pass "wired table passes" audit_bundle "$table_ready"

mermaid_ready="$(make_project mermaid-ready)"
write_narrative "$mermaid_ready"
perl -0pi -e 's#</head>#  <script defer src="lib/alpine.js"></script>\n</head>#; s#</main>#<pre class="mermaid">graph TD; A-->B</pre></main>#' \
  "$mermaid_ready/index.html"
expect_pass "Mermaid helper wires design-free page" \
  "$script_dir/add_mermaid_bundle.sh" "$mermaid_ready"
expect_pass "wired Mermaid passes" audit_bundle "$mermaid_ready"
printf '\n/* artifact-specific viewer color */\n' >>"$mermaid_ready/assets/diagram-viewer.css"
expect_pass "first-party Mermaid CSS remains editable" audit_bundle "$mermaid_ready"
printf '\n/* broken vendor */\n' >>"$mermaid_ready/lib/mermaid.min.js"
expect_fail "active Mermaid vendor is immutable" "[OWNER_DIVERGENCE]" \
  audit_bundle "$mermaid_ready"

react_flow_missing="$(make_project react-flow-missing)"
write_react_flow_page "$react_flow_missing"
expect_fail "active React Flow requires helper wiring" "[DEPENDENCY_WIRING]" \
  audit_bundle "$react_flow_missing"

react_flow_ready="$(make_project react-flow-ready)"
write_react_flow_page "$react_flow_ready"
expect_pass "React Flow helper wires active page" \
  "$script_dir/add_react_flow_bundle.sh" "$react_flow_ready"
expect_pass "wired React Flow passes" audit_bundle "$react_flow_ready"
react_hash_before="$(shasum -a 256 "$react_flow_ready/index.html" | awk '{print $1}')"
expect_pass "React Flow helper is idempotent" \
  "$script_dir/add_react_flow_bundle.sh" "$react_flow_ready"
react_hash_after="$(shasum -a 256 "$react_flow_ready/index.html" | awk '{print $1}')"
[[ "$react_hash_before" == "$react_hash_after" ]] \
  || fail "React Flow helper changed an already wired page"
pass

react_flow_invalid="$(make_project react-flow-invalid-json)"
write_react_flow_page "$react_flow_invalid"
perl -0pi -e 's/"edges": \[/"edges": [BROKEN/' "$react_flow_invalid/index.html"
expect_pass "invalid React Flow fixture receives helper assets" \
  "$script_dir/add_react_flow_bundle.sh" "$react_flow_invalid"
expect_fail "invalid React Flow JSON is blocked" "[REACT_FLOW_CONFIG]" \
  audit_bundle "$react_flow_invalid"

react_flow_template="$(make_project react-flow-missing-template)"
write_react_flow_page "$react_flow_template"
perl -0pi -e 's/"template":"node-intake"/"template":"node-missing"/' \
  "$react_flow_template/index.html"
expect_pass "missing-template fixture receives helper assets" \
  "$script_dir/add_react_flow_bundle.sh" "$react_flow_template"
expect_fail "missing React Flow template is blocked" "[REACT_FLOW_CONFIG]" \
  audit_bundle "$react_flow_template"

react_flow_edge="$(make_project react-flow-bad-edge)"
write_react_flow_page "$react_flow_edge"
perl -0pi -e 's/"target":"work"/"target":"missing"/' "$react_flow_edge/index.html"
expect_pass "bad-edge fixture receives helper assets" \
  "$script_dir/add_react_flow_bundle.sh" "$react_flow_edge"
expect_fail "unknown React Flow edge endpoint is blocked" "[REACT_FLOW_CONFIG]" \
  audit_bundle "$react_flow_edge"

react_flow_data="$(make_project react-flow-data-array)"
write_react_flow_page "$react_flow_data"
perl -0pi -e 's/"template":"node-intake"/"template":"node-intake","data":[]/' \
  "$react_flow_data/index.html"
expect_pass "data-array fixture receives helper assets" \
  "$script_dir/add_react_flow_bundle.sh" "$react_flow_data"
expect_fail "React Flow node data must be an object" "data must be an object" \
  audit_bundle "$react_flow_data"

react_flow_nan="$(make_project react-flow-nan)"
write_react_flow_page "$react_flow_nan"
perl -0pi -e 's/"x":0/"x":NaN/' "$react_flow_nan/index.html"
expect_pass "NaN fixture receives helper assets" \
  "$script_dir/add_react_flow_bundle.sh" "$react_flow_nan"
expect_fail "React Flow rejects non-JSON NaN" "non-finite JSON number" \
  audit_bundle "$react_flow_nan"

printf '\n/* artifact override */\n' >>"$react_flow_ready/assets/react-flow-theme.css"
expect_pass "first-party React Flow bridge remains editable" audit_bundle "$react_flow_ready"
printf '\n/* artifact-owned interaction extension */\n' \
  >>"$react_flow_ready/assets/react-flow-init.js"
expect_pass "first-party React Flow adapter remains editable" audit_bundle "$react_flow_ready"
printf '\n/* broken vendor */\n' >>"$react_flow_ready/lib/react-flow.vendor.js"
expect_fail "active React Flow vendor is immutable" "[OWNER_DIVERGENCE]" \
  audit_bundle "$react_flow_ready"

react_flow_absent="$(make_project react-flow-absent)"
write_narrative "$react_flow_absent"
expect_fail "React Flow helper requires an active host" \
  "no page contains a data-react-flow host" \
  "$script_dir/add_react_flow_bundle.sh" "$react_flow_absent"
[[ ! -e "$react_flow_absent/lib/react-flow.vendor.js" ]] \
  || fail "React Flow helper copied assets without an active host"
pass

if rg -n 'from\s*["'\''](?:react|@xyflow)|require\(["'\''](?:react|@xyflow)|import\(["'\''](?:react|@xyflow)' \
  "$skill_dir/assets/react-flow/lib/react-flow.vendor.js" \
  || rg -n '\bfetch\s*\(' \
    "$skill_dir/assets/react-flow/assets/react-flow-init.js"; then
  fail "React Flow shipped runtime contains a network or bare-import route"
fi
pass

if rg -q 'dangerouslySetInnerHTML' \
  "$skill_dir/assets/react-flow/assets/react-flow-init.js" \
  || ! rg -q 'content\.cloneNode\(true\)' \
    "$skill_dir/assets/react-flow/assets/react-flow-init.js"; then
  fail "React Flow template content can be recreated during node resize"
fi
pass

if ! rg -q 'fitViewOnMobile' \
  "$skill_dir/assets/react-flow/assets/react-flow-init.js"; then
  fail "React Flow mobile default can shrink large nodes into thumbnails"
fi
pass

if rg -n -U '\.react-flow__node-html\s*\{[^}]*(inline-size|width|padding|background|border)' \
  "$skill_dir/assets/react-flow/assets/react-flow-theme.css" \
  || rg -n -U '\[data-react-flow\]\s*\{[^}]*\n\s*(block-size|inline-size|width|height|border|border-radius|background|overflow)\s*:' \
    "$skill_dir/assets/react-flow/assets/react-flow-theme.css" \
  || rg -n -U '\.(rf-html-node|rf-node-content)\s*\{[^}]*(inline-size|width|padding|background|border)' \
    "$skill_dir/assets/react-flow/assets/react-flow-theme.css" \
  || rg -n '\.(rf-html-node|rf-node-content)\s+(details|summary|button|article|section|h[1-6])' \
    "$skill_dir/assets/react-flow/assets/react-flow-theme.css"; then
  fail "React Flow bridge imposes node anatomy instead of preserving artifact freedom"
fi
pass

echarts_missing="$(make_project echarts-missing)"
write_echarts_page "$echarts_missing"
expect_fail "active ECharts requires helper wiring" "[DEPENDENCY_WIRING]" \
  audit_bundle "$echarts_missing"

echarts_ready="$(make_project echarts-ready)"
write_echarts_page "$echarts_ready"
expect_pass "ECharts helper wires active page" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_ready"
expect_pass "wired ECharts passes" audit_bundle "$echarts_ready"
echarts_hash_before="$(shasum -a 256 "$echarts_ready/index.html" | awk '{print $1}')"
expect_pass "ECharts helper is idempotent" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_ready"
echarts_hash_after="$(shasum -a 256 "$echarts_ready/index.html" | awk '{print $1}')"
[[ "$echarts_hash_before" == "$echarts_hash_after" ]] \
  || fail "ECharts helper changed an already wired page"
pass

echarts_custom_basename="$(make_project echarts-custom-basename)"
write_echarts_page "$echarts_custom_basename"
mkdir -p "$echarts_custom_basename/assets/custom"
printf 'window.customEChartsHook = true;\n' \
  >"$echarts_custom_basename/assets/custom/echarts-init.js"
perl -0pi -e 's#</body>#<script src="assets/custom/echarts-init.js"></script></body>#' \
  "$echarts_custom_basename/index.html"
expect_pass "ECharts helper preserves same-basename authored resource" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_custom_basename"
grep -Fq 'src="assets/custom/echarts-init.js"' \
  "$echarts_custom_basename/index.html" \
  || fail "ECharts helper removed authored same-basename resource"
pass

echarts_invalid="$(make_project echarts-invalid-json)"
write_echarts_page "$echarts_invalid"
perl -0pi -e 's/"series": \[/"series": [BROKEN/' "$echarts_invalid/index.html"
expect_pass "invalid ECharts fixture receives helper assets" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_invalid"
expect_fail "invalid ECharts JSON is blocked" "[ECHARTS_CONFIG]" \
  audit_bundle "$echarts_invalid"

echarts_series="$(make_project echarts-missing-series)"
write_echarts_page "$echarts_series"
perl -0pi -e 's/"series": \[\{"type":"bar","data":\[44,82\]\}\]/"series": []/' \
  "$echarts_series/index.html"
expect_pass "missing-series ECharts fixture receives helper assets" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_series"
expect_fail "empty ECharts series is blocked" "[ECHARTS_CONFIG]" \
  audit_bundle "$echarts_series"

echarts_aria="$(make_project echarts-missing-description)"
write_echarts_page "$echarts_aria"
perl -0pi -e 's/ aria-labelledby="sales-summary"//' "$echarts_aria/index.html"
expect_pass "missing-description fixture receives helper assets" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_aria"
expect_fail "ECharts requires an authored description" "[ECHARTS_CONFIG]" \
  audit_bundle "$echarts_aria"

echarts_label_ref="$(make_project echarts-bad-labelledby)"
write_echarts_page "$echarts_label_ref"
perl -0pi -e 's/aria-labelledby="sales-summary"/aria-labelledby="missing-summary"/' \
  "$echarts_label_ref/index.html"
expect_pass "bad-labelledby fixture receives helper assets" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_label_ref"
expect_fail "ECharts rejects a missing labelledby target" "missing id(s)" \
  audit_bundle "$echarts_label_ref"

echarts_empty_label="$(make_project echarts-empty-labelledby)"
write_echarts_page "$echarts_empty_label"
perl -0pi -e 's#>Розница лидирует: 82 заказа\.</figcaption>#></figcaption>#' \
  "$echarts_empty_label/index.html"
expect_pass "empty-labelledby fixture receives helper assets" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_empty_label"
expect_fail "ECharts rejects an empty labelledby target" "empty id(s)" \
  audit_bundle "$echarts_empty_label"

echarts_nan="$(make_project echarts-nan)"
write_echarts_page "$echarts_nan"
perl -0pi -e 's/\[44,82\]/[44,NaN]/' "$echarts_nan/index.html"
expect_pass "ECharts NaN fixture receives helper assets" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_nan"
expect_fail "ECharts rejects non-JSON NaN" "non-finite JSON number" \
  audit_bundle "$echarts_nan"

echarts_renderer="$(make_project echarts-bad-renderer)"
write_echarts_page "$echarts_renderer"
perl -0pi -e 's/data-echart="sales-option"/data-echart="sales-option" data-echart-renderer="webgl"/' \
  "$echarts_renderer/index.html"
expect_pass "bad-renderer fixture receives helper assets" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_renderer"
expect_fail "ECharts renderer is svg or canvas" "[ECHARTS_CONFIG]" \
  audit_bundle "$echarts_renderer"

printf '\n/* artifact-owned ECharts extension */\n' >>"$echarts_ready/assets/echarts-init.js"
expect_pass "first-party ECharts adapter remains editable" audit_bundle "$echarts_ready"
printf '\n/* broken vendor */\n' >>"$echarts_ready/lib/echarts.min.js"
expect_fail "active ECharts vendor is immutable" "[OWNER_DIVERGENCE]" \
  audit_bundle "$echarts_ready"

echarts_absent="$(make_project echarts-absent)"
write_narrative "$echarts_absent"
expect_fail "ECharts helper requires an active host" \
  "no page contains a data-echart host" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_absent"
[[ ! -e "$echarts_absent/lib/echarts.min.js" ]] \
  || fail "ECharts helper copied assets without an active host"
pass

echarts_false_marker="$(make_project echarts-false-marker)"
write_narrative "$echarts_false_marker"
perl -0pi -e 's#</main>#<!-- data-echart="fake" --><code>data-echart="fake"</code></main>#' \
  "$echarts_false_marker/index.html"
expect_fail "ECharts helper ignores comment and code markers" \
  "no page contains a data-echart host" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_false_marker"
[[ ! -e "$echarts_false_marker/lib/echarts.min.js" ]] \
  || fail "ECharts false marker copied assets"
pass

echarts_minified="$(make_project echarts-minified)"
cat >"$echarts_minified/index.html" <<'HTML'
<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'self' data: blob:; connect-src 'none'; font-src 'self' data:; frame-src 'self'; img-src 'self' data: blob:; media-src 'self' data: blob:; object-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; worker-src 'self' blob:"><title>Минифицированный chart</title><link rel="stylesheet" href="assets/local.css"></head><body><main><h1>Минифицированный chart</h1><div aria-label="Два значения" data-echart="mini"></div><script id="mini" type="application/json">{"series":[{"type":"bar","data":[1,2]}],"xAxis":{},"yAxis":{}}</script></main></body></html>
HTML
expect_pass "ECharts helper wires one-line HTML" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_minified"
minified_hash_before="$(shasum -a 256 "$echarts_minified/index.html" | awk '{print $1}')"
expect_pass "ECharts one-line wiring is idempotent" \
  "$script_dir/add_echarts_bundle.sh" "$echarts_minified"
minified_hash_after="$(shasum -a 256 "$echarts_minified/index.html" | awk '{print $1}')"
[[ "$minified_hash_before" == "$minified_hash_after" ]] \
  || fail "ECharts one-line helper changed repeated output"
pass
expect_pass "wired one-line ECharts page passes" audit_bundle "$echarts_minified"

if rg -n '\bfetch\s*\(|\bimport\s*\(' \
  "$skill_dir/assets/echarts/assets/echarts-init.js"; then
  fail "ECharts adapter contains a network or module route"
fi
pass

for recipe in "Ranked Bar" "Line" "Scatter" "Sankey" "Treemap"; do
  rg -q "$recipe" "$skill_dir/references/echarts.md" \
    || fail "ECharts editable recipe is missing: $recipe"
done
pass

new_root="$tmp_root/new-root"
mkdir -p "$new_root"
expect_pass "new bundle creates blank scaffold" \
  "$script_dir/new_html_bundle.sh" blank "$new_root"
if [[ ! -f "$new_root/_workspace/HTML_artifacts/blank/index.html" ]] \
  || [[ ! -f "$new_root/_workspace/HTML_artifacts/index.html" ]]; then
  fail "new bundle did not create artifact and catalog"
fi
pass

finish_root="$tmp_root/finish-root"
mkdir -p "$finish_root"
"$script_dir/new_html_bundle.sh" ready "$finish_root" >/dev/null
write_narrative "$finish_root/_workspace/HTML_artifacts/ready"
expect_pass "finish validates then rebuilds catalog" \
  "$script_dir/finish_html_bundle.sh" ready "$finish_root"
if ! grep -Fq '&quot;slug&quot;:&quot;ready&quot;' "$finish_root/_workspace/HTML_artifacts/index.html"; then
  fail "catalog does not contain finished artifact"
fi
pass

catalog_hash_before="$(shasum -a 256 "$finish_root/_workspace/HTML_artifacts/index.html" | awk '{print $1}')"
printf '<img src="missing.png">\n' >>"$finish_root/_workspace/HTML_artifacts/ready/index.html"
expect_fail "failed finish blocks catalog mutation" "[RESOURCE_LINK]" \
  "$script_dir/finish_html_bundle.sh" ready "$finish_root"
catalog_hash_after="$(shasum -a 256 "$finish_root/_workspace/HTML_artifacts/index.html" | awk '{print $1}')"
[[ "$catalog_hash_before" == "$catalog_hash_after" ]] \
  || fail "failed finish mutated catalog"
pass

expect_fail "catalog slug is reserved" "artifact name must be one directory name" \
  "$script_dir/finish_html_bundle.sh" _catalog "$finish_root"

printf 'PASS: %s design-free bundle contract checks\n' "$pass_count"
