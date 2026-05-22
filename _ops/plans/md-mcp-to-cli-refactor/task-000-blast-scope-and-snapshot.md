# Зафиксировать blast scope и snapshot текущего состояния

## Цель
До любых правок зафиксировать точный inventory того, что задевает рефактор: где живёт MCP registration, какие файлы ссылаются на md_* tool names, какие сигнатуры и envelope shape у каждого из 29 tools. Это reference document, на который опираются все последующие task'и.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (project root rules)
- `experiments/md-embedding-server/AGENTS.md` (subtree, если есть)
- `_ops/project-graph.md` — Cross-project blast секция

## Подшаги

- [ ] Зафиксировать MCP registration paths. Найти где `md-mcp` зарегистрирован для Claude/Codex.
  - `rg "md-mcp|md_mcp" ~/.claude ~/.codex --type-add 'cfg:*.{json,toml}' -t cfg 2>/dev/null`
  - Проверить `~/.claude/plugins/`, `~/.claude/mcp.json`, `~/.codex/mcp.json`, repo-level `.mcp.json`, `~/.claude/marketplaces/`
  - Список найденных registration paths сохранить в `_ops/findings/2026-05-22-mcp-registration-locations.md`

- [ ] Inventory 29 tool signatures как single source of truth перед миграцией.
  - Запустить запущенный `mcp__md-mcp__md_ping` и получить список tools
  - Для каждого tool: name, input_schema (zod → JSON Schema), annotations (readOnly/destructive/openWorld/idempotent), description text (WHEN/WHY/INPUT/OUTPUT/ALT/COST)
  - Источник правды — `experiments/md-embedding-server/mcp/src/tools/*.js`
  - Записать в `experiments/md-embedding-server/docs/tool-signatures-snapshot.json`

- [ ] Snapshot envelope shape (`envelope.js`).
  - Документировать поля `_envelope.{version, tool, corpus_root, corpus_state, lock, cost, size_estimate, next_step[]}` точно как сейчас выдаёт MCP
  - Включая структуру `corpus_state` (state/model/index_exists/drift_count/recommended_action/...)
  - Записать в `experiments/md-embedding-server/docs/envelope-shape-snapshot.md` как golden reference

- [ ] Inventory всех cross-project references на md_* tool names.
  - `rg -n "md_[a-z_]+" ~/.claude/skills ~/.codex/skills 2>/dev/null | grep -v ".pyc"` → save list per skill
  - `rg -n "md_[a-z_]+" /Users/triton/Documents/GitHub/agentic-research --include="*.md" | grep -v "experiments/md-embedding-server/"` → save list
  - Discovered (initial inventory 2026-05-22): **13 skills на каждой платформе** ссылаются на MCP — не только 1md-navigator/1md-graph. Полный список: core (2) + 1ia-audit, 1instruction-layer, 1planning, 1strategy, 1strategy-docs, 1folder-contract, 1assumption-audit, 1work-review, 1skill-architect, 1smart-simple, 1cli-tools (11 extended)
  - Записать в `experiments/md-embedding-server/docs/migration-blast-inventory.md` — per-skill diff stats (ref count, primary tools used, semantic patterns)

- [ ] **Snapshot real MCP JSON responses** (audit fix Smith #5 + Implementation #7):
  - Для canonical args каждого из 29 tools — запустить MCP tool через subprocess (живой server) и сохранить response в `experiments/md-embedding-server/tests/golden/mcp-responses/<tool>.json`
  - Volatile fields (timestamps, cost.session_usd, random ids) — заменить на placeholder pattern `"__VOLATILE__"` или вырезать перед save
  - Эти snapshots становятся source of truth для parity tests в Phase 2 (task-201) и snapshot tests в Phase 5 (task-502) — после удаления живого MCP
  - Без этого шага parity tests становятся stale после Phase 5 removal

- [ ] Создать git tag `pre-mcp-refactor-2026-05-22` на текущем main как rollback point.
  - `git tag pre-mcp-refactor-2026-05-22 main`
  - Не push в remote — локальная safety net

- [ ] Подтвердить что smoke test проходит на baseline.
  - `cd experiments/md-embedding-server/mcp && npm run smoke`
  - Ожидание: 37/37 passing (md_audit skipped без SMOKE_AUDIT=1)
  - Если красное — починить до начала рефактора (refactor не должен начинаться на сломанной базе)

## Готово
- [ ] `_ops/findings/2026-05-22-mcp-registration-locations.md` существует и перечисляет все места регистрации.
- [ ] `docs/tool-signatures-snapshot.json` существует и содержит 29 tool definitions.
- [ ] `docs/envelope-shape-snapshot.md` существует и golden reference envelope shape.
- [ ] `docs/migration-blast-inventory.md` существует и перечисляет каждый файл с количеством refs (13 skills + repo docs).
- [ ] `tests/golden/mcp-responses/<tool>.json` — 29 файлов с volatile fields stripped.
- [ ] git tag `pre-mcp-refactor-2026-05-22` создан локально.
- [ ] `npm run smoke` зелёный 37/37.

## Красные линии
- [ ] Не править ни один файл MCP / skills / docs в этой задаче. Только observation + snapshot.
- [ ] Не push tag в remote.
- [ ] Не удалять старые snapshot файлы из `docs/refactor-plan/` — они часть исторической evidence.

## Проверка
1. `ls experiments/md-embedding-server/docs/` — три новых файла (tool-signatures-snapshot.json, envelope-shape-snapshot.md, migration-blast-inventory.md)
2. `git tag | grep pre-mcp-refactor` — тег существует
3. `cat _ops/findings/2026-05-22-mcp-registration-locations.md` — заполнен
4. `cd experiments/md-embedding-server/mcp && npm run smoke` — 37/37 passing
