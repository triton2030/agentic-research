---
aliases:
  - ELK Square SVG
  - AtlasGrid
tags:
  - experiment/obsidian
  - experiment/elk
  - experiment/svg
cssclasses:
  - obsidian-beauty-lab
---

# AtlasGrid

> [!summary]+ Что проверяем
> **Цель:** проверить `AtlasGrid`: локальную генерацию квадратного SVG через
> `elkjs`, который Obsidian показывает прямо внутри заметки как обычную
> картинку.
>
> Это не требует постоянного dev server. Команда обновляет файл
> `generated/elk-square-demo.svg`, а заметка просто встраивает готовый SVG.

## Inline SVG

![[generated/elk-square-demo.svg|697]]

## Как Обновить

```bash
cd experiments/obsidian-beauty-lab
npm run render:elk
```

## Что Здесь Важно

> [!success]+ Рабочий режим
> ELK.js используется как локальный раскладчик: он получает JSON-граф, пробует
> несколько алгоритмов и направлений раскладки, выбирает вариант ближе к
> квадрату и рисует `1:1` SVG.

> [!tip]- Почему это удобнее iframe
> SVG — обычный файл. Его можно встроить через `![[...]]`, открыть отдельно,
> хранить в git и пересоздавать командой. Obsidian не должен выполнять
> JavaScript внутри заметки.

> [!warning]- Ограничение
> Это пока генератор артефакта, а не нативный renderer code block. Если нужен
> живой блок прямо из Markdown-синтаксиса, следующим шагом будет Obsidian
> plugin или отдельный preprocessor.

## Force Layout

Да, такой класс раскладки существует. В D3 это `d3-force`: связи притягивают
ноды, `many-body` отталкивает их друг от друга, `center` тянет граф к центру,
а `collide` помогает не накладывать блоки.

В этом ELK-демо используется похожая идея без D3: генератор пробует `stress`,
`force`, `radial`, `mrtree` и `layered`, а для плотного квадратного результата
после `stress` запускает `sporeOverlap`, чтобы убрать пересечения блоков.

## Имена Экспериментов

- `TinyFlow` — наш простой Mermaid-like DSL и HTML/SVG renderer.
- `AtlasGrid` — текущий no-server ELK.js pipeline: JSON-граф в квадратный SVG.
- `GravityMap` — будущий вариант с физикой: притяжение связей, отталкивание
  нод, центр-гравитация и collision-проход.

## Файлы

- `data/elk-square-demo.json` — входной граф.
- `scripts/render-elk-square-svg.js` — генератор: ELK layout + SVG renderer.
- `generated/elk-square-demo.svg` — готовая картинка `AtlasGrid` для Obsidian.
- `package.json` — локальная зависимость `elkjs` и команда `render:elk`.

## Связанные Файлы

- [[00-obsidian-beauty-lab|Главное демо]]
- [[04-custom-js-diagram|Кастомная JS-диаграмма]]
