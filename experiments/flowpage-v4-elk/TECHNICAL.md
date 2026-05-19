# FlowPage v4 Technical Map

Этот файл объясняет, как устроен experiment `flowpage-v4-elk` изнутри. Он
должен помогать следующему агенту менять код без возврата к старой смешанной
модели.

## Главная Модель

FlowPage v4 — локальный viewer графов с ручной правкой и явным ELK-пересчётом.
Контент графа пишет AI в `src/pages/<slug>.js`; приложение показывает граф,
сохраняет визуальное состояние и даёт пользователю шлифовать картинку.

Есть три разных слоя:

- **Page source** — `src/pages/<slug>.js`. Это смысл графа: узлы, рёбра,
  подписи, типы карточек.
- **Layout snapshot** — `data/layouts/<slug>.json`. Это полная правда одного
  графа: позиции, маршруты рёбер, viewport и текущий ELK-пресет.
- **Runtime UI state** — React state в `App.jsx` / `Page.jsx`. Это только
  отображение текущего snapshot'а и текущих действий пользователя.

В коде не должно быть второго скрытого источника правды для графа. Нет
`localStorage` для layout, settings, custom pages или legacy fallback'ов.

## Snapshot Shape

`data/layouts/<id>.json` всегда хранит полный snapshot:

```json
{
  "positions": {
    "node-id": { "x": 120, "y": 80 }
  },
  "routes": {
    "source-target": {
      "sections": [
        {
          "startPoint": { "x": 10, "y": 20 },
          "bendPoints": [{ "x": 30, "y": 40 }],
          "endPoint": { "x": 50, "y": 60 }
        }
      ],
      "routing": "SPLINES"
    }
  },
  "viewport": { "x": 0, "y": 0, "zoom": 1 },
  "options": {
    "algorithm": "layered",
    "nodeNode": 110,
    "betweenLayers": 150,
    "edgeNode": 20,
    "edgeEdge": 15,
    "thoroughness": 10,
    "forceIterations": 300,
    "stressEdgeLength": 100,
    "radialRadius": 0,
    "nodePlacement": "BRANDES_KOEPF",
    "layering": "NETWORK_SIMPLEX"
  },
  "direction": "DOWN"
}
```

`storage.js` валидирует, что `positions`, `options` и `direction` есть. Если
snapshot сломан, это ошибка файла, а не повод искать запасную копию в браузере.

## Load Flow

При смене страницы `App.jsx` сбрасывает видимый ELK-пресет к default, чтобы в
sidebar не оставались значения прошлой страницы.

`Page.jsx` создаёт новый `ReactFlowProvider` через `key={page.id}`. Это
разворачивает чистый экземпляр React Flow для каждой страницы.

`usePageLayout` делает единственный load:

1. строит grid-состояние через `buildInitialNodes` / `buildInitialEdges`;
2. читает `data/layouts/<id>.json` через `/api/layout/<id>`;
3. если файла нет — оставляет grid и ждёт действия пользователя;
4. если файл есть — восстанавливает `positions`, `routes`, `viewport`;
5. передаёт `options` и `direction` наверх через `onPresetLoaded`.

На load нельзя запускать ELK. Загрузка страницы — только чтение snapshot'а.

## Save Flow

Сохранение всегда пишет весь snapshot в `data/layouts/<id>.json`.

- **Preset change**: slider/select/direction меняет `opts` / `direction` в
  `App.jsx` и вызывает `Page.savePreset(options, direction)`. Геометрия не
  пересчитывается.
- **Apply ELK**: `Page.applyLayout()` берёт текущий preset, запускает ELK,
  обновляет positions/routes, делает `fitView`, затем пишет полный snapshot.
- **Drag**: `onNodeDragStop` пишет новые positions и инвалидирует маршруты
  затронутых рёбер: `sections: null`. Так fallback-рисование честно показывает,
  что маршрут уже не ELK-calculated.
- **Viewport move**: `onMoveEnd` с задержкой 250 ms пишет новый viewport в тот
  же snapshot.

`usePageLayout` держит `saveQueueRef`, чтобы последовательные save'ы не
перепрыгивали друг друга.

## ELK Pipeline

`elk-layout.js` — единственное место, где формируется input для ELK.

Пайплайн:

