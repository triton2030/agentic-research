---
title: Obsidian HTML smoke test
tags:
  - test
  - obsidian/html
---

# Obsidian HTML smoke test

Короткая проверка того, как Obsidian рендерит HTML внутри Markdown-заметки.

## Inline HTML

Markdown рядом работает обычно: **bold**, `code`.

HTML inline: <u>underline</u>, <s>strike</s>, <mark>mark</mark>, <span style="color:#e26d5a; font-weight:700;">colored span</span>.

## Self-contained HTML block

<div style="border:1px solid var(--background-modifier-border); border-radius:8px; padding:12px; background:var(--background-secondary);"><strong>HTML block:</strong> это один самодостаточный блок. Markdown внутри него, например **bold** и `code`, ожидаемо должен остаться обычным текстом.</div>

## HTML table

<table><thead><tr><th>Элемент</th><th>Что проверяем</th></tr></thead><tbody><tr><td><code>&lt;u&gt;</code></td><td>Подчёркивание</td></tr><tr><td><code>&lt;span style="..."&gt;</code></td><td>Inline styling</td></tr><tr><td><code>&lt;div style="..."&gt;</code></td><td>Самодостаточный styled block</td></tr></tbody></table>

## Native disclosure

<details><summary>Раскрывающийся HTML-блок без JavaScript</summary><p>Если этот блок раскрывается в Reading view, нативный HTML interactive element проходит.</p></details>

## Iframe smoke test

<iframe src="https://www.openstreetmap.org/export/embed.html?bbox=76.85%2C43.18%2C76.99%2C43.29&amp;layer=mapnik" width="100%" height="240" style="border:1px solid var(--background-modifier-border); border-radius:8px;"></iframe>
