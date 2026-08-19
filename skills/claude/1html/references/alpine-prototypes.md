# Alpine: Быстрые Прототипы

Читай эти карточки, когда artifact показывает несколько UI states, dropdown,
comments, связанные controls или повторяемый prototype instrument. В scaffold
закреплён локальный Alpine `3.15.12`.

## Карточка: Native До Alpine

**Сигнал:** нужен один disclosure, modal или выбор без derived state.

**Практика:** сначала используй links, `details`, `dialog`, radio и checkbox.
Alpine оправдан, когда несколько controls меняют одну модель или нужно
разговаривать о состояниях интерфейса.

## Карточка: Один Владелец State

**Сигнал:** одна модель состояния объявлена inline в нескольких местах.

**Практика:** конкретный экран держит собственные states, fixtures и comments.
Повторяемую project-specific интерактивность вынеси в один asset с
`Alpine.data()` и подключи до `alpine.js`; HTML остаётся semantic source.

**Не делай:** не создавай global store для page-local state. `Alpine.store`
нужен только настоящим shared consumers на одной странице.

## Карточка: Чистый Экран По Умолчанию

**Сигнал:** annotations и служебная панель конкурируют с макетом.

**Практика:** artifact открывается в чистом состоянии. Comments, source overlay
и inspection tools включаются отдельно. Много states выбираются компактным
`select`, а не длинным рядом кнопок.

**Не делай:** не прячь за comments-toggle комментарии агента о неуверенности,
найденных ошибках и пробелах — это содержание страницы, а toggle скрывает
только разговорные fixtures прототипа.

## Карточка: Primitive По Жизненному Циклу

| Нужный эффект | Primitive | Ограничение |
| --- | --- | --- |
| Связать control и value | `x-model` | state остаётся рядом с page data |
| Часто показывать и скрывать | `x-show` | DOM сохраняется |
| Редко создавать тяжёлую ветку | `<template x-if>` | один root |
| Рисовать список | `<template x-for>` | стабильный `:key` |
| Переиспользовать state/methods | `Alpine.data()` | регистрация до startup |
| Читать DOM после update | `$nextTick` | не заменяет data flow |
| Реагировать на изменение | `$watch` | не меняет watched object |

## Карточка: Transition Только Для State

**Сигнал:** custom animation написана до выбора state primitive.

**Практика:** для `x-show` начни с `x-transition`: Alpine по умолчанию использует
fade + scale, 150 ms на вход и 75 ms на выход. Для чтения часто достаточно
`x-transition.opacity`. Custom classes получают `motion-safe:` и
`motion-reduce:`.

**Не делай:** `x-if` не поддерживает `x-transition`. Не добавляй delay,
масштабирование или движение, если они не объясняют смену состояния.

## Карточка: Не Домысливать Runtime

- Core Alpine не router; переход между HTML-файлами перезагружает страницу.
- State сам не переносится между страницами.
- Comments — fixtures для разговора, не база данных и не совместное
  редактирование.
- Alpine не даёт HTML includes.
- Persist, Focus, Collapse, Sort и другие plugins не входят в bundle.

Добавляй один локальный plugin только под реальный повторяемый эффект. Для
сохранения state используй `localStorage` или отдельно добавленный Persist.

## Карточка: Короткие Failure Modes

- Большой повторяемый inline `x-data` → отдельный project-specific asset с
  `Alpine.data`, подключённый до `alpine.js`.
- `x-for` без `:key` → неверные DOM associations после сортировки.
- Скрытая ветка мелькает → `x-cloak`; базовый CSS уже включён.
- `$watch` меняет тот же object → реактивный цикл.
- State хранится дважды → выбери одного owner и derived view.
- Lucide-иконка добавлена после init → вызови `lucide.createIcons()` после
  вставки DOM.

## Официальные Опоры

- [Alpine directives](https://alpinejs.dev/directives/)
- [Alpine x-show](https://alpinejs.dev/directives/show)
- [Alpine x-if](https://alpinejs.dev/directives/if)
- [Alpine x-transition](https://alpinejs.dev/directives/transition)
- [Alpine.data](https://alpinejs.dev/globals/alpine-data)
- [Alpine.store](https://alpinejs.dev/globals/alpine-store)
- [Alpine plugins](https://alpinejs.dev/plugins/)
