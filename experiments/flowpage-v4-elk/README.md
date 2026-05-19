# FlowPage v4 — ELK workspace

Рабочая поверхность для агентных диаграмм поверх ELK. Не sandbox физики (это
v3), а попытка собрать **полезный workspace** с:

- ELK-раскладкой со сплайнами для рёбер по кнопке «Применить ELK»;
- сохранением полного snapshot'а графа (positions + routes + viewport +
  options + direction) в файл `data/layouts/<page>.json` через Vite-dev API;
- ELK-пресетом в том же snapshot-файле: slider'ы, select'ы и direction
  сохраняются сразу, но не меняют геометрию без «Применить ELK»;
- algorithm-aware UI: показываются только настройки, которые выбранный
  алгоритм ELK поддерживает;
- sidebar со страницами — несколько диаграмм в одном приложении;
- разными визуальными вариантами узлов по типу и весу — origin, skill, gate,
  doc, output, review, branch, truth.

Техническая карта внутренней механики: [`TECHNICAL.md`](./TECHNICAL.md).
Правила авторства графов для агента: [`GRAPH-AUTHORING.md`](./GRAPH-AUTHORING.md).

## Страницы из коробки

1. **Agent loop** — цикл работы агента: запрос → правда → почва → правка →
   проверка. Каноническая цепочка из `1start-here`.
2. **Галерея — все типы** — визуальный справочник node-типов и edge-стилей.
3. **Хуки — зачем** — как runtime hooks защищают дисциплину агента.
4. **Система планирования** — как README, PROJECT-ROADMAP и task-файлы
   связаны друг с другом, кто что владеет, куда течёт информация.
5. **Почему MAVO сработает** — смысловая карта позитивных факторов успеха:
   спрос, студии, каталог, доверие и экономика.

Новые страницы добавляются файлом в `src/pages/<slug>.js`. Viewer не хранит
скрытые браузерные страницы.

## Открыть

```bash
cd experiments/flowpage-v4-elk
npm install
npm run dev
```

Откроется на `http://127.0.0.1:5176/`.

## Развернуть в другом проекте

Этот тул — viewer графов с ручной правкой, который можно копировать как
есть и подключать к новому проекту.

```bash
# 1. Скопировать всю папку рядом с любым проектом
cp -r flowpage-v4-elk /путь/к/новому/проекту/graphs

# 2. Установить зависимости
cd /путь/к/новому/проекту/graphs
npm install

# 3. Если нужен полностью свой набор страниц — удалить встроенные
rm src/pages/agent-loop.js src/pages/planning-system.js src/pages/hooks-system.js src/pages/gallery.js

# 4. Попросить AI сгенерировать страницы под контекст нового проекта:
#    «создай src/pages/<slug>.js по схеме flowpage-v4-elk объясняющий <тему>»

# 5. Запустить
npm run dev
```

Граф сохраняется в `data/layouts/<slug>.json` целиком: положения, маршруты,
viewport и текущий ELK-пресет. Этот файл можно коммитить в git и переносить
вместе с viewer.

## Architecture

**Single source of truth — layout snapshot.** Файл `data/layouts/<page>.json`
содержит полное состояние одного графа:

```js
{
  positions: { nodeId: { x, y } },          // позиции узлов
  routes:    { edgeId: { sections, routing } },  // ELK-маршруты рёбер
  viewport:  { x, y, zoom },                // zoom/pan канваса
  options:   { algorithm, ...elkOptions },  // текущий ELK-пресет
  direction: "DOWN" | "RIGHT" | "UP" | "LEFT"
}
```

Принципы, выведенные на бумагу для будущего агента:

1. **Snapshot — единственная правда о графе.** Что в файле — то и на экране:
   позиции, маршруты, viewport и ELK-пресет. Загрузка страницы = чистое чтение
   snapshot'а, без алгоритмов.
2. **Settings сохраняются, но не применяются сами.** Slider'ы / select'ы /
   direction пишутся в тот же snapshot как пресет инструмента. Изменение
   настройки **не** меняет текущую геометрию, не запускает ELK. Неактуальные
   для выбранного алгоритма настройки скрываются.
