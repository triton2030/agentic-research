# 1orchestration — папка-история

Owner: `skills/shared/1orchestration/portable/` (+ `platforms/codex/`).
Tracked projections: `skills/{claude,codex}/1orchestration/`.
Installed: `~/.claude/skills/`, `~/.codex/skills/` — напрямую не правятся.

Здесь: происхождение правил, вырезанное, evidence, снятые файлы.

Внешние зависимости, проверенные чтением 2026-08-31:

- `skills/claude/1codex/SKILL.md` — отрицательный routing: «Claude's own
  subagents are 1orchestration»;
- `skills/claude/1codex/references/delegate.md` — ссылается на «общее правило
  `1orchestration`» о том, что два воркера не правят один файл; такого правила
  здесь нет с v5, расхождение записано в
  `_ops/findings/2026-08-31-224500-orchestration-stale-seams.md`;
- специализированные волны остаются у `1fresh-eyes` и `1deep-agents`.

Прежние адреса `skills/claude/1codex/references/{orchestration,fleet}.md` и
`skills/shared/1planning/portable/references/delegation.md` мертвы: оба пакета
перекроены, файлов больше нет.

С версии v13 (2026-08-31) живой пакет — один `SKILL.md` без reference-файлов:
три блока `Уникальный Контекст · Твоя задача · Твоя цель` и список состояний,
которые не считаются достижением. Нумерованного протокола в нём нет.

- `roles-retired-2026-08-10.md` — снятая таблица прав ролей и форматы
  промпта/возврата v2; заменены картой волны и фокусировкой (v3).
