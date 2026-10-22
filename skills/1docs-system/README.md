---
description: "История растворённого скила 1docs-system: рефактор 1document-system 2026-09-04, растворён 2026-09-05 в 1docs-write и 1canon-write."
---

# 1docs-system — растворён

Эта папка хранит историю `1docs-system` и не является пакетом скила; живого
владельца и установленной копии нет.

`1docs-system` — рефактор `1document-system`, начатый 2026-09-04. На
следующий день он растворён в два скила, `1docs-write` и `1canon-write`
([происхождение `1docs-write`](../1docs-write/origin.md)); `1canon-write` снят
2026-09-09.

- [`versions/draft-2026-09-04/`](versions/draft-2026-09-04/) — clean-room черновик пакета.
- [`cut.md`](cut.md) — карта потерь рефактора из `1document-system`.
- [`product-frame.principles.md`](product-frame.principles.md) — принципы
  черновика; работу не направляют.
- [`work/refactor-2026-09-04/`](work/refactor-2026-09-04/) — намерение
  (`intent.md`) и первая волна проверки (`review-wave-1.md`).

Пакет, из которого шёл рефактор, — [`../1document-system/live-claude-2026-09-04/`](../1document-system/live-claude-2026-09-04/).
Ссылки внутри файлов на `_backups/` относятся ко времени записи.

До 2026-10-22 эти файлы лежали в
`~/.claude/skills/_backups/1docs-system-dissolved-2026-09-05/history/`;
перенесены по решению владельца[^backups].

[^backups]: [Слова владельца, 2026-10-22](../../_ops/chat-recall/2026-10-22-235727-claude-code-4acb96f5.md#recall-bdd2d81f8fce4bd79924703b6be3c6c6).
