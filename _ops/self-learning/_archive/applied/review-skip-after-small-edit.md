# Review Skip After Small Edit

## Observation

После маленькой one-line правки модель прыгает к следующему действию
(ответить на параллельный вопрос, продолжать обсуждение) без
`1work-review`, потому что edit субъективно ощущается как maintenance /
mechanical. Stop hook ловит и требует review.

**«Size of edit ≠ substantive-ness»**: substantive определяется surface
(sensitive vs ordinary), не diff size. One-line правка sensitive файла
(`~/.claude/CLAUDE.md`, `_ops/criteria/*.md`, `_ops/GOAL.md`,
`_ops/PROJECT-ROADMAP.md`, `AGENTS.md`) — substantive. Review нужен.

Pattern combo: **streetlight effect** (мозг видит «большое следующее
дело», не оборачивается назад) + **size-as-stakes proxy**
(маленькое = «не сильно важное»).

## Counter

- 2026-05-20 [Claude Opus 4.7]: после правки global
  `~/.claude/CLAUDE.md` (one-line replace owner skill name
  `1instruction-layer` → `1folder-contract`) я сразу перешёл к analysis
  4 скилов (большая задача в том же ходу) и delivered результат без
  вызова `1work-review`. Stop hook поймал. Edit к global CLAUDE.md —
  sensitive surface, review должен был запуститься сразу после Edit,
  до перехода к analysis.
- 2026-05-21 [Claude Opus 4.7]: после Edit двух SKILL.md
  (`~/.claude/skills/1planning/SKILL.md` +
  `~/.codex/skills/1planning/SKILL.md` — синхронная правка
  Navigator/Graph touch-points) создал «closeout summary» в чате —
  таблички Что изменено / Anchor docs / Constraints / Findings —
  иллюзия review. Skill `1work-review` не позван, маркер
  `1work-review: да` отсутствовал. Stop hook словил на следующем ходе.
  **Pattern delta к 2026-05-20:** self-made closeout summary
  subjectively «закрывает» edit, но это формат отчёта, не review.
  Review = сравнение с anchor docs + метки applied/read-now-only +
  routing к owner-скилам, не chat-formatting. Маркер `1work-review:
  да` — единственный structural detector что skill реально запущен.

## Possible upgrade

Hook уже ловит (Stop hook на sensitive surfaces) — structural
enforcement работает. Возможный addition в skill / instruction layer:
explicit rule «substantive sensitive edit → review до next substantive
action **внутри того же turn**, не до конца turn». Сейчас интуиция —
review в closeout, но closeout для **edit**, не для **turn**. Если в
одном turn два substantive шага через разные surfaces, review нужен
между.

Парный с feedback `moment-layer-no-skip` (before-write side, global
memory). Этот counter — after-write side того же phenomenon.
