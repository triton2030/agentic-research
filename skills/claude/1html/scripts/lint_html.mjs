#!/usr/bin/env node
// Advisory-линтер дисциплины классов зоны HTML_artifacts. Запуск только по
// явному запросу; в обычное «Готово» не входит. Без браузера.
// Проверяет для каждой страницы:
//   1. каждый класс из assets/<slug>.css объявлен в плане страницы
//      (первый <details> после <body>);
//   2. собственных font-size / font-family — ноль;
//   3. план существует.
// Использование: node lint_html.mjs <page.html | папка зоны> [...]
// Exit: 0 — чисто, 1 — есть находки, 2 — ошибка входа.

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, dirname, basename } from "node:path";

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("usage: node lint_html.mjs <page.html | zone-dir> [...]");
  process.exit(2);
}

const SKIP = new Set(["index.html", "_template.html"]);
const pages = [];
for (const a of args) {
  let st;
  try { st = statSync(a); } catch { console.error(`not found: ${a}`); process.exit(2); }
  if (st.isDirectory()) {
    for (const f of readdirSync(a)) {
      if (f.endsWith(".html") && !SKIP.has(f)) pages.push(join(a, f));
    }
  } else {
    pages.push(a);
  }
}

let findings = 0;
for (const page of pages) {
  const html = readFileSync(page, "utf8");
  const slug = basename(page, ".html");
  const cssPath = join(dirname(page), "assets", `${slug}.css`);
  const out = [];

  const body = html.slice(html.indexOf("<body"));
  const planMatch = body.match(/<details[^>]*>[\s\S]*?<\/details>/);
  const plan = planMatch ? planMatch[0] : "";
  if (!plan) out.push("план не найден: нет <details> в начале страницы");

  if (existsSync(cssPath)) {
    const css = readFileSync(cssPath, "utf8")
      .replace(/\/\*[\s\S]*?\*\//g, "")
      .replace(/url\([^)]*\)/g, "");
    const own = [...new Set([...css.matchAll(/\.([A-Za-z_][\w-]*)/g)].map(m => m[1]))].sort();
    const undeclared = own.filter(c => !plan.includes(c));
    if (undeclared.length) out.push(`классы вне плана (${undeclared.length}): ${undeclared.join(", ")}`);
    for (const prop of ["font-size", "font-family"]) {
      const n = (css.match(new RegExp(`(?<![-\\w])${prop}\\s*:`, "g")) || []).length;
      if (n) out.push(`собственных ${prop}: ${n} (должно быть 0 — ступени берутся утилитами)`);
    }
    const media = (css.match(/@media/g) || []).length;
    if (media) out.push(`инфо: @media — ${media}; каждый должен быть назван в плане как перелом композиции`);
  } else {
    out.push(`нет CSS по конвенции: ${cssPath}`);
  }

  if (out.length) {
    findings += out.filter(l => !l.startsWith("инфо:")).length;
    console.log(`✗ ${basename(page)}`);
    for (const l of out) console.log(`  ${l}`);
  } else {
    console.log(`✓ ${basename(page)}`);
  }
}
process.exit(findings ? 1 : 0);
