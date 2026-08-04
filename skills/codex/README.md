# Codex Skill Sources

Эта папка содержит tracked runtime owners и tracked projections глобальных
Codex skills. Cross-runtime owners перечислены в
[`../shared/README.md`](../shared/README.md); `~/.codex/skills/<name>` —
installed projection, не отдельный owner.

## Контракт

- Сначала проверить registry в `skills/shared/README.md`. Если package там
  перечислен, править shared owner и собирать projection его sync-командой;
  иначе править `skills/codex/<name>`.
- Для package со shared owner состав общих файлов и platform deltas задаёт его
  manifest. Без shared owner общая логика должна совпадать с Claude runtime
  owner побайтно; runtime files различаются только из-за реального platform
  delta.
- Глобальная правка требует structural check, shared-file parity и smoke из
  чужого project cwd.
