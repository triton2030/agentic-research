---
name: 1writing-style
description: >
  Когда пользователь просит оформить, визуализировать или сделать читаемее
  Markdown/Obsidian artifact либо его presentation CSS: сначала учти
  canon/_ops/projection и не создавай вторую истину.
  Genre/sections/folders/metadata → `1document-system`; semantic search →
  `1md-search`; dependency impact → `1md-graph`; live vault/render →
  `1obsidian-cli`.
---

# Writing Style — Zone-Aware Readability

Улучшай читаемость после определения authority и жанра. Plain Markdown —
полноценный default; визуальная форма нужна только когда она материально
ускоряет понимание отношения, сравнения, статуса или решения. Не добавляй к
owner-тексту второй «слой сканирования» с теми же изменяемыми утверждениями.

## Zone Router

Сначала исполни nearest project instructions и local document contract. Если
проект использует другую topology, сопоставь её ролям ниже; не создавай новые
папки ради оформления.

| Роль artifact | Письмо | Допустимая форма | Жёсткая граница |
| --- | --- | --- | --- |
| `canon/` — current truth | decision-dense, section-complete, короткие точные ответы | headings, lists, Markdown tables; Mermaid только как точная owner-модель | не менять genre sections/metadata; не добавлять HTML cards/banner или повторный summary |
| `_ops/` — change/control state | status, owner, evidence, decision и next action видны сразу | обычный Markdown, tasks, callouts, tables; Mermaid для реального workflow | не превращать plan/finding/decision в current product truth |
| `projections/` — reader view | порядок, prose и emphasis под конкретного reader-а | callouts, diagrams, HTML cards, banners, styled tables, embeds | `authority: projection`, `derived-from`, section-level `depends-on` для current claims; ни одного нового или усиленного claim |

Если роль неясна и от неё зависит допустимая форма, сначала найди live owner.
Material ambiguity назови до визуальной переработки.

## Default Path

1. Зафиксируй reader job и роль artifact. Если нужно выбрать type, headings,
   metadata, folders или источник истины, передай эту часть
   `1document-system`; presentation не переопределяет его контракт. Для
   projection сначала примени его local/`1document-system` lineage contract.
   Если нет explicit `as-of`, считай view maintained: запиши
   `authority: projection`, source-level `derived-from` и hard section-level
   `depends-on`; body bibliography это не заменяет. Не выдумывай
   `artifact-type: projection`: projection — authority/zone, не canonical type.

   ```yaml
   ---
   authority: projection
   derived-from:
     - "[[../canon/<owner>.md]]"
   depends-on:
     - "[[../canon/<owner>.md#<heading>]]"
   ---
   ```

   Держи `derived-from` и `depends-on` плоскими YAML lists; не группируй edges
   вложенной map.
2. Сохрани обязательные headings, identifiers, links, unresolved markers и
   section ownership. В canon сначала закрой coverage, затем сокращай ответы
   внутри sections; не удаляй section ради лёгкого чтения.
3. Выбери минимальную форму по отношению информации, а не по желанию
   «украсить» файл. Один очевидный тезис оставь текстом; точное сопоставление —
   списком или таблицей; branching/sequence/hierarchy — Mermaid.
4. Оставь один изменяемый owner каждого утверждения. В canon и `_ops` форма
   должна быть самим ответом, а не пересказом соседнего абзаца. Reader-oriented
   повтор выноси в projection и привязывай к canon sources.
5. Оптимизируй зрительную строку: короткие абзацы, один блок — один вопрос,
   первая строка section даёт ответ. Не склеивай source, status и несколько
   commitments в один длинный bullet.
6. Менял сложный HTML, CSS или Mermaid → закрой «Проверку Рендера».

## Form Rules

- HTML mini-review, banner, compare, gallery и `mavo-table` используй только в
  projection или явно неканоническом reader view. Если такой блок нужен для
  canon, создай/обнови source-bound projection, а canon оставь agent-readable.
- Не превращай внутреннюю metadata в reader claim. В частности, `approved`
  интерпретируй только по owner contract; не используй его как trust/finality
  gate по собственному предположению.
- Callout используй в `_ops` или projection для одного operational status,
  warning или bounded aside. В canon используй его только по explicit local
  template; никогда не оборачивай `SECTION-STATUS`, обязательный section,
  decision или current rule в callout.
