# Убрать MCP server registration

## Цель
Полностью удалить registration `md-mcp` server из всех Claude/Codex конфигов. После этой задачи Claude/Codex больше не пытаются спавнить Node MCP server при старте сессии.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)
- `_ops/project-graph.md` — veto-class сross-project blast

## Зависимости
- task-000 закрыт (известны все registration paths из findings)
- task-301 + task-302 + task-303 закрыты (skills уже работают через CLI, MCP больше никому не нужен)

## Подшаги

- [ ] Прочитать `_ops/findings/2026-05-22-mcp-registration-locations.md` (создан в task-000) — список всех мест где живёт `md-mcp` registration.

- [ ] Для каждого найденного места:
  - Открыть файл
  - Найти секцию относящуюся к `md-mcp` (typically `mcpServers.md-mcp` или похожая структура)
  - Удалить блок
  - Сохранить, проверить что JSON/TOML/YAML остаётся валидным

- [ ] **Codex `~/.codex/config.toml` точные lines к удалению** (audit cycle-2 Codex G4):
  - Эти 3 строки на line ~348-350:
    ```toml
    [mcp_servers.md-mcp]
    command = "node"
    args = ["/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/src/server.js"]
    ```
  - Использовать Edit tool с этим точным `old_string` (3 lines, unique pattern). Не трогать `[mcp_servers.gemini-mcp]` рядом (line ~340) и `[mcp_servers.claude-mcp]` (line ~336).
  - После Edit — verify TOML syntax: `python3 -c "import tomllib; tomllib.loads(open('/Users/triton/.codex/config.toml').read()); print('ok')"` → "ok"

- [ ] Известные potential locations к проверке (verified против actual filesystem 2026-05-22):
  - `~/.claude/settings.json` — `mcpServers` секция (проверено: md-mcp здесь нет)
  - `~/.claude/settings.local.json` — same
  - `~/.claude/plugins/*/mcp.json` — plugin-level registration
  - `~/.claude/marketplaces/*/plugins/*/mcp.json` — marketplace plugin registration
  - **`~/.codex/config.toml`** — Codex MCP servers под `[mcp_servers.md-mcp]` (TOML format, **подтверждено**, файл существует ~9883 bytes). Также там есть `[mcp_servers.gemini-mcp]` — не трогать.
  - **`~/.codex/mcp.json` НЕ существует** — это миф из early plan, удалить из проверки
  - Repo-level `.mcp.json` в `/Users/triton/Documents/GitHub/agentic-research/`

- [ ] Add Bash allowlist для CLI (audit Codex #4):
  - **Claude**: В `~/.claude/settings.json` (или `~/.claude/settings.local.json`):
    ```json
    "permissions": {
      "allow": [
        "Bash(md *)"
      ]
    }
    ```
    Это позволит Claude вызывать CLI без permission prompt каждый раз.
  - **Codex**: НЕТ `~/.codex/permissions.json` — это миф. Codex использует `sandbox_mode = "workspace-write"` (line 4 в config.toml) + per-project `trust_level = "trusted"`. Для trusted projects Bash работает без allowlist. **Никаких permission правок Codex side не нужно** при условии что user работает в trusted projects.
  - Document в evidence file что Codex side требует только удаление `[mcp_servers.md-mcp]`, без permission setup.

- [ ] Verify removal:
  - `find ~/.claude ~/.codex -name "*.json" -o -name "*.toml" -o -name "*.yaml" 2>/dev/null | xargs grep -l "md-mcp\|md_mcp" 2>/dev/null` → empty или только в комментариях/legacy

- [ ] Перезапустить Claude / Codex после правок (если требуется для cache reload):
  - Документировать в task notes если restart требуется
  - Verify что в новой сессии deferred tools list НЕ содержит `mcp__md-mcp__*`

- [ ] Document changes:
  - Запись в `_ops/findings/2026-05-22-mcp-registration-removed.md` — какие файлы изменены, какие удалены, какие Bash allow добавлены

## Готово
- [ ] Все registration points удалены — `find ... | xargs grep "md-mcp"` пусто
- [ ] Bash allowlist `Bash(md *)` добавлен в Claude settings
- [ ] Bash allowlist для Codex (если применимо)
- [ ] В новой Claude сессии deferred tools не содержат `mcp__md-mcp__*`
- [ ] `_ops/findings/2026-05-22-mcp-registration-removed.md` документирует все правки

## Красные линии
- [ ] Не трогать другие MCP servers в settings (только md-mcp).
- [ ] Не делать backup settings.json перед правкой (Edit tool already preserves).
- [ ] Не push settings.json в git если содержит сensitive — только локально править.
- [ ] Не оставлять permission allow без удаления registration (это лишнее разрешение).

## Проверка
1. `find ~/.claude ~/.codex -type f \( -name "*.json" -o -name "*.toml" -o -name "*.yaml" \) 2>/dev/null | xargs grep -l "md-mcp" 2>/dev/null` → empty
2. `cat ~/.claude/settings.json | jq '.permissions.allow | map(select(. | contains("md")))'` → contains "Bash(md *)" или конкретные tools
3. Manual: launch Claude session, check deferred tools list — `mcp__md-mcp__*` absent
4. `md ping` invoked through Bash без permission prompt в новой Claude сессии
