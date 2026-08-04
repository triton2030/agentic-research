# Claude Skill Sources

Эта папка содержит tracked runtime owners и tracked projections глобальных
Claude skills. Cross-runtime owners перечислены в
[`../shared/README.md`](../shared/README.md); `~/.claude/skills/<name>` —
installed projection, не отдельный owner.

## Контракт

- Сначала проверить registry в `skills/shared/README.md`. Если package там
  перечислен, править shared owner и собирать projection его sync-командой;
  иначе править `skills/claude/<name>` и разворачивать ту же package shape в
  `~/.claude/skills/<name>`.
- Для package без shared owner Codex runtime-owner живёт в
  `skills/codex/<name>`. Общие scripts/references должны совпадать побайтно;
  runtime files различаются только из-за реального platform delta.
- Общий Claude core работает на целевых Claude-моделях из `_ops/GOAL.md`.
  Model routing и prompting deltas живут в `knowledge/wisdom-claude-*.md`, а не
  копируются в каждый skill.
- В installed package не добавлять human docs или историю; они остаются здесь
  либо в `knowledge/`.
- Глобальная правка требует structural check, internal-link check, trigger и
  near-miss probes по риску, а helper-команды — smoke из чужого project cwd.

Точный рабочий model set задаёт `_ops/GOAL.md`; общий authoring contract —
`knowledge/practical-guides/how-to-write-skills/`.
