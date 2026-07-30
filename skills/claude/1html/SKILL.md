---
name: 1html
description: "Когда нужен максимально быстрый локальный HTML-черновик или многоэкранный prototype: report, explainer, comparison, plan, diagram, deck, UI states и comments. Создаёт автономный project bundle, добавляет его в табличный локальный каталог с тегами и использует готовые DaisyUI/Alpine assets; без browser/Playwright-проверок. Не для production website, app или deploy."
---

# HTML

## Результат

Выдай переносимый локальный HTML-черновик с минимальной задержкой между запросом
и показом. При каждом запуске сначала создай `_workspace/HTML_artifacts/` в
корне текущего проекта, если каталога ещё нет. Корневой `index.html` — одна
постоянная точка входа во все **artifact projects**. Каждый непосредственный
дочерний каталог — один автономный проект: одна входная страница либо связный
набор экранов, состояний и комментариев.

```text
_workspace/
└── HTML_artifacts/
    ├── index.html
    ├── _catalog/
    │   ├── assets/
    │   └── lib/
    └── <artifact-name>/
        ├── index.html              # project entry
        ├── assets/
        │   ├── theme.css
        │   └── project.js          # shared Alpine state/navigation
        ├── pages/                  # optional internal screens
        │   ├── _template.html
        │   └── <screen>.html
        └── lib/
            ├── daisyui.css
            ├── daisyui-themes.css
            ├── tailwind.js
            ├── alpine.js
            └── lucide.min.js
```

Корневой каталог показывает по одной широкой строке на artifact project:
название, крупную иконку, теги, число внутренних страниц и относительную дату
создания. Он не перечисляет проекты в верхней навигации и не выводит внутренние
страницы отдельными строками.

По умолчанию название проекта берётся из первого `<h1>`. Для точного
preview-title, крупной иконки и фильтруемых тегов задай в `<head>`:

```html
<meta name="artifact-title" content="Короткий заголовок для каталога">
<meta name="artifact-icon" content="sparkles">
<meta name="artifact-tags" content="prototype, alpine, research">
```

Пустой `artifact-title` сохраняет fallback на первый `<h1>`; пустой
`artifact-icon` оставляет строку без иконки. `artifact-tags` — разделённые
запятыми project-level tags; каталог даёт multi-tag filter и сортировку по
новизне, названию или первому тегу. Внутренний экран не дублирует metadata:
owner проекта — `<artifact-name>/index.html`.

`_catalog/` хранит общие локальные стили и runtime.
`<artifact-name>/index.html` — вход в проект; дополнительные экраны живут в
`pages/` и используют его assets.
Повторяемые цвета, типографика, ритм и layout-роли принадлежат
`assets/theme.css`, общая Alpine-логика и список экранов —
`assets/project.js`. `lib/` — локальные закреплённые зависимости; CDN, npm
install и build step не нужны. Lucide даёт локальные именованные SVG-иконки,
которые наследуют цвет активной DaisyUI-темы через `currentColor`.

`sources/` создавай только когда у артефакта есть реальные входные материалы,
provenance или вложения. Не называй CSS и runtime-файлы «источниками».

## Быстрый Старт

Для нового artifact project из корня проекта скопируй готовый starter:

```bash
"<каталог skill>/scripts/new_html_bundle.sh" "<artifact-name>"
```

Если рабочая директория не является корнем проекта, передай его вторым
аргументом. Скрипт сам создаёт `_workspace/HTML_artifacts/`, обновляет каталог и
печатает два адреса: новый artifact и постоянный catalog.

Затем меняй `index.html` и, если визуальный язык действительно отличается,
малую часть `assets/theme.css`. Для дополнительных экранов копируй
`pages/_template.html`, добавляй каждый экран один раз в
`ARTIFACT_PROJECT.pages` внутри `assets/project.js`. Project navigation живёт
внутри проекта; корневой каталог остаётся списком проектов. Не переписывай
runtime, тему, panel или список экранов в каждом HTML.

После ручного удаления или переименования папок обнови каталог:

```bash
"<каталог skill>/scripts/rebuild_html_catalog.sh" "<корень проекта>"
```