3. **Apply ELK — единственный путь preset → geometry.** Явное действие
   пользователя. Берёт текущий пресет, прогоняет ELK, кладёт новый snapshot
   на диск.
4. **Drag — частичное обновление snapshot'а.** Новые positions, маршруты
   затронутых рёбер инвалидируются (sections=null → bezier fallback). После
   reload — та же фиксация состояния.
5. **Viewport — часть snapshot'а.** Зум/пан пользователя сохраняются с
   короткой задержкой, при reload восстанавливаются. Никакого автомагического
   `fitView`.
6. **Empty load = grid.** Если snapshot'а нет, оставляем grid-раскладку из
   `buildInitialNodes`. Пользователь жмёт «Применить ELK» сам.

Это убирает целый класс race conditions: settings → auto-apply → switch
страницы → save в неправильный pageId. Раньше эти случаи закрывались
накладками; теперь архитектурно не возникают.

## Файловая карта `src/`

- `main.jsx` — entry, монтирует `<App/>`.
- `App.jsx` — каркас: sidebar + canvas. Держит state `activeId` / `opts` /
  `direction`. Получает пресет из snapshot'а через `Page`, сохраняет его через
  `Page.savePreset`; layout не меняется, пока пользователь не нажмёт
  «Применить ELK».
- `Page.jsx` — оркестратор одной страницы. Создаёт `useNodesState` /
  `useEdgesState`, refs для async closures, подключает hooks
  (`useElkRunner`, `usePageLayout`), expose-ит `applyLayout` и `savePreset`
  через `useImperativeHandle`.
- `page/buildInitial.js` — pure-функции `buildInitialNodes/Edges` из
  page-данных (grid-раскладка до первого apply).
- `page/useElkRunner.js` — чистый ELK-калькулятор. Принимает
  `{nodes, edges, opts, direction}`, возвращает positioned nodes + edges
  с routes. Persistence не знает.
- `page/usePageLayout.js` — жизненный цикл snapshot: load при смене страницы
  (restore positions + routes + viewport + preset), autosave на drag/settings,
  команда `applyLayout`, сохранение viewport с короткой задержкой на
  `onMoveEnd` и guard'ом от ложной записи после restore.
- `page/PageCanvas.jsx` — рендер `<ReactFlow>` (Background, Controls,
  MiniMap, Panel). Без логики, без эффектов.
- `storage.js` — строгое file-only чтение/запись snapshot'а через
  `/api/layout/<id>`. Никаких browser fallback'ов и legacy-migration веток.
- `elk-layout.js` — `layoutWithELK` (обёртка над elkjs) + `DEFAULT_OPTIONS`
  + `SLIDER_DEFS` / `SELECT_DEFS` для UI. Здесь же живёт матрица
  algorithm → supported options. Edge routing hardcoded в
  `EDGE_ROUTING = "SPLINES"` только для `layered`; остальные алгоритмы
  сохраняют routes как `POLYLINE`.
- `nodes/` — node-типы для React Flow. **Auto-discovery**: `index.js`
  собирает `nodeTypes` map из `nodes/*.jsx`. Каждый файл default-exports
  компонент и named-exports `nodeType` (строка). `SkillCard.jsx` —
  универсальная карточка (kicker + title + body + bullets) с 4 handles.
