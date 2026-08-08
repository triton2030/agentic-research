---
description: "Archived versions of the retired 1instruction-layer skill."
---

# 1instruction-layer — снят 2026-08-08

**Скил снят.** Заменён `1instruction-shaping` — сменился охват и жанр: вместо
слоя прозаических инструкций скил владеет швом между всеми пятью слоями,
влияющими на поведение агента (корень, папка, скил, хук, план), и не пишет ни
одного файла до «да» владельца.

Живого owner-а у этой папки нет, она целиком историческая.

- `tracked-claude-2026-08-08/` — полный пакет из `skills/claude/`
  (`SKILL.md` + 25 references: гейтовая машина Gate 0…Gate 6, `steering-cell`,
  `llm-divergences`, `language-quality-*`, `placement-protocol` и др.).
  `~/.claude/skills/1instruction-layer` был симлинком сюда.
- `live-codex-2026-08-08/` — отдельная установленная Codex-версия на момент
  снятия.

Что сознательно не перенесено в преемника и почему —
`skills/1instruction-shaping/cut.md`. Если окажется, что какая-то часть
гейтовой машины меняла решение, а не форму, она возвращается точечно отсюда.
