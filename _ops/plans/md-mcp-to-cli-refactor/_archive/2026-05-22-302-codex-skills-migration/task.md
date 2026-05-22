# Codex skills migration: 1md-navigator + 1md-graph + agents/openai.yaml

## Цель
Зеркало task-301 для Codex. Те же правки, но в `~/.codex/skills/1md-{navigator,graph}/`, плюс обновить `agents/openai.yaml` (metadata/policy/dependencies surface).

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)
- `~/.codex/AGENTS.md` если существует
- `_ops/project-graph.md` — cross-project blast секция

## Execution-side marker
**Codex-only OR Claude-running-in-repo execution.** Если запускает Claude — он не triggers Codex skills (просто edit files). Если запускает Codex — он НЕ правит Claude surfaces.

## Architectural anchor (code locality)
НЕ добавлять Python scripts в `~/.codex/skills/`. Только SKILL.md + references/ + agents/openai.yaml (declarative).

## Status — 2026-05-22

completed. Codex `1md-navigator` and `1md-graph` now use real `md`
subcommands, transaction-token wording, and CLI runtime checks.
`agents/openai.yaml` metadata stayed in the existing shape; no invented
`tools:`/`dependencies:` fields. Fresh-eyes drift around stale plain `md_*`
tokens and index-before-work metadata was accepted and repaired. Evidence:
`_ops/findings/2026-05-22-codex-skills-cli-migration.md` and
`_ops/findings/2026-05-22-fresh-eyes-md-cli-audit.md`.

## Зависимости
- task-003 закрыт (semantic equivalence doc)
- task-201 + task-202 + task-203 + task-204 закрыты (CLI работает) — **исправлено deps** (audit Smith #2): task-302 не depend на task-301; обе можно выполнять параллельно после Phase 2
- task-104 закрыт (catalog)

## Подшаги

- [ ] Открыть Claude версии SKILL.md (`~/.claude/skills/1md-navigator/SKILL.md` и `1md-graph/SKILL.md`) как reference. Codex и Claude версии должны быть синхронны.

- [ ] Перейти в `~/.codex/skills/1md-navigator/` и обновить:
  - `SKILL.md` — те же правки MCP syntax → CLI syntax
  - `references/setup.md` — обновить под Codex environment specifics (если есть Codex-only paths)
  - `references/index-lifecycle.md` — обновить
  - `references/engine-internals.md` — обновить
  - `agents/openai.yaml` — обновить `dependencies` / `tools` секции если они упоминают md-mcp; добавить depends на `md-tools` CLI (или alternative metadata если openai.yaml не имеет dependency syntax)

- [ ] Перейти в `~/.codex/skills/1md-graph/` и обновить:
  - `SKILL.md`
  - `agents/openai.yaml`

- [ ] Verify Codex-specific differences (если есть):
  - Возможно Codex skill использует другой syntax invocations (например `$skill_run`)
  - Codex использует другие env vars или paths
  - Если различия есть — документировать в comments в SKILL.md

- [ ] **Transaction safety blocker from task-003 review**:
  - `~/.codex/skills/1md-navigator/SKILL.md` currently says `md_index` /
    `md_profile_sections` use `dry_run + confirm` without an explicit
    transaction token.
  - During migration, rewrite this to CLI safety wording:
    `md index CORPUS --dry-run --json` → read returned `transaction_id` →
    `md index CORPUS --confirm --transaction-id <id> --json`; same for
    `md profile-sections` when `mode=llm`.
  - Do not leave any runnable bare `--confirm` instruction.

- [ ] Run skill sync check (Claude → Codex parity):
  - `python3 experiments/md-embedding-server/scripts/sync-skill-docs.py --check`
  - Этот script сейчас проверяет Claude/Codex skill docs sync. Может потребовать обновления под новый CLI syntax (см. task-303).
  - Допустимый intentional drift между Claude и Codex — должен быть документирован.

- [ ] `agents/openai.yaml` specifics (audit Codex #2 — corrected after actual file inspection):
  - **Реальный shape**: `~/.codex/skills/1md-navigator/agents/openai.yaml` имеет `interface.default_prompt` (большой prose-блок с описанием как звать tools), `interface.short_description`, `policy.allow_implicit_invocation: true`. НЕТ секций `tools:` или `dependencies:`.
  - **Не выдумывать** эти отсутствующие поля.
  - **Главная правка — `default_prompt`**:
    - Содержит inline mentions `md_navigator.py index/search/overlaps`, `MD_NAVIGATOR_SCRIPT` env var, MCP server lookup logic
    - Переписать под `md` CLI invocations
    - Добавить guidance: «Полный каталог инструментов: `md tools --json`», «Описание конкретного tool: `md tools <name>`»
    - Удалить все упоминания MCP server / MD_NAVIGATOR_SCRIPT / md_navigator.py paths
  - **1md-graph specifics**: `~/.codex/skills/1md-graph/agents/openai.yaml` содержит только `interface.short_description` + `default_prompt` (без `policy:`). Сохранить асимметрию с navigator (которая имеет policy).

## Готово
- [ ] `~/.codex/skills/1md-navigator/SKILL.md` не содержит `md_<name>({` syntax
- [ ] `~/.codex/skills/1md-graph/SKILL.md` не содержит `md_<name>({`
- [ ] `~/.codex/skills/1md-navigator/SKILL.md` не содержит bare confirm prose
  for `md_index` / `md_profile_sections`
- [ ] `~/.codex/skills/1md-navigator/agents/openai.yaml` обновлён
- [ ] `~/.codex/skills/1md-graph/agents/openai.yaml` обновлён
- [ ] Все references обновлены (setup, index-lifecycle, engine-internals)
- [ ] `sync-skill-docs.py --check` либо проходит, либо явно документирует expected drift

## Красные линии
- [ ] Не вносить Codex specifics в Claude skills (это task-301).
- [ ] Не менять semantic content / W-recipes — только syntax.
- [ ] Не править Claude skills из Codex side (cross-platform правило из AGENTS.md).
- [ ] Не выдумывать `agents/openai.yaml` поля которых не было.

## Проверка
1. `grep -rE "md_[a-z_]+\(\{" ~/.codex/skills/1md-navigator ~/.codex/skills/1md-graph` → 0 matches
2. `grep -rE "mcp__md-mcp" ~/.codex/skills/1md-navigator ~/.codex/skills/1md-graph` → 0 matches
3. `diff <(grep -E "md [a-z-]+" ~/.codex/skills/1md-navigator/SKILL.md) <(grep -E "md [a-z-]+" ~/.claude/skills/1md-navigator/SKILL.md)` → minimal (allowed Codex-specific exceptions)
4. `python3 experiments/md-embedding-server/scripts/sync-skill-docs.py --check` → ok or documented drift only
