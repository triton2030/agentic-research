# Apache ECharts — Данные Как Наглядное Отношение

Используй локальный ECharts, когда реальные количественные данные требуют
интерактивного chart, которого уже не выразить проще через native HTML/CSS/SVG.
Это opt-in runtime, не обязательный слой страницы и не набор design templates.

## Подключение

```html
<script defer src="lib/echarts.min.js"></script>
<script defer src="assets/shared/echarts-init.js"></script>
```

ECharts 6.1.0, adapter и notices уже лежат в общей HTML_artifacts zone.
Подключай runtime только на странице с `data-echart`. Страница работает через
`file://` без dev server, CDN, module loader, runtime build и сетевых запросов.

## Контракт

Сам artifact владеет композицией, размерами и текстовым объяснением:

```html
<figure aria-labelledby="sales-title">
  <h2 id="sales-title">Продажи по каналу</h2>
  <div
    data-echart="sales-option"
    aria-label="Розница лидирует: 82 заказа; партнёры — 61; сайт — 44."
  ></div>
  <figcaption>
    Розница лидирует: 82 заказа. Источник: CRM, 1–31 июля 2026.
  </figcaption>
</figure>
<script type="application/json" id="sales-option">
{
  "xAxis": {"type": "value", "name": "заказы"},
  "yAxis": {"type": "category", "data": ["Сайт", "Партнёры", "Розница"]},
  "series": [{"type": "bar", "data": [44, 61, 82]}]
}
</script>
```

```css
/* Размер — решение текущего artifact, shared add-on его не задаёт. */
[data-echart] {
  inline-size: 100%;
  block-size: clamp(20rem, 48vw, 34rem);
}
```

`data-echart` указывает на соседний `script[type="application/json"]`. JSON
является обычным ECharts option object и требует непустой `series`. Adapter не
переписывает типы charts и data. Default renderer — SVG; для действительно
тяжёлых наборов можно поставить `data-echart-renderer="canvas"`.

`aria-label`, `aria-labelledby` или `aria.label.description` обязательны.
Adapter включает ECharts ARIA и передаёт туда authored description. Но chart не
является semantic source: рядом остаются видимые heading, вывод, единица,
период и источник в `figcaption`, summary или таблице.

## Palette, Font, Motion

Adapter читает computed font и Daisy cupcake tokens. Обычный ink берётся из
`base-content`; axis/grid — из контрастной смеси `base-content` с `base-100`,
а не из близких по светлоте соседних base surfaces. Default data ink — из
проверенной brand-content тройки `primary-content`, `secondary-content`,
`accent-content`. Adapter
переводит CSS color в формат, который понимает ECharts; page не пишет
conversion code. Authored `option` остаётся свободным.

Три brand colors — default только для максимум трёх равноправных categories или
series. Если цвет различает четыре и более, задай `option.color` из brand/base
tokens и производных `color-mix()` под текущие данные. `info`, `success`,
`warning`, `error` не расширяют categorical palette: это реальные statuses.
Label, shape или line style дублируют важное различие.

```json
"color": [
  "var(--color-primary-content)",
  "var(--color-secondary-content)",
  "var(--color-accent-content)",
  "var(--color-base-content)",
  "color-mix(in oklch, var(--color-primary-content) 64%, var(--color-base-100))"
]
```

Adapter разрешает эти строковые CSS colors/expressions в RGB перед передачей
ECharts. Gradient object задавай в поддерживающем его series/item style, а не в
глобальном palette `option.color`.

При `prefers-reduced-motion: reduce` animation отключается. `ResizeObserver`
подгоняет chart после изменения контейнера.

## Пять Рецептов, Не Пять Макетов

Ниже независимые data/spec recipes. Копируй только подходящий relationship,
заменяй данные, подписи, единицы и scale. Не копируй page/card composition.

### 1. Ranked Bar — сравнить категории

Сортируй данные осмысленно; нулевая ось обязательна для честного сравнения.

```json
{
  "grid": {"containLabel": true, "left": 8, "right": 24},
  "tooltip": {"trigger": "axis"},
  "xAxis": {"type": "value", "name": "заказы", "min": 0},
  "yAxis": {
    "type": "category",
    "data": ["Сайт", "Партнёры", "Розница"]
  },
  "series": [{
    "type": "bar",
    "data": [44, 61, 82],
    "label": {"show": true, "position": "right"}
  }]
}
```

### 2. Line — факт против плана во времени

Разделяй серии label и line style, а не только цветом.

```json
{
  "legend": {"data": ["Факт", "План"]},
  "tooltip": {"trigger": "axis"},
  "xAxis": {
    "type": "category",
    "boundaryGap": false,
    "data": ["Апр", "Май", "Июн", "Июл"]
  },
  "yAxis": {"type": "value", "name": "заказы", "min": 0},
  "series": [
    {"name": "Факт", "type": "line", "data": [38, 51, 56, 72]},
    {
      "name": "План",
      "type": "line",
      "data": [42, 48, 60, 68],
      "lineStyle": {"type": "dashed"}
    }
  ]
}
```

### 3. Scatter — увидеть связь двух величин

Каждая точка должна быть наблюдением, а не придуманной иллюстрацией.

```json
{
  "tooltip": {"trigger": "item"},
  "xAxis": {"type": "value", "name": "время ответа, мин", "min": 0},
  "yAxis": {"type": "value", "name": "конверсия, %", "min": 0},
  "series": [{
    "type": "scatter",
    "symbolSize": 14,
    "data": [[3, 31], [8, 27], [13, 23], [21, 16], [34, 11]]
  }]
}
```

### 4. Sankey — показать объём между этапами

`value` относится к потоку, а не к размеру нарисованного блока.
Если nodes больше трёх и цвет выражает identity, добавь authored
`option.color`; не позволяй default palette назначить status colors этапам.

```json
{
  "tooltip": {"trigger": "item"},
  "series": [{
    "type": "sankey",
    "emphasis": {"focus": "adjacency"},
    "data": [
      {"name": "Новые"},
      {"name": "Уточнение"},
      {"name": "Приняты"},
      {"name": "Отказ"}
    ],
    "links": [
      {"source": "Новые", "target": "Уточнение", "value": 36},
      {"source": "Новые", "target": "Приняты", "value": 44},
      {"source": "Уточнение", "target": "Приняты", "value": 24},
      {"source": "Уточнение", "target": "Отказ", "value": 12}
    ]
  }]
}
```

### 5. Treemap — показать иерархию и доли

Площадь кодирует только одну аддитивную величину. Label не заменяет summary.

```json
{
  "tooltip": {"trigger": "item"},
  "series": [{
    "type": "treemap",
    "roam": false,
    "label": {"show": true, "formatter": "{b}"},
    "data": [
      {
        "name": "Печать",
        "value": 72,
        "children": [
          {"name": "Визитки", "value": 41},
          {"name": "Буклеты", "value": 31}
        ]
      },
      {
        "name": "Сувениры",
        "value": 38,
        "children": [
          {"name": "Кружки", "value": 22},
          {"name": "Футболки", "value": 16}
        ]
      }
    ]
  }]
}
```

## Официальные Опоры

- [Apache ECharts: Get Started](https://echarts.apache.org/handbook/en/get-started/)
- [Apache ECharts: Accessibility](https://echarts.apache.org/handbook/en/best-practices/aria/)
- [Apache ECharts: Canvas vs SVG](https://echarts.apache.org/handbook/en/best-practices/canvas-vs-svg/)
- [Apache ECharts 6.1.0 package](https://www.npmjs.com/package/echarts/v/6.1.0)
