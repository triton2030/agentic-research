---
aliases:
  - Obsidian Beauty Lab
tags:
  - experiment/obsidian
cssclasses:
  - obsidian-beauty-lab
---

# Obsidian Beauty Lab

<div class="obl-hero" style="margin: 18px 0 26px; padding: 34px; border-radius: 28px; border: 1px solid rgba(74,58,33,.16); background: radial-gradient(circle at 18% 18%, rgba(246,214,146,.55), transparent 32%), radial-gradient(circle at 88% 12%, rgba(118,176,165,.42), transparent 30%), linear-gradient(135deg, #fff8ec 0%, #f3eee6 48%, #e7efe9 100%); box-shadow: 0 22px 70px rgba(53, 45, 32, .16);">
<div style="display: inline-flex; gap: 8px; align-items: center; padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,.62); color: #6b5130; font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;">Markdown + HTML + Mermaid</div>
<h2 style="margin: 16px 0 8px; max-width: 760px; font-size: 44px; line-height: 1.02; color: #26221b;">Одна заметка как живая проектная поверхность</h2>
<p style="margin: 0; max-width: 710px; font-size: 17px; line-height: 1.55; color: #534a3d;">Ниже смешаны нативные callouts, переносимый Markdown, встроенный HTML и Mermaid-схемы. Без CSS это остаётся читаемой заметкой; с CSS snippet превращается в аккуратную Obsidian-страницу.</p>
<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px;"><span style="padding: 8px 12px; border-radius: 999px; background: #2c514b; color: #fffdf8; font-weight: 700;">callouts</span><span style="padding: 8px 12px; border-radius: 999px; background: #7b4c39; color: #fffdf8; font-weight: 700;">HTML</span><span style="padding: 8px 12px; border-radius: 999px; background: #c28a34; color: #fffdf8; font-weight: 700;">Mermaid</span><span style="padding: 8px 12px; border-radius: 999px; background: #313744; color: #fffdf8; font-weight: 700;">Canvas</span></div>
</div>

## Быстрый Осмотр

<div class="obl-bento" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 18px 0 26px;">
<div style="min-height: 118px; padding: 18px; border-radius: 20px; background: #fffaf1; border: 1px solid rgba(130,91,40,.16); box-shadow: 0 12px 34px rgba(64,49,28,.08);"><strong style="color:#3b3124;">Нативная база</strong><br><span style="color:#675b4b;">Callouts, headings, links and properties остаются обычным Markdown-слоем.</span></div>
<div style="min-height: 118px; padding: 18px; border-radius: 20px; background: #edf7f2; border: 1px solid rgba(51,106,96,.18); box-shadow: 0 12px 34px rgba(33,66,58,.08);"><strong style="color:#244942;">HTML-витрина</strong><br><span style="color:#48625b;">Inline HTML даёт hero, сетки, бейджи и компактные панели без отдельного сайта.</span></div>
<div style="min-height: 118px; padding: 18px; border-radius: 20px; background: #f8eef2; border: 1px solid rgba(137,75,95,.16); box-shadow: 0 12px 34px rgba(83,39,54,.08);"><strong style="color:#56303d;">Mermaid-сцены</strong><br><span style="color:#684c55;">Схемы можно сделать мягче через themeVariables, classDef и короткие подписи.</span></div>
<div style="min-height: 118px; padding: 18px; border-radius: 20px; background: #eff1fb; border: 1px solid rgba(68,79,132,.16); box-shadow: 0 12px 34px rgba(36,45,91,.08);"><strong style="color:#303a67;">CSS snippet</strong><br><span style="color:#4d5678;">Красота живёт снаружи заметки, а не ломает смысловой Markdown.</span></div>
</div>

> [!summary]+ Смысл демо
> **Цель:** показать верхнюю границу красивой Obsidian-заметки, которая всё ещё
> остаётся читаемой в git, терминале и Codex.
>
> Лучший путь — не “весь HTML”, а связка: короткая Markdown-структура,
> нативные callouts, точечный HTML для витринных блоков и CSS snippet для
> визуального слоя.

> [!warning]- Где HTML становится плохой идеей
> Если важный смысл живёт только внутри большого HTML-блока, будущий агент или
> человек хуже его редактирует. HTML здесь годится как витрина, но не как
> единственный источник правды.

> [!tip]- Что делает CSS snippet
> Snippet из `snippets/obsidian-beauty-lab.css` усиливает только заметки с
> `cssclasses: obsidian-beauty-lab`: расширяет страницу, смягчает callouts,
> добавляет тени, меняет Mermaid-контейнер и делает hero/bento чище.

## Mermaid: Маршрут Решения

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#fff8ec","primaryColor":"#fff2d8","primaryTextColor":"#28231b","primaryBorderColor":"#caa35a","lineColor":"#54756f","secondaryColor":"#e7f2ed","tertiaryColor":"#f8edf1","fontFamily":"Inter, ui-sans-serif, system-ui"},"flowchart":{"curve":"basis"}}}%%
flowchart LR
    A["Желание<br/>сделать красиво"] --> B{"Что должно<br/>остаться правдой?"}
    B --> C["Markdown<br/>как owner"]
    B --> D["HTML<br/>как витрина"]
    B --> E["Mermaid<br/>как схема"]
    C --> F["Callouts<br/>для чтения"]
    D --> G["Hero, bento,<br/>status panels"]
    E --> H["Маршруты,<br/>карты, связи"]
    F --> I["Obsidian<br/>surface"]
    G --> I
    H --> I
    classDef origin fill:#fff2d8,stroke:#c28a34,color:#2b2418,stroke-width:2px;
    classDef truth fill:#edf7f2,stroke:#4d7c70,color:#213f39,stroke-width:2px;
    classDef display fill:#f8eef2,stroke:#9c6374,color:#4e2935,stroke-width:2px;
    class A,B origin;
    class C,F,I truth;
    class D,E,G,H display;
