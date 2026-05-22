# Codex extended skills migration (11 skills)

## Цель
Зеркало task-304 для Codex. Те же 11 skills, но `~/.codex/skills/**`. Включая Codex-specific surfaces: `agents/openai.yaml.default_prompt` (где tool invocation guidance зашита в prose), `references/`, и `scripts/` если present.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)
- `~/.codex/AGENTS.md` (если есть)
- `_ops/project-graph.md`

## Execution-side marker
**Codex-only OR Claude-running-in-repo execution.** Эта задача правит `~/.codex/skills/**`. Если запускает Claude — он не должен trigger каких-либо Codex skills (просто edit files). Если запускает Codex — он не должен править Claude surfaces (task-304 — Claude only).

## Зависимости
- task-003 закрыт (semantic equivalence doc)
- task-201 + task-202 + task-203 + task-204 закрыты (CLI работает)
- task-104 закрыт (catalog)
- task-304 closed OR parallel (independent после task-003 + Phase 2)

## Подшаги

- [ ] Использовать `docs/skills-semantic-equivalence.md` как source of truth.

- [ ] **11 skills к миграции в Codex side**:
  - `~/.codex/skills/1ia-audit/SKILL.md`
  - `~/.codex/skills/1instruction-layer/SKILL.md`
  - `~/.codex/skills/1planning/SKILL.md`
  - `~/.codex/skills/1strategy/SKILL.md`
  - `~/.codex/skills/1strategy-docs/SKILL.md`
  - `~/.codex/skills/1folder-contract/SKILL.md`
  - `~/.codex/skills/1assumption-audit/SKILL.md`
  - `~/.codex/skills/1work-review/SKILL.md`
  - `~/.codex/skills/1skill-architect/SKILL.md`
  - `~/.codex/skills/1smart-simple/SKILL.md`
  - `~/.codex/skills/1cli-tools/` (SKILL.md + references + agents)

- [ ] Для каждого skill — те же правки что в task-304, по той же mapping table.

- [ ] **CRITICAL FIX (audit cycle-2 Codex G1)**: первоначальный план целился в `agents/openai.yaml.default_prompt` как primary target. **Реальность**: `grep` по `~/.codex/skills/*/agents/openai.yaml` показал **0 MCP refs** во всех 13 yaml files. Все MCP refs живут в **SKILL.md**, как и на Claude side.
  - **Primary target — SKILL.md** (mirror task-304 mapping, 11 skills)
  - `default_prompt` rewrite — **только** если scan показывает refs (scan-and-skip pattern):
    - `grep -lE "md_[a-z_]+|md-mcp|MD_NAVIGATOR_SCRIPT" ~/.codex/skills/*/agents/openai.yaml` → если non-empty список, в нём — только targets
    - Если для конкретного skill yaml пуст по MCP refs — НЕ править default_prompt того skill
  - Single exception (likely): `~/.codex/skills/1md-navigator/references/setup.md` использует `MD_NAVIGATOR_SCRIPT` env var + uv shebang path — обновить под `uv tool install md-tools` (task-302 покрывает)

- [ ] Verify что `agents/openai.yaml` структура сохранена:
  - НЕ выдумывать поля `tools:` или `dependencies:` если их не было
  - НЕ менять `policy:` секции если они там есть (например `policy.allow_implicit_invocation`)
  - Только `default_prompt` content и `short_description` если упоминают MCP

- [ ] **CLI binary discovery в Codex sandbox**:
  - Codex `sandbox_mode = "workspace-write"` — read access вне workspace доступен
  - `md` CLI находится в `~/.local/bin/md` (после `uv tool install`)
  - Verify Codex env PATH включает `~/.local/bin/` (обычно да, sandbox не блокирует PATH)
  - Если sandbox не пускает — это Phase 4 problem (task-401 / task-204)

- [ ] **Mutating tools в Codex sandbox**:
  - `md init`, `md strip`, `md index` пишут в `<corpus>/.md-navigator/`
  - Если corpus вне Codex workspace — `sandbox_mode="workspace-write"` блокирует
  - Document в risk section evidence file: workspace boundary важна для mutating

- [ ] **Architectural anchor (code locality — scope clarification audit cycle-2 Codex G3)**:
  - НЕ добавлять **md-tools-related** Python scripts в `~/.codex/skills/`
  - Существующие `scripts/` папки в 12 Codex skills (1start-here, 1findings, 1interview-tool, 1user-said, 1cli-tools, etc.) — **не md-related**, НЕ трогать (out of scope этого refactor)
  - Только SKILL.md, references/, agents/openai.yaml (декларативные правки)
  - Если в одном из 11 target skills (1md-navigator/1md-graph/extended) есть scripts что-то md-tools related — переместить в `experiments/md-embedding-server/`

- [ ] **Evidence file**:
  - Создать `_ops/findings/2026-MM-DD-codex-extended-skills-migration.md`
  - List of 11 skills + diff stats
  - Manual verification: 2 skills тестируются в реальной Codex session с trigger phrase
  - `default_prompt` review per skill — confirmed CLI invocations work

- [ ] **Verify**:
  - `grep -rE "md_[a-z_]+\(\{" ~/.codex/skills/` (кроме core 2) → 0
  - `grep -rE "mcp__md-mcp\|MD_NAVIGATOR_SCRIPT\|md_navigator\.py" ~/.codex/skills/` → 0 (или только в legit historical context)
  - `find ~/.codex/skills/1ia-audit ~/.codex/skills/1instruction-layer ~/.codex/skills/1planning ~/.codex/skills/1strategy ~/.codex/skills/1strategy-docs ~/.codex/skills/1folder-contract ~/.codex/skills/1assumption-audit ~/.codex/skills/1work-review ~/.codex/skills/1skill-architect ~/.codex/skills/1smart-simple ~/.codex/skills/1cli-tools -name "*.py" -o -name "*.sh" 2>/dev/null` → expected count (preserves only non-md-tools scripts если они есть)

## Готово
- [ ] Все 11 Codex SKILL.md / references / `agents/openai.yaml` обновлены
- [ ] `default_prompt` в каждом yaml ссылается на `md` CLI, не на MCP / MD_NAVIGATOR_SCRIPT
- [ ] Никаких new Python scripts в `~/.codex/skills/` (code locality)
- [ ] Evidence file `_ops/findings/2026-MM-DD-codex-extended-skills-migration.md` exists
- [ ] Manual Codex session smoke pass (2+ skills work через CLI)

## Красные линии
- [ ] Не править Claude skills (task-304).
- [ ] Не менять meaning skills.
- [ ] Не выдумывать `agents/openai.yaml` поля.
- [ ] Не trust «mirror task-304» — Codex specifics (default_prompt prose) requires actual rewrite.
- [ ] Не добавлять executable code в skill folders — code locality.

## Проверка
1. `grep -rE "md_[a-z_]+\(\{" ~/.codex/skills/ | grep -v "1md-navigator\|1md-graph"` → 0
2. `grep -rE "MD_NAVIGATOR_SCRIPT" ~/.codex/skills/` → 0
3. Manual: open `~/.codex/skills/1planning/agents/openai.yaml`, verify `default_prompt` mentions `md` CLI
4. Evidence file exists с specific Codex smoke results
