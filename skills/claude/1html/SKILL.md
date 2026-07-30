---
name: 1html
description: "Когда нужен максимально быстрый локальный HTML-черновик или многоэкранный prototype: report, explainer, comparison, plan, diagram, deck, UI states и comments. Создаёт автономный project bundle, добавляет его в локальный каталог и использует готовый DaisyUI/Alpine vocabulary; fast path без проверок. Отдельный явный audit/cleanup существующего 1html artifact даёт необязательный visual anti-drift review. Не для production website, app или deploy."
---

# HTML

## Результат

Выдай переносимый локальный HTML-черновик с минимальной задержкой между запросом
и первым просмотром. При каждом запуске создай `_workspace/HTML_artifacts/` в
корне текущего проекта, если каталога ещё нет.

Корневой `index.html` — постоянная точка входа во все artifact projects. Каждый
его непосредственный дочерний каталог — один автономный проект: одна страница
либо связный набор экранов, состояний и комментариев.

```text
_workspace/HTML_artifacts/
├── index.html
├── _catalog/
└── <artifact-name>/
    ├── index.html
    ├── assets/
    │   ├── theme.css
    │   └── project.js
    ├── pages/
    └── lib/
```

Корневой каталог показывает по одной широкой строке на проект: название,
крупную иконку, теги, число внутренних страниц и относительную дату создания.
Название берётся из первого `<h1>`, если в `<head>` не задан точный
`artifact-title`.

```html
<meta name="artifact-title" content="Заголовок для каталога">
<meta name="artifact-icon" content="sparkles">
<meta name="artifact-tags" content="prototype, alpine, research">
```

Metadata принадлежит project entry, а не каждому внутреннему экрану.
`sources/` создавай только для реальных входных материалов, provenance или
вложений; CSS и runtime не являются источниками.

## Быстрый Старт

Из корня проекта создай artifact из готового рабочего starter:

```bash
"<каталог skill>/scripts/new_html_bundle.sh" "<artifact-name>"
```

Если текущая директория не является корнем проекта, передай корень вторым
аргументом. Скрипт создаёт нужные папки, обновляет каталог и печатает адреса
artifact и catalog.

Меняй `index.html`; `assets/theme.css` трогай только когда нужен другой
визуальный язык. Для дополнительных экранов копируй `pages/_template.html` и
один раз добавляй экран в `ARTIFACT_PROJECT.pages` внутри `assets/project.js`.
Общие тема, панель, навигация и state provider не копируются в каждый HTML.

После ручного удаления или переименования проектов обнови каталог:

```bash
"<каталог skill>/scripts/rebuild_html_catalog.sh" "<корень проекта>"
```

Starter — рабочий output asset, а не пример для чтения. Не открывай его целиком
до создания: скопируй и меняй только нужные места.

## Главный Контракт Смысла

До компонентов зафиксируй вопрос читателя, короткий ответ страницы и изменение:
что после неё можно понять, решить или сделать.

- одна страница выполняет одну информационную работу;
- первый экран даёт ориентацию и ответ, а не меню всех найденных тем;
- видимый хребет идёт от ответа к опоре и следующему ходу;
- скрывается только необязательная глубина, связанная с ближайшим тезисом;
- другая reader job получает внутреннюю страницу того же artifact project.

Catalog, dashboard и reference могут быть модульными: их единая работа
действительно состоит в поиске, мониторинге или сравнении элементов.

Артефакт понятен из исходного HTML без запуска JS: DOM следует ходу рассказа,
первый смысловой блок даёт краткий ответ, разделы имеют содержательные
заголовки и стабильные `id`, а существенный смысл выражен текстом и
семантической разметкой.

## Роутер Практик

Открывай только тот reference, без которого нельзя принять текущее решение. Не
читай все файлы подряд и не дублируй их правила в artifact.

