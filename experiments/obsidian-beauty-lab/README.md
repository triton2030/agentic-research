# Obsidian Beauty Lab

Мини-эксперимент: насколько далеко можно довести обычный Markdown в Obsidian
без превращения его в отдельное приложение.

## Что открыть

- `00-obsidian-beauty-lab.md` — главная демонстрационная заметка.
- `02-iframe-and-clever-paths.md` — пробы iframe, локального HTML и других
  обходных визуальных путей.
- `03-meta-bind-and-obsidian-primitives.md` — широкая витрина Meta Bind,
  checkbox-statuses, callouts, embeds, tables, query, math и Mermaid.
- `04-custom-js-diagram.md` — прототип собственного Mermaid-like DSL на
  JavaScript: ссылка на HTML-страницу, SVG fallback и iframe-проба.
- `05-elk-square-svg.md` — `AtlasGrid`: ELK.js напрямую, локальная генерация
  квадратного SVG для inline-вставки в Obsidian.
- `06-skillmap-d2.md` — `SkillMap`: D2-диаграмма про работу `1*`-скилов с
  готовой типографикой и SVG export.
- `07-instruction-map-d2.md` — `InstructionMap`: более подробный D2-граф про
  работу инструкций, скилов, критериев и Obsidian-поверхности.
- `08-flowpage-react-flow-elk.md` — `FlowPage`: отдельная React Flow страница
  с zoom/pan, крупными HTML-узлами и ELK-раскладкой.
- `09-svg-file-embed.md` — красивый SVG лежит отдельным asset-файлом, а
  заметка встраивает его коротким wikilink.
- `01-beauty-board.canvas` — Canvas-вид той же идеи.
- `iframe-and-html.base` — Base-вид с формулой `html()`.
- `controls/meta-bind-mini-panel.md` — reusable control block для
  `meta-bind-embed`.
- `snippets/obsidian-beauty-lab.css` — CSS snippet для полного визуального
  слоя.
- `web-panels/mini-control-room.html` — локальная HTML-панель для iframe-пробы.
- `web-panels/tinyflow.js` и `web-panels/tinyflow-demo.html` — мини-библиотека
  и renderer кастомных диаграмм.
- `generated/tinyflow-demo.svg` — статический fallback для Obsidian, если
  интерактивный iframe не открылся.
- `data/elk-square-demo.json`, `scripts/render-elk-square-svg.js` и
  `generated/elk-square-demo.svg` — `AtlasGrid` no-server pipeline: JSON-граф,
  автоматическая раскладка и готовый квадратный SVG.
- `data/skillmap.d2`, `data/instruction-map.d2`,
  `scripts/render-d2-svg.mjs`, `generated/skillmap.svg` и
  `generated/instruction-map.svg` — D2 pipeline: готовый diagram renderer
  вместо самописных SVG-стилей.
- `flowpage.html`, `src/flowpage/**`, `vite.config.mjs` — React Flow + ELK
  prototype: отдельная страница для зумируемой карты.

## Граница

Это не новый канон проекта и не рабочий task-файл. Папка существует как
визуальный полигон: HTML показывает, что можно встроить прямо в заметку,
Mermaid показывает схему, а CSS snippet усиливает нативные callouts и страницу.

Obsidian читает snippets из `.obsidian/snippets/`; здесь CSS лежит как
source-файл эксперимента, потому что корневая `.gitignore` игнорирует
`.obsidian/`. Для проверки скопируй или синхронизируй содержимое
`snippets/obsidian-beauty-lab.css` в snippets-папку vault.
