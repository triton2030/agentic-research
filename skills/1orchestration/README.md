# 1orchestration — папка-история

Owners с 2026-09-06: `skills/codex/1orchestration/` и
`skills/claude/1orchestration/`. Installed `~/.codex/skills/1orchestration/`
и `~/.claude/skills/1orchestration/` — проекции соответствующих runtime owners.
Общий portable owner снят; sync: `skills/shared/sync_simple_projections.py`.

Codex: [версия 2026-09-06](versions/codex-2026-09-06/SKILL.md),
[карта переноса](work/codex-merge-2026-09-06/preservation.md),
[решения по проверке](work/codex-merge-2026-09-06/review-decisions.md).
Объединяет прежний Codex 1orchestration и 1codex-bg-threads; Claude сохранён
побайтно относительно начала этой работы.

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

Предыдущая правка 2026-09-05: разделение с `1agent-steering`; карта сохранения
в `cut.md`, исходный пакет в `work/steering-2026-09-05/before/`.
Прежний общий состав: `SKILL.md`, `references/brief.md`, `references/session.md`
и Codex UI metadata. Описание v13 выше относится к истории.