| Сигнал задачи | Открыть | Чем владеет |
| --- | --- | --- |
| Нужно выстроить рассказ, иерархию, headings, длину строк или раскрытие | [`references/readable-design.md`](references/readable-design.md) | Читаемость, один вопрос, answer-first, связное progressive disclosure |
| Выбираются DaisyUI-компоненты, semantic colors или motion | [`references/daisy-storytelling.md`](references/daisy-storytelling.md) | Component semantics, native primitives, theme roles, анимация |
| Нужны UI states, dropdown, comments или связанные controls | [`references/alpine-prototypes.md`](references/alpine-prototypes.md) | State ownership, Alpine primitives, transitions, failure modes |
| Знание находится в связях, порядке, ветвлении или иерархии | [`references/mermaid-diagrams.md`](references/mermaid-diagrams.md) | Diagram choice, ELK, viewer, theming, accessibility |
| Сложный artifact многоэкранный, интерактивный или diagram-heavy | [`references/agent-readable-artifacts.md`](references/agent-readable-artifacts.md) | DOM-порядок, стабильные anchors, текстовые state/diagram outcomes, provenance |
| Пользователь отдельно просит audit красоты, cleanup или проверку style drift | [`references/visual-audit.md`](references/visual-audit.md) | Advisory visual review, DaisyUI fidelity, rhythm, intentional exceptions |
| Неизвестно точное имя DaisyUI-компонента | Точечный поиск в `references/daisyui-llms.txt` | Актуальная структура выбранного компонента |
| Неизвестно имя Lucide-иконки | Точечный поиск в `references/lucide-icon-names.txt` | Допустимое локальное имя иконки |

## Runtime-Границы

- Default art direction уже в starter и
  `references/editorial-style.png`: тёплая бумага, графит, крупный serif,
  моноширинные labels, тонкие контуры, спокойные sage/clay поверхности.
- Полный локальный DaisyUI bundle доступен. Сначала semantic component и theme
  role, затем Tailwind utilities для конкретной композиции.
- Visual authority: явный пользовательский или project-local reference →
  текущие starter/theme этого skill → semantic DaisyUI. Без явного reference
  starter/theme и DaisyUI остаются default. Соседние и старые artifacts —
  результаты, не примеры и не источник стиля.
- Сначала переиспользуй `.artifact-*` roles, semantic colors и уже выбранный
  spacing. Не создавай новую palette или числовую шкалу, если текущий owner уже
  выражает роль.
- Кастомная композиция, CSS или анимация допустима, когда помогает конкретному
  reader job и не выражается готовым vocabulary. Оставляй исключение локальным;
  не превращай его автоматически в новый default.
- Нативные links, `details`, `dialog`, radio и checkbox идут раньше Alpine.
- Alpine нужен только для связанных состояний и prototype instruments; общая
  логика живёт в `assets/project.js`.
- Lucide уже подключён. Иконка выбирается по смыслу, наследует `currentColor` и
  не остаётся единственным носителем значения.
- Mermaid добавляется только при diagram-задаче:

```bash
"<каталог skill>/scripts/add_mermaid_bundle.sh" "<artifact-name>" "<project-root>"
```

- Все зависимости локальны и закреплены; CDN, npm install, server и build step
  не нужны.

Интерактивность и motion допустимы, только когда сокращают путь к пониманию или
показывают реальное изменение состояния.

## Скорость

Это draft-local surface. Сразу верни постоянную ссылку на
`_workspace/HTML_artifacts/index.html`; direct link на текущий artifact добавляй
только когда он полезен.

При обычном создании не запускай server, browser, Playwright, QA, screenshot
loop, console check, responsive matrix или interaction audit.

Явный отдельный запрос на audit/cleanup — другой, необязательный maintenance
mode. Он может посмотреть текущий render или screenshot, если без этого нельзя
судить о визуальной цельности, но не блокирует artifact, не становится его
acceptance gate и не создаёт постоянный regression suite.

## Готово Когда

- создан `_workspace/HTML_artifacts/<artifact-name>/index.html`;
- корневой табличный каталог обновлён;
- каждая страница выполняет одну информационную работу;
- раскрываемые слои продолжают видимый тезис;
- artifact использует готовые общие assets и передаёт запрошенный смысл;
- пользователю дана постоянная ссылка на каталог;
- в обычном режиме не выполнены никакие проверки.
