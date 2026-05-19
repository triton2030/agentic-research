---
aliases:
  - InstructionMap
tags:
  - experiment/obsidian
  - experiment/d2
  - experiment/svg
cssclasses:
  - obsidian-beauty-lab
---

# InstructionMap

> [!summary]+ Что проверяем
> **Цель:** посмотреть, насколько D2 подходит не только для короткого графа,
> но и для объясняющей карты с контейнерами, длинными текстовыми блоками,
> разными формами и подписями на связях.
>
> Это всё ещё простой Obsidian-путь: `.d2` → `generated/instruction-map.svg` →
> inline embed в заметке.

![[generated/instruction-map.svg|760]]

## Что Здесь Видно

> [!example]+ Возможности D2
> - контейнеры для смысловых слоёв;
> - Markdown-like текстовые блоки внутри узлов;
> - разные формы: `oval`, `document`, `cylinder`, `page`, `hexagon`,
>   `diamond`, `package`, `cloud`;
> - подписи на стрелках;
> - автоматическая раскладка через `elk`.

> [!warning]- Главный предел
> D2 красиво раскладывает и оформляет схему, но не заменяет текст рядом с ней.
> Для Obsidian важный смысл лучше держать и в диаграмме, и в обычном Markdown.

## Как Обновить

```bash
cd experiments/obsidian-beauty-lab
npm run render:d2:instruction-map
```

## Файлы

- `data/instruction-map.d2` — исходный D2-граф.
- `scripts/render-d2-svg.mjs` — общий SVG-render для D2-диаграмм.
- `generated/instruction-map.svg` — готовый SVG для Obsidian.

## Связанные Файлы

- [[00-obsidian-beauty-lab|Главное демо]]
- [[06-skillmap-d2|SkillMap]]
