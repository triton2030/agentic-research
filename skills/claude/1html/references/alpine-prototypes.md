# Alpine Для Быстрых Прототипов

Читай этот reference, когда HTML-артефакт показывает несколько состояний,
экранов, комментарии, синхронные controls или повторяемый prototype instrument.
Для обычного disclosure сначала используй нативные `details`, `dialog`, radio и
checkbox.

## Проверенный Snapshot

В skill локально закреплён Alpine `3.15.12`
([npm package](https://www.npmjs.com/package/alpinejs), актуальный release на
2026-07-30). Core подключается после собственного project JS и не требует CDN,
npm или build step:

```html
<script defer src="assets/project.js"></script>
<script defer src="lib/alpine.js"></script>
```

Официальная поверхность включает directives, magics, globals и плагины:
[directives](https://alpinejs.dev/directives/),
[`Alpine.data`](https://alpinejs.dev/globals/alpine-data),
[`Alpine.store`](https://alpinejs.dev/globals/alpine-store) и
[plugins](https://alpinejs.dev/plugins/).

## Главный Паттерн Проекта

Общая панель, список страниц и повторяемая логика живут в
`assets/project.js`. Конкретный HTML объявляет только свои состояния, данные и
комментарии:

```html
<body x-data="prototypeViewer({
  state: 'обычный',
  states: ['обычный', 'загрузка', 'пусто', 'ошибка'],
  comments: [
    {
      id: 'empty',
      title: 'Пустой исход',
      body: 'Причина и действие различимы.',
    },
  ],
})">
```

Не копируй одну и ту же панель или массив страниц во все HTML-файлы. Добавь
реальные экраны один раз в `ARTIFACT_PROJECT.pages`; dropdown в starter и
`pages/_template.html` подхватит список.

Страница прототипа по умолчанию показывает чистый интерфейс. Служебная панель,
комментарии и annotations включаются отдельно и не вплетаются в продуктовый
текст.

## Выбор Primitive

| Нужный эффект | Alpine primitive | Ограничение |
| --- | --- | --- |
| Выбрать состояние из dropdown | `x-model` + `x-show` | Список состояний хранится рядом с page data |
| Переключать частые состояния | `x-show` + `x-transition` | Добавь `x-cloak`, если начальное состояние скрыто |
| Создавать редкую тяжёлую ветку | `<template x-if>` | Один root; `x-transition` не поддерживается |
| Рисовать список или комментарии | `<template x-for>` | Один root и стабильный `:key` |
| Переиспользовать state/methods | `Alpine.data()` | Регистрируй в `alpine:init` до core startup |
| Реально общий state на странице | `Alpine.store()` | Не использовать вместо локального component state |
| Связать label/control ID | `x-id` + `$id()` | Полезно для повторяемых accessible controls |
| Читать DOM после реактивного update | `$nextTick` | Не заменяет обычную data flow |
| Реагировать на конкретное изменение | `$watch` | Не изменяй watched object внутри callback |

Официальные детали:
[`x-show`](https://alpinejs.dev/directives/show),
[`x-if`](https://alpinejs.dev/directives/if),
[`x-for`](https://alpinejs.dev/directives/for),
[`x-id`](https://alpinejs.dev/directives/id),
[`$nextTick`](https://alpinejs.dev/magics/nextTick) и
[`$watch`](https://alpinejs.dev/magics/watch).

## Что Не Надо Домысливать

- Core Alpine не является router: переход между HTML-файлами перезагружает
  страницу.
- State сам не переносится между страницами. Для действительно нужного
  сохранения используй `localStorage` или отдельно добавленный
  [Persist plugin](https://alpinejs.dev/plugins/persist); он не включён в
  bundle по умолчанию.
- Комментарии в starter — fixtures для разговора, а не база данных, совместное
  редактирование или export.
- Alpine не даёт HTML includes и не синхронизирует повторённую разметку между
  файлами. Общую логику выноси в JS; повторяемую разметку — только когда её
  второй реальный consumer оправдывает небольшой renderer.
- Официальные плагины `Mask`, `Intersect`, `Resize`, `Persist`, `Focus`,
  `Collapse`, `Anchor`, `Morph` и `Sort` доступны отдельно, но не являются
  обязательным комплектом. Добавляй один локальный plugin только под реальный
  повторяемый эффект; plugin script должен идти до Alpine core.

## Короткие Failure Modes

- Десятки полей и методов в inline `x-data` → вынеси component в
  `assets/project.js` через `Alpine.data`.
- Один global store для всех экранов → оставь page-local state локальным;
  store нужен только настоящим shared consumers на одной странице.
- `x-if` ради обычного toggle → используй `x-show`, чтобы сохранить DOM и
  получить transition.
- `x-for` без `:key` при сортировке → возможны неверные DOM associations.
- Скрытая ветка мелькает до старта Alpine → добавь `x-cloak`; базовый CSS уже
  включён в `theme.css`.
- `$watch` меняет тот же watched object → бесконечный реактивный цикл.

Готовый визуальный пример:
`references/daisy-examples/06-alpine-prototype.html`.
