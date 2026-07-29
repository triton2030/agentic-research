# Claude skills migration: 1md-navigator + 1md-graph

## Цель
Обновить `~/.claude/skills/1md-navigator/` и `~/.claude/skills/1md-graph/` (SKILL.md + references) — заменить MCP function-call syntax на CLI invocation syntax. Сохранить overlay style (skill = надстройка над tool catalog, не дубль descriptions).

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root — repo-wide rules)
- `~/.claude/CLAUDE.md` — global user instructions
- `_ops/project-graph.md` — cross-project blast секция (veto-class)

## Execution-side marker (audit Codex #5)
**Claude-only execution.** Эта задача правит `~/.claude/skills/**`. AGENTS.md rule: «Для Codex поверхности Claude всегда только для чтения». Codex агенту не запускать эту задачу.

## Status — 2026-05-22

blocked-for-codex. Codex did not edit `~/.claude/**`. Stale MCP-era refs remain
in Claude `1md-navigator` and `1md-graph`; evidence and consequence are recorded
in `_ops/findings/2026-05-22-claude-skills-migration-blocker.md`.

## Architectural anchor (code locality)
НЕ добавлять никаких Python scripts или executable artifacts в skill folders. Только SKILL.md + references/. Это user requirement: skills disposable, tool stable.

## Зависимости
- task-003 закрыт (semantic equivalence doc — source of truth для patterns)
- task-104 закрыт (`md tools --json` есть как catalog)
- task-201 + task-202 + task-203 + task-204 закрыты (все 29 tools работают)
- task-105 закрыт (md selftest verify передаётся)

## Подшаги

- [ ] Inventory mapping. Создать конкретный mapping из текущих skill references:
  - `md_orient({ corpus })` → `md orient --corpus PATH`
  - `md_search({ corpus, query })` → `md search PATH "query"` (positional corpus per CLI conventions)
  - `md_edit_context({ path, mode: "preview" })` → `md edit-context --path PATH --mode preview`
  - `md_read_related({ paths: [...], scan, mode })` → `md read-related --path PATH --scan ROOT --mode MODE`
  - `md_overlaps({ corpus })` → `md overlaps PATH`
  - `md_repeated_concepts({ corpus })` → `md repeated-concepts PATH`
  - `md_audit({ corpus })` → `md audit PATH`
  - `md_refactor_candidates({ corpus, top })` → `md refactor-candidates PATH --top N`
  - `md_query_by_type({ corpus, types })` → `md query-by-type PATH --types open-question,decision`
  - `md_corpus_scan({ root })` → `md corpus-scan --root PATH`
  - `md_section_blast_radius({ path, corpus, query })` → `md section-blast-radius --path PATH --corpus PATH --query "..."`
  - `md_preflight({ path })` → `md preflight --path PATH`
  - `md_impact({ path })` → `md impact --path PATH`
  - `md_deps({ depth })` → `md deps --path PATH --depth N`
  - `md_health` → `md health --scan PATH`
  - `md_cycles` → `md cycles --scan PATH`
  - `md_check` → `md check --scan PATH`
  - `md_scan` → `md scan --paths PATH`
  - `md_changed` → `md changed --base BRANCH`
  - `md_init`, `md_strip`, `md_index`, `md_profile_sections` →
    dry-run first, then confirm only with returned `transaction_id`

- [ ] Перейти в `~/.claude/skills/1md-navigator/` и обновить:
  - `SKILL.md` — заменить все `md_X({...})` на `md X ...` syntax
  - `references/setup.md` — обновить setup instructions (uv tool install вместо MCP register)
  - `references/index-lifecycle.md` — обновить commands
  - `references/engine-internals.md` — обновить если упоминает MCP

- [ ] Перейти в `~/.claude/skills/1md-graph/` и обновить:
  - `SKILL.md` — заменить syntax
  - (нет references по результатам file list)

