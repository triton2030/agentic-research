# md-mcp → CLI Refactor

## Цель

Убрать Node MCP server (`experiments/md-embedding-server/mcp/`, ~2228 LOC JS, 29 tools), заменить его единым Python CLI `md` с library/CLI split. Skills обновляются механически (find&replace), внешний контракт для агентов остаётся: те же 29 имён tools, та же envelope shape, тот же dry-run/confirm.

## Почему refactor в polygon-проекте

`_ops/GOAL.md#NOT in scope` говорит: «Runtime-код агентов или продуктовая кодовая база» не в scope. Этот refactor затрагивает 2228 LOC JS + новый Python package — кажется runtime-кодом. Anchor-line: **`md` CLI и `navigator/` библиотека — infrastructure под `_ops/` workflow самого полигона** (skills, hooks, retrieval, instruction sync), не product. Без него polygon не работает. Это in-scope как **рабочий инструмент полигона**, не как продукт.

## Что не делаем

- Backward-compat MCP wrapper — big-bang, без моста.
- Empirical SKILL.md trigger test — доверяемся mechanical replace.
- Смена языка (Rust/Go) — Python оставляем, потеря NetworkX/pymorphy/markdown ecosystem не оправдана.
- Распределённое наращивание фич — refactor по форме, не по поведению.

## Анкор

`_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor` (current path).

## Blast scope (исправлено после inventory)

**Не 2 skills, а 13** на каждой платформе (Claude + Codex) ссылаются на MCP tools:

**Core (создатели контракта):**
- `1md-navigator`, `1md-graph`

**Extended consumers (используют md_* как механизмы):**
- `1ia-audit` (22 refs) — md_audit, md_search, md_repeated_concepts, md_overlaps, md_toc, md_extract
- `1instruction-layer` (14 refs) — md_overlaps, md_repeated_concepts, md_audit, md_search (+rerank)
- `1planning` (11 refs) — md_orient, md_ls, md_search, md_extract, md_query_by_type
- `1strategy` (8 refs) — md_search, md_extract
- `1strategy-docs` (Claude 6, Codex 9 refs) — частично already CLI-shaped (`1md-navigator status _ops/`)
- `1folder-contract` — md_changed (staged), md_search
- `1assumption-audit` — md_search, md_overlaps, md_read_related
- `1work-review` — md_changed, md_preflight, md_health, md_check, md_edit_context
- `1skill-architect` — md_index (dry-run/confirm), md_search, md_overlaps
- `1smart-simple` — md_search, md_index с dry-run/confirm
- `1cli-tools` (только references) — Claude+Codex

Эти skills имеют **семантические patterns of use** (threshold values, scope flags, recipe-specific invocations), которые надо сохранить — не просто find&replace tool name, но и проверить что pattern всё ещё работает.

## Фазы (с учётом audit corrections)

### Phase 0 — Preflight
| Task | Что закрывает |
|---|---|
| `task-000-blast-scope-and-snapshot.md` | Inventory blast, snapshot MCP JSON responses в golden fixtures (для parity tests без живого MCP) |
| `task-001-cli-signature-conventions.md` | Единый стиль CLI flags по 29 tools; multi-word naming (kebab vs snake) |
| `task-002-cli-framework-spike.md` | NEW: argparse-vs-Typer spike на 3 hardest tools до commit на framework |
| `task-003-skill-semantic-equivalence-doc.md` | NEW: документ доказывающий что каждый из 13 skills сохраняет логику после migration (purpose + MCP usage + CLI invocation + semantic patterns) |

### Phase 1 — CLI foundation
| Task | Что закрывает |
|---|---|
| `task-101-pyproject-and-dispatch.md` | pyproject, entry `md`, lazy dispatch, `--help` без heavy imports, PEP 723 shebang preservation |
| `task-102-envelope-module.md` | `envelope.py` — single wrap point; atomic write для cost ledger; Codex session_id fallback chain |
| `task-103-transactions-module.md` | Stateless fingerprint + intent-binding; TTL race fix |
| `task-104-tool-catalog.md` | `md tools --json` discovery; size budget; Codex agent default_prompt mention |
| `task-105-selftest-and-doctor.md` | In-process selftest (не 29×subprocess); `md doctor` |

### Phase 2 — Tool migration
| Task | Что закрывает |
|---|---|
| `task-201-atomic-tools-navigator-graph.md` | 22 navigator + 8 graph atomic; parity tests против golden fixtures (не live MCP) |
| `task-202a-navigator-public-api-refactor.md` | NEW (audit cycle-2 G7): expose importable Python functions в navigator/__init__.py для composites |
| `task-202-composite-tools.md` | 4 composite; fail-fast semantics |
| `task-203-hybrid-tool.md` | 1 hybrid; section-blast-radius parallel |
| `task-204-mutating-guards.md` | dry-run/confirm/fingerprint; Codex sandbox-mode проверка для mutating |

### Phase 3 — Skills migration (большое расширение)
| Task | Что закрывает |
|---|---|
| `task-301-claude-md-skills-migration.md` | Claude `1md-navigator` + `1md-graph` (core); evidence file; Claude-only execution marker |
| `task-302-codex-md-skills-migration.md` | Codex `1md-navigator` + `1md-graph`; `agents/openai.yaml.default_prompt` rewrite; Codex-only execution marker |
| `task-303-references-and-catalog-sync.md` | Generated tool-catalog.md mirrored на обе платформы |
| `task-304-claude-extended-skills-migration.md` | NEW: Claude 11 extended skills (1ia-audit, 1instruction-layer, 1planning, 1strategy, 1strategy-docs, 1folder-contract, 1assumption-audit, 1work-review, 1skill-architect, 1smart-simple, 1cli-tools) |
| `task-305-codex-extended-skills-migration.md` | NEW: Codex 11 extended skills (те же) |

