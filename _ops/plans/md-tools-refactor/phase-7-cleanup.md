# Phase 7 — Cleanup (final)

**Estimated cost**: ~0.5 часа (после burn-in confirmation)
**Depends on**: P6 + **burn-in period** (≥1 real session usage P1-P6 без fallback к Bash)
**Unblocks**: done

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md`. **Эта phase удаляет файлы из cross-project surfaces (`~/.claude/skills/**`, `~/.codex/skills/**`) — `_ops/project-graph.md` помечает это как veto-class. Требуется explicit `AskUserQuestion` подтверждение перед удалением.**

## Цель

Финальная уборка после того как unified backend + MCP стабильны:

1. **Удалить `scripts/` папки из всех skill folders** (Claude + Codex × navigator + graph = 4 папки)
2. **Обновить `mcp/README.md`** — финальный tool catalog
3. **Обновить `experiments/md-embedding-server/README.md`** — реальную shape backend (no legacy MLX server references)
4. **Обновить `_ops/project-graph.md`** — отразить что `~/.claude/skills/**` теперь pure SKILL.md
5. **Удалить .bak файлы** оставшиеся после P1 migration

## In scope

- Удаление `scripts/` из 4 skill folders
- Удаление симлинков в скилл-папках (если P1 их оставил)
- README обновления в mcp/ и md-embedding-server/
- `_ops/project-graph.md` cross-project blast section update
- Removal of any leftover `.bak.YYYYMMDD` files

## NOT in scope

- Архивация старых plans (уже сделано до начала refactor)
- Removal of `experiments/md-embedding-server/scripts/md_navigator.py` (entry-script остаётся — это canonical CLI fallback)
- Удаление uv inline deps (networkx/scipy остаются — нужны backend)

## Definition of done

- `~/.claude/skills/1md-navigator/scripts/` — **удалена** (whole folder)
- `~/.claude/skills/1md-graph/scripts/` — **удалена**
- `~/.codex/skills/1md-navigator/scripts/` — **удалена**
- `~/.codex/skills/1md-graph/scripts/` — **удалена**
- `experiments/md-embedding-server/mcp/README.md` — final tool catalog с workflow grouping
- `experiments/md-embedding-server/README.md` — отражает unified backend (graph migrated, link_graph+importance added, profile в sections table)
- `_ops/project-graph.md` cross-project blast section упоминает что skills теперь pure
- Нет `*.bak.YYYYMMDD` файлов в repo или skill folders
- Smoke `npm run smoke` final: 22+/22+ passed (или actual final count после P5)
- Fresh Claude session запускается, MCP `md_orient`, `md_edit_context`, etc. работают **без CLI fallback** (даже для index — pointer на repo CLI всё ещё есть, но не нужен в обычной работе)
- Fresh Codex session — то же

## Stop rules

- Burn-in period не подтверждён — STOP, не удалять scripts/
- User explicit hesitates — STOP, retain scripts/ as safety net
- Smoke regression после удаления — restore scripts/, investigate

## Подшаги

### P7.0 — Burn-in confirmation (pre-requisite)

**Перед P7 execution**:

1. ≥1 real session (≥30 min usage) с MCP composite tools без fallback к Bash
2. User explicit подтвердил «scripts/ можно удалять»
3. Smoke 100% passing на latest version (post-P6)
4. `claude mcp list` показывает `md-mcp: ✓ Connected`
5. Codex `config.toml` показывает `[mcp_servers.md-mcp]` block, restart Codex done

Если хотя бы один пункт не выполнен — defer P7.

### P7.1 — AskUserQuestion confirmation (5 минут)

Перед удалением — explicit user confirm через `AskUserQuestion`:

```
"Удаление scripts/ из 4 skill folders необратимо без git restore.
Backend единый, MCP стабилен. Подтверждаешь?"
Options:
- Yes, remove scripts/
- Defer P7
```

If "Defer P7" → не выполнять P7.

### P7.2 — Removal: ~/.claude/skills/ scripts (5 минут)

```bash
# Backup positions сначала
echo "Pre-removal symlinks state:"
ls -la ~/.claude/skills/1md-navigator/scripts/ 2>&1
ls -la ~/.claude/skills/1md-graph/scripts/ 2>&1

# Remove
rm -rf ~/.claude/skills/1md-navigator/scripts/
rm -rf ~/.claude/skills/1md-graph/scripts/

# Verify
ls ~/.claude/skills/1md-navigator/ 2>&1
ls ~/.claude/skills/1md-graph/ 2>&1
# Expected: only SKILL.md, references/, agents/ (if any) — no scripts/
```

### P7.3 — Removal: ~/.codex/skills/ scripts (5 минут)

```bash
# Same procedure
ls -la ~/.codex/skills/1md-navigator/scripts/ 2>&1
ls -la ~/.codex/skills/1md-graph/scripts/ 2>&1

rm -rf ~/.codex/skills/1md-navigator/scripts/
rm -rf ~/.codex/skills/1md-graph/scripts/

ls ~/.codex/skills/1md-navigator/ 2>&1
ls ~/.codex/skills/1md-graph/ 2>&1
```

### P7.4 — Update mcp/README.md (10 минут)

**Файл**: `experiments/md-embedding-server/mcp/README.md`

Финальный tool catalog (composite primary first, atomic public second, internal third):

```markdown
# md-mcp

Unified MCP server для Markdown corpus tooling. Single backend в repo,
single MCP source, single CLI entry. Skill folders pure SKILL.md.

## Tool catalog (final, version 0.X.0)

### Composite primary (6) — use these first

| Tool | Workflow | Description |
|---|---|---|
| `md_orient` | W1 orient | Instant orientation in unfamiliar corpus (status + ls + importance) |
| `md_edit_context` | W4 edit safety | Pre-edit packet (3 modes: preview / full / strict) |
| `md_section_blast_radius` | W5b rename section | Hybrid graph + semantic для секции |
| `md_audit` | W6 corpus health | Orchestrated audit (slow, ~minutes) |
| `md_refactor_candidates` | W7 refactor opportunities | Top-N proposals (Tier 2) |
| `md_query_by_type` | W8 semantic-shape query | Filter by profile.type (Tier 2) |

### Atomic public (~9) — building blocks

| Tool | Note |
|---|---|
| `md_status` | Index freshness |
| `md_ls` | Folder + optional link counts |
| `md_toc` | Heading menu |
| `md_search` | Semantic + keyword retrieval |
| `md_read_related` | Linked neighborhood, anchor-aware default, optional preview mode |
| `md_preflight` | Pre-edit graph slice |
| `md_impact` | Delete/rename graph blast |
| `md_health` | Graph health summary |
| `md_importance` | Centrality metrics (NOT semantic ownership) |
| `md_cat` | Heading-aware extract from map |
| `md_ping` | Health check |

### Internal (not exposed in listTools)

`md_pick`, `md_deps`, `md_classify_section`, `md_originality`, `md_owner_candidates`
— used by composites internally.

## Architecture

Single Python backend: `experiments/md-embedding-server/scripts/navigator/`
- `markdown_io.py` — parsing primitives (single source)
- `folder_map.py` — file/section inventory, link counts
- `search.py`, `index*.py` — embeddings + sqlite-vec
- `graph.py` — graph capabilities (migrated from md_graph.py в P1)
- `link_graph.py` — NetworkX graph builder (P1)
- `importance.py` — centrality metrics (P1)
- `section_profile.py` — LLM-prompt classifier with cache (P4)
- `originality.py`, `owner_detector.py`, `refactor_proposals.py` — Tier 2 (P5)

Entry script: `scripts/md_navigator.py` — uv self-bootstrap with inline deps.

MCP server: Node, `mcp/src/server.js`, registered в Claude + Codex.

## Skills (pure workflow docs)

`~/.claude/skills/1md-navigator/SKILL.md` — understanding workflows
`~/.claude/skills/1md-graph/SKILL.md` — edit-safety workflows
`~/.codex/skills/1md-{navigator,graph}/SKILL.md` — Codex mirrors

No scripts/ folders в skill packages — backend единый в repo.

## CLI fallback

Все capabilities available через `md_navigator.py` (entry-script).
Mutating commands (`index`, `init`, `strip`, `profile-sections`) — CLI-only by design.
```

### P7.5 — Update experiments/md-embedding-server/README.md (10 минут)

**Файл**: `experiments/md-embedding-server/README.md`

Обновить:
- Убрать legacy MLX server mention (или объяснить как историю)
- Описать unified backend shape (graph migrated, link_graph, importance, section_profile)
- Указать что навigator теперь exposes graph subcommands тоже
- Обновить commands list

### P7.6 — Update _ops/project-graph.md (5 минут)

**Файл**: `_ops/project-graph.md`

В `## Veto-class` секции, в `Cross-project blast`:

```markdown
**Cross-project blast** (требует явного `AskUserQuestion` перед commit):

- `~/.claude/skills/**` — правка задевает все Claude-проекты.
  **Note (post-P7 refactor 2026-MM-DD)**: skills теперь pure SKILL.md
  (no scripts/). Backend живёт в `experiments/md-embedding-server/scripts/navigator/`.
- `~/.codex/skills/**` — то же, post-refactor.
- ... (rest existing) ...
```

### P7.7 — Remove .bak files (2 минуты)

```bash
find ~/.claude/skills/1md-graph -name "*.bak.*" -type f -delete 2>&1
find ~/.codex/skills/1md-graph -name "*.bak.*" -type f -delete 2>&1
find /Users/triton/Documents/GitHub/agentic-research -name "*.bak.*" -type f 2>&1
```

### P7.8 — Final smoke + cross-runtime verification (15 минут)

```bash
cd /Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp
npm run smoke
# Expected: final 22+/22+ passed
```

Manual cross-runtime check:
1. New Claude session: list tools → md_orient, md_edit_context, ... всё visible
2. New Codex session: same
3. Trigger `md_orient knowledge` from both — works
4. Trigger `md_search knowledge "test query"` from both — works

## Verification (общая для P7)

- [ ] 4 skill `scripts/` folders deleted
- [ ] `mcp/README.md` обновлён с finals tool catalog
- [ ] `experiments/md-embedding-server/README.md` обновлён
- [ ] `_ops/project-graph.md` Cross-project blast section отражает post-P7 state
- [ ] No `*.bak.*` files remain
- [ ] Smoke final pass
- [ ] Fresh Claude session: composite tools work without fallback к Bash
- [ ] Fresh Codex session: same

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| User regrets removal of scripts/ for CLI fallback in skill folder | git restore — все scripts/ removal is git-tracked. Can revert. |
| Existing scripts in skill folder were symlinks; rm -rf на symlink удалит исходный файл | Symlink deletion ≠ target deletion (rm -rf на symlink directory удалит сам symlink или contents через target?). **Verify тип scripts/ — folder или symlink** перед rm. If symlink: `rm symlink-name`. If folder с симлинками внутри: `rm -rf folder-name` only removes folder + symlink files, not targets. |
| Cross-runtime drift не замечен | Final manual check both Claude и Codex sessions; same MCP server, no divergence possible на runtime side |
| project-graph.md update забыли — future agent предполагает старую shape | Explicit update в P7.6 |

## Hand-off

После P7 готов: **refactor complete**.

- Backend единый в repo
- MCP — single bridge
- Skills pure workflow
- All Tier 1 + Tier 2 capabilities ready
- Cross-runtime works
- README обновлены, project-graph обновлён

Closeout:
- `_ops/PROJECT-ROADMAP.md` — `1planning` обновляет current active front (P7 done, готовы к следующей задаче)
- Archive task folder: `_ops/plans/md-tools-refactor/` → `_ops/plans/_archive/md-tools-refactor/` (всё ещё может быть полезно для reference)
- Final summary commit (if applicable git push)

## Anchors / Evidence

- High-level контракт: `task-001-md-tools-unified-backend.md`
- All previous phases must be complete
- Burn-in confirmation от user (explicit «can remove scripts/»)
- `_ops/project-graph.md` Veto-class section about cross-project blast surfaces
