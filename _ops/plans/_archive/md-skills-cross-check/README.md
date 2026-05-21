# md-skills-cross-check

После закрытия md-tools-refactor (2026-05-21): проверить **все** упоминания `1md-navigator` и `1md-graph` в остальных скилах (Claude + Codex) и поправить stale signals.

## Зачем

Refactor закрылся, но скилы, которые ссылаются на graph/navigator, могли остаться на старой surface:
- Stale script paths (`~/.claude/skills/1md-*/scripts/...` — больше не существует)
- Старые tool names (`md_overlaps`/`md_repeated_concepts`/`md_cluster` — теперь internal к `md_audit`)
- Старые версии MCP (0.3.x / 0.4.x → 0.5.x)
- Stale framing («skill ships bundled CLI», «scripts/ symlink» — пост-рефактор неверно)
- Wrong tool routing

## Batches

| Batch | Файл | Скилы | ~файлов |
|---|---|---|---|
| 1 | [`batch-1-tools-navigation.md`](batch-1-tools-navigation.md) | `1cli-tools`, `1start-here`, `1repo-map`, `1smart-simple` | ~14 |
| 2 | [`batch-2-architecture.md`](batch-2-architecture.md) | `1instruction-layer`, `1folder-contract`, `1skill-architect`, `1planning` | ~12 |
| 3 | [`batch-3-decision-verification.md`](batch-3-decision-verification.md) | `1strategy`, `1strategy-docs`, `1work-review`, `1ia-audit`, `1assumption-audit`, `1findings` | ~14 |
| 4 | [`batch-4-obsidian.md`](batch-4-obsidian.md) | `1obsidian` (heavy single skill: 4 files × 2 platforms) | ~10 |

Все batches могут идти параллельно — disjoint file slices.

## Reference truth (для каждого subagent)

Прочитать перед правками:

1. `~/.claude/skills/1md-navigator/SKILL.md` — canonical navigator workflows post-refactor
2. `~/.claude/skills/1md-graph/SKILL.md` — canonical graph workflows post-refactor
3. `/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/README.md` — current MCP catalog (19 tools, composite/atomic/internal layers)
4. `/Users/triton/Documents/GitHub/agentic-research/_ops/findings/2026-05-21-md-refactor-editorial-verification.md` — refactor closure summary
5. `/Users/triton/Documents/GitHub/agentic-research/_ops/project-graph.md` — post-P7 cross-project blast notes

## Closeout

После всех 4 batches:
1. Parent session собирает отчёты
2. Если ничего серьёзного не уплыло — один сводный commit
3. Никаких side-effects сами subagents не делают (не запускают smoke, не комитят)
