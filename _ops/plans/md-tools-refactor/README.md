# md-tools refactor — overview

Эта папка содержит полный план рефактора Markdown corpus tooling (`1md-navigator` + `1md-graph` capabilities) в единый Python backend, выставленный агенту **только через MCP**. Skill folders становятся pure `SKILL.md` без кода.

## Чтение этой папки

Fresh agent, читающий впервые: начни с **этого README**, затем **`task-001-md-tools-unified-backend.md`** (high-level контракт — цель, scope, definition of done), затем phase tasks в порядке `phase-1` → `phase-7`. Каждый phase task self-contained — file paths, code snippets, verification steps, без dependency на этот чат.

## Высокоуровневый контекст

**Что было до рефактора (2026-05-21)**:
- Navigator backend живёт в `experiments/md-embedding-server/scripts/navigator/` (Python package, 22 модуля, ~8200 LOC, clean)
- Graph backend живёт в `~/.claude/skills/1md-graph/scripts/md_graph.py` (1446 LOC, монолит, **дублирует parsing** из navigator)
- MCP server в `experiments/md-embedding-server/mcp/` (Node, версия 0.3.0, 14 tools зарегистрированы в Claude+Codex)
- Skill folders содержат `scripts/` с симлинками на backend
- Tier 1 capabilities partially готовы (anchor-aware extraction в `read-related`, `md_section_blast_radius` hybrid coordinator)
- Tier 2 capabilities (section profile, originality, refactor proposals) — не реализованы

**Что строим**:
- Единый backend в repo (graph мигрирован в navigator package, никакого parsing дублирования)
- MCP — **единственный** мост от skills к backend (CLI fallback через симлинки во время migration, удаляется в P7)
- Tier 1 atomic + composite tools (link counts, importance, md_orient, md_edit_context с modes)
- Tier 2: section profile (LLM-prompt classifier), originality, refactor proposals (proposal output shape, не verdict)
- Workflow recipes в SKILL.md
- Backend deps: `networkx`, `scipy` (inline в uv shebang)

## Phase overview

| Phase | Файл | Цель | Cost | Depends on |
|---|---|---|---|---|
| P1 | [`phase-1-foundation-refactor.md`](phase-1-foundation-refactor.md) | Перенос md_graph → navigator/graph.py, deduplicate parsing, новые модули link_graph + importance | ~1.5 дня | — |
| P2 | [`phase-2-tier1-atomic-capabilities.md`](phase-2-tier1-atomic-capabilities.md) | link counts в md_ls/md_toc, новый md_importance, preview mode в md_read_related | ~0.5 дня | P1 |
| P3 | [`phase-3-tier1-composite-tools.md`](phase-3-tier1-composite-tools.md) | md_orient (cheap), md_edit_context (3 modes) | ~0.5 дня | P2 |
| P4 | [`phase-4-section-profile-foundation.md`](phase-4-section-profile-foundation.md) | section_profile.py (LLM-prompt classifier), cache в sections table, invalidation rules | ~1.5-2 дня | P1 (не P3) |
| P5 | [`phase-5-tier2-capabilities.md`](phase-5-tier2-capabilities.md) | md_originality, md_owner_candidates (internal), md_refactor_candidates + md_query_by_type composite | ~2 дня | P4 |
| P6 | [`phase-6-workflow-recipes.md`](phase-6-workflow-recipes.md) | 5-7 recipes в каждом из 4 SKILL.md | ~0.5 дня | P3 (Tier 1) или P5 (всё) |
| P7 | [`phase-7-cleanup.md`](phase-7-cleanup.md) | Удалить scripts/ из skill папок, обновить README, project-graph | ~0.5 часа | Burn-in после P3+P6 |

**Total ~6-7 дней работы**. Phase boundaries — каждая phase это атомарный commit, можно paused между phases.

## Tool surface (target после рефактора)

| Layer | Tools | Описание |
|---|---|---|
| **Composite primary (6)** | `md_orient`, `md_edit_context`, `md_section_blast_radius`, `md_audit`, `md_refactor_candidates`, `md_query_by_type` | Pre-baked workflows. Описания начинаются с `**Primary tool for X workflow**`. |
| **Atomic public (~9)** | `md_search`, `md_ls`, `md_toc`, `md_read_related`, `md_preflight`, `md_impact`, `md_health`, `md_status`, `md_ping` | Building blocks. Описания начинаются с `Building block — usually called via Y composite`. |
| **Internal (не expose)** | `md_pick`, `md_cat`, `md_deps`, `md_classify_section`, `md_originality`, `md_owner_candidates` | Используются только composite tools внутри. Не зарегистрированы в `listTools`. |

