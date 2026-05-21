# Work-Review Auto-Fire Skip on ~/.claude/ Writes

## Observation

`1work-review` description явно содержит auto-fire signal: «Stop hook
требует review при ≥3 файлах или задетой sensitive surface
(`_ops/criteria/`, `_ops/GOAL.md`, `_ops/PROJECT-ROADMAP.md`,
`AGENTS.md`, `CLAUDE.md`, **`~/.claude/`**)». Также «Auto-fire: после
substantive Edit / Write / MultiEdit».

Несмотря на это — модель **продолжает работу** после substantive Edit
в `~/.claude/skills/<name>/SKILL.md` без proactive call к
`1work-review`. Stop hook ловит и feedback'ом пинает:
«Стоп. Это второй ход подряд с substantive write без `1work-review`».

Pattern: **forward momentum bias** — модель в режиме «делаю задачу
end-to-end» не activates review-skill потому что review feels как
interruption flow. Auto-fire phrase в description прочитана при skill
list load, но не сработала на момент substantive edit.

## Counter

- 2026-05-20 [Claude Opus 4.7]: substantive Edit в
  `~/.claude/skills/1md-navigator/SKILL.md` (4 правки) +
  `~/.codex/skills/1md-navigator/SKILL.md` (4 правки) — это `~/.claude/`
  и parallel `~/.codex/` sensitive surface. Не запустил `1work-review`
  proactively, продолжил empirical test, finding, summary. Stop hook
  напомнил после второго substantive turn. После hook — выполнил
  review корректно.
- 2026-05-20 [Claude Opus 4.7]: повтор того же паттерна — Edit
  `~/.claude/skills/1ia-audit/SKILL.md` (5) + `~/.codex/skills/1ia-audit/SKILL.md`
  (3). Дал summary в чат, не позвал review. Stop hook снова напомнил.
  Counter растёт за один день — Possible upgrade #1 (PostToolUse hook)
  выглядит уже как реальный сигнал, не теоретический.
- 2026-05-20 [Claude Opus 4.7]: третий повтор за один день. Edit
  `~/.claude/skills/1folder-contract/SKILL.md` (2) +
  `~/.codex/skills/1folder-contract/SKILL.md` (2). После 4 substantive
  edits выдал self-claim «✓ closeout» в чате без `1work-review`. Stop
  hook поправил на 2-м substantive ходу подряд. Особенность этого
  случая: existing counter с двумя предыдущими записями за сегодня
  лежал в `_ops/self-learning/` доступный к Read — но не загружен в
  context автоматически, и forward-momentum не позвал self-learning
  проактивно до edit'а. Counter без runtime enforcement не учит модель
  даже когда тема свежая в файлах. Status upgrade #1: confirmed signal,
  3 cases / 1 day.

## Possible upgrade

Auto-fire signal в `1work-review` description — недостаточен для
поведения. Структурные защиты:

1. **PostToolUse hook** для Edit/Write/MultiEdit с target в
   `~/.claude/` или `~/.codex/` — emit reminder в session-state
   «next turn должен иметь review marker».
2. **Skill body of 1md-navigator / 1skill-architect** при routing к
   substantive write — добавить «после правки → review» как explicit
   handoff step.
3. **Or — session-state counter** «substantive_writes_since_last_review»
   с soft threshold (≥2) после которого Stop hook твёрже блокирует.

Memory-side reminder («помни делать review») не работает, потому что
forward momentum во время задачи перекрывает passive memory recall.

Связано с `autonomous-capture-skip` (skip автономного capture при
форвард-моментуме) и `adjacent-skill-not-activated` (skills рядом
не активируются).
