<!-- 1html-generated: shared carrier map -->
# Что Уже Установлено В Зоне

Тема — DaisyUI `bumblebee`, второй палитры нет. Всё ниже лежит рядом и работает
по `file://`.

## Краска

Пары surface/content не разбивай. Хотя бы одно поле страницы — не бумага.

| Роль | Класс | Токены | В bumblebee |
|---|---|---|---|
| бумага | `.surface-paper` | `base-100` / `base-content` | белое, почти чёрный текст |
| тихая бумага | `.surface-quiet` | `base-200`, `base-300` | лёгкие ступени фона |
| **чернила** | `.surface-ink` | `accent` / `accent-content` | **чистый чёрный, белый текст** |
| тёмное поле | `.surface-dark` | `neutral` / `neutral-content` | тёплый тёмно-серый |
| **бренд** | `.surface-brand` | `primary` / `primary-content` | **жёлтый, тёмно-янтарный текст** |
| второй бренд | — | `secondary` / `secondary-content` | оранжевый |

**Жёлтый — цвет поверхности, а не текста.** `primary` на бумаге даёт контраст
1,57:1 и не читается. Значимая краска на бумаге берётся из `*-content`:
`primary-content`, `secondary-content`, `accent-content`. Сам `primary` идёт
заливкой, а текст на нём — `primary-content`.

`info` `success` `warning` `error` — только настоящие статусы, не категории
данных; больше трёх категорий берут `color-mix()` от токенов выше.

## Форма

Зона владеет начертанием заголовков (`--display`, засечный) и шкалой
`--step-hero → --step-fine`; размер каждого заголовка выбирает страница.
Роли текста opt-in: `.display` `.title` `.lede` `.eyebrow` `.figure-big` `.fine`.

| Класс | Отношение | Ручка |
|---|---|---|
| `page` + `.wide` `.full` | полоса страницы, выход во всю ширину | — |
| `flow` · `rhythm` | поток сверху вниз | `--space` |
| `cluster` | ряд меток, перенос по содержимому | `--gap` |
| `switcher` | ряд ↔ колонка целиком | `--threshold` |
| `with-sidebar` | панель + текучее тело | `--side` |
| `auto-grid` | равноправные карточки | `--min` |
| `bento` + `.lead` `.wide-tile` | плитки разного веса | `--min` |
| `tile` + `-ink` `-dark` `-brand` | плитка с назначенной поверхностью | — |
| `reel` | горизонтальная лента в рамке | `--gap` |

Порог переноса — минимум ширины блока, не ширина экрана. Имена DaisyUI
`stack`, `join`, `mask`, `indicator` не занимать.

## Носители

Подключай только тот, который показывает отношение.

**Таблица** — источником остаётся обычный `<table>`; adapter даёт поиск, фильтр
и сортировку.

```html
<script defer src="assets/shared/artifact-table.js"></script>
```

**Mermaid** — topology, sequence, state, timeline; определение читаемым текстом
в `<pre class="mermaid">`. Цвета внутри определения не задавай: `var()` в
`classDef` роняет парсер и схема не рендерится вовсе — роли различай формой
узла, `stroke-width`, `stroke-dasharray`.

```html
<link href="assets/shared/diagram-viewer.css" rel="stylesheet">
<script defer src="lib/mermaid.min.js"></script>
<script defer src="lib/mermaid-layout-elk.iife.min.js"></script>
<script defer src="lib/panzoom.min.js"></script>
<script defer src="assets/shared/diagram-viewer.js"></script>
<script defer src="assets/shared/mermaid-init.js"></script>
```

**ECharts** — величины, доли, изменение. Host `<div data-echart="id">`, option в
`<script type="application/json" id="id">`.

```html
<script defer src="lib/echarts.min.js"></script>
<script defer src="assets/shared/echarts-init.js"></script>
```

**React Flow** — граф с произвольной анатомией узла. Host
`<div data-react-flow="id">`, содержимое узлов — semantic HTML из `<template>`.

```html
<link href="lib/react-flow.css" rel="stylesheet">
<link href="assets/shared/react-flow-theme.css" rel="stylesheet">
<script defer src="lib/react-flow.vendor.js"></script>
<script defer src="assets/shared/react-flow-init.js"></script>
```

Adapters сами берут токены темы — свою палитру им не передавай.
