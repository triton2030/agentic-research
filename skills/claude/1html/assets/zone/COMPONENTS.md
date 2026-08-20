<!-- 1html-generated: shared carrier map -->
# Shared Visual Carriers

Это карта уже установленных возможностей общей `HTML_artifacts` zone. DaisyUI
`cupcake` владеет совпавшей component-анатомией и палитрой; artifact владеет
page layout, typography, bespoke carrier, node anatomy и размерами.

## Base

Каждая новая страница уже подключает:

- `lib/daisyui.css` и `lib/daisyui-themes.css` — component anatomy и palette;
- `lib/tailwind.js` — utility CSS;
- `lib/lucide.min.js` — icons; neutral scaffold уже вызывает
  `lucide.createIcons()`, при ручной странице вызови его после загрузки script;
- `lib/alpine.js` — небольшие UI states;
- `assets/shared/components.css` — только повторившийся carrier, которого нет в
  Daisy; не второй atom system и не palette;
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
`<script type="application/json" id="option-id">`. Размер, данные и page
composition принадлежат текущей странице; palette приходит из cupcake.

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
Внутри свободной node совпавшие button, badge, collapse и alert остаются Daisy
components.

Все shared bridges наследуют Daisy cupcake tokens. Они не принимают
`--artifact-*` palette aliases и не используют status colors как нейтральные
data categories.

Все runtimes локальны и работают через `file://`; server, CDN и build step не
нужны. Подключай только carrier, который действительно показывает отношение.
