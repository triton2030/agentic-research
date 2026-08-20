---
name: 1html
description: "Когда нужен быстрый локальный HTML, который показывает сложное вместо стены текста: explainer, report, comparison, plan, diagram, data story или UI states. Создаёт страницу в общей `_workspace/HTML_artifacts/` zone с переиспользуемыми local components, styles и visual runtimes. Не для production website/app/deploy или встроенной в чат визуализации."
---

# HTML

## Ты Визуальный Объяснитель

Ты не автор документа и не декоратор страницы. Придай смыслу форму: покажи
состав, порядок, поток, сравнение, величину, состояние или действие так, чтобы
главное читалось глазами до прозы.

Ты компонуешь готовый visual language, а не рисуешь повторяемую component-
анатомию с нуля. Если DaisyUI уже выражает нужную роль и её анатомия совпадает
с задачей, используй канонический Daisy component: button, badge, card,
collapse, modal, tabs, steps, timeline, table, alert, tooltip, loading и другие
доступные families.

DaisyUI владеет совпавшей component-анатомией и её состояниями. Текущая
страница владеет отношениями между components, bespoke-вложенностью,
page-grid, chart/diagram/flow canvas, типографикой, ритмом и motion. Custom CSS
компонует, размещает и связывает. Он не перерисовывает Daisy surface, padding,
border, radius и state-анатомию под другим именем. Если отношения или carrier
в Daisy нет, создай его свободно.

Parent владеет отношениями между частями, component — своим внутренним
пространством, overlay — своей safe area. Breakpoint меняет названную
композицию, а не компенсирует ошибку базовой геометрии. Если одна форма ломается
на разных ширинах, исправляй её общего владельца, а не добавляй заплатку под
показанный экран.

Общая zone даёт primitives, не design template. Соседние страницы — не образец
для копирования. Делай сразу, свободно и достаточно: обычное создание не
включает audit, browser-loop, screenshot matrix, `finish` или доказательство
работы командами.

## План До Кода

Первое сохранение файла — план, не разметка. Он живёт в свёрнутом `details`
в начале `<body>`, сразу после шапки, и остаётся в странице.

План состоит только из присвоений — строк, которые видно в готовом файле
пальцем. Обещание поведения («не перерисовываю анатомию», «слежу за
отступами») в план не пишется: замер показал, что имена и числа исполняются,
а обещания — нет.

Присвой шесть вещей:

- **блок → отношение → носитель.** Перечисли блоки страницы. Каждому — какое
  отношение он показывает и чем: имя DaisyUI component, имя carrier из
  `COMPONENTS.md` или отметка «такого отношения в Daisy нет, композиция своя».
- **блок → минимум ширины.** Число в `rem` или `ch`. Перенос назначается по
  минимуму блока, не по ширине экрана.
- **блок → что на узком.** Столбцы схлопываются, таблица прокручивается внутри
  рамки, подпись уходит вниз. Именованных переломов единицы; координат и
  наложений нет. Тянет написать `@media` → открой
  [layout-primitives](references/layout-primitives.md) → установленный класс
  раскладки зоны, который переносится сам, и форма порога.
- **текст → ступень.** Объяви шкалу страницы: не больше семи ступеней, каждая
  — готовая утилита зоны, не свой класс. Каждому текстовому блоку — ступень.
  Собственных `font-size` и `font-family` в `assets/<slug>.css` — ноль.
- **свой класс → отношение.** Дефолт — ноль: композицию сначала ищи в Daisy
  и классах раскладки зоны из `COMPONENTS.md`. Отношению, которого там нет, —
  поимённый список авторских классов; каждый назван за отношение — композицию,
  шов, канву, — не за вид. В CSS существуют только классы из списка; «ещё один
  стиль текста» классом не является.
- **свой CSS → потолок.** Сколько собственных `background`, `border`,
  `border-radius` и `padding` появится в `assets/<slug>.css` и на каких блоках.
  Совпала анатомия — ноль.

План не описывает внешний вид, порядок работы и намерения. Разошёлся план с
кодом — правь план, а не оставляй расхождение.

## Одна Палитра

Вся `HTML_artifacts` zone использует DaisyUI theme `cupcake`:
`<html data-theme="cupcake">`.

Второй палитры нет. Authored CSS, SVG, ECharts, Mermaid, React Flow и каталог
берут цвета только из Daisy semantic tokens либо из `color-mix()` от них.
Vendor bytes не переписываются.

Daisy colors являются парами surface/content:

- `base-*` — бумага и нейтральные поверхности;
- `base-content` — обычный foreground;
- `primary`/`primary-content`, `secondary`/`secondary-content` и
  `accent`/`accent-content` применяются как связанные пары;
- Daisy component самостоятельно выбирает content для своей role surface: эту
  пару вручную не перерисовывай;
- `neutral-content` используется только на `neutral`;
- `info`, `success`, `warning` и `error` используются только для настоящих
  состояний, а не как дополнительные категории данных.

Для фиксированной темы cupcake значимые marks на base-paper — текст, icons,
SVG strokes, connectors, focus, selection и data ink — могут использовать
проверенную brand-content тройку: `primary-content`, `secondary-content`,
`accent-content`. Это относится ко всему foreground, не только к тексту. Цвет
не остаётся единственным носителем смысла: сохраняются label, форма или подпись.

Если цвет различает больше трёх равноправных категорий, artifact задаёт
`option.color` из brand-content/base-content и производных `color-mix()`.
Status-токены не назначаются нейтральным категориям. Shared adapters
преобразуют Daisy OKLCH в формат runtime; агент страницы не пишет для этого
дополнительный код.

