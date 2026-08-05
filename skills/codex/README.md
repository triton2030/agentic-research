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
  manifest.
- Если положительный job зависит от native Codex surface и честного
  Claude-эквивалента нет, `skills/codex/<name>` — единственный
  runtime-specific owner; фиктивный Claude twin не создаётся. Для portable
  package с отдельным Claude owner общая логика совпадает побайтно, кроме
  реального platform delta.
- `~/.codex/skills/<name>` всегда projection. Для runtime-specific owner
  проверяй structural contract, побайтную parity установленной projection и
  smoke из чужого project cwd; отсутствие Claude-копии не является parity gap.
