# Claude extended skills migration (11 skills)

## Цель
Обновить 11 Claude skills которые используют MCP tools как **механизмы** (не только упоминают): 1ia-audit, 1instruction-layer, 1planning, 1strategy, 1strategy-docs, 1folder-contract, 1assumption-audit, 1work-review, 1skill-architect, 1smart-simple, 1cli-tools. Каждый сохраняет свой semantic pattern of use; меняется только syntax (MCP function-call → CLI invocation).

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)
- `~/.claude/CLAUDE.md` (global user instructions)
- `_ops/project-graph.md` — Cross-project blast (veto-class)

## Execution-side marker
**Claude-only execution.** Эта задача правит файлы в `~/.claude/skills/**`. AGENTS.md rule: «Для Codex поверхности Claude всегда только для чтения». Codex агенту не запускать эту задачу.

## Зависимости
- task-003 закрыт (semantic equivalence doc — определяет patterns которые надо сохранить)
- task-201 + task-202 + task-203 + task-204 закрыты (CLI работает)
- task-104 закрыт (`md tools --json` каталог)

## Подшаги

- [ ] Использовать `docs/skills-semantic-equivalence.md` (task-003) как source of truth для каждого skill. Не выдумывать новые mappings.

- [ ] **Внутреннее разделение task на 2 sub-groups** (audit cycle-2 Smith G3 — undifferentiated 11-skill block):
  - **Sub-group A — pure syntax replace (no semantic patterns)**: `1cli-tools/references/`, `1strategy`, `1folder-contract`, `1strategy-docs` (частично already CLI-shaped) — fast mechanical.
  - **Sub-group B — patterns-preserving**: `1ia-audit`, `1instruction-layer`, `1planning`, `1assumption-audit`, `1work-review`, `1skill-architect`, `1smart-simple` — каждая имеет специфические patterns (threshold, scope, rerank, dry-run/confirm flows) которые надо verify per-skill против equivalence doc.
  - Evidence file имеет separate sub-sections для A и B (different verification rigor).

- [ ] **Skill 1: `~/.claude/skills/1ia-audit/SKILL.md`** (22 refs)
  - Replace MCP function-calls на CLI invocations согласно equivalence doc
  - Особенно table «6 IA-classes routing» — там много md_audit references
  - Сохранить classification mapping (smeared_owner_truth, tight_duplicates, etc.)

- [ ] **Skill 2: `~/.claude/skills/1instruction-layer/SKILL.md`** (14 refs total in SKILL.md + references)
  - Replace в SKILL.md
  - Replace в `references/language-quality-audit.md`
  - Сохранить rerank patterns, scope=descriptions usage

- [ ] **Skill 3: `~/.claude/skills/1planning/SKILL.md`** (11 refs)
  - Replace в W1-W5 recipes
  - Особенно `md_orient`, `md_extract`, `md_query_by_type`, `md_preflight`, `md_edit_context`, `md_changed`
  - Сохранить «status + map + importance в одном проходе» pattern для `md_orient`

- [ ] **Skill 4: `~/.claude/skills/1strategy/SKILL.md`** (8 refs)
  - Replace MCP `md_search` и `md_extract` на CLI

- [ ] **Skill 5: `~/.claude/skills/1strategy-docs/SKILL.md`**
  - Этот skill **частично already CLI-shaped** (uses `1md-navigator status _ops/`, `1md-graph preflight`)
  - Verify all invocations match new CLI syntax (е.g. `md status _ops/` или `1md-navigator` остаётся как pointer to skill, а tool call всё равно `md status`)
  - Decision: содержание `1md-navigator <subcommand>` references — это skill name pointer, не CLI command. Возможно нужно `md <subcommand>` directly.

- [ ] **Skill 6: `~/.claude/skills/1folder-contract/SKILL.md`**
  - Replace `md_changed({ staged: true })` → `md changed --staged --json`
  - Replace `md_search` references

- [ ] **Skill 7: `~/.claude/skills/1assumption-audit/SKILL.md`**
  - Replace MCP `md_search` с threshold/scope/limit parameters
  - Replace `md_overlaps({ corpus, threshold: 0.85, top: 10 })` → `md overlaps PATH --threshold 0.85 --top 10 --json`
  - Replace `md_read_related`

- [ ] **Skill 8: `~/.claude/skills/1work-review/SKILL.md`**
  - Replace `md_changed`, `md_preflight`, `md_health`, `md_check`, `md_edit_context`
  - Сохранить closeout/post-execution gate logic

