---
description: "Retired 1index: why it was removed and where its packages and history live."
---

# 1index — снят

Скил снят 2026-10-24 вместе с концепцией INDEX-файлов: владелец счёл её
устаревшей. Корневой `INDEX.md` удалён.[^removal] Действующих runtime owners
и установленных копий больше нет.

- [`versions/retired-shared-2026-10-24/`](versions/retired-shared-2026-10-24/) —
  последний общий owner: `portable/` и Codex-дельта `platforms/`.
- [`versions/retired-claude-2026-10-24/`](versions/retired-claude-2026-10-24/),
  [`versions/retired-codex-2026-10-24/`](versions/retired-codex-2026-10-24/) —
  последние tracked-проекции.
- [`product-frame.md`](product-frame.md) и
  [`product-frame.principles.md`](product-frame.principles.md) — прежний
  замысел; после снятия не направляют работу.
- `origin.md`, `cut.md`, `evidence.md`, `state.md`, `work/`, `review-*`,
  `candidate-*`, `before-*`, `live-*` — история разработки и проверок до
  снятия.

Из действующих `1goal`, `1instruction-authoring`, `1context-refactor` и
`1handoff` убраны ссылки на `1index` и INDEX. Эти снимки хранят историю и не
предназначены для запуска.

[^removal]: [Слова владельца, 2026-10-24](../../_ops/chat-recall/2026-10-24-161239-claude-code-fe5b972b.md#recall-21245be217cc4c3d81e311e0cc0612ab).
