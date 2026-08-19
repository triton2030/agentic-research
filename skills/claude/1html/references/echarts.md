# Apache ECharts — Данные Как Наглядное Отношение

Используй локальный ECharts, когда реальные количественные данные требуют
интерактивного chart, которого уже не выразить проще через native HTML/CSS/SVG.
Это opt-in runtime, не обязательный слой страницы и не набор design templates.

## Подключение

```bash
"<каталог skill>/scripts/add_echarts_bundle.sh" \
  "<artifact-name>" "<project-root>"
```

Helper копирует ECharts 6.1.0, тонкий adapter и license notices локально, затем
подключает их только к live pages с `data-echart`. Страница работает через
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

Adapter читает computed font и semantic variables artifact:
`--color-primary`, `--color-secondary`, `--color-accent`, status colors,
`--color-base-content`, `--color-base-300`. Из них собирается только ECharts
theme bridge; authored `option` остаётся свободным. При
`prefers-reduced-motion: reduce` animation отключается. `ResizeObserver`
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

## Проверка

- Подключён только локальный `lib/echarts.min.js`; Network пуст при `file://`.
- Каждый host имеет ненулевые computed width/height и `data-echart-ready=true`.
- Если host вычислился в ноль, adapter даёт только технический `min-block-size`
  и ждёт `ResizeObserver`; после раскрытия `details` chart монтируется сам.
  Обычный размер, aspect ratio и surface всё равно задай в `local.css`.
- SVG существует внутри host по умолчанию; `canvas` появляется только opt-in.
- Font, ink и palette вычислены из текущего artifact, а не из отдельной темы.
- При reduced motion ECharts option получает `animation: false`.
- Видимый вывод остаётся понятным без JavaScript и без hover tooltip.
- Data, единицы, период и источник совпадают с semantic summary.

## Официальные Опоры

- [Apache ECharts: Get Started](https://echarts.apache.org/handbook/en/get-started/)
- [Apache ECharts: Accessibility](https://echarts.apache.org/handbook/en/best-practices/aria/)
- [Apache ECharts: Canvas vs SVG](https://echarts.apache.org/handbook/en/best-practices/canvas-vs-svg/)
- [Apache ECharts 6.1.0 package](https://www.npmjs.com/package/echarts/v/6.1.0)