## Сюжет Перед Компонентами

До разметки сформулируй narrative spine: что происходит → главный вывод → почему
он важен → что делать дальше. DaisyUI здесь не декор, а готовый словарь
смысловых ходов.

Раздели материал на три слоя:

- **must-see** — заголовок, главный вывод, действие и критический риск; всегда
  видимы;
- **on-demand** — evidence, источники, оговорки, примеры и технические детали;
  прячутся в `collapse` / accordion, а равноправные альтернативы — в `tabs`;
- **omit** — всё, что не помогает текущей задаче читателя; не выводится.

Выбирай форму по смыслу: `steps` для процедуры, `timeline` для хронологии,
side-by-side или `diff` для сравнения, `chat` для разговора, `stats` для чисел,
`tabs` / `swap` для альтернативных представлений. Не прячь основной вывод,
действие или критический риск. `tooltip` и `carousel` содержат только
необязательный материал.

`badge` — короткий статус или ярлык, не предложение. Если текст может занять
несколько строк, используй обычный текст, heading, `alert`, `card` или
`collapse-title`. Общая тема страхует случайный перенос, но не делает длинную
фразу правильным badge.

## Визуальный Язык

Default art direction уже зашит в starter и сохранён в
`references/editorial-style.png`: тёплая бумага, графитовый текст, крупный
редакционный serif, моноширинные labels, тонкие контуры, спокойные sage/clay
карточки и щедрый ритм. Явный пользовательский или project-local референс сильнее
этого default.

Полный локальный DaisyUI bundle доступен: выбирай любой компонент закреплённой
версии, а не только знакомый короткий набор. Начинай с DaisyUI component
(`card`, `badge`, `menu`, `btn`, `alert`, `collapse`, `tabs`, `table` и
остальные), применяй semantic colors (`primary`, `base`, `success`, `warning`,
`error`), затем добавляй Tailwind utilities для конкретной композиции. Не
закрепляй случайные palette colors и SVG fill/stroke, если ту же роль выражает
тема. Стабильная повторяемая роль принадлежит `theme.css`; одноразовое
расположение может остаться utility-классом.

## Alpine И Многоэкранные Прототипы

Нативные `details`, `dialog`, links, radio и checkbox остаются самым быстрым
выбором для простого disclosure. Используй уже локальный Alpine, когда
артефакту нужны несколько значимых состояний, dropdown-переключатель,
комментарии/annotations, связанные controls, derived UI или общий prototype
instrument.

Повторяемая логика проекта живёт в `assets/project.js` через `Alpine.data`;
страница объявляет только собственные `state`, `states`, fixtures и comments.
Чистый интерфейс — default: comments, source overlays и служебная панель
выключены при открытии. Для множества состояний выбирай компактный `select`, а
не ряд кнопок, который начинает закрывать макет.

- `x-model` связывает dropdown и state;
- `x-show` держит частые состояния в DOM и поддерживает `x-transition`;
- `x-if` создаёт редкую тяжёлую ветку, но требует `<template>` с одним root и
  не поддерживает transition;
- `x-for` требует один root и стабильный `:key`;
- `x-cloak` скрывает ветку до старта Alpine; базовый CSS уже включён;
- `$nextTick` нужен только для DOM после реактивного update;
- `$watch` не должен менять тот же watched object.

Core Alpine не является router и не переносит state между HTML-файлами.
Страницы остаются обычными локальными links. Persist, Focus, Collapse, Sort и
другие официальные plugins не входят в bundle: добавляй один локально только
под реальный повторяемый эффект.

Точные patterns, verified snapshot, project provider, официальные ссылки и
failure modes читай только для интерактивных prototype-задач в
[`references/alpine-prototypes.md`](references/alpine-prototypes.md).

## Иконки

Lucide уже подключён starter-ом. Используй именованную иконку без inline SVG:

```html
<button class="btn btn-primary">
  <i data-lucide="sparkles" class="size-4" aria-hidden="true"></i>
  Создать артефакт
</button>
```

