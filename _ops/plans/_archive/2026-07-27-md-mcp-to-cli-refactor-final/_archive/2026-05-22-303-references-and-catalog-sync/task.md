# Generated tool-catalog.md + sync-skill-docs.py update

## Цель
Создать generated `references/tool-catalog.md` в обоих skill folders (Claude + Codex), который служит skill-side discovery surface (mirror to `md tools --json`). Обновить `sync-skill-docs.py` под новый CLI ландшафт.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-104 закрыт (есть `md tools --json` + generator script)
- task-301 + task-302 закрыты (skills уже мигрированы)

## Status — 2026-05-22

partial. Codex-side generated catalog exists at
`/Users/triton/.codex/skills/1md-navigator/references/tool-catalog.md` and
`scripts/sync-skill-docs.py --check` validates Codex stale refs, invalid old
CLI command names, and catalog freshness. The generated Codex catalog is now
CLI-native: it leads with real `md <subcommand>` commands. Claude-side
catalog/sync remains blocked by the Codex read-only rule for `~/.claude/**`; see
`_ops/findings/2026-05-22-claude-skills-migration-blocker.md`.

## Подшаги

- [ ] Запустить `scripts/generate_tool_catalog_md.py` → `~/.claude/skills/1md-navigator/references/tool-catalog.md`
  - Содержит full descriptions (WHEN/WHY/INPUT/OUTPUT/ALT/COST) всех 29 tools
  - Имеет header «Auto-generated. Не править руками. Регенерация: `python3 .../generate_tool_catalog_md.py > references/tool-catalog.md`»

- [ ] Скопировать (или симлинк) в `~/.claude/skills/1md-graph/references/tool-catalog.md` (для graph tools subset) — ИЛИ один файл живёт только в 1md-navigator, а 1md-graph ссылается на него.
  - Решить: один shared catalog или два разделённых subsets?
  - Рекомендация: один shared catalog в 1md-navigator/references/, 1md-graph упоминает «полный catalog в 1md-navigator/references/tool-catalog.md»

- [ ] Mirror в Codex: `~/.codex/skills/1md-navigator/references/tool-catalog.md`

- [ ] Update `experiments/md-embedding-server/scripts/sync-skill-docs.py`:
  - Сейчас этот script проверяет skill docs sync между Claude и Codex side
  - Обновить чтобы он:
    - Знал про новый CLI-based syntax
    - Проверял что `references/tool-catalog.md` exists в обоих skill folders
    - Проверял что generated catalog matches latest `md tools --json` (детектирует out-of-date catalog)
  - Добавить `--regenerate` flag: автоматически обновляет catalog if drift detected
  - Не должен править Claude side из Codex side (already constraint)

- [ ] Update SKILL.md в обоих 1md-navigator (Claude + Codex):
  - Добавить ссылку на `references/tool-catalog.md` как primary discovery surface
  - В разделе «Как этот скил работает с CLI» — упомянуть «для полных tool descriptions — `md tools <name>` или `references/tool-catalog.md`»

- [ ] Verify regenerate cycle:
  - Изменить description одного tool в `src/md_cli/catalog.py`
  - Run `python3 scripts/generate_tool_catalog_md.py > ~/.claude/skills/1md-navigator/references/tool-catalog.md`
  - Diff matches the change

- [ ] Document in skill `references/setup.md` (Claude + Codex):
  - «После обновления `md-tools` запустить regenerate: `python3 .../generate_tool_catalog_md.py > references/tool-catalog.md`»
  - Или add reminder в `md doctor` output

## Готово
- [ ] `~/.claude/skills/1md-navigator/references/tool-catalog.md` exists, содержит 29 tools full descriptions
- [ ] `~/.codex/skills/1md-navigator/references/tool-catalog.md` exists (mirror)
- [ ] `sync-skill-docs.py` обновлён под CLI, проверяет catalog freshness
- [ ] SKILL.md ссылается на catalog как primary discovery
- [ ] Regenerate cycle verified (изменение в catalog.py → script → updated catalog.md)

## Красные линии
- [ ] Не править tool-catalog.md руками (всегда regenerate из catalog.py).
- [ ] Не дублировать в SKILL.md tool descriptions из catalog.
- [ ] Не делать catalog.md живущим только в одном из (Claude/Codex) — должен быть в обоих.

## Проверка
1. `wc -l ~/.claude/skills/1md-navigator/references/tool-catalog.md` → значительно больше 100 строк (29 full descriptions)
2. `diff ~/.claude/skills/1md-navigator/references/tool-catalog.md ~/.codex/skills/1md-navigator/references/tool-catalog.md` → empty (identical)
3. `python3 experiments/md-embedding-server/scripts/sync-skill-docs.py --check` → ok
4. Manual: изменить one description в catalog.py, run regenerate, see diff in tool-catalog.md
