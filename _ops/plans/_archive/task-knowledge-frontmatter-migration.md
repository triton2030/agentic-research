---
owner: 1planning
parents: []
children: []
siblings: []
description: Task to migrate knowledge Markdown files to 1md-graph frontmatter.
---

# Task — Мигрировать knowledge/\*\* на frontmatter-граф

Статус: открыто.

## Якорь

Polygon-режим из `_ops/PROJECT-ROADMAP.md`: `knowledge/` — активный слой знаний, который будущая сессия читает под текущую просьбу.

## Применимые критерии

* [`instruction-layer`](/broken/pages/gm24WNIfQ3REVOMpf3f9) — graph-связи роутятся в `1md-graph`, смысл файла остаётся у owner.
* [`knowledge-maintenance`](/broken/pages/bAuSjidpF1TYfWNeSzhd) — `knowledge/` должен быть активным input-layer, а не складом истории.
* [`repo-structure-and-runtime-guards`](/broken/pages/QwzQ0cLtKIkYIVyLwG1X) — не создавать новый surface без функции и держать форму проверяемой.
* [`work-review-and-evidence`](/broken/pages/OaH8WRUSCjTAH4CLaIKu) — evidence должен быть наблюдаемым.

## Почва

`python3 /Users/triton/.codex/skills/1md-graph/scripts/md_graph.py doctor knowledge` нашёл 38 `MISSING_FRONTMATTER` в `knowledge/**`.

`check knowledge` не доказывает наличие frontmatter: файлы без frontmatter пропускаются. До инициализации схемы обязательный gate — `scan` / `doctor`; после инициализации — `check` / `related --check`.

Один из файлов — `knowledge/examples/anthropic-design-generator/CLAUDE.md`. Codex не редактирует Claude-поверхности без отдельного решения, поэтому этот случай надо явно закрыть: мигрировать через Claude-side workflow, оставить как read-only exception или получить прямое разрешение пользователя.

## Подшаги

* [ ] Выбрать минимальные правила графа для `knowledge/**`. EN: Define owner, description, and relationship conventions for wisdom, guides, practical guides, examples, and research files without changing their meaning.
* [ ] Инициализировать frontmatter без выдумывания связей. EN: Add the portable `1md-graph` schema to knowledge Markdown files, keeping unknown relationships empty until they are verified; exclude `knowledge/**/CLAUDE.md` unless a separate permission or Claude-side workflow is chosen first.
* [ ] Заполнить `description` и `owner`. EN: Give every migrated knowledge file a useful one-line description and a semantic owner that helps future agents choose the file.
* [ ] Связать только очевидные зависимости. EN: Add `parents`, `children`, and `siblings` only where the relation is clear from existing content or accepted project truth.
* [ ] Проверить граф и исключения. EN: Run `doctor`, `check`, and `related --check` for `knowledge/**`; document any intentional read-only exception instead of hiding it.
* [ ] Отделить `_ops` graph pass от `knowledge/**`. EN: Keep this task knowledge-only; if `_ops/**` needs graph migration, create or update a separate task instead of expanding this one.

## Готово

* [ ] Все Codex-editable Markdown-файлы в `knowledge/**` имеют frontmatter v1.
* [ ] `description` и `owner` не являются `TODO`.
* [ ] Graph links не содержат missing target / missing reverse, кроме явно принятого read-only exception.
* [ ] Related-docs sections, если они есть, совпадают с frontmatter.
* [ ] Смысл knowledge-файлов не переписан ради схемы.

## Красные линии

* [ ] Не редактировать `CLAUDE.md` или `.claude/**` из Codex без отдельного разрешения.
* [ ] Не выдумывать связи ради заполнения графа.
* [ ] Не считать `check` доказательством, что frontmatter уже есть.
* [ ] Не расширять эту задачу на `_ops/**`.
* [ ] Не превращать миграцию frontmatter в пересборку содержания `knowledge/`.

## Проверка

1. `python3 /Users/triton/.codex/skills/1md-graph/scripts/md_graph.py scan knowledge` Ожидаемо: нет `MISSING_FRONTMATTER`, `TODO` в `description`/`owner`, legacy fields или malformed graph fields для Codex-editable файлов.
2. `python3 /Users/triton/.codex/skills/1md-graph/scripts/md_graph.py doctor knowledge` Ожидаемо: нет незакрытых critical/cleanup issues.
3. `python3 /Users/triton/.codex/skills/1md-graph/scripts/md_graph.py check knowledge` Ожидаемо: graph targets, reverse links, wikilinks и Markdown links валидны.
4. `python3 /Users/triton/.codex/skills/1md-graph/scripts/md_graph.py related --check knowledge` Ожидаемо: related-docs sections совпадают с frontmatter или отсутствуют там, где связей нет.
