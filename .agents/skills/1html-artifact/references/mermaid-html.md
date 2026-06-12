# Mermaid In HTML Artifacts

Читай, когда HTML-артефакт содержит Mermaid или нужно выбрать тип диаграммы.
Цель — чаще показывать структуру визуально, но не превращать диаграмму во
второй source of truth.

## Когда Добавлять

Добавляй Mermaid по умолчанию, если в материале есть хотя бы одно:

- порядок шагов, стадий или проверок;
- роли и обмен сообщениями;
- развилка решения или альтернативные пути;
- статусная карта, канбан-снимок или цепочка выбора;
- простые доли;
- карта смыслов, где mindmap реально короче текста.

Пропускай, если таблица, список из 3-5 пунктов или одна фраза читаются быстрее.

## HTML-Обёртка

Минимум:

```html
<pre class="mermaid">
flowchart TD
  A["Вход"] --> B["Проверка"] --> C["Выход"]
</pre>
<script src="mermaid-init.js"></script>
```

Лучший вариант с подписью:

```html
<figure class="diagram">
  <pre class="mermaid">
flowchart TD
  intake@{ shape: doc, label: "Вход" }
  owner@{ shape: diamond, label: "Owner ясен?" }
  html@{ shape: rounded, label: "HTML-артефакт" }

  intake --> owner
  owner -- "да" --> html
  owner -- "нет" --> intake
  </pre>
  <figcaption>Схема показывает маршрут чтения; правила остаются в тексте.</figcaption>
</figure>
```

Если диаграмм несколько:

```html
<div class="diagram-grid">
  <figure class="diagram">
    <pre class="mermaid">
pie title Статусы
  "готово" : 3
  "риск" : 1
    </pre>
    <figcaption>Снимок статусов.</figcaption>
  </figure>
  <figure class="diagram">
    <pre class="mermaid">
gitGraph TB:
  commit id: "вход"
  branch clarify
  checkout clarify
  commit id: "уточнить"
  checkout main
  merge clarify id: "решение"
    </pre>
    <figcaption>Развилка пути решения.</figcaption>
  </figure>
</div>
```

Подключай `<script src="mermaid-init.js"></script>` один раз перед `</body>`.

## Выбор Типа

- `flowchart TD` — процесс, owner-route, проверка, ветвление; `LR` только для
  3-5 коротких узлов.
- `sequenceDiagram` — кто кому что передаёт во времени.
- `quadrantChart` — сравнение по двум осям; русские и длинные labels бери в
  кавычки.
- `pie` — только простые доли, не аналитика с мелкими категориями.
- `gitGraph` — история развилки, путь решения, пользовательский путь.
- `kanban` — снимок состояния внутри артефакта; не task source of truth.
- `mindmap` — короткая карта формы/понятий; следи за отступами.

Если сомневаешься в синтаксисе, прочитай `1mermaid/references/syntax.md`.

## Стиль

Общий стиль живёт в `styles.css` и `mermaid-init.js`: тёплая палитра,
контрастный текст, dark mode, рамка, масштаб по ширине. В HTML-файле не
дублируй тему.

Для уникального смыслового акцента допустимы `classDef` и `linkStyle`, но только
после читаемой структуры. Не раскрашивай каждый узел отдельно: один акцент,
один warning и обычные нейтральные узлы обычно достаточно.

## Проверка

- Диаграмма имеет короткую подпись или соседний текст, объясняющий смысл.
- В сыром HTML блок понятен без рендера.
- Нет гигантского `flowchart LR`, который ужимается в микротекст.
- `mermaid-init.js` подключён один раз и лежит рядом с HTML-файлом.
- Mermaid не заменяет owner-док, цитату, таблицу данных или критерий проверки.
