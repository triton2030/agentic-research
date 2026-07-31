# Codex Skill Sources

Эта папка — tracked source of truth для поддерживаемых глобальных Codex skills.
`~/.codex/skills/<name>` — installed projection, не отдельный owner.

## Контракт

- Сначала править `skills/codex/<name>`, затем проверять live projection.
- Общая логика cross-runtime skill должна совпадать с Claude-owner побайтно;
  runtime-specific `SKILL.md`, UI metadata, transcript reader и тесты могут
  различаться только из-за реального platform delta.
- Глобальная правка требует structural check, shared-file parity и smoke из
  чужого project cwd.
