---
aliases:
  - SVG File Embed
  - External SVG Probe
tags:
  - experiment/obsidian
  - experiment/svg
cssclasses:
  - obsidian-beauty-lab
---

# SVG File Embed

> [!summary]+ Что проверяем
> **Цель:** держать красивый SVG отдельным файлом, а в Markdown оставлять
> только короткую ссылку-вставку.
>
> Это лучший режим для агентского контекста: человек видит картинку, агент
> читает компактную заметку и открывает SVG-source только если это нужно.

![[generated/svg-file-embed-proof.svg|720]]

## Что Считать Успехом

- SVG виден в Obsidian как картинка.
- Markdown-заметка не содержит SVG-source.
- Визуальную сложность можно наращивать в отдельном `.svg` без раздувания
  основного документа.

## Граница Пробы

Если SVG становится смысловым owner-файлом, ему нужен нормальный source route:
скрипт, генератор, дизайн-файл или отдельная инструкция. Если это только
визуальный asset, короткой embed-ссылки достаточно.

## Связанные Файлы

- [[00-obsidian-beauty-lab|Главное демо]]
- [[02-iframe-and-clever-paths|Iframe And Clever Paths]]
- [[05-elk-square-svg|AtlasGrid]]
