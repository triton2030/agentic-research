---
description: "Product truth, version packages, and refactor evidence for 1chat-recall."
---

# 1chat-recall

Эта папка владеет продуктовой рамкой и историей `1chat-recall`, но не является
runtime package. Живые runtime owners находятся в
`skills/codex/1chat-recall/` и `skills/claude/1chat-recall/`; установленные
`~/.codex/skills/1chat-recall/` и `~/.claude/skills/1chat-recall/` — их
projections.

## Топология

- `versions/<version-id>/` — самостоятельный снимок package. Если Codex и
  Claude расходятся намеренно, версия хранит отдельные `codex/` и `claude/`.
- `work/<work-id>/` — служебные материалы создания и проверки: intent, cut,
  preservation map, reviews, probes и verification.
- `product-frame.md` — живая продуктовая правда скила.
- `cut.md` — общая история снятых и перенесённых смыслов между версиями.

Текущая установленная версия:
`versions/installed-2026-08-31/`.
Её намерение и terminal evidence: `work/install-2026-08-31/`.

Предшествовавший проверенный кандидат сохранён в
`versions/candidate-2026-08-31/`, а его полное evidence — в
`work/recheck-2026-08-30/`.

Предыдущий draft package находится в `versions/draft-2026-08-29/`, а его
review history — в `work/refactor-2026-08-29/`.

Версия не становится owner-ом после установки. Promotion всегда меняет
tracked runtime owner, после чего installed package остаётся projection.