```

## Mermaid: Сценарий Сессии

```mermaid
%%{init: {"theme":"base","themeVariables":{"actorBkg":"#fff2d8","actorBorder":"#b98134","actorTextColor":"#2b2418","signalColor":"#486e67","signalTextColor":"#2b2418","activationBkgColor":"#e7f2ed","activationBorderColor":"#4d7c70","fontFamily":"Inter, ui-sans-serif, system-ui"}}}%%
sequenceDiagram
    participant U as Пользователь
    participant O as Obsidian
    participant M as Markdown
    participant C as CSS snippet
    U->>O: Открывает demo-vault
    O->>M: Рендерит заметку
    M->>O: Callouts, HTML, Mermaid
    O->>C: Применяет класс страницы
    C-->>U: Визуальная поверхность без потери текста
```

## AtlasGrid: Квадратный SVG

> [!example]+ Что получилось лучше Mermaid
> Здесь диаграмма не тянется строго слева направо. `AtlasGrid` через `elkjs`
> раскладывает граф, выбирает вариант ближе к квадрату, а Obsidian получает
> обычный SVG-файл.

![[generated/elk-square-demo.svg|720]]

## SkillMap: D2 Без Самописной Типографики

> [!example]+ Что проверяем
> `SkillMap` описывает работу `1*`-скилов в D2. Здесь renderer сам берёт на
> себя тему, карточки, подписи и SVG-export.

![[generated/skillmap.svg|720]]

## InstructionMap: Подробный D2-Граф

> [!example]+ Что проверяем
> `InstructionMap` показывает, как D2 держит контейнеры, длинные текстовые
> блоки, разные формы и подписи на связях в одной объясняющей схеме.

![[generated/instruction-map.svg|720]]

## FlowPage: React Flow + ELK

> [!example]+ Что проверяем
> Если карта должна зумиться и двигаться как рабочая поверхность, её лучше
> вынести в отдельную страницу. `FlowPage` оставляет Obsidian входом, а
> интерактивность отдаёт React Flow.

[Открыть FlowPage](http://127.0.0.1:5173/flowpage.html)

## HTML: Маленький Пульт

<div class="obl-control" style="display: grid; grid-template-columns: 1.2fr .8fr; gap: 14px; margin: 20px 0;">
<div style="padding: 20px; border-radius: 22px; background: #242a2f; color: #fff7e8; box-shadow: 0 18px 44px rgba(20,25,28,.18);"><div style="font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: #f4cb82; font-weight: 800;">Status</div><div style="font-size: 30px; line-height: 1.1; margin-top: 8px; font-weight: 850;">Beautiful but still readable</div><p style="margin: 12px 0 0; color: #d8d1c4;">Главная проверка: если CSS выключить, заметка не должна развалиться в мусор.</p></div>
<div style="display: grid; gap: 10px;"><div style="padding: 14px 16px; border-radius: 18px; background: #fff7e8; border: 1px solid rgba(80,62,39,.14);"><strong>Owner</strong><br><span style="color:#655947;">Markdown</span></div><div style="padding: 14px 16px; border-radius: 18px; background: #e8f4ef; border: 1px solid rgba(57,105,92,.16);"><strong>Display</strong><br><span style="color:#49635b;">Obsidian preview</span></div><div style="padding: 14px 16px; border-radius: 18px; background: #f7edf1; border: 1px solid rgba(133,80,99,.16);"><strong>Risk</strong><br><span style="color:#684c55;">HTML drift</span></div></div>
</div>

## Слои

> [!example]+ Слой 1: обычный Markdown
> - Заголовки дают каркас.
> - Списки дают сканируемость.
> - Wikilinks и Markdown-ссылки дают навигацию.
> - Frontmatter даёт свойства, но не должен плодить новые типы данных без owner.

> [!example]+ Слой 2: Obsidian callouts
> Callouts хороши тем, что они нативные, сворачиваемые и всё ещё читаются как
> текст. Это лучший default для красивой рабочей заметки.

> [!example]+ Слой 3: HTML-вставки
> HTML лучше использовать для витринных блоков: hero, карточки, статусы,
> компактные панели. Не стоит прятать в нём правила, критерии или единственную
> версию важного решения.

> [!example]+ Слой 4: CSS snippet
> CSS должен усиливать уже понятную структуру. Если без CSS заметка теряет
> смысл, значит красота стала вторым источником правды.

## Мини-Детали

<details class="obl-details" open><summary>Почему это не отдельный сайт</summary><p>Obsidian хорош, когда рабочая заметка остаётся заметкой: её можно читать в git, менять обычным редактором и связывать с другими файлами. Сайт красивее контролирует пиксели, но дороже поддерживается.</p></details>
<details class="obl-details"><summary>Где предел</summary><p>Сложные интерактивные элементы, JavaScript, полноценные формы и состояние лучше выносить из заметки. В Obsidian их можно имитировать, но это быстро становится хрупким.</p></details>

## Связанные Файлы

- [[README|README эксперимента]]
- [[01-beauty-board.canvas|Canvas-доска]]
- [[02-iframe-and-clever-paths|Iframe и хитрые пути]]
- [[03-meta-bind-and-obsidian-primitives|Meta Bind и Obsidian-примитивы]]
- [[04-custom-js-diagram|Кастомная JS-диаграмма]]
- [[05-elk-square-svg|AtlasGrid]]
- [[06-skillmap-d2|SkillMap]]
- [[07-instruction-map-d2|InstructionMap]]
- [[08-flowpage-react-flow-elk|FlowPage]]
- [[iframe-and-html.base|Base-вид]]
- `snippets/obsidian-beauty-lab.css`