- [ ] **Сохранить overlay style**:
  - Skills НЕ дублируют WHEN/WHY/INPUT/OUTPUT — это в `md tools --json` (точка discovery)
  - Skills учат WHEN применять и HOW читать output
  - Если skill сейчас содержит inline tool description — удалить, оставить ссылку на `md tools <name>`

- [ ] Обновить **CLI Fallback** секции:
  - Сейчас: «CLI-вызов — только для отладки. Основной путь — MCP.»
  - Стало: «Основной путь — CLI. Без MCP.»
  - Удалить упоминания о MCP server

- [ ] **Transaction safety blocker from task-003 review**:
  - `~/.claude/skills/1md-navigator/SKILL.md` currently names
    `md_index` / `md_profile_sections` as `dry_run + confirm` without explicit
    transaction wording.
  - During migration, rewrite to:
    `md index CORPUS --dry-run --json` → read `transaction_id` →
    `md index CORPUS --confirm --transaction-id <id> --json`; same for
    `md profile-sections` when `mode=llm`.
  - Do not leave runnable bare `--confirm` guidance.

- [ ] Обновить **«Как этот скил работает с MCP»** секцию:
  - Переименовать → «Как этот скил работает с CLI»
  - Заменить «MCP `listTools`» → «`md tools` (или `md tools --json`)»
  - «Этот скил — надстройка» → текст остаётся, ссылка на CLI catalog

- [ ] Обновить SKILL.md frontmatter `name`/`description`:
  - description должна содержать примеры invocation syntax (CLI shape, не function shape)
  - Поскольку description загружается на все sessions, важно чтобы trigger-фразы остались точны

- [ ] Запустить self-check после правок:
  - `python3 experiments/md-embedding-server/scripts/sync-skill-docs.py --check` для Claude side
  - Если есть устаревший check который ожидает MCP — обновить или skip script (он не authoritative gate)

## Готово
- [ ] `~/.claude/skills/1md-navigator/SKILL.md` не содержит `md_<name>({` syntax (grep returns 0)
- [ ] `~/.claude/skills/1md-graph/SKILL.md` не содержит `md_<name>({`
- [ ] `~/.claude/skills/1md-navigator/references/setup.md` упоминает `uv tool install`, не MCP register
- [ ] `~/.claude/skills/1md-navigator/references/index-lifecycle.md` использует CLI commands
- [ ] Overlay style сохранён — нет дубля WHEN/WHY/INPUT/OUTPUT из catalog
- [ ] CLI Fallback / How-skill-works sections переписаны под CLI primary path
- [ ] **Evidence file** (audit Smith #8): `_ops/findings/2026-MM-DD-claude-md-skills-migration.md` создан с записью: дата, какой prompt дан в bare-prompt subagent test, какой первый CLI command в trace, прошёл ли
- [ ] Code locality: `find ~/.claude/skills/1md-navigator ~/.claude/skills/1md-graph -name "*.py" -o -name "*.sh" 2>/dev/null` → 0 new code files

## Красные линии
- [ ] Не править Codex skills — это task-302.
- [ ] Не менять meaning W1-W8 recipes — только syntax in tool invocations.
- [ ] Не удалять references files целиком — обновлять content.
- [ ] Не делать backward-compat пропуска через 2 syntax. Только CLI после refactor.

## Проверка
1. `grep -rE "md_[a-z_]+\(\{" ~/.claude/skills/1md-navigator ~/.claude/skills/1md-graph` → 0 matches
2. `grep -rE "mcp__md-mcp" ~/.claude/skills/1md-navigator ~/.claude/skills/1md-graph` → 0 matches
3. `grep -E "uv tool install" ~/.claude/skills/1md-navigator/references/setup.md` → есть упоминание
4. Manual smoke: launch fresh Claude session, ask "о чём папка `_ops`?" — skill срабатывает, использует `md orient`, не выдаёт MCP syntax
