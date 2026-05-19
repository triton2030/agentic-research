---
aliases:
  - Custom JS Diagram
tags:
  - experiment/obsidian
  - experiment/javascript-diagram
cssclasses:
  - obsidian-beauty-lab
---

# Custom JS Diagram

> [!summary]+ Что проверяем
> **Цель:** сделать маленький кастомный аналог Mermaid: свой DSL, JavaScript
> parser/layout, SVG-renderer и вставка в Obsidian.
>
> Прямо в Markdown-заметке Obsidian не стоит рассчитывать на выполнение
> JavaScript. Поэтому самый надёжный рабочий путь — ссылка на локальную
> HTML-страницу. Статический SVG остаётся fallback, а `iframe` — необязательная
> проба.

## Open HTML Page

Открыть интерактивный renderer как обычную HTML-страницу:

[Open TinyFlow HTML](file:///Users/triton/Documents/GitHub/agentic-research/experiments/obsidian-beauty-lab/web-panels/tinyflow-demo.html)

## Static Fallback

Если iframe не открылся, этот SVG всё равно должен показываться в Obsidian как
обычная локальная картинка:

![[generated/tinyflow-demo.svg|746]]

## Live Demo

Этот блок можно считать экспериментальным. Если Obsidian блокирует локальный
`file://` внутри iframe, используй ссылку выше.

<div class="obl-frame-shell" style="margin: 18px 0 26px; padding: 14px; border-radius: 24px; background: linear-gradient(135deg, #fff8ec, #e7f2ed); border: 1px solid rgba(74,58,33,.15); box-shadow: 0 18px 54px rgba(48,39,26,.12);">
<div style="display:flex; justify-content:space-between; gap:12px; align-items:center; margin:0 0 10px;"><strong>TinyFlow iframe renderer</strong><span style="font-size:12px; color:#675b4b;">local JS + SVG</span></div>
<iframe src="file:///Users/triton/Documents/GitHub/agentic-research/experiments/obsidian-beauty-lab/web-panels/tinyflow-demo.html" width="100%" height="720" style="border:0; border-radius:18px; background:#fff;"></iframe>
</div>

## DSL

```tinyflow
title: Obsidian render path
direction: LR
skin: warm

A[start: User asks]
B[process: TinyFlow DSL]
C{Can Obsidian run JS?}
D[risk: Not inside note]
E[data: iframe HTML]
F[success: SVG diagram]
G((Demo ready))

A -> B: write
B -> C: parse
C -> D: direct note
C -> E: safe path
E -> F: render
F -> G
```

## Файлы

- `web-panels/tinyflow.js` — простая библиотека: parser, layout, SVG renderer.
- `web-panels/tinyflow-demo.html` — локальная страница с textarea и live preview.
- `generated/tinyflow-demo.svg` — статический SVG, сгенерированный из DSL.
- Этот файл — Obsidian-оглавление: ссылка на HTML, SVG fallback и iframe-проба.

## Что Это Доказывает

> [!success]+ Рабочая идея
> Если нужен кастомный Mermaid-like язык, самый быстрый путь — локальная
> HTML-страница плюс статический SVG fallback. HTML может исполнять JavaScript
> и рисовать SVG, а Markdown-заметка остаётся понятным оглавлением.

> [!warning]- Ограничение
> Такой renderer не становится нативным Obsidian block renderer. Интерактивная
> версия живёт как отдельная HTML-страница; iframe может быть удобным, но не
> обязан работать. Для полноценного опыта с нативным `tinyflow` code block прямо
> в заметке нужен отдельный Obsidian plugin.

## Если Делать Следующий Шаг

1. Оставить HTML-link режим для быстрых прототипов.
2. Сделать генератор статического SVG рядом с Markdown, если нужна переносимость.
3. Делать Obsidian plugin только если хотим нативный code block renderer.

## Связанные Файлы

- [[00-obsidian-beauty-lab|Главное демо]]
- [[02-iframe-and-clever-paths|Iframe и хитрые пути]]
- [[03-meta-bind-and-obsidian-primitives|Meta Bind и Obsidian-примитивы]]
