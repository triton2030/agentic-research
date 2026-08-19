---
name: 1html
description: "Когда нужен быстрый автономный HTML-артефакт, который показывает сложное вместо стены текста: explainer, report, comparison, plan, diagram, data story или UI states. Создаёт нейтральный локальный bundle, подключает только нужные visual add-ons и блокирует поломки переносимости перед каталогом. Не для production website/app/deploy или встроенной в чат визуализации."
---

# HTML

## Результат

Выдай переносимый локальный HTML-артефакт, в котором главный смысл виден до
чтения объяснительной прозы. Он открывается напрямую через `file://`, не требует
сервера, сети или build step и остаётся понятным без запуска JavaScript.

Это личная рабочая документация владельца, не production-сайт и не рекламная
страница. Главный критерий — скорость понимания: факт, состояние, решение,
граница, устройство или следующий шаг находятся глазами.

## Покажи, Не Пересказывай

Сначала выдели реальные отношения в материале: состав, порядок, поток,
сравнение, долю, изменение, состояние или действие. Для каждого существенного
отношения выбери самый простой визуальный носитель; в heading, caption или
видимой подписи назови, что он показывает. Нет отношения или reader job,
которым помогает visual, — visual не нужен. Вопрос и короткий answer-first блок
уместны для explainer или decision, но не являются общей композицией artifact.

Текст подписывает форму и сохраняет точность. Он не должен повторять то, что
уже видно:

- «что внутри чего» показывай вложенной композицией;
- процесс, ветвление и движение данных — flow;
- план и события — steps или timeline;
- сравнение — рядом или таблицей;
- реальные величины, доли и изменение — подходящим chart;
- действие и смену состояния — управляемым motion;
- необязательную глубину — `details`, popover или `dialog` рядом с тезисом.

Полная карта выбора, анти-кейсы и лестница носителей —
[`references/visual-routing.md`](references/visual-routing.md). Открой её перед
композицией сложного explainer, plan, diagram или data story.

Форма допустима только для отношения, которое действительно есть в источнике.
Не рисуй оценочные числа как измерения, линейный список как сеть и статическое
утверждение как процесс. Карточки с теми же абзацами — всё ещё стена текста.

## Факт Или Комментарий

Артефакт переводит подтверждённый материал в наглядную форму, а не сочиняет
удобную версию.

- **Факт** принадлежит канону, документу, коду, данным или прямым словам
  владельца. Упрощай форму, не смысл; не заполняй пробел правдоподобным.
- **Комментарий** добавлен агентом: риск, гипотеза, вопрос, найденная ошибка или
  вывод. Назови тип и визуально отдели его от фактов.

Если материала не хватает, покажи пробел. Существенный смысл остаётся в
семантическом DOM: headings, labels, captions, text summary и обычные links.
Цвет, spatial position, hover, animation и canvas не являются единственным
носителем ответа.

## Быстрый Старт

Из корня проекта:

```bash
"<каталог skill>/scripts/new_html_bundle.sh" "<artifact-name>"
```

Если текущая директория не является корнем проекта, передай его вторым
аргументом. Скрипт создаёт нейтральный scaffold, регистрирует проект в каталоге
и печатает адреса. Меняй `index.html` и `assets/local.css`: HTML, композиция,
палитра, типографика и motion принадлежат текущему artifact. Scaffold и прошлые
artifacts не являются design template.

Для дополнительных экранов создай плоские `pages/<name>.html` с правильными
относительными путями. Отдельный reader job получает отдельную страницу;
состояния одной модели могут оставаться на текущей странице.

Metadata project entry:

```html
<meta name="artifact-title" content="Точное имя для каталога">
<meta name="artifact-icon" content="sparkles">
<meta name="artifact-tags" content="explainer, plan, prototype">
```

После ручного удаления или переименования проекта обнови каталог:

```bash
"<каталог skill>/scripts/rebuild_html_catalog.sh" "<корень проекта>"
```

## Носители И Add-ons

Начинай с native HTML, CSS, SVG и уже локальных DaisyUI, Tailwind, Alpine и
Lucide. Подключай add-on только когда он выражает отношение лучше и проще.

- Таблица с реальным поиском, фильтрами или сортировкой:

```bash
"<каталог skill>/scripts/add_table_bundle.sh" "<artifact-name>" "<project-root>"
```

- Mermaid для topology, sequence, state, timeline, gantt и простых charts:

```bash
"<каталог skill>/scripts/add_mermaid_bundle.sh" "<artifact-name>" "<project-root>"
```

- Apache ECharts для нескольких quantitative views, interactive exploration,
  Sankey, treemap, heatmap или scatter, которые native SVG/Mermaid выражают
  хуже:

```bash
"<каталог skill>/scripts/add_echarts_bundle.sh" "<artifact-name>" "<project-root>"
```

ECharts — opt-in local runtime, не default и не page template. Данные и
`option` остаются рядом с текущим artifact; пять редактируемых recipes и
accessibility contract — [`references/echarts.md`](references/echarts.md).

- React Flow только когда одновременно нужны крупные интерактивные nodes,
  pan/zoom исследуемого полотна и направленные data-flow edges:

```bash
"<каталог skill>/scripts/add_react_flow_bundle.sh" "<artifact-name>" "<project-root>"
```

