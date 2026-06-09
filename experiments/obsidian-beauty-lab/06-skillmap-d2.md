---
aliases:
  - SkillMap
tags:
  - experiment/obsidian
  - experiment/d2
  - experiment/svg
cssclasses:
  - obsidian-beauty-lab
---

# SkillMap

> [!summary]+ Что проверяем
> **Цель:** заменить самописную типографику готовым D2 renderer: D2 сам
> отвечает за карточки, подписи, переносы, тему и SVG-export.
>
> Режим тот же удобный для Obsidian: `.d2` → `generated/skillmap.svg` →
> `![[...]]` прямо внутри заметки.

## Inline SVG

![[generated/skillmap.svg|760]]

## Как Обновить

```bash
cd experiments/obsidian-beauty-lab
npm run render:d2
```

## Что Показывает Карта

> [!example]+ Смысл
> Локальный context/owner pass сначала восстанавливает реальную просьбу и
> выбирает маршрут. Дальше работа расходится в стратегию, правку, системные
> правила, owner truth или проверку.
>
> Это не полный каталог всех `1*`-скилов, а компактная карта основного
> рабочего цикла.

> [!tip]- Почему D2 здесь лучше
> В `SkillMap` мы почти не пишем визуальный renderer. Описываем связи и группы,
> а D2 сам делает SVG, тему, размеры и подписи.

> [!warning]- Ограничение
> D2 снимает большую часть визуальной работы, но не решает смысл карты:
> какие узлы показать и где граница между скилами, всё равно выбираем мы.

## Файлы

- `data/skillmap.d2` — исходная D2-диаграмма.
- `scripts/render-d2-svg.mjs` — Node/WASM render без dev server.
- `generated/skillmap.svg` — D2 SVG export.

## Связанные Файлы

- [[00-obsidian-beauty-lab|Главное демо]]
- [[05-elk-square-svg|AtlasGrid]]
- [[07-instruction-map-d2|InstructionMap]]