`md_cat` остаётся public но scoped: «heading-aware extract from map. For one-file path use built-in Read».

## Skill boundaries

Backend единый, но skills остаются два — по **intent** пользователя:

**`1md-navigator`** owns workflows: orient (W1), find (W2), read-with-context (W3), corpus health (W6), refactor opportunities (W7), semantic-shape query (W8).

**`1md-graph`** owns workflows: edit safety (W4), rename/delete safety (W5).

**Cross-cutting**: `md_edit_context` упомянут в обоих SKILL.md как primary — trigger «я буду править X» + trigger «обогатить контекст файла» оба правомерны.

## Decisions made (зафиксированы перед planning)

- `md_orient` — final name for W1 composite (не `md_overview`, не `md_cold_start`)
- `md_edit_context` — primary в обоих SKILL.md (dup OK для cross-cutting)
- Section classifier — **lightweight LLM-prompt** через OpenRouter (не fine-tune, не rule-based как primary)
- `section_profile` — richer model чем плоский type. Profile = `{ type, subject, owns_terms, mentions, evidence_sources, confidence }` (адресовано в адверсариальном review)
- `md_refactor_candidates` output — **proposal shape** (evidence + confidence + why), не verdict, не automation
- Scripts/ удаление в skill folders — **two-step**: P1 оставляет симлинки (CLI safety), P7 удаляет после burn-in
- `obsidiantools` отклонён после spike: наш корпус — mixed-link-style (markdown links доминируют), obsidiantools парсит только `[[wikilinks]]`. Используем NetworkX напрямую с нашим `markdown_io`
- Editorial verification (P5), не accuracy labels: «real refactor session, ≥5/10 proposals actionable»

## Adversarial review points (integrated)

External agent ревью (2026-05-21) поймал критические gaps, которые integrated в plan:
- Tool surface раздут (22 → ~15) — composite-first, internal helpers hidden
- `section_profile` > `section_classifier` (richer foundation)
- Cache invalidation must-have в P4 (mtime + model + prompt version)
- md_edit_context modes (preview/full/strict) — иначе context bloat
- md_orient cheap-only discipline — иначе дублирует audit
- NetworkX metrics ≠ owner truth — composite signal в owner_candidates
- proposal output shape для refactor_candidates — evidence/confidence/why, no automation
- editorial verification (не accuracy labels) для Tier 2

## Stop rules для всего refactor

- LLM profile cost эскалирует > $0.50 на `knowledge/` corpus — stop P4, оставить P1-P3 как deliverable
- `md_refactor_candidates` outputs noise > signal в editorial session — stop P5, reshape
- P1 backend migration ломает CLI consumers — rollback, переоценить migration strategy
- User explicit меняет goal/scope/done — escalate в `1strategy-docs`, не продолжать рефактор по инерции

## Где начать (для нового агента)

1. Прочитать `task-001-md-tools-unified-backend.md` — high-level контракт
2. Прочитать `phase-1-foundation-refactor.md` — детальный план первой phase
3. Прочитать соответствующие anchor docs (`_ops/GOAL.md`, root `AGENTS.md`, root `CLAUDE.md`, `_ops/AGENTS.md`)
4. Прочитать current backend code: `experiments/md-embedding-server/scripts/navigator/markdown_io.py`, `~/.claude/skills/1md-graph/scripts/md_graph.py`
5. Запустить smoke до изменений: `cd experiments/md-embedding-server/mcp && npm run smoke` — должно быть 15/15
6. Начать P1

После каждой phase — запустить smoke и golden output diff (где применимо).

## Связанные документы

- `task-001-md-tools-unified-backend.md` — high-level контракт (цель / DoD / risks)
- `_ops/GOAL.md` — project-wide контракт
- `_ops/PROJECT-ROADMAP.md` — current active front (pointer на этот task)
- `_ops/user-said/2026-05-21.md` — durable architecture decision (один backend, MCP-only)
- `_ops/self-learning/user-workflow-probe-skip-on-design.md` — paterns learned during design
- `experiments/md-embedding-server/mcp/README.md` — current MCP catalog (обновляется в P7)
- `~/.claude/skills/1md-navigator/SKILL.md`, `~/.claude/skills/1md-graph/SKILL.md` — skill workflow docs (обновляются в P6)
- `~/.codex/skills/1md-{navigator,graph}/SKILL.md` — Codex зеркала skills (обновляются в P6)
