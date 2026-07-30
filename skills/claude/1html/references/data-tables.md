# DaisyUI + Alpine: Рабочие Таблицы

Читай эти карточки, когда artifact должен искать, фильтровать или сортировать
строки. DaisyUI владеет формой таблицы и controls; локальный Alpine helper
владеет только derived view. Полная HTML-страница здесь намеренно не хранится.

## Карточка: Таблица Нужна Для Общих Полей

**Сигнал:** читатель сравнивает несколько объектов по одинаковым признакам.

**Практика:** используй `<table>`, когда строки — однотипные объекты, а столбцы
имеют стабильный смысл. Назови таблицу через `<caption>` и оставь один объект
одной строкой.

**Не делай:** не превращай непрерывный рассказ, разные типы карточек или длинные
абзацы в сетку только ради компактности.

## Карточка: Добавить Интерактивность Готовым Bundle

Добавь helper только когда строки действительно нужно искать, фильтровать или
сортировать:

```bash
"<каталог skill>/scripts/add_table_bundle.sh" \
  "<artifact-name>" "<project-root>"
```

Подключи напечатанный script **после** `assets/pages.js` и
`assets/project.js`, но **до** `lib/alpine.js`. Для внутренней страницы
используй путь с `../assets/`.

```html
<script defer src="assets/pages.js"></script>
<script defer src="assets/project.js"></script>
<script defer src="assets/artifact-table.js"></script>
<script defer src="lib/alpine.js"></script>
```

Helper регистрирует `artifactTable()` и не добавляет CSS, зависимость или build
step.

## Карточка: HTML Остаётся Источником Данных

**Сигнал:** строки собираются вторично в JavaScript-массиве.

**Практика:** запиши все существенные строки обычными `<tr data-table-row>`.
Ячейке, которая участвует в фильтре или сортировке, дай стабильный
`data-table-key`. `data-table-value` нужен только когда машинное значение
отличается от видимого.

```html
<tbody data-table-body>
  <tr data-table-row>
    <th
      scope="row"
      data-table-key="title"
      data-table-value="Mockup Studio"
    >Mockup Studio</th>
    <td data-table-key="status" data-table-value="active">
      <span class="badge badge-success">Активно</span>
    </td>
    <td data-table-key="tags" data-table-value="mockup|prototype">
      mockup · prototype
    </td>
    <td data-table-key="score" data-table-value="92">92</td>
  </tr>
</tbody>
```

Для нескольких значений одного поля разделяй машинные tokens символом `|`.
Для даты оставляй в `data-table-value` ISO-формат, а в ячейке показывай
человеческую дату.

**Не делай:** не рисуй все строки через `x-for`, если данные уже известны при
создании artifact. Без JS таблица должна оставаться полным читаемым документом.

## Карточка: Один Контроллер На Таблицу

Минимальный root объявляет доступные filter keys. Поиск проверяет слова по всей
строке; filters соединяются через AND. Массив значений одного filter key тоже
означает AND — строка должна содержать каждый выбранный token.

```html
<section
  class="space-y-4"
  x-data="artifactTable({
    filters: { status: '', tags: [] },
  })"
>
  <div class="flex flex-wrap items-center gap-3" x-cloak>
    <label class="input input-sm">
      <i data-lucide="search" class="size-4" aria-hidden="true"></i>
      <input
        type="search"
        placeholder="Поиск по строкам"
        x-model.debounce.150ms="query"
      >
    </label>

    <select class="select select-sm" x-model="filters.status">
      <option value="">Все статусы</option>
      <option value="active">Активные</option>
      <option value="planned">Запланированные</option>
    </select>

    <button class="btn btn-sm btn-ghost" type="button" @click="reset()">
      Сбросить
    </button>

    <span class="text-sm opacity-70">
      <span x-text="visibleCount"></span> из
      <span x-text="rowCount"></span>
    </span>
  </div>

  <!-- table -->

  <div
    class="alert"
    x-cloak
    x-show="rowCount > 0 && visibleCount === 0"
  >Нет строк с таким набором условий.</div>
</section>
```

Для tag-buttons используй `toggleFilter('tags', 'prototype')` и
`filterActive('tags', 'prototype')`. Не создавай отдельное состояние рядом с
`artifactTable()`.

## Карточка: Сортировка Живёт В Заголовке

**Сигнал:** сортировка вынесена в далёкий select и связь со столбцом не видна.

**Практика:** оберни текст sortable column в настоящий `<button>`, а
`aria-sort` поставь на `<th>`. Helper поддерживает `string`, `number` и `date`;
пустые значения всегда остаются внизу.

```html
<th scope="col" :aria-sort="sortAria('score')">
  <button
    class="btn btn-sm btn-ghost"
    type="button"
    @click="toggleSort('score', 'number')"
  >Оценка</button>
</th>
```

Сортируемый заголовок должен отличаться не только цветом. Текст, иконка или
форма control показывают, что на него можно нажать.

## Карточка: DaisyUI Владеет Плотностью И Overflow

Начни с готовой композиции:

```html
<div class="overflow-x-auto rounded-box border border-base-300 bg-base-100">
  <table class="table table-sm table-zebra">
    <caption class="sr-only">Название и назначение таблицы</caption>
    <!-- thead + tbody -->
  </table>
</div>
```

- `table-sm` — default для рабочих матриц; `table-md` оставь коротким спискам;
- `table-pin-rows` добавляй только высокой таблице;
- badges держат короткие status/tag, а не предложения;
- длинное пояснение лучше открыть из строки через link или native dialog;
- не сжимай пять важных столбцов в мобильные карточки автоматически:
  горизонтальный scroll сохраняет сравнимость.

## Карточка: Граница Helper

Helper обслуживает десятки и умеренные сотни локальных строк. Он не владеет
редактированием ячеек, resize/reorder колонок, server pagination, виртуализацией
или тысячами записей. Такой сценарий уже является data-grid, а не быстрым
HTML-артефактом, и требует отдельного осознанного runtime.

Не подключай Alpine Sort для сортировки данных по столбцу: этот plugin
переставляет элементы drag-and-drop. `artifactTable()` уже владеет обычной
ascending/descending сортировкой.

## Короткие Failure Modes

- Search control работает, а строки исчезают без empty state.
- Видимое число сортируется как строка → передай тип `number`.
- Дата сортируется по русскому тексту → положи ISO в `data-table-value`.
- Filter сравнивает текст badge вместе с декором → задай точное машинное value.
- Вложенные controls делают всю строку одной кнопкой → оставь действия
  отдельными links/buttons.
- Helper подключён после Alpine → component не зарегистрируется.

## Официальные Опоры

- [daisyUI Table](https://daisyui.com/components/table/?lang=en)
- [daisyUI Filter](https://daisyui.com/components/filter/?lang=en)
- [Alpine x-data](https://alpinejs.dev/directives/data)
- [Alpine x-model](https://alpinejs.dev/directives/model)
- [Alpine Sort plugin](https://alpinejs.dev/plugins/sort)
- [W3C sortable table example](https://www.w3.org/WAI/ARIA/apg/patterns/table/examples/sortable-table/)