- [ ] **Skill 9: `~/.claude/skills/1skill-architect/SKILL.md`** (audit cycle-2 Implementation G9 — recursive blast risk)
  - Replace `md_index({ corpus: "~/.claude/skills", confirm: true })` → `md index --corpus ~/.claude/skills --confirm --transaction-id <id>` (с two-step dry-run/confirm protocol)
  - Replace `md_search({ corpus: "~/.claude/skills", ... })`
  - Replace `md_overlaps({ corpus: "~/.claude/skills", threshold: 0.7, top: 10 })`
  - **CRITICAL note**: `md index --corpus ~/.claude/skills` мутирует то же место где живёт сам skill. SKILL.md должна явно учить: «при testing workflow на skills/ — использовать tmpdir copy `cp -r ~/.claude/skills /tmp/skills-test && md index --corpus /tmp/skills-test ...`, не live `~/.claude/skills/`». Это safety pattern для recursive surface.

- [ ] **Skill 10: `~/.claude/skills/1smart-simple/SKILL.md`**
  - Replace MCP `md_search({ corpus, query, limit: 3 })` → `md search PATH "query" --limit 3 --json`
  - Replace MCP `md_index dry-run/confirm` flow на CLI version
  - Сохранить cost-guard pattern (~$0.02 per ~1000 sections)

- [ ] **Skill 11: `~/.claude/skills/1cli-tools/references/markdown-track.md` + `tool-map.md`**
  - Replace MCP references на CLI references
  - Эти files — references, не SKILL.md — но они tool selection hints

- [ ] **Architectural anchor (code locality)**:
  - НЕ добавлять Python скрипты или executable artifacts в skill folders
  - Только SKILL.md и `references/*.md` (declarative + reference docs)
  - Все executable code остаётся в `experiments/md-embedding-server/`

- [ ] **Evidence file**:
  - Создать `_ops/findings/2026-MM-DD-claude-extended-skills-migration.md`:
    - List of 11 skills migrated
    - Diff stats per skill (lines changed, refs replaced)
    - Manual verification: 2-3 skills тестируются bare-prompt subagent
    - Any unexpected drift / pattern mismatches

- [ ] **Verify нет stale MCP refs**:
  - `grep -rE "md_[a-z_]+\(\{" ~/.claude/skills/` (исключая 1md-navigator, 1md-graph которые уже в task-301) → должен быть пуст
  - `grep -rE "mcp__md-mcp" ~/.claude/skills/` → пусто

## Готово
- [ ] Все 11 SKILL.md / references обновлены под CLI syntax
- [ ] `grep -rE "md_[a-z_]+\(\{" ~/.claude/skills/` (кроме core 2) → 0 matches
- [ ] `grep -rE "mcp__md-mcp" ~/.claude/skills/` → 0 matches
- [ ] Evidence file создан с diff stats и manual verification notes
- [ ] Никаких scripts/Python в skill folders (code locality rule соблюдён)
- [ ] Semantic patterns из equivalence doc сохранены (threshold, scope, rerank, dry-run/confirm flows)

## Красные линии
- [ ] Не править Codex skills (это task-305).
- [ ] Не менять meaning skills (W-recipes, IA classes, routing) — только syntax tool invocations.
- [ ] Не добавлять scripts/code в skill folders — code locality anchor.
- [ ] Не пропускать `1cli-tools/references/` — это тоже affected.
- [ ] Не выдумывать new CLI flags которых нет в catalog (task-104).

## Проверка
1. `grep -rE "md_[a-z_]+\(\{" ~/.claude/skills/ | grep -v "1md-navigator\|1md-graph"` → 0
2. `grep -rE "mcp__md-mcp" ~/.claude/skills/` → 0
3. `find ~/.claude/skills/1ia-audit ~/.claude/skills/1instruction-layer ~/.claude/skills/1planning ~/.claude/skills/1strategy ~/.claude/skills/1strategy-docs ~/.claude/skills/1folder-contract ~/.claude/skills/1assumption-audit ~/.claude/skills/1work-review ~/.claude/skills/1skill-architect ~/.claude/skills/1smart-simple ~/.claude/skills/1cli-tools -name "*.py" -o -name "*.sh" 2>/dev/null` → 0 new code files
4. Bare-prompt subagent test: запустить 2-3 skills с trigger phrases → используют `md` CLI
5. Evidence file `_ops/findings/2026-MM-DD-claude-extended-skills-migration.md` exists
