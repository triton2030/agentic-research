# Mermaid Syntax For Obsidian

Краткая шпаргалка по Mermaid-синтаксису для `1writing-style`. Используй её, когда
создаёшь или правишь Mermaid-блок в Obsidian и не уверен в точной форме записи.
Obsidian может отставать от текущих Mermaid docs, поэтому после нового паттерна
проверяй черновик глазами.

## Общий Block

````md
```mermaid
flowchart LR
  A["Короткий label"] --> B["Следующий"]
```
````

Правило Obsidian: короткие labels, без markdown-списков внутри узлов, длинный
смысл рядом обычным Markdown.

## Direction / Layout

Для `flowchart`:

```mermaid
flowchart LR
  A["01: Вход"] --> B["02: Проверка"] --> C["03: Выход"]
```

Варианты направления: `TB`/`TD`, `BT`, `LR`, `RL`. Горизонтально держи 3-4
коротких блока; больше — вертикально или дробить.

Для `gitGraph` направление задаётся после типа:

```mermaid
gitGraph TB:
  commit id: "open"
  commit id: "choice"
```

## Flowchart: New Shapes

Новая форма задаётся через `id@{ shape: ..., label: "..." }`.

```mermaid
flowchart LR
  start@{ shape: circle, label: "Старт" }
  brief@{ shape: doc, label: "Бриф" }
  decision@{ shape: diamond, label: "Готово?" }
  order@{ shape: tag-rect, label: "Заказ" }
  docs@{ shape: docs, label: "Документы" }

  start --> brief --> decision
  decision -- "да" --> order --> docs
  decision -- "нет" --> brief
```

Полезные shapes: `rounded`, `doc`, `docs`, `diamond`, `tag-rect`, `database`,
`circle`, `hex`, `stadium`, `text`, `process`.

## Flowchart: Manual Snake

Mermaid не делает автоматический wrap строк. Ручная змейка работает через
несколько `subgraph` с разными `direction`, но это хрупкий вариант.

```mermaid
flowchart TB
  subgraph row1["Вход"]
    direction LR
    A["01: Бриф"] --> B["02: Проверка"] --> C["03: Каталог"]
  end

  subgraph row2["Заявка"]
    direction RL
    F["06: Счёт"] --> E["05: Оценка"] --> D["04: Заявка"]
  end

  row1 --> row2
```

## SequenceDiagram

```mermaid
sequenceDiagram
  participant Studio as Студия
  participant Mavo as MAVO
  participant Prod as Производство

  Studio->>Mavo: заявка
  Mavo-->>Studio: уточнение
  Mavo->>Prod: заказ
  Prod-->>Mavo: статус
  Mavo-->>Studio: следующий шаг
```

Для длинного пояснения используй `Note`, а не огромный текст на стрелке:

```mermaid
sequenceDiagram
  participant Studio as Студия
  participant Mavo as MAVO
  Note over Studio,Mavo: Короткое пояснение<br/>в несколько строк
  Studio->>Mavo: заявка
```

## QuadrantChart

Русские и многословные labels бери в кавычки.

```mermaid
quadrantChart
  title "Когда Mermaid помогает"
  x-axis "Мало ясности" --> "Много ясности"
  y-axis "Мало влияния" --> "Много влияния"
  quadrant-1 "Показать схемой"
  quadrant-2 "Сначала распутать"
  quadrant-3 "Не тратить экран"
  quadrant-4 "Коротко текстом"
  "Путь заявки": [0.82, 0.86]
  "Сырая стратегия": [0.28, 0.82]
```

## Pie

```mermaid
pie title Заявки
  "Приняты" : 15
  "Уточнение" : 7
  "Отложены" : 2
```

## GitGraph

GitGraph полезен для развилки пути, не только для Git. Держи `id` короткими.

```mermaid
gitGraph
  commit id: "open"
  commit id: "catalog"
  branch clarify
  checkout clarify
  commit id: "brief"
  commit id: "details"
  checkout main
  commit id: "choice"
  merge clarify id: "ready"
  commit id: "accept"
```

Дополнительно:

