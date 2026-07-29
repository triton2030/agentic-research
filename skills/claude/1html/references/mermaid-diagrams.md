# Mermaid Диаграммы

## Выбор Формы

Используй Mermaid, когда ребро, порядок, ветвление или иерархия сами несут
знание. Один тезис, набор независимых карточек или декоративный flow остаются
обычным текстом и DaisyUI.

- `flowchart` — процесс, архитектура, зависимости и развилки;
- `sequenceDiagram` — сообщения и порядок взаимодействий;
- `stateDiagram-v2` — состояния и переходы;
- `mindmap` — компактная иерархия;
- `quadrantChart` — позиционирование объектов по двум осям.

Простой flowchart оставляй на `dagre`. Для нескольких кластеров, перекрёстных
связей, обратных петель или большого числа узлов включай ELK.

## Локальный Runtime

Добавь закреплённый Mermaid, ELK и viewer в уже созданный artifact:

```bash
"<каталог skill>/scripts/add_mermaid_bundle.sh" "<artifact-name>" "<project-root>"
```

Подключи стили в `<head>`:

```html
<link href="assets/diagram-viewer.css" rel="stylesheet">
```

Обёртка viewer-а:

```html
<div class="diagram-viewer" data-diagram-viewer>
  <div class="diagram-viewer__canvas" data-diagram-canvas>
    <pre class="mermaid">
flowchart TB
  A["Смысл"] --> B{"Есть развилка?"}
  B -->|да| C["Mermaid"]
  B -->|нет| D["DaisyUI"]
    </pre>
  </div>
</div>
```

Загрузи локальные scripts в конце `<body>` и инициализируй viewer только после
того, как Mermaid заменил text definition на SVG:

```html
<script src="lib/mermaid.min.js"></script>
<script src="lib/mermaid-layout-elk.iife.min.js"></script>
<script src="lib/panzoom.min.js"></script>
<script src="assets/diagram-viewer.js"></script>
<script>
  mermaid.registerLayoutLoaders(MermaidElkLayouts.default);
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
    theme: "base",
    themeVariables: {
      background: "#f4f0e7",
      primaryColor: "#dfe8dc",
      primaryTextColor: "#1b201d",
      primaryBorderColor: "#46664f",
      secondaryColor: "#dce8eb",
      tertiaryColor: "#f3ddd6",
      lineColor: "#656b65",
      clusterBkg: "#fbf8f1",
      clusterBorder: "#aaa69b"
    }
  });

  (async () => {
    await mermaid.run({ querySelector: ".mermaid" });
    HTMLDiagramViewer.initAll();
  })();
</script>
```

Для сложного flowchart добавь frontmatter в саму диаграмму:

```text
---
config:
  layout: elk
  elk:
    mergeEdges: false
    nodePlacementStrategy: NETWORK_SIMPLEX
---
flowchart TB
```

## Визуальные Правила

- DaisyUI владеет карточкой, toolbar, dialog, пояснениями и раскрытиями.
- Mermaid получает те же роли как hex через `themeVariables`; его theme engine
  не читает DaisyUI custom properties напрямую.
- `classDef` выделяет семантические роли узлов; цвет не остаётся единственным
  носителем смысла.
- Сначала показывай всю диаграмму целиком. Крупной схеме добавляй viewer:
  pan, wheel/pinch zoom, reset-to-fit и fullscreen.
- Не задавай Mermaid SVG принудительный `min-width`. Для узкого контейнера
  выбирай `TB` или viewer; `LR` с большой минимальной шириной создаёт
  недоступный горизонтальный overflow.
- Если даже с ELK схема остаётся стеной, раздели её по вопросу читателя.
