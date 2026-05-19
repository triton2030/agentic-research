# Assumption From Analogy

## Observation

Модель применила структурное assumption от одной runtime-системы (Claude: hooks привязаны к skill папкам в `~/.claude/skills/<skill>/scripts/`) к другой (Codex) без verification. Поверхностный `ls ~/.codex/skills/1start-here/scripts/` показал что hook'a нет — модель заключила что у Codex **нет** stop hook в принципе. Реально Codex держит hooks в отдельной папке `~/.codex/hooks/`.

Pattern: **cross-runtime structure assumption**. Когда два runtime имеют общий namespace (skills, hooks, settings), модель проектирует структуру одного на другой. Quick negative result в expected location → premature conclusion absent.

## Counter

- 2026-05-19 [Claude Opus 4.7]: при обновлении stop hook'ов для self-learning. Я искал hook в `~/.codex/skills/1start-here/scripts/` по аналогии с Claude. Не нашёл → claimed «Codex не имеет stop hook» в closeout. User поправил «найди его». Hook оказался в `~/.codex/hooks/stop_work_review_reminder.py`.

## Possible upgrade

Когда модель не находит expected file/feature в expected location другого runtime — **расширить search до broad find/grep по всему runtime root** (`find ~/.codex -name "*stop*"`), а не объявлять absent. Особенно для cross-runtime parity questions (hooks, settings, permissions, config files).

Альтернатива: закрепить cross-runtime structural map в `1folder-contract` knowledge или AGENTS.md проекта:

- Claude: `~/.claude/{settings.json, hooks/, skills/<x>/scripts/}` (hooks могут быть и внутри skill, и в settings.json под hooks-секцией).
- Codex: `~/.codex/{config.toml, hooks/, skills/<x>/scripts/}` (hooks отдельная папка).

Релевантно: любые questions про Codex internals от Claude session и наоборот; любые cross-runtime parity edits.
