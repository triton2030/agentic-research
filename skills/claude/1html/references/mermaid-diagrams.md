# Mermaid: Читаемые Диаграммы

Читай эти карточки, когда знание находится в связях, порядке, ветвлении или
иерархии. Runtime, ELK, viewer и init уже лежат в общей HTML_artifacts zone.

Подключение страницы:

```html
<link href="assets/shared/diagram-viewer.css" rel="stylesheet">
<script defer src="lib/mermaid.min.js"></script>
<script defer src="lib/mermaid-layout-elk.iife.min.js"></script>
<script defer src="lib/panzoom.min.js"></script>
<script defer src="assets/shared/diagram-viewer.js"></script>
<script defer src="assets/shared/mermaid-init.js"></script>
```

## Карточка: Диаграмма Показывает Связь

**Сигнал:** Mermaid используется как декоративная версия списка.

**Практика:** назови связь, которую показывает topology. Один тезис и
независимые карточки оставь обычным текстом или DaisyUI.

**Не делай:** не помещай абзацы в nodes; labels называют сущность, состояние
или действие.

## Карточка: Тип По Отношению

| Знание | Тип |
| --- | --- |
| Процесс, зависимости, развилка | `flowchart` |
| Порядок сообщений | `sequenceDiagram` |
| Состояния и переходы | `stateDiagram-v2` |
| Компактная иерархия | `mindmap` |
| Сравнение по двум осям | `quadrantChart` |
| План и события | `timeline`, `gantt` |
| Доли одного целого | `pie` |
| Величины/изменение с числовой осью | `xychart-beta` |

Chart-типы используют только реальные данные, единицы и labels. `-beta` syntax
закреплён текущим local bundle, но не является стабильным межверсионным API;
не делай его единственным носителем приёмочного результата.

## Карточка: Direction По Форме

**Сигнал:** `LR` создаёт длинную горизонтальную ленту.

**Практика:** `TB` — default для узких экранов, глубоких процессов и нескольких
кластеров. `LR` подходит короткому линейному маршруту. Сначала сократи labels и
число одновременных веток.

**Не делай:** не задавай SVG принудительный `min-width`.

## Карточка: ELK Только Для Сложности

**Сигнал:** есть несколько кластеров, cross-links, обратные петли или много
узлов.

**Практика:** простой graph оставь на `dagre`; сложный flowchart переключи на
`layout: elk`. Начни с defaults. `mergeEdges` и
`nodePlacementStrategy` меняй только под наблюдаемую проблему раскладки.

**Не делай:** ELK не превращает смешанные reader jobs в одну понятную схему.
Если topology остаётся стеной, раздели её по вопросу читателя.

## Карточка: DaisyUI Владеет Обрамлением

**Сигнал:** toolbar, пояснения и controls рисуются внутри diagram syntax.

**Практика:** DaisyUI владеет card, toolbar, legend, dialog и disclosure.
Mermaid владеет topology. Локальный init использует `theme: base` и переносит
computed cupcake surfaces, ink и brand-content line color в Mermaid. Он сам
переводит Daisy OKLCH в поддерживаемый Mermaid формат. Через
`window.HTMLMermaidConfig` можно менять layout/behavior, но не `theme`,
`themeCSS`, `themeVariables` или `fontFamily`: они всегда приходят из computed
artifact style и cupcake. Init-directive внутри diagram source тоже не
переопределяет эти palette/font keys.

Semantic node roles различай label и формой. Не вводи diagram-local palette
через `classDef`; status по-прежнему должен быть назван словами.

## Карточка: Viewer Для Реально Большой Схемы

**Сигнал:** fit-to-width делает labels нечитаемыми.

**Практика:** первый кадр показывает всю систему. Большая схема получает
локальный viewer с pan, wheel/pinch zoom, reset-to-fit и fullscreen. Viewer
инициализируется только после того, как Mermaid заменил definition на SVG.
Не копируй runtime в отдельную page-folder. Готовый viewer:

```html
<article
  class="card diagram-viewer border border-base-300"
  data-diagram-viewer
>
  <div class="card-body">
    <div class="diagram-viewer__canvas" data-diagram-canvas>
      <pre class="mermaid">
flowchart TB
  accTitle: Короткое имя схемы
  accDescr: Что показывает главный путь и развилка
  A[Вход] --> B{Проверка}
  B -->|Да| C[Готово]
  B -->|Нет| D[Исправить]
      </pre>
    </div>
  </div>
</article>
```

## Карточка: Текстовый Маршрут Остаётся

**Сигнал:** вывод доступен только через исследование графа.

**Практика:** рядом дай короткое резюме: что показано, главный путь, развилка и
вывод. В diagram definition задай `accTitle` и `accDescr`.

**Не делай:** цвет, spatial position и hover не остаются единственными
носителями смысла.

## Официальные Опоры

- [Mermaid layouts](https://mermaid.js.org/config/layouts.html)
- [Mermaid flowcharts](https://mermaid.js.org/syntax/flowchart)
- [Mermaid theming](https://mermaid.js.org/config/theming.html)
- [Mermaid accessibility](https://mermaid.js.org/config/accessibility)