1. `Page` держит React Flow nodes/edges.
2. `useElkRunner` вызывает `layoutWithELK(nodes, edges, opts, direction)`.
3. `layoutWithELK` строит ELK graph:
   - `children` получают размеры из `data.layoutWidth/layoutHeight`;
   - `edges` передаются как `sources` / `targets`;
   - `ports` и `portConstraints` не задаются.
4. ELK возвращает позиции узлов и `edge.sections`.
5. `useElkRunner` кладёт sections в `edge.data.elkSections`.
6. `ElkEdge.jsx` рисует SVG path из sections.

Важный инвариант: стороны входа/выхода рёбер не фиксируются заранее. ELK должен
сам выбирать геометрию рёбер из графа и выбранного алгоритма.

## Algorithm Matrix

Настройки не универсальны. `elk-layout.js` держит одну матрицу применимости,
которую используют и UI, и `buildLayoutOptions`.

- `layered` — основной режим для directed flow. Читает direction, spacing,
  layering, node placement, thoroughness. Рёбра сохраняются как `SPLINES`.
- `mrtree` — дерево / spanning-tree взгляд. Читает direction, node spacing,
  edge-node spacing. Рёбра сохраняются как `POLYLINE`.
- `force` — сеть без направления. Читает node spacing и iterations.
- `stress` — сеть через желаемую длину связи. Читает desired edge length.
- `radial` — только undirected tree. Перед ELK есть guard: граф должен быть
  связным деревом без циклов.

Если настройка не применима к выбранному алгоритму, она не показывается в UI и
не отправляется в ELK.

## Rendering

React Flow отвечает за canvas, drag, zoom/pan, controls и minimap.

`ElkEdge.jsx` отвечает за рёбра:

- `SPLINES` рисуются как cubic Bezier segments из ELK bend points;
- `POLYLINE` рисуется как ломаная;
- `sections: null` даёт fallback на обычный React Flow bezier.

Этот fallback нужен после ручного drag: позиции уже сохранены, но точный ELK
route для затронутых рёбер больше не правдив.

## File Map

- `src/App.jsx` — shell: active page, visible preset, sidebar, export PNG.
- `src/Page.jsx` — orchestration одной страницы и imperative API
  `applyLayout/savePreset`.
- `src/page/usePageLayout.js` — load/save lifecycle snapshot'а.
- `src/page/useElkRunner.js` — запуск ELK без persistence.
- `src/page/buildInitial.js` — page source → React Flow nodes/edges.
- `src/elk-layout.js` — ELK options, algorithms, validation, route extraction.
- `src/storage.js` — file-only snapshot API.
- `src/ElkEdge.jsx` — отрисовка ELK routes.
- `src/nodes/` — auto-discovery node types. `IconNode` поддерживает обычный
  текст/emoji и локально подключённый `Material Symbols Rounded`.
- `src/pages/` — auto-discovery built-in graph pages.
- `vite.config.mjs` — dev API `/api/layout/<id>` для чтения/записи JSON.

## Extension Rules

Чтобы добавить страницу, создай `src/pages/<slug>.js`. Не добавляй browser
storage, UI-editor и runtime-generated pages.

Чтобы добавить node type, создай `src/nodes/<Name>.jsx` с `default`, `nodeType`
и `nodeSize`. `nodes/index.js` подхватит файл автоматически.

Чтобы использовать Material Icons, вызывай `materialIcon({ icon: "rule" })` из
`src/pages/_helpers.js`. Шрифт подключён через npm-пакет
`@fontsource/material-symbols-rounded`, без runtime-запросов к Google Fonts.

Чтобы добавить ELK-настройку, обнови сразу оба места в `elk-layout.js`:

- UI definition: `SLIDER_DEFS` или `SELECT_DEFS`;
- actual ELK mapping: `buildLayoutOptions`.

Если настройка работает только для части алгоритмов, укажи `appliesTo`.

## Проверка После Правок

Минимальный технический smoke:

```bash
npm run build
```

Для поведения через браузер:

1. открыть `http://127.0.0.1:5176/`;
2. убедиться, что страница читает `data/layouts/<id>.json`;
3. изменить slider — файл обновился, геометрия не пересчиталась;
4. нажать «Применить ELK» — обновились positions/routes/options/direction;
5. подвигать узел — positions обновились, затронутые routes стали
   `sections: null`;
6. изменить zoom/pan — viewport сохранился и восстановился после reload.

Если после правки снова появляется `localStorage` для графа или пресета, это
почти наверняка возврат к старой ошибке архитектуры.
