# React Flow — Свободные Интерактивные Nodes

Бери React Flow, когда блоки со стрелками должны быть живыми: внутри узла есть
что нажать или раскрыть или по стрелкам надо показать течение. Схеме из
подписанных узлов без этого хватает Mermaid.

## Подключение

```html
<link href="lib/react-flow.css" rel="stylesheet">
<link href="assets/shared/react-flow-theme.css" rel="stylesheet">
<script defer src="lib/react-flow.vendor.js"></script>
<script defer src="assets/shared/react-flow-init.js"></script>
```

Предварительно собранный local IIFE, React Flow CSS, adapter и palette bridge
уже лежат в общей HTML_artifacts zone. Подключай их только на странице с
`data-react-flow`. Никакого dev server, CDN, import map, `fetch` или runtime
build.

## Граница Свободы

`<template>` здесь — только неактивный контейнер для произвольного DOM. Это не
design template и не предписанная анатомия node. Adapter переносит содержимое
как есть и не создаёт header/body/footer, card, accordion или icon.

Одна node может быть только emoji и короткой подписью, другая — большим
заголовком и двумя `<details class="collapse">`, третья — icon, текстом, form
controls и тремя disclosures. Количество, порядок, semantic tags, размеры и
responsive поведение задаёт сама страница в `assets/<slug>.css`. Совпавшие
button, badge, collapse, alert и другие anatomy внутри node остаются Daisy.

Bridge оставляет два стабильных hooks:

- `.rf-html-node` — прозрачный технический wrapper;
- `.rf-node-content` — корень перенесённого DOM.

Для разных форм передай обычный `className` в config, например `signal-node` и
`decision-node`. Не добавляй в shared bridge selectors внутренней разметки
node: `details`, `summary`, `button`, headings и cards принадлежат artifact.

## HTML Contract

Topology хранится в JSON, а содержимое каждой сложной node — в semantic HTML.
Пример намеренно показывает разные формы, а не каталог готовых карточек:

```html
<section aria-labelledby="flow-title">
  <h2 id="flow-title">Как данные проходят через заказ</h2>
  <p>Главный путь: сигнал → проверка → решение.</p>

  <template id="node-signal">
    <span aria-label="Новый сигнал">📨 Вход</span>
  </template>

  <template id="node-check">
    <section>
      <h3>Проверка заказа</h3>
      <p>Состав и срок подтверждаются отдельно.</p>
      <details class="collapse collapse-arrow border border-base-300">
        <summary class="collapse-title">Состав</summary>
        <ul class="collapse-content"><li>Позиции</li><li>Тираж</li></ul>
      </details>
      <details class="collapse collapse-arrow border border-base-300">
        <summary class="collapse-title">Срок</summary>
        <p class="collapse-content">Обещанная дата и запас.</p>
      </details>
    </section>
  </template>

  <template id="node-ready">
    <strong aria-label="Заказ готов">✓ Готово</strong>
  </template>

  <div data-react-flow="order-flow" aria-label="Поток данных заказа"></div>
  <script type="application/json" id="order-flow">
  {
    "nodes": [
      {"id":"signal","template":"node-signal","className":"signal-node"},
      {"id":"check","template":"node-check","className":"check-node"},
      {"id":"ready","template":"node-ready","className":"signal-node"}
    ],
    "edges": [
      {"id":"signal-check","source":"signal","target":"check","label":"получено"},
      {"id":"check-ready","source":"check","target":"ready","label":"подтверждено"}
    ]
  }
  </script>
</section>
```

```css
/* Это CSS текущего artifact, не часть React Flow add-on. */
[data-react-flow] {
  inline-size: 100%;
  block-size: min(44rem, 72vh);
  min-block-size: 28rem;
  overflow: clip;
  border: 1px solid var(--color-base-300);
  border-radius: var(--radius-box);
  background: var(--color-base-100);
}
.react-flow__node.signal-node { inline-size: 7rem; }
.signal-node .rf-node-content { padding: 0.8rem; border-radius: 999px; }
.react-flow__node.check-node { inline-size: 24rem; }
.check-node .rf-node-content { padding: 1.25rem; border-radius: 1.25rem; }
```

Runtime добавляет только аварийный `min-block-size`, если host вычислился в
ноль; обычную геометрию и surface всегда задай здесь сам.

Config root — object с массивами `nodes` и `edges`. Node требует уникальный
`id` и может получить `template`, короткий `label`, любые React Flow node
options и `data`. Template ID должен существовать. Edge требует уникальный
`id`, существующие `source`/`target`; default `dataFlow` показывает движение
пакета по линии.

## Раскладка Без Координат

Координаты узлам не пиши: адаптер измеряет узлы и раскладывает их по связям
(dagre), а после поздних стилей, шрифтов или раскрытия внутри узла раскладывает
заново, чтобы узлы не наехали друг на друга. Новый узел — строка в `nodes`,
новая стрелка — строка в `edges`; пересчитывать соседей не нужно.

Направление и промежутки — в `options.layout`:

```json
"options": {"layout": {"direction": "TB", "nodeGap": 48, "rankGap": 96}}
```

`direction` — `LR` (по умолчанию, слева направо), `RL`, `TB` (сверху вниз) или
`BT`; ручки узлов по умолчанию встают по этому направлению. Вид подгоняется под
рамку, пока читатель не тронул полотно.

Ручной `position` нужен только когда само место несёт смысл: карта, схема
помещения. Тогда `position` получает каждый узел; если хотя бы у одного его
нет, адаптер раскладывает все узлы сам и пишет предупреждение в консоль.
Вложенные sub-flows (`parentId`) раскладываются только вручную.

## Интерактивность В Node

Adapter ставит node content классы `nodrag nopan nowheel`: button, toggle,
accordion и внутренний scroll не двигают canvas. `ResizeObserver`, `toggle` и
`transitionend` обновляют node internals после любого изменения размера, чтобы
edges остались на handles.

Используй native controls. Не делай весь node кнопкой и не прячь главный вывод
внутри canvas. Рядом оставь короткое textual summary: source остаётся понятным
без JavaScript.

## Palette И Motion

Bridge наследует `font-family` и Daisy bumblebee roles: base surfaces,
`base-content`, `base-300` и `primary-content` для meaningful edge/selection.
При их отсутствии он использует system colors и `currentColor`, а не свою
палитру. Node composition может переопределить geometry variables в
`assets/<slug>.css`, но не вводит второй palette dialect.

Generated Pause/Play, load error и edge label используют Daisy `btn`, `alert`
и `badge`; page CSS отвечает только за их положение относительно canvas.

Animated edge показывает направление только для текущего потока. При
`prefers-reduced-motion: reduce` частица исчезает; статичная линия и label
сохраняют смысл. Бесконечный flow получает видимый Pause/Play.

На узком экране default показывает первую node в читаемом масштабе, а не
ужимает всё полотно до миниатюры; остальные nodes доступны pan. Только если
обзор topology важнее чтения node, задай `"fitViewOnMobile": true` в options.

## Официальные Опоры

- [React Flow custom nodes](https://reactflow.dev/learn/customization/custom-nodes)
- [React Flow utility classes](https://reactflow.dev/learn/customization/utility-classes)
- [React Flow handles](https://reactflow.dev/learn/customization/handles)
- [React Flow animating edges](https://reactflow.dev/examples/edges/animating-edges)
- [React Flow theming](https://reactflow.dev/learn/customization/theming)