- Markdown table используй для точных повторяющихся mappings. Длинный rationale
  и independently retrievable claims оставляй под headings, не запирай в cells.
- Mermaid используй, когда edge/order сам несёт знание. Сохраняй стабильные
  identifiers и короткие labels; определения и evidence держи обычным Markdown.
- Wikilinks, embeds, tasks и длинный смысл держи вне HTML: иначе они теряют
  кликабельность, индексацию или редактируемость.
- Цвет и shape не должны быть единственным носителем статуса или смысла.

## Routes

- [HTML_PATTERNS.md](references/HTML_PATTERNS.md) — читай только для projection
  или явно reader-facing non-truth view.
- [MERMAID_SYNTAX.md](references/MERMAID_SYNTAX.md) — читай при создании или
  починке Mermaid.
- [CALLOUTS.md](references/CALLOUTS.md) — читай при выборе types, folding или
  nesting.
- [PROPERTIES.md](references/PROPERTIES.md) — читай при работе с property types,
  tags, aliases или `cssclasses`.
- [EMBEDS.md](references/EMBEDS.md) — читай при note/image/PDF/audio/video/search
  embeds.

## CSS Snippets

Два независимых asset-а не смешивают vault-wide UI с reader components:

- [assets/mavo-vault-ui.css](assets/mavo-vault-ui.css) задаёт горячую → холодную
  шкалу `h1`–`h4` и приглушает в дереве служебные `AGENTS.md`,
  `CLAUDE.md`, `GEMINI.md`. Устанавливай при запросе настроить общий стиль
  Obsidian как в MAVO.
- [assets/mavo-readability.css](assets/mavo-readability.css) обслуживает
  projection HTML, styled tables и Mermaid fit. Устанавливай только когда
  выбранная reader surface реально использует эти components.

```bash
cp <skill-base>/assets/mavo-vault-ui.css .obsidian/snippets/mavo-vault-ui.css
cp <skill-base>/assets/mavo-readability.css .obsidian/snippets/mavo-readability.css
```

Устанавливай только нужный слой. Vault UI остаётся presentation: цвет не несёт
единственный смысл, служебные файлы остаются видимыми, CSS не делает canon
полным.

При правке CSS покрой `.markdown-preview-view`, `.markdown-rendered` и
`.markdown-source-view`; CodeMirror chrome меняй только component-scoped.
Vault chrome вроде file explorer держи в отдельном snippet. Не форсируй
`cssclasses`, если их запрещает local schema.

## Проверка Рендера

После изменения CSS snippet или сложного HTML/Mermaid проверь live Obsidian
через `1obsidian-cli`, если vault открыт:

```bash
obsidian snippets:enabled
obsidian dev:dom selector=".mavo-review" total
obsidian dev:css selector=".mavo-review-grid" prop=display
obsidian dev:css selector=".markdown-rendered h1" prop=color
obsidian dev:css selector=".markdown-source-view .cm-header-1" prop=font-size
obsidian dev:css selector=".nav-file-title[data-path='AGENTS.md'] .nav-file-title-content" prop=opacity
obsidian dev:screenshot path=/tmp/obsidian-note-check.png
obsidian dev:errors
```

Проверь Reading view и Live Preview, рабочую и узкую внутреннюю панель, а также
`scrollWidth <= clientWidth`. Raw HTML в screenshot → сними фокус с блока;
default computed CSS → snippet не включён или selector не попал в DOM. Live
Obsidian недоступен → назови render-check непокрытым.

## Validation And Stop

Готово, когда zone/genre contract сохранён, читатель быстрее находит нужный
ответ, mutable claim не получил второго owner-а, canon остался
agent-retrievable, а projection имеет required metadata/manifest lineage и не
противоречит sources. Сложный visual должен пройти live render check.

Остановись, если presentation требует выдумать missing truth, скрыть обязательный
section, ослабить evidence boundary или сделать ops/projection единственным
current owner-ом. Верни проблему в `1document-system`, а не маскируй стилем.

## References

- [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown)
- [Internal links](https://help.obsidian.md/links)
- [Embed files](https://help.obsidian.md/embeds)
- [Callouts](https://help.obsidian.md/callouts)
- [Properties](https://help.obsidian.md/properties)
