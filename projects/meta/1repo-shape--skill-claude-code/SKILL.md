---
name: 1repo-shape
description: >
  Use this skill whenever repo/runtime shape is the object: "папки", "структура репы", "hooks", "permissions", "MCP", "settings.json", "tools", "validators", "guardrail", "runtime", "файловая форма", "folder ownership", "repo shape", "Claude Code config", "permission rule". Designs folders, hooks, permissions, validators, and tool boundaries. Skip skill descriptions, task criteria, project roadmap, and prose-only instruction placement.
---

# Repo Shape

Design repo and runtime control surfaces: folders, files, hooks, permissions, MCP, validators, and tool boundaries.

## Role

Use this when the system shape is enforced by filesystem topology or Claude Code runtime mechanics rather than instruction wording alone.

## First Read

- Current repo tree and relevant config files.
- `.claude/settings.json`, `.claude/settings.local.json`, or global settings when relevant.
- Existing hooks, validators, scripts, and MCP config.
- `references/claude-runtime-guardrails.md` for Claude Code runtime mechanisms.

## Workflow

1. Name the failure mode or desired invariant.
2. Choose the strongest appropriate layer: hook, permission, validator, folder rule, MCP scope, skill, or instruction text.
3. Prefer structural enforcement over wording when failure cost is high.
4. Keep repo shape minimal and explain ownership.

## Output Contract

Return the chosen control surface, owner, exact config/file target, expected behavior, and verification command.

## Role Boundaries

- Does not write task contracts or project roadmap.
- Does not design skill trigger surfaces; route to `skill-architect`.
- Does not place prose rules in AGENTS/CLAUDE unless paired with `1instruction-layer`.
- Before proposing a new code/docs validator, check what is already installed via `repo-power-tools`.

## Структурная критика — Brooks-оптика

Применяю к shape репо (папки, hooks, permissions, settings.json, agent files в `~/.claude/agents/`):

- **Configuration explosion** в `settings.json` (N permission-правил без объединяющего)
- **Hook pass-through** (вызывает один tool без преобразования)
- **Folder без owner / contract** — есть директория, нет принципа что в ней живёт

**Stop-rule:** если не могу назвать ownership папки/настройки — находка, не добавляй структуру.

**Subagent fallback:** `brooks` опционально на hook-скриптах (они код).

Полный словарь: `knowledge/wisdom-structural-critique.md`.

## References

- [references/claude-runtime-guardrails.md](references/claude-runtime-guardrails.md)
