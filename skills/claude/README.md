# Claude Skill Sources

Эта папка — tracked source of truth для поддерживаемых глобальных Claude skills.
`~/.claude/skills/<name>` — installed projection, не отдельный owner.

## Контракт

- Сначала править `skills/claude/<name>`, затем разворачивать ту же package shape
  в `~/.claude/skills/<name>` и подтверждать exact diff.
- Codex installed packages были import evidence для этой миграции, не upstream
  owner и не parity promise. Дальнейшие изменения портируются осознанно через
  semantic diff; Claude-native frontmatter, tool/agent names, discovery и
  invocation semantics сохраняются.
- Общий Claude core работает на целевых Claude-моделях из `_ops/GOAL.md`.
  Model routing и prompting deltas живут в `knowledge/wisdom-claude-*.md`, а не
  копируются в каждый skill.
- В installed package не добавлять human docs или историю; они остаются здесь
  либо в `knowledge/`.
- Глобальная правка требует structural check, internal-link check, trigger и
  near-miss probes по риску, а helper-команды — smoke из чужого project cwd.

Точный рабочий model set задаёт `_ops/GOAL.md`; общий authoring contract —
`knowledge/practical-guides/how-to-write-skills/`.
