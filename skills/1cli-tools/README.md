# История 1cli-tools

Живой владелец — [`skills/claude/1cli-tools/`](../claude/1cli-tools/SKILL.md);
установленные копии — `~/.claude/skills/1cli-tools` и
`~/.codex/skills/1cli-tools` (у Codex своя строка о zsh и `agents/openai.yaml`).

- Последняя переработка — [work/freshness-2026-10-31/](work/freshness-2026-10-31/brief.md).
- Версия до неё — [versions/tracked-owner-2026-10-31/](versions/tracked-owner-2026-10-31/SKILL.md).
- `origin.md`, `cut.md`, `evidence.md` — история через версии. Их копии
  в папке владельца расходятся с этими и не дописываются.
- 2026-11-05: `npm install-scripts ls` (npm 12.2.1, проверено `npm install-scripts --help`) рядом с `approve-scripts`; ловушка dependency-cruiser 18.7 с удаляемыми TypeScript импортами (проба: неиспользуемый импорт пропал из графа без `tsPreCompilationDeps`, появился с ним). Найдено в работе над subfrost-banner-maker.