```mermaid
gitGraph TB:
  commit id: "open"
  commit id: "choice" type: HIGHLIGHT
  branch clarify
  checkout clarify
  commit id: "details" tag: "risk"
```

## Kanban

Колонка: `id[Title]`. Задача внутри колонки: `taskId[Task title]`.

```mermaid
kanban
  Backlog[Нужно]
    task1[Собрать карточки]
    task2[Проверить форму]
  Doing[В работе]
    task3[Сравнить layout]
  Done[Готово]
    task4[Включить mermaid fit]
```

Metadata есть, но в Obsidian лучше не усложнять без нужды:

```mermaid
kanban
  Todo[Нужно]
    task1[Проверить заявку]@{ assigned: "MAVO", priority: "High" }
```

## Mindmap

Mindmap строится от отступов. Самая частая ошибка — сломать иерархию
неодинаковыми отступами.

```mermaid
mindmap
  root((MAVO))
    Каталог
      Карточки
      Фильтры
    Заявка
      {{Бриф}}
      Уточнение
      Оценка
    Заказ
      ))Счёт((
      Производство
      Выдача
```

Полезные формы: `id[квадрат]`, `id(rounded)`, `id((circle))`,
`id{{hexagon}}`, `id))bang((`, `id)cloud(`.

Иконки в mindmap (`::icon(...)`) считаются experimental; в Obsidian не обещай
их без проверки.

## Theme Frontmatter

Для новых Mermaid версий предпочтительнее frontmatter config, а не старые
`%%{init: ...}%%` directives. В Obsidian всё равно проверяй глазами.

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#eef2ff"
    primaryTextColor: "#1f2937"
    primaryBorderColor: "#7c3aed"
    lineColor: "#475569"
---
flowchart LR
  A["Каталог"] --> B["Заявка"] --> C["Оценка"]
```

Допустимые базовые themes в docs: `default`, `base`, `dark`, `forest`,
`neutral`. Для кастомных цветов используй `base`.

## classDef / linkStyle

```mermaid
flowchart LR
  A["Каталог"]:::source --> B["Заявка"]:::work --> C["Заказ"]:::done
  A -. "уточнение" .-> D["Правки"]:::warn

  classDef source fill:#e0f2fe,stroke:#0284c7,color:#0f172a
  classDef work fill:#eef2ff,stroke:#7c3aed,color:#1f2937
  classDef done fill:#dcfce7,stroke:#16a34a,color:#052e16
  classDef warn fill:#fff7ed,stroke:#f97316,color:#1f2937

  linkStyle 0 stroke:#475569,stroke-width:2px
  linkStyle 1 stroke:#f97316,stroke-width:2px,stroke-dasharray: 5 5
```

## ELK Layout

ELK — эксперимент в Obsidian. Парсер может принять config, но визуально
рендериться как обычный `dagre`.

```mermaid
---
config:
  layout: elk
  elk:
    mergeEdges: true
    nodePlacementStrategy: BRANDES_KOEPF
  flowchart:
    nodeSpacing: 60
    rankSpacing: 80
---
flowchart TB
  A["Вход"] --> B{"Данных хватает?"}
  B -->|да| C["Оценка"]
  B -->|нет| D["Уточнение"]
  D --> A
```

Если ELK не даёт явной визуальной пользы, дроби схему на несколько Mermaid.

## Источники

- Mermaid Flowchart docs: https://mermaid.js.org/syntax/flowchart.html
- Mermaid Sequence Diagram docs: https://mermaid.js.org/syntax/sequenceDiagram.html
- Mermaid Quadrant Chart docs: https://mermaid.js.org/syntax/quadrantChart.html
- Mermaid Pie docs: https://mermaid.js.org/syntax/pie.html
- Mermaid GitGraph docs: https://mermaid.js.org/syntax/gitgraph.html
- Mermaid Kanban docs: https://mermaid.js.org/syntax/kanban.html
- Mermaid Mindmap docs: https://mermaid.js.org/syntax/mindmap.html
- Mermaid Theme docs: https://mermaid.js.org/config/theming.html
- Mermaid Layout docs: https://mermaid.js.org/config/layouts.html
- Mermaid Directives docs: https://mermaid.js.org/config/directives.html
