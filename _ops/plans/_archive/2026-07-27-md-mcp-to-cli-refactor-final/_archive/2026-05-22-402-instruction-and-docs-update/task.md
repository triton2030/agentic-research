# Update instruction files и repo docs

## Цель
Обновить все instruction files (`AGENTS.md`, `CLAUDE.md` корневые и subtree) и repo docs (`README.md`, `_ops/project-graph.md`, server README) — убрать MCP wording, добавить CLI.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (project root rules)
- `CLAUDE.md` (project root)
- `_ops/project-graph.md`
- `experiments/md-embedding-server/AGENTS.md` (если существует)
- `~/.claude/CLAUDE.md` — global user instructions (если содержит refs)

## Зависимости
- task-401 закрыт (registration убран, теперь docs могут это reflect)

## Подшаги

- [ ] Update `/Users/triton/Documents/GitHub/agentic-research/CLAUDE.md`:
  - Найти упоминания «MCP» / «md-mcp» / function-call syntax `md_X({...})`
  - Заменить на CLI syntax `md X ...`
  - Раздел «$1md-navigator теперь использует ...» обновить под CLI
  - Сохранить общий смысл (когда использовать какие commands), только syntax заменить

- [ ] Update `/Users/triton/Documents/GitHub/agentic-research/AGENTS.md`:
  - Те же правки
  - Раздел «Локальные Инструменты» если упоминает MCP — обновить

- [ ] Update `/Users/triton/Documents/GitHub/agentic-research/_ops/project-graph.md`:
  - Раздел «Cross-project blast» note про post-P7 refactor — обновить, добавить note про post-MCP refactor (2026-05-22):
    > Note (post-MCP refactor 2026-05-22): MCP server удалён. Skills используют CLI `md` (Python). Backend живёт в `experiments/md-embedding-server/src/`. CLI — единственная точка вызова.
  - Зависимости папок — `experiments/md-embedding-server/` теперь не depends-on MCP server (его нет). Корректировать wording.

- [ ] Update `/Users/triton/Documents/GitHub/agentic-research/README.md`:
  - Если упоминает md-MCP — заменить на md CLI
  - Если есть «как запустить» — обновить под `uv tool install`

- [ ] Update `/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/README.md`:
  - Главная правка: убрать «MCP server is the single bridge» wording
  - Заменить на: «CLI `md` is the unified entry point. Python library `navigator/` is the pure backend.»
  - Удалить раздел про MCP-каталог
  - Удалить упоминания `npm run smoke` → заменить на `md selftest`
  - Update «Developer workflow» table — убрать MCP rows
  - Update «Embedding backend» section (keep как есть — embedding logic не меняется)

- [ ] Update `experiments/md-embedding-server/AGENTS.md` если существует — те же правки

- [ ] Scan для оставшихся MCP refs в repo docs:
  - `grep -rn "mcp\|MCP\|md-mcp" /Users/triton/Documents/GitHub/agentic-research --include="*.md" 2>/dev/null | grep -v "experiments/md-embedding-server/mcp/" | grep -v "_ops/plans/_archive/" | grep -v "/_ops/plans/md-mcp-to-cli-refactor/"` → ideally empty
  - Если есть валидные historical refs (например в archived plans) — оставить как есть с note «historical context»

- [ ] **Не править** `_ops/plans/_archive/` — archived plans — это historical record, не source of truth для current state

- [ ] Verify routing инструкции (CLAUDE.md / AGENTS.md):
  - «$1md-navigator используется для ...» — wording должен work для CLI

- [ ] **Code locality pre-commit gate** (audit cycle-2 Implementation G3):
  - Создать `~/.claude/hooks/pre-tool-Write.py` (или PreToolUse matcher для `Write|Edit` в `~/.claude/settings.json`)
  - Hook блокирует write в `~/.claude/skills/**/*` и `~/.codex/skills/**/*` если файл вне whitelist:
    - Allowed: `SKILL.md`, `references/*.md`, `agents/openai.yaml`, `assets/*.{png,jpg,gif,svg}`
    - Blocked: `*.py`, `*.sh`, `*.js`, `*.ts`, `*.mjs`, `*.rb`, any other extension
  - Это proactive enforcement, не after-fact `find` scan
  - Document hook в `_ops/findings/2026-MM-DD-code-locality-hook.md`

## Готово
- [ ] `CLAUDE.md`, `AGENTS.md` — нет references к MCP server / md_* function-call syntax
- [ ] `_ops/project-graph.md` обновлён, depends-on links корректны
- [ ] `README.md` (root и server) — обновлены
- [ ] Скан MCP refs в repo docs (вне archive и mcp/ folder) → 0 unintended refs
- [ ] Routing работает: новая сессия со skill `1md-navigator` использует CLI

## Красные линии
- [ ] Не править archived plans (`_ops/plans/_archive/`).
- [ ] Не править Goal-цитату в AGENTS.md/CLAUDE.md (sync через `1folder-contract` — owner для этой Goal-quote).
- [ ] Не удалять MCP wording из historical findings/decisions (это часть истории).
- [ ] Не менять wording GOAL.md (это `1strategy-docs` owner).

## Проверка
1. `grep -rn "mcp__md-mcp\|md_orient({" /Users/triton/Documents/GitHub/agentic-research/CLAUDE.md /Users/triton/Documents/GitHub/agentic-research/AGENTS.md` → 0 matches
2. `grep -rE "md_[a-z_]+\(\{" experiments/md-embedding-server/README.md` → 0 matches
3. `cat _ops/project-graph.md | grep "post-MCP refactor 2026-05-22"` → есть note
4. Manual: launch new Claude session, ask «как использовать `1md-navigator`?» — answer cites CLI commands, not MCP