React Flow здесь заранее собран в локальный IIFE вместе с React runtime:
artifact по-прежнему открывается через `file://` без dev server и сети. Его
nodes и edges наследуют CSS variables, шрифт и цвета самого artifact; add-on не
задаёт палитру. Детали, config contract и пример —
[`references/react-flow.md`](references/react-flow.md).

Интерактивность и motion допустимы, только когда сокращают путь к пониманию или
показывают реальное изменение. Всегда сохраняй static meaning и
`prefers-reduced-motion`. Актуальные native возможности и fallback —
[`references/modern-web.md`](references/modern-web.md).

## Роутер Практик

Открывай только reference текущего решения.

| Сигнал | Открыть | Владелец |
| --- | --- | --- |
| Выбрать форму для сложного материала | [`visual-routing.md`](references/visual-routing.md) | relation → carrier, charts, flows, nesting, motion |
| Выстроить понятный путь и иерархию | [`readable-design.md`](references/readable-design.md) | reader job, outline, visual hierarchy |
| Спрятать необязательную глубину | [`compact-disclosure.md`](references/compact-disclosure.md) | details/accordion/tabs/popover/dialog/drawer |
| Выбрать DaisyUI component или semantic role | [`daisy-storytelling.md`](references/daisy-storytelling.md) | component grammar и role, не визуальный template |
| Связанные UI states и controls | [`alpine-prototypes.md`](references/alpine-prototypes.md) | state ownership и transitions |
| Интерактивная таблица | [`data-tables.md`](references/data-tables.md) | semantic rows и table helper |
| Mermaid topology или chart | [`mermaid-diagrams.md`](references/mermaid-diagrams.md) | diagram choice, ELK, viewer, accessibility |
| Разные quantitative charts, Sankey или treemap | [`echarts.md`](references/echarts.md) | local runtime, data/options recipes, accessible fallback |
| Крупные interactive nodes и data-flow | [`react-flow.md`](references/react-flow.md) | threshold, config, node controls, animated edges |
| Popover, native accordion, modern motion/CSS | [`modern-web.md`](references/modern-web.md) | current capability и fallback |
| Явный audit красоты или cleanup | [`visual-audit.md`](references/visual-audit.md) | advisory visual review |
| Неизвестно имя DaisyUI component | точечный поиск в `references/daisyui-llms.txt` | bundled component syntax |
| Неизвестно имя Lucide icon | точечный поиск в `references/lucide-icon-names.txt` | local icon name |

## Runtime-Границы

- Все зависимости локальны и закреплены; не добавляй CDN, network fetch,
  remote font, npm install, server или build step в artifact workflow.
- Local-only CSP из scaffold блокирует случайные runtime network routes;
  сохраняй его на каждом current live page.
- Native links, `details`, `dialog`, popover, radio и checkbox идут раньше
  Alpine. Alpine нужен для связанных состояний или derived presentation.
- DaisyUI задаёт component semantics, но не композицию и не palette artifact.
  Соблюдай структуру выбранного component; затем оформляй её в `local.css`.
- Текстовый `.card` кладёт content в direct `.card-body`; media-only card может
  обойтись без него. `.hero` получает direct `.hero-content`. Это contract
  padding/layout, не visual template.
- Не называй собственный layout-класс именем DaisyUI component (`hero`,
  `card`, `navbar`, `drawer`), если не используешь его contract: library CSS
  уже придаёт такому классу layout behavior. Для локальной формы дай
  artifact-specific имя.
- Lucide icon наследует `currentColor` и имеет видимый либо доступный label.
- Главная связь и ориентация доступны без раскрытия controls. Скрывается только
  необязательная глубина; tooltip и hover никогда не несут единственный
  существенный смысл.
- Простые charts выражай native HTML/SVG или Mermaid. ECharts подключай только
  когда реальные данные требуют нескольких quantitative views, exploration,
  Sankey, treemap, heatmap или scatter; не загружай его ради одного простого bar.

## Скорость И Проверка

Обычное создание остаётся fast path: не запускай server, browser, screenshot
loop, responsive matrix или visual QA. Программный gate проверяет переносимость
и целостность, а не навязывает внешний вид.

Перед сдачей выполни один переход:

```bash
"<каталог skill>/scripts/finish_html_bundle.sh" "<artifact-name>" "<project-root>"
```

Ненулевой код означает, что artifact не готов. Команда проверяет HTML,
локальные ресурсы, add-on wiring и generation contract, затем пересобирает
catalog и печатает обе ссылки. Для созданного старой версией bundle используй
явный `--legacy`; current bundle не может обходить текущий gate этим flag.

Явный запрос audit/cleanup — отдельный maintenance mode. Он может открыть
render или screenshot и запустить advisory source scan:

```bash
"<каталог skill>/scripts/audit_html_style.py" "<artifact-project-or-index.html>"
```

## Готово Когда

- главный смысл и отношения понятны глазами до чтения подробной прозы;
- визуальная форма показывает подтверждённый смысл, а не украшает его;
- факты и комментарии агента различимы;
- artifact автономно открывается через `file://`, а существенный смысл доступен
  без JavaScript и motion;
- `finish_html_bundle.sh` завершился успешно и вернул artifact/catalog links.