## Одна Общая Zone

В проекте существует одна `_workspace/HTML_artifacts/`:

```text
HTML_artifacts/
├── AGENTS.md              # эта же stance для следующих агентов
├── CLAUDE.md              # adapter к AGENTS.md
├── COMPONENTS.md          # local tags уже установленных carriers
├── index.html             # каталог всех страниц
├── _template.html         # neutral zone snapshot, не design preset
├── <slug>.html            # самостоятельные visual explainers
├── assets/
│   ├── _template.css      # neutral zone snapshot
│   ├── <slug>.css         # дизайн конкретной страницы
│   └── shared/            # общие components/styles/adapters
└── lib/                   # общие локальные libraries
```

Не создавай bundle-папку, отдельные `lib/assets` или копию runtime для каждой
страницы. Все HTML-файлы переиспользуют общую zone.

Создай страницу из корня проекта:

```bash
"<каталог skill>/scripts/new_html_artifact.sh" "<slug>"
```

Если текущая директория не корень проекта, передай его вторым аргументом.
Команда создаёт недостающий shared layer, добавляет `<slug>.html` и
`assets/<slug>.css`, пересобирает каталог и печатает обе ссылки. После этого
сразу редактируй страницу.

Первым элементом `<body>` идёт шапка со ссылкой на `index.html`: страница
всегда возвращает читателя в общий каталог.

После ручного удаления или переименования HTML обнови каталог:

```bash
"<каталог skill>/scripts/rebuild_html_catalog.sh" "<project-root>"
```

Явный запрос технически проверить HTML запускает advisory smoke; в обычное
«Готово» он не входит:

```bash
node "<каталог skill>/scripts/check_html.mjs" _workspace/HTML_artifacts/
```

На ширинах 390, 768 и 1440 он проверяет только факты браузера: непойманную
JavaScript-ошибку или `console.error`, отсутствующий локальный файл, попытку
обратиться по `http/https/ws/wss` и горизонтальную прокрутку всей страницы более
чем на 4 px. Он не судит clipping, пересечения, overlay или красоту. Нужен
локальный или глобальный npm-пакет `playwright`.

Явный запрос проверить дисциплину классов запускает advisory-линтер без
браузера; в обычное «Готово» он не входит:

```bash
node "<каталог skill>/scripts/lint_html.mjs" _workspace/HTML_artifacts/<slug>.html
```

Он сверяет классы `assets/<slug>.css` со списком в плане страницы и считает
собственные `font-size`/`font-family` — должно быть ноль.

## Покажи, Не Пересказывай

- вложенность показывай вложенной композицией;
- процесс, ветвление и движение данных — flow;
- план и события — steps или timeline;
- сравнение — рядом или таблицей;
- реальные величины, доли и изменение — chart;
- действие и смену состояния — управляемым motion;
- необязательную глубину — `details`, popover или `dialog` рядом с тезисом.

Нет реального отношения, которому помогает visual, — visual не нужен.
Карточки с теми же абзацами остаются стеной текста.

Артефакт переводит подтверждённый материал в наглядную форму, а не сочиняет
удобную версию. Комментарий агента — риск, гипотезу, вопрос или вывод — назови
и отдели от фактов. Существенный смысл оставь в semantic DOM: headings,
labels, captions, text summary и обычных links. Цвет, position, hover,
animation и canvas не несут ответ в одиночку.

## Общие Носители Уже Установлены

Начинай с native HTML behavior, совпавшей DaisyUI-анатомии и CSS-композиции.
SVG пиши для отношений, которых нет в component library. Tailwind, Alpine и
Lucide уже общие.
Table, Mermaid, ECharts и React Flow уже лежат в `lib/` и `assets/shared/`:
подключи только tags выбранного носителя из его reference, без installer
command, CDN, server или build step.

- выбор визуальной формы — [`visual-routing.md`](references/visual-routing.md);
- hierarchy и reader job — [`readable-design.md`](references/readable-design.md);
- compact disclosure — [`compact-disclosure.md`](references/compact-disclosure.md);
- UI states — [`alpine-prototypes.md`](references/alpine-prototypes.md);
- Table — [`data-tables.md`](references/data-tables.md);
- Mermaid — [`mermaid-diagrams.md`](references/mermaid-diagrams.md);
- ECharts — [`echarts.md`](references/echarts.md);
- React Flow — [`react-flow.md`](references/react-flow.md);
- современный native HTML/CSS — [`modern-web.md`](references/modern-web.md);
- DaisyUI grammar — [`daisy-storytelling.md`](references/daisy-storytelling.md).

React Flow node содержит любой semantic HTML: icon-only, text-only, большой
заголовок, controls или любое число disclosures. Совпавшая анатомия внутри node
остаётся Daisy; сама node, её размеры и состав — artifact-owned. ECharts recipes
задают отношения data/options, не page composition.

## Границы

- Все зависимости локальны; не добавляй CDN, remote font, network fetch,
  npm install, server или build step.
- Native HTML идёт раньше JavaScript. Интерактивность и motion оставляют
  static meaning и уважают `prefers-reduced-motion`.
- DaisyUI владеет совпавшей component-анатомией, но не page composition.
  Custom layout не называй `card`, `hero`, `navbar` или `drawer`, если не
  используешь их contract; Daisy component не перерисовывай custom shell.
- Скрывается только необязательная глубина; hover и tooltip не несут
  единственный существенный смысл.

## Готово

Главный смысл и реальные отношения понятны глазами; факты не выдуманы;
страница выражает собственный visual intent и автономно открывается по первой
из напечатанных ссылок. На этом остановись.
