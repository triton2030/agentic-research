# Современный HTML И CSS — Native First

Снимок решений на 2026-08-20. Читай, когда новая browser capability может
заменить JavaScript или сделать причинность/раскрытие понятнее. Это не showcase:
каждая возможность должна улучшать текущую reader job и иметь static fallback.

## Надёжный Default

### Native Accordion

Группа `<details name="group">` образует mutually-exclusive accordion без JS.
Используй только для связанных однотипных глубин; главный смысл остаётся
видимым. В одной группе не ставь `open` более чем одному элементу и не вкладывай
одноимённую группу в себя.

### Popover

`popover` + `popovertarget` дают top layer, light dismiss и управление без JS.
Подходит короткому необязательному контексту или набору локальных действий.
Расположи popover рядом с trigger в DOM. Обязательное содержание и длинную
задачу оставь на странице либо в `<dialog>`.

### Dialog

`<dialog>.showModal()` — редкая сфокусированная задача с modal semantics.
Явно выбери начальный focus через `autofocus`. Закрытая страница остаётся
понятной без содержимого dialog.

### Entry/Exit Motion

`@starting-style` и `transition-behavior: allow-discrete` позволяют мягко
показывать top-layer/discrete элементы. Без поддержки элемент просто появляется;
это и есть fallback. Motion получает `prefers-reduced-motion`.

## Progressive Enhancement

### Anchor Positioning — Baseline 2026

CSS anchor positioning связывает popover/label с trigger без ручного JS.
Используй `@supports (top: anchor(bottom))`; базовая позиция должна оставаться
рабочей в старом браузере. Это размещение, не новый способ скрыть смысл.

### Scroll-driven Animations

`animation-timeline: scroll()`/`view()` связывает motion со scroll, а не с
часами. Используй только для одного visual, чьи состояния действительно
объясняют изменение. Оберни в `@supports` и оставь финальное статическое
состояние по умолчанию.

### Same-document View Transitions

`document.startViewTransition()` может показать связь между двумя DOM states.
Всегда вызывай через feature detection и сначала реализуй обычное обновление.
Cross-document transitions не являются контрактом локального `file://`
artifact: origin/support неоднородны.

## Experimental — Не В Основной Путь

`interpolate-size: allow-keywords` и `calc-size()` упрощают animation к
intrinsic size, но в 2026 ещё не Baseline. Допустимы только внутри `@supports`
с обычным открытием без animation. Не включай их в acceptance и не заменяй ими
native disclosure semantics.

## Опоры

- [WHATWG: details and exclusive groups](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-details-element)
- [WHATWG: Popover](https://html.spec.whatwg.org/multipage/popover.html)
- [MDN: `@starting-style`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40starting-style)
- [MDN: CSS anchor positioning](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/anchor)
- [MDN: scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations)
- [MDN: View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)
- [MDN: `interpolate-size`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/interpolate-size)
