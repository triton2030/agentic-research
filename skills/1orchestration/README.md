# 1orchestration — папка-история

Owner: `skills/shared/1orchestration/portable/` (+ `platforms/codex/`).
Tracked projections: `skills/{claude,codex}/1orchestration/`.
Installed: `~/.claude/skills/`, `~/.codex/skills/` — напрямую не правятся.

Здесь: происхождение правил, вырезанное, evidence, снятые файлы.

Внешние зависимости:
- `skills/claude/1codex/references/{orchestration,fleet}.md`
  указывает сюда как на контракт волны — второй держатель шва;
- `skills/shared/1planning/portable/references/delegation.md`
  оставляет плану state/outcome, а сюда делегирует порядок волны,
  барьеры и wait/probe/repair — второй живой владелец шва.

Живой пакет держит два прогрессивных reference-а:
`wave-folder.md` для дорогого no-plan cold start и `repair.md` для stalled
return в любом режиме.

- `roles-retired-2026-08-10.md` — снятая таблица прав ролей и форматы
  промпта/возврата v2; заменены картой волны и фокусировкой (v3).
