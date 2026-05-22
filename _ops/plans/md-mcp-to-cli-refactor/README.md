# md-mcp → CLI Refactor

## Status

Closed 2026-05-22. Task files moved to `_archive/2026-05-22-*/task.md`.
Closeout evidence:
`_ops/findings/2026-05-22-mcp-refactor-closeout.md`.

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

`_ops/PROJECT-ROADMAP.md#Archived 2026-05-22`.

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
| `task-101-pyproject-and-dispatch.md` | pyproject, entry `md`, lazy dispatch, runner + ToolResult, PEP 723 shebang preservation |
| `task-102-envelope-module.md` | `envelope.py` — runner-owned single wrap point; atomic write для cost ledger |
| `task-103-transactions-module.md` | Stateless fingerprint + intent-binding; TTL race fix |
| `task-104-tool-catalog.md` | `catalog.py` — contract map для 29 tools (library_function/workflow_function references) |
| `task-105-selftest-and-doctor.md` | In-process selftest; `md doctor` |
| `task-106-architecture-lock.md` | NEW (architectural review): GATE — frozen mcp-tool-snapshot.json + boundary/transaction/lazy-import tests перед Phase 2 |

### Phase 2 — Tool migration (REORDERED: 202a первым)
| Task | Что закрывает |
|---|---|
| `task-202a-navigator-public-api-refactor.md` | **ПЕРВЫМ**: implement 24 atomic + 5 workflow functions в navigator/. Без этого handlers оборачивают cmd_*. |
| `task-201-atomic-tools-navigator-graph.md` | 16 navigator + 8 graph atomic handlers (24 total, **не 30**); parity tests против golden fixtures |
| `task-202-composite-tools.md` | 4 composite handlers (thin wrappers над navigator.workflows.*) |
| `task-203-hybrid-tool.md` | 1 hybrid handler (thin wrapper над navigator.workflows.section_blast_radius) |
| `task-204-mutating-guards.md` | 4 mutating handlers (md_init/md_strip/md_index/md_profile_sections) с dry-run/confirm/fingerprint |

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
| `task-501-cross-project-smoke-pre-removal.md` | NEW ORDER: cross-project smoke ДО deletion; verify parity tests already snapshot-based |
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

## Architecture (4-layer, после architectural review)

```
LAYER 1 — Library functions (pure, importable)
  src/navigator/{status,search,map,...}.py
  → 24 atomic functions: typed args in, dict out, no IO кроме file/HTTP, no envelope
  → navigator/__init__.py exports all 24 в __all__

LAYER 2 — Workflow functions (agent-facing, importable)
  src/navigator/workflows/{orient,edit_context,refactor_candidates,query_by_type,section_blast_radius}.py
  → 5 workflows: композируют library functions
  → import only from navigator (atomic), не из md_cli, не друг из друга
  → returns dict, не печатает JSON, не строит envelope

LAYER 3 — CLI commands (thin handlers)
  src/md_cli/handlers/{md_<name>}.py
  → 29 handlers (24 atomic + 5 workflow)
  → каждый ≤30 LOC; argparse parsing + call library OR workflow function
  → returns dataclass ToolResult(payload: dict, exit_code: int)
  → NEVER prints JSON, NEVER imports envelope module

LAYER 4 — Central runner (single point envelope ownership)
  src/md_cli/main.py + src/md_cli/runner.py
  → argparse dispatch
  → calls handler.run(args) → ToolResult
  → wraps ToolResult.payload в envelope.wrap()
  → serializes к JSON, prints to stdout
  → exits with ToolResult.exit_code
```

**Почему**: handler-печатает-JSON распределяет envelope creation по 29 файлам → drift; composite в `md_cli/composites/` смешивает agent-logic с CLI mechanics → coupling; navigator без public API forces handlers parse stdout from old CLI → not a real refactor.

**Tool count contract** (точная сверка с MCP `listTools`):
- 24 atomic = 16 navigator (md_audit, md_corpus_scan, md_extract, md_importance, md_index, md_init, md_ls, md_overlaps, md_ping, md_profile_sections, md_read_related, md_repeated_concepts, md_search, md_status, md_strip, md_toc) + 8 graph (md_changed, md_check, md_cycles, md_deps, md_health, md_impact, md_preflight, md_scan)
- 5 workflow = 4 composite (md_orient, md_edit_context, md_refactor_candidates, md_query_by_type) + 1 hybrid (md_section_blast_radius)
- **Total: 29** — соответствует `TOOL_ANNOTATION_ALLOWLIST` в `mcp/src/server.js`

Note: предыдущая версия плана говорила «22 navigator + 8 graph = 30» — **ошибка** (реально 16+8=24). Также `md_ping` defined inline в `server.js` line ~141, не в `tools/*.js` — этот tool нужно явно включить в catalog.

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

## Architectural corrections round (после cycle-2 audit + user review)

User дал architectural-level feedback который пропустили все 3 audit агента (они смотрели «как написано», а не «куда положить ответственность»). 6 правок:

1. **Contract map как single source of truth** — `src/md_cli/catalog.py` (task-104) расширен: для каждого из 29 tools поля `library_function` или `workflow_function`, `handler_module`, `category` (atomic/workflow), `tests_module`. Без этого drift между «29 tools / 30 atomic handlers / 30+ subcommands» начнётся в первый же день.
2. **4-layer architecture** (см. выше) — workflow layer между library и CLI; central runner владеет envelope; handlers тонкие (`ToolResult` pattern).
3. **Navigator full public API** — task-202a требует **24 atomic functions** (полное покрытие), не «минимум 10». Все atomic capabilities имеют typed signature.
4. **Workflow layer в `navigator/workflows/`** — не в `md_cli/composites/`. Композиции — это agent-facing logic, importable, reusable за пределами CLI (например, hook scripts могут импортировать `navigator.workflows.orient`).
5. **md_profile_sections — cost-bearing** — добавлен в task-204 рядом с md_init/md_strip/md_index (lazy LLM profiling stoит реальных $).
6. **Deletion gate clean install** — task-501 enhanced: `uv tool install . --force` в temp HOME, cwd вне repo, потом `md ping/status/tools/selftest --json`. Тест на installed package, не editable repo (catches missing deps в pyproject).