Выбирай иконку по смыслу, а не для заполнения пустоты. Одна крупная иконка может
держать тему карточки или секции; не превращай каждый label в пиктограмму.
Иконка наследует цвет текста или semantic color через `currentColor`. Для
декоративной иконки ставь `aria-hidden="true"`; icon-only control получает
видимый `tooltip` и `aria-label`. Критический смысл никогда не передавай только
иконкой.

Оптимизируй форму под задачу чтения или решения: сравнения рядом, sequence как
flow/timeline, hierarchy как structure. Интерактивность добавляй только когда она
сокращает путь к пониманию. Если пользователь меняет данные внутри артефакта,
дай явный выход обратно в работу: copy as prompt, JSON, Markdown или уместный
export.

Для plan покажи порядок, зависимости, владельцев и статус; декоративная
сложность вторична. Для architecture/stack diagram сделай диаграмму главным
содержанием и сократи prose. Click, animation и смена темы нужны только когда
помогают чтению.

## Mermaid

Используй Mermaid, когда знание находится в связях, порядке, ветвлении или
иерархии. Один тезис, независимые карточки и декоративный flow оставляй текстом
или DaisyUI-компонентами.

- `flowchart` — процесс, архитектура, зависимости и развилки;
- `sequenceDiagram` — порядок сообщений;
- `stateDiagram-v2` — состояния и переходы;
- `mindmap` — иерархия;
- `quadrantChart` — сравнение по двум осям.

Простую схему оставляй на стандартной раскладке. Для нескольких кластеров,
перекрёстных связей, обратных петель или большого числа узлов используй ELK.
Стилизуй Mermaid через `theme: base`, hex-зеркало семантических цветов DaisyUI,
малый `themeCSS` и `classDef`; цвет не остаётся единственным носителем смысла.

Крупная диаграмма сначала показывает всю систему целиком и получает локальный
viewer с pan, wheel/pinch zoom, reset-to-fit и fullscreen. Не форсируй
`min-width` у SVG: для узкого контейнера выбирай `TB` или viewer. Добавь готовый
runtime:

```bash
"<каталог skill>/scripts/add_mermaid_bundle.sh" "<artifact-name>" "<project-root>"
```

Точный шаблон HTML, инициализации, ELK и темизации читай только для Mermaid-задач
в [`references/mermaid-diagrams.md`](references/mermaid-diagrams.md).

## Примеры И Документация

Не загружай галерею на fast path: starter уже является рабочим default. Если
задача требует другой композиции, открой
`references/daisy-examples/index.html` и выбери один ближайший пример. Все
примеры — часть этого skill и используют тот же `theme.css`, локальную DaisyUI
и локальный Tailwind runtime, что и starter.

Для богатого объяснения с несколькими смысловыми ходами используй компактную
карту `references/daisy-storytelling.md`. Она связывает задачу читателя,
компонент DaisyUI и правило раскрытия, не превращая основной contract в каталог.
Для UI states, dropdown и comments ближайший готовый пример —
`references/daisy-examples/06-alpine-prototype.html`.

Если неизвестно точное имя DaisyUI-компонента, ищи только нужный термин в
`references/daisyui-llms.txt`; не читай файл целиком.

Если неизвестно имя Lucide-иконки, ищи один смысловой термин в
`references/lucide-icon-names.txt`. Не загружай весь список в контекст.

## Скорость

Это draft-local surface. Сразу верни одну постоянную ссылку на
`_workspace/HTML_artifacts/index.html`; direct link на текущий artifact добавляй
только когда он действительно полезен. Не запускай server, browser, Playwright,
QA, screenshot loop, console check, responsive matrix или interaction audit. У
этого skill нет проверки ни по умолчанию, ни по запросу.

## Готово Когда

- `_workspace/HTML_artifacts/<artifact-name>/` создана и содержит `index.html`;
- корневой табличный каталог обновлён и показывает explicit `artifact-title`
  или первый `<h1>`, optional большую Lucide-иконку, теги, число страниц и
  относительную дату создания;
- artifact project ведёт обратно в каталог, а многоэкранный project держит
  внутреннюю навигацию и общий Alpine provider в своих assets;
- артефакт передаёт запрошенный смысл и использует готовые общие стили;
- пользователю сразу дана постоянная ссылка на каталог;
- не выполнены никакие проверки.
