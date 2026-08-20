<!-- 1html-generated: shared carrier map -->
# Shared Visual Carriers

Это карта уже установленных возможностей общей `HTML_artifacts` zone. Она не
задаёт page layout, palette, typography, card anatomy или размеры.

## Base

Каждая новая страница уже подключает:

- `lib/daisyui.css` и `lib/daisyui-themes.css` — component grammar;
- `lib/tailwind.js` — utility CSS;
- `lib/lucide.min.js` — icons; neutral scaffold уже вызывает
  `lucide.createIcons()`, при ручной странице вызови его после загрузки script;
- `lib/alpine.js` — небольшие UI states;
- `assets/shared/components.css` — общий zone-owned component layer;
- `assets/<slug>.css` — дизайн только текущей страницы.

## Table

```html
<script defer src="assets/shared/artifact-table.js"></script>
<script defer src="lib/alpine.js"></script>
```

HTML остаётся source: обычные `<table>`, `<caption>`, `<tr data-table-row>`.
Adapter добавляет Alpine `artifactTable()` для search/filter/sort.

## Mermaid

```html
<link href="assets/shared/diagram-viewer.css" rel="stylesheet">
<script defer src="lib/mermaid.min.js"></script>
<script defer src="lib/mermaid-layout-elk.iife.min.js"></script>
<script defer src="lib/panzoom.min.js"></script>
<script defer src="assets/shared/diagram-viewer.js"></script>
<script defer src="assets/shared/mermaid-init.js"></script>
```

Используй для topology, sequence, state, timeline и простых charts. Definition
остаётся читаемым text source в `<pre class="mermaid">`.

## ECharts

```html
<script defer src="lib/echarts.min.js"></script>
<script defer src="assets/shared/echarts-init.js"></script>
```

Host: `<div data-echart="option-id" aria-label="..."></div>`. Option хранится в
`<script type="application/json" id="option-id">`. Размер, palette, данные и
page composition принадлежат текущей странице.

## React Flow

```html
<link href="lib/react-flow.css" rel="stylesheet">
<link href="assets/shared/react-flow-theme.css" rel="stylesheet">
<script defer src="lib/react-flow.vendor.js"></script>
<script defer src="assets/shared/react-flow-init.js"></script>
```

Host: `<div data-react-flow="flow-id" aria-label="..."></div>`. Config хранится
в JSON; содержимое nodes — произвольный semantic HTML из `<template>`. Shared
bridge не задаёт node anatomy, surface, padding или количество disclosures.

Все runtimes локальны и работают через `file://`; server, CDN и build step не
нужны. Подключай только carrier, который действительно показывает отношение.