- `ElkEdge.jsx` — кастомное ребро, рисует SVG path из `data.elkSections`
  (sections были посчитаны ELK'ом). Если sections нет — fallback на bezier
  (drag invalidate, или нет snapshot'а).
- `ui/CollapsibleSection.jsx`, `ui/Toast.jsx`, `ui/useToast.js` —
  UI-примитивы.
- `sidebar/PagesSection.jsx` / `CurrentPageSection.jsx` /
  `ElkSettingsSection.jsx` — секции левой панели.
- `pages/` — встроенные страницы. **Auto-discovery**: `index.js` собирает
  `BUILTIN_PAGES` через `import.meta.glob('./*.js')`. Каждый файл —
  default-export объекта `{ id, title, description, nodes, edges }`.
- `styles.css` — визуальный слой.

## Алгоритмы ELK

- **Layered** — основной режим для направленных агентных схем. Читает
  direction, spacing, layering, node placement и thoroughness; лучше всего
  борется с пересечениями в потоке.
- **MrTree** — дерево или spanning-tree взгляд на граф. Читает direction,
  node spacing и edge-node spacing.
- **Force** — сеть без направления. Direction, layering и edge spacing не
  применяются; полезны node spacing и iterations.
- **Stress** — сеть через равенство расстояний. Главная ручка —
  desired edge length; direction не применяется.
- **Radial** — только дерево: связный граф без циклов и multi-parent связей.
  Для обычных flow-страниц это не запасной “красивый layered”, а отдельный
  режим под tree-shaped данные.

## Как добавить новую страницу

1. Создай `src/pages/<slug>.js`:
   ```js
   export default {
     id: "my-page",
     title: "Моя страница",
     description: "одна строка",
     nodes: [
       { id: "n1", kind: "skill", weight: 2, title: "Узел 1",
         kicker: "kicker", body: "пояснение" },
       // ...
     ],
     edges: [
       ["n1", "n2", "label?"],
       // ...
     ]
   };
   ```
2. Перезапусти dev (Vite подхватит через `import.meta.glob`). Всё.

Snapshot страницы сохранится в `data/layouts/my-page.json` при первом Apply
ELK / drag / pan-zoom / изменении ELK-пресета.

## Как добавить новый тип узла

1. Создай `src/nodes/MyNode.jsx`:
   ```jsx
   export const nodeType = "myNode";
   export default function MyNode({ data }) {
     return <div className="my-node">{data.label}</div>;
   }
   export function nodeSize(data) {
     return { width: 200, height: 80 };
   }
   ```
2. В page-файле: `{ id: "x", type: "myNode", label: "..." }` или через helper в `_helpers.js`.
3. Стили — в `styles.css`.

## Палитра node-типов

Открой страницу «Галерея — все типы» в приложении — это визуальный
справочник.

- **SkillCard** (`card({...})`) — универсальная карточка: kicker, title,
  body, bullets. Стилизуется через `kind` (origin/skill/gate/memory/review/
  doc/output/branch/truth) + `weight` (1/2/3).
- **TextNote** (`note({ text, size })`) — текст без рамки, размеры s/m/l.
  Для аннотаций, заметок, мини-пояснений.
- **SectionHeader** (`header({ title, subtitle? })`) — крупный заголовок
  над группой. Без рамки, акцентный шрифт.
- **IconNode** (`icon({ icon, label?, tooltip? })` /
  `materialIcon({ icon, label?, tooltip? })`) — круглый узел с символом,
  emoji или Material Symbols Rounded. Маркер, breakpoint, иконка-связка.
- **Decision** (`decision({ title })`) — diamond для развилок и условий.
- **Quote** (`quote({ text, cite? })`) — выделенная цитата с акцентной
  полосой. Для важных формулировок и правил.
- **FileCard** (`file({ title, note? })`) — карточка-документ с явным
  значком расширения (.md, .json, .yaml, .js, …).

## Edge-варианты

В `edge(source, target, { kind })` и в tuple-форме автоматически
`solid`. Доступные `kind`:

- `solid` — обычное ребро (default).
- `dashed` — пунктир, для опциональных/альтернативных путей.
- `dotted` — точки, для аннотаций и слабых связей.
- `bold` — толстая линия, для главного пути.
- `dimmed` — приглушённый, для второстепенных связей.
- `accent` — яркий красный, для подчёркивания.

## Связано

- `../obsidian-beauty-lab/src/flowpage/` — v1 (ELK + estimateHeight).
- `../flowpage-v2/` — v2 (ELK + measured + race-guard).
- `../flowpage-v3-cola/` — v3 (cola.js physics эксперимент).
