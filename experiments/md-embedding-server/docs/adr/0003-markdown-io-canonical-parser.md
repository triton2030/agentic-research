---
description: "ADR-0003: markdown_io — единственный канонический парсер Markdown-ссылок (консолидация graph_edges pending)."
read-before-edit: []
edit-after-edit: []
---
# ADR-0003 — `markdown_io` — канонический парсер ссылок

- **Статус:** Accepted (консолидация `graph_edges` pending)
- **Дата:** 2026-05-31 (инвариант зафиксирован ранее; ADR документирует решение и
  текущий разрыв)

## Контекст

«Что такое валидная Markdown/wikilink-ссылка» было определено в двух местах:
`navigator.markdown_io` (полная семантика — снимает `<>`, режет `?query`,
фильтрует `mailto:`/`tel:`/`data:`, basename-резолв) и `navigator.graph_edges`
(упрощённый параллельный парсер). Граф-стек ел версию `graph_edges`, остальные
модули — `markdown_io`. Это давало тихий дрейф между `md health`/`md check` и
реальным графом ссылок (находка thermo-nuclear аудита про дубль парсеров).

## Решение

`navigator.markdown_io` — единственный канонический владелец парсинга и резолва
Markdown/link. `graph_edges` может строить graph-specific edges (`Edge`,
`scan_doc`), но не должен держать второй wikilink/markdown-link parser.
Зафиксировано инвариантом в `architecture-lock.md` и `AGENTS.md`.

## Последствия / текущий разрыв (честно)

- **Инвариант пока не доведён до кода:** `graph_edges` всё ещё определяет
  `parse_wikilink` / `wikilinks_from_text` / `markdown_links`. Это известный
  долг, а не скрытый баг.
- Консолидация (свести `graph_edges` к надстройкам над `markdown_io`) —
  отдельная code-задача: требует сверки семантики через owner-skill `1md-graph`,
  чтобы упрощения `graph_edges` не несли сознательно иной контракт.
- До консолидации возможен дрейф «валидной ссылки» между граф-командами и
  остальными читателями корпуса.