### Phase 4 — Repo migration
| Task | Что закрывает |
|---|---|
| `task-401-mcp-registration-removal.md` | Codex `~/.codex/config.toml` `[mcp_servers.md-mcp]` (TOML); Claude sources; Bash allowlist (только Claude — Codex использует trust_level) |
| `task-402-instruction-and-docs-update.md` | CLAUDE.md, AGENTS.md, project-graph.md, server README обновлены |

### Phase 5 — Removal & closeout
| Task | Что закрывает |
|---|---|
| `task-501-cross-project-smoke-pre-removal.md` | NEW ORDER: cross-project smoke ДО deletion; parity test conversion to snapshot-based |
| `task-502-remove-mcp-and-final-closeout.md` | MCP folder удалён; closeout + archive task capsules; explicit Codex smoke prompt + evidence |

## Порядок выполнения

Фазы строго последовательны: 0 → 1 → 2 → 3 → 4 → 5.

**Корректировки порядка после audit:**
- Phase 5: **сначала smoke (task-501), потом deletion (task-502)** — обратный порядок от прежнего; не удалять MCP до проверки что без него всё работает
- task-301 и task-302 идут параллельно (independent после Phase 2)
- task-304 и task-305 идут параллельно (independent после task-303)

**Cross-platform execution rule (AGENTS.md):**
- task-301 / task-304 — execute Claude-side **ТОЛЬКО**. Codex must not edit Claude surfaces.
- task-302 / task-305 — execute Codex-side **ТОЛЬКО** (или Claude если работает с repo, не с installed Codex skills).

## Архив

`_archive/` существует. После каждой завершённой task — переезд в `_archive/YYYY-MM-DD-<task-slug>/` capsule.

## Code locality (architectural anchor)

**Весь executable код живёт в `experiments/md-embedding-server/`** — pyproject, library, CLI, tests, fixtures, scripts, spike. Skill folders (`~/.claude/skills/**` и `~/.codex/skills/**`) — **pure declarative**.

**Whitelist для skill folders** (audit cycle-2 Smith G8 — verification through whitelist, не black list):
- `SKILL.md`
- `references/*.md` (включая generated `tool-catalog.md` — Smith G7 exception зафиксирована: this is generated documentation artifact, не code; lifecycle через `sync-skill-docs.py` в repo)
- `agents/openai.yaml`
- `assets/*.png` / `assets/*.jpg` (illustrations если есть)

**ANY other file** — verification fail. Это покрывает не только `.py`/`.sh`, но и `.mjs`/`.ts`/`.rb`/inline heredoc scripts.

**Mechanism**: пользователь должен иметь возможность удалять / переименовывать / disable skills без поломки инструмента. Tool — стабильный, skills — disposable. Это обратное направление dependency: skills depend on `md` CLI, `md` CLI не depends на skills.

Применяется в:
- task-101 (Python package shape)
- task-301/302/304/305 (red lines + whitelist verification)
- task-303 (generated `tool-catalog.md` — explicit exception в whitelist)
- task-402 (pre-commit hook для proactive gate — audit cycle-2 Implementation G3)

## Audit history

План прошёл **два цикла** 3-агентского аудита (smith + implementation + Codex parity).

**Cycle 1** (29 findings) — integrated:
- Method-as-goal: parity tests изначально на live MCP → snapshot-based (task-000 + task-201)
- Hidden coupling: task-302 deps fixed (task-201/202/203/204, не task-301)
- One-way door: Phase 5 swapped — smoke до deletion (task-501 smoke, task-502 deletion+closeout)
- Scope failure: Phase 3 расширено (добавлены task-304/305 для extended skills)
- Codex specifics: default_prompt rewrite, config.toml, sandbox-mode, session_id fallback

**Cycle 2** (26 findings) — integrated:
- **CRITICAL (Codex G1)**: task-305 переписан — primary target SKILL.md, не `agents/openai.yaml` (там MCP refs нет, проверено)
- task-202 split → task-202a navigator public API + task-202 composites
- task-501 explicit quorum criteria (3/3 Claude + 2+ Codex skills + extended coverage)
- task-501 Codex restart verification + explicit commands
- task-501 ↔ task-401 ordering — accepted rollback cost с explicit procedure
- task-003 — extraction script automation + evidence path к `1fresh-eyes` review
- task-002 — Phase A (framework) vs Phase B (catalog-driven) + tie-breaker + failure escalation
- Code locality — whitelist verification (audit Smith G8); pre-commit hook в task-402 (audit Implementation G3); `tool-catalog.md` explicit exception
- task-304 — internal split на sub-group A (pure syntax) и sub-group B (patterns-preserving)
- task-305 — code locality scope clarification (только md-related scripts)
- task-401 — exact TOML line removal pattern для Codex
- task-102 — cost ledger rotation; CODEX_SESSION_ID verification
- task-104 — examples в Codex default_prompt (не только catalog hint)
- task-304 1skill-architect — recursive blast warning + tmpdir testing pattern

**Total task count: 23** (was 18 → 22 → 23 after cycle-2 task-202a split).
