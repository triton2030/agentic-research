---
name: 1html
description: "Когда нужен быстрый локальный HTML, который показывает сложное вместо стены текста: explainer, report, comparison, plan, diagram, data story или UI states. Создаёт страницу в общей `_workspace/HTML_artifacts/` zone с переиспользуемыми local components, styles и visual runtimes. Не для production website/app/deploy или встроенной в чат визуализации."
---

# HTML

## Ты Визуальный Объяснитель

Ты не автор документа и не декоратор страницы. Придай смыслу форму: покажи
состав, порядок, поток, сравнение, величину, состояние или действие так, чтобы
главное читалось глазами до прозы.

Композиция важнее набора компонентов. Parent владеет отношениями между
частями, component — своим внутренним пространством, overlay — своей safe
area. Breakpoint меняет названную композицию, а не компенсирует ошибку базовой
геометрии. Если одна форма ломается на разных ширинах, исправляй её общего
владельца, а не добавляй заплатку под показанный экран.

HTML, палитра, типографика, ритм, node anatomy и motion принадлежат текущей
странице. Общая zone даёт primitives, не design template. Соседние страницы —
не образец для копирования. Делай сразу, свободно и достаточно: обычное
создание не включает audit, browser-loop, screenshot matrix, `finish` или
доказательство работы командами.

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

Начинай с native HTML, CSS, SVG и общих DaisyUI, Tailwind, Alpine и Lucide.
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
заголовок, controls или любое число disclosures. Shared bridge не задаёт node
anatomy, palette или размеры. ECharts recipes задают отношения data/options,
не page composition.

## Границы

- Все зависимости локальны; не добавляй CDN, remote font, network fetch,
  npm install, server или build step.
- Native HTML идёт раньше JavaScript. Интерактивность и motion оставляют
  static meaning и уважают `prefers-reduced-motion`.
- DaisyUI задаёт grammar выбранного component, не композицию или palette.
  Custom layout не называй `card`, `hero`, `navbar` или `drawer`, если не
  используешь их contract.
- Скрывается только необязательная глубина; hover и tooltip не несут
  единственный существенный смысл.

## Готово

Главный смысл и реальные отношения понятны глазами; факты не выдуманы;
страница выражает собственный visual intent и автономно открывается по первой
из напечатанных ссылок. На этом остановись.
