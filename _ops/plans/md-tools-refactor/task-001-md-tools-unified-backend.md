# Task 001 — md-tools унифицированный backend + workflow tools

**Status**: P1-P6 + P8 done. P5 editorial verification done 2026-05-21 (task-002 closed, bar reframed). **Outstanding**: P7 cleanup deferred until burn-in.
**Created**: 2026-05-21
**Owner skill**: `1planning` (task content), `1md-navigator` / `1md-graph` (capability ownership), `1instruction-layer` (SKILL.md updates)

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md` (plans/ rules — каждая папка внутри `plans/` получает свой `_archive/`).

## Цель

Унифицировать backend для Markdown corpus tooling (navigator + graph capabilities) в **одном Python package** в repo. Backend выставляется агенту **только через MCP**; skill folders становятся pure `SKILL.md` без своего кода. Tool surface переоформлен **workflow-first** — 6 composite tools для типичных моментов агента, ~9 atomic tools как building blocks. Tier 2 capabilities (section profile, originality, owner candidates, refactor proposals) ложатся на refactor foundation, не патчами.

**Why now**: текущий стек имеет дублированный parsing (`navigator/markdown_io.py` vs `md_graph.py`), graph скрипт живёт вне repo (`~/.claude/skills/`), и любая новая capability требует patches в двух местах. Plus boundary skill/MCP мы установили («MCP = spec, skill = workflow»), но scripts/ в skill folders дублируют backend и подсказывают модели Bash вместо MCP.

## In scope

- Перенос `md_graph.py` (1446 LOC) → `navigator/graph.py` с deduplicate parsing через `markdown_io`
- Новые модули: `navigator/link_graph.py` (NetworkX DiGraph), `navigator/importance.py`
- Tier 1 capabilities: link counts (in/out-degree) в `md_ls`/`md_toc`, новый atomic `md_importance`, новый composite `md_orient`, новый composite `md_edit_context` (с modes preview/full/strict), preview mode для `md_read_related`
- Tier 2 foundation: `navigator/section_profile.py` (LLM-prompt based), cache в `sections` table с invalidation по mtime + model + prompt version
- Tier 2 capabilities: `md_originality` (internal), `md_owner_candidates` (internal), composite `md_refactor_candidates` (proposal output shape), composite `md_query_by_type`
- Tool surface curation: composite-first descriptions, atomic как building blocks, internal helpers не exposed через MCP
- Skill SKILL.md cleanup в конце (P7): удалить scripts/ из 4 skill папок, обновить SKILL.md в обоих runtime (Claude + Codex × navigator + graph) — только после burn-in
- Workflow recipes в обоих SKILL.md
- Smoke + editorial verification per phase

## NOT in scope

- Local llama.cpp inference (vs OpenRouter) — оставляем cloud embeddings
- Write-side tools (create/edit/move/delete файлов через MCP) — намеренно CLI-only
- Time dimension (`md_change_pulse`), packet optimizer, `md_filler_score`, `md_orphan_quarantine` — defer до realistic need
- `obsidiantools` dependency — spike показал mismatch с нашим корпусом (Obsidian-style `[[wikilinks]]` only, мы mixed style). Используем NetworkX напрямую, parsing через свой `markdown_io`
- `mistletoe` replacement парсинга — наши regex'ы работают, не источник боли
- Section auto-link insertion (`md_auto_wikilink`) — automation territory, опасно
- Re-shape `_ops/PROJECT-ROADMAP.md` (это `1strategy-docs`, не здесь)

## Definition of done

- Backend единый: `navigator/` package содержит **и** navigator, **и** graph capabilities; никакого дублирующего parsing
- MCP surface: 6 composite primary + ~9 atomic, descriptions явно разделяют PRIMARY vs Building block
- Tier 1 capabilities работают через MCP: `md_orient`, `md_edit_context` (3 modes), `md_importance`, link counts в `md_ls`/`md_toc`, preview mode в `md_read_related`
- Tier 2 capabilities работают через MCP: `md_query_by_type`, `md_refactor_candidates` с proposal output shape
- Section profile cached с invalidation rules (mtime + model_id + prompt_version)
- Smoke 100% passes на всех phases
- **Editorial verification** (не accuracy labels): real refactor session — agent+user используют `md_refactor_candidates`, suggestions actionable
- 4 SKILL.md обновлены — pure workflow doc, без CLI examples primary (CLI fallback упомянут одной строкой), MCP tools используются как primary
- scripts/ удалены из 4 skill папок (только после burn-in P7)
- Cross-runtime подтверждён: Claude и Codex оба видят все capabilities через MCP

## Stop rules

- spike Tier 2 LLM classifier показывает unacceptable cost (>$0.50 для polygon корпуса) или unacceptable accuracy (proposal noise > signal) → stop Tier 2, оставить P1-P3 как deliverable
- editorial verification fail на Tier 2: suggestions не actionable, user не использует — переосмыслить P5 shape
- core refactor (P1) ломает existing CLI consumers — rollback, переоценить migration strategy
- user explicit меняет goal/scope/done → escalate в `1strategy-docs`

## Подшаги (Phases)

### P1 — Foundation refactor (~1.5 дня)

- Перенести `~/.claude/skills/1md-graph/scripts/md_graph.py` в `experiments/md-embedding-server/scripts/navigator/graph.py`, использовать `markdown_io` для parsing (deduplicate WIKILINK_RE / MD_LINK_RE / HEADING_RE / `iter_markdown` / `split_frontmatter`)
- Создать `navigator/link_graph.py`: build `nx.MultiDiGraph` из `markdown_io` (wikilinks + markdown-links + frontmatter `read-before-edit` / `edit-after-edit`), edges с type + anchor info
- Создать `navigator/importance.py`: in_degree / out_degree / pagerank / centrality через NetworkX
- Расширить `navigator/cli.py`: добавить `graph-*` subcommands (или просто include как regular)
- `~/.claude/skills/1md-graph/scripts/md_graph.py` остаётся как **симлинк** на новый backend (CLI fallback survives)
- Аналогично `~/.codex/skills/1md-graph/scripts/md_graph.py` → симлинк
- Inline deps в uv shebang `md_navigator.py`: добавить `networkx`, `scipy`

**Verification P1**: smoke test (15/15 passed), CLI fallback тест: `md_graph.py preflight knowledge/agents/evaluation.md` работает identically до и после migration. Manual golden output diff на 3 файлах.

### P2 — Tier 1 atomic capabilities (~0.5 дня)

- Extend `folder_map.build_map`: param `with_link_counts: bool`, добавляет `in_degree` / `out_degree` per file через `link_graph`
- MCP wrapper: `md_ls` / `md_toc` принимают `with_link_counts: boolean`
- New atomic tool `md_importance({ corpus, top?, sort_by?: "pagerank"|"centrality"|"in_degree"|"out_degree" })`
- Extend `md_read_related`: param `mode: "preview" | "full"` (default `"full"`). Preview = descriptions + headings only, no content body

**Verification P2**: smoke добавляет 4 новых assertions; manual check: `md_importance knowledge` returns top hubs match intuitive expectations.

### P3 — Tier 1 composite tools (~0.5 дня)

- New composite `md_orient({ corpus })` — внутри: status + ls (с link counts) + importance top-10. **Cheap-only**: no embeddings calls, no HTTP except optional status meta. Description явно: «Instant orientation. For deeper semantic audit → `md_audit`»
- New composite `md_edit_context({ path, mode: "preview"|"full"|"strict", query? })`:
  - `preview` — descriptions + heading titles из preflight + must-update + must-read (без content body)
  - `full` (default) — + anchor-aware section content + optional `md_search(query)` results
  - `strict` — только blockers (anchor-drift risk, missing-target, broken-link, cycles), no context body

**Verification P3**: smoke тестирует все 3 modes; manual: `md_orient` на агрегированном корпусе должен ответить < 2s; `md_edit_context` preview vs full vs strict — token differential 5-10x.

### P4 — Tier 2 foundation: section profile (~1.5-2 дня)

- Schema extension `sections` table (additive, nullable): `profile_type`, `profile_subject`, `profile_owns_terms` (JSON array), `profile_evidence`, `profile_confidence`, `profile_version`, `profile_model`, `profile_classified_at`
- New module `navigator/section_profile.py`:
  - Profile shape: `{ type, subject, owns_terms[], mentions[], evidence_sources[], confidence }`
  - LLM-prompt classifier (structured prompt + decision rules) через OpenRouter (тот же endpoint что embeddings)
  - Cost target: ~$0.001 per section, ~0.5s latency
  - Cache invalidation: mtime change → re-profile; `model_id` change → re-profile; `prompt_version` bump → re-profile; `confidence_threshold` change → filter at read, не re-profile
- New atomic tool `md_classify_section({ path, heading_id })` — INTERNAL, не exposed через MCP. Используется только composite tools
- `index` command расширен: при indexing новых sections также profile'ит (батч до 50 за раз)

**Verification P4**: один full corpus run на `knowledge/` (~300 sections), cost report < $0.50, manual review 20 случайных profiles — type assignment > 80% intuitively correct. Cache invalidation: повторный `index` без изменений → 0 LLM calls; touch 1 файла → re-profile только эти sections.

### P5 — Tier 2 capabilities (~2 дня)

- New atomic `md_originality({ corpus, section_id })` — uniqueness score = cosine distance to nearest neighbor section in corpus. INTERNAL
- New atomic `md_owner_candidates({ corpus, text | section_id })` — composite signal: graph centrality + uniqueness + section_profile.type=="definition" + length. Returns ranked candidates с evidence. INTERNAL
- New composite `md_refactor_candidates({ corpus, top?: 10 })` — orchestrates: scan top suspicious sections (low uniqueness + type=="uses") + find owner_candidates + format as proposal. Output shape:
  ```json
  {
    "proposals": [
      {
        "proposal_type": "replace_with_wikilink" | "extract_to_owner" | "merge_with_X" | "orphan_quarantine",
        "affected_section": { path, heading_id, line_range },
        "target_owner": { path, heading_id } | null,
        "evidence": { cosine, profile, in_degree_target },
        "confidence": 0.0-1.0,
        "why": "human-readable rationale",
        "no_automation": true
      }
    ]
  }
  ```
- New composite `md_query_by_type({ corpus, types: ["open-question", "decision", ...], filter? })` — filter by section_profile.type

**Verification P5 — editorial scenario, не accuracy labels**:
- Real refactor session: user+agent используют `md_refactor_candidates` на `knowledge/`
- Acceptance: ≥ 5 из top-10 proposals user считает actionable (replace by wikilink / merge / extract сделан или явно отклонён с обоснованием)
- Если signal < noise (большая часть proposals — false positives) → stop rule fires, reshape

### P6 — Workflow recipes в SKILL.md (~0.5 дня)

В обоих `~/.claude/skills/1md-navigator/SKILL.md` + `~/.codex/skills/1md-navigator/SKILL.md`:
- Секция `## Workflow recipes` с 5-7 recipes:
  - «Понять незнакомый корпус → `md_orient`»
  - «Найти где обсуждается X → `md_search`»
  - «Обогатить понимание файла → `md_read_related anchor_aware=true`»
  - «Refactor opportunities → `md_refactor_candidates`»
  - «Найти все open questions → `md_query_by_type types=['open-question']`»
- Аналогично в `1md-graph/SKILL.md`:
  - «Я буду править file X → `md_edit_context mode=full`»
  - «Удалить / переименовать file → `md_impact`»
  - «Переименовать секцию → `md_section_blast_radius`»
  - «Pre-edit safety check → `md_preflight`»

### P7 — Cleanup (только после burn-in, ~0.5 часа)

- Удалить `scripts/` из 4 skill папок (Claude + Codex × navigator + graph)
- Удалить симлинки в этих папках
- Обновить mcp/README.md — финальный tool catalog с workflow grouping
- Обновить `experiments/md-embedding-server/README.md` — отразить unified backend shape
- Возможно обновить `_ops/project-graph.md` (cross-project blast block — `~/.claude/skills/**` теперь contains pure SKILL.md)

**Burn-in критерий перед P7**: P1-P6 готовы и стабильны в течение ≥ 1 сессии реального использования, user explicit подтверждает «можно убирать scripts/».

## Verification (общая)

| Phase | Verification |
|---|---|
| P1 | Smoke 15/15 + CLI golden output identical pre/post migration |
| P2 | Smoke добавлены 4 assertion + manual `md_importance` sanity check |
| P3 | Smoke 3 modes + composite latency targets |
| P4 | Full corpus profile run + cost report + cache invalidation test |
| P5 | **Editorial scenario** done 2026-05-21: structural L1 filter landed, bias finding closed, bar reframed — corpus sparse-duplicate. Tool useful as editorial-input surface. See `_ops/findings/2026-05-21-md-refactor-editorial-verification.md` |
| P6 | Manual: новая Claude сессия видит workflow recipes, выбирает MCP первым |
| P7 | scripts/ удалены, ничего не сломалось, MCP стабилен в новой сессии |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| `md_graph` migration ломает existing CLI consumers | Симлинки в skill folders → старые пути работают; smoke per migration step |
| NetworkX scipy dep слишком тяжёлый для inline uv | scipy optional — PageRank fallback к pure NetworkX без scipy (медленнее, работает) |
| LLM profile noise (false positives в classification) | Confidence threshold + manual sample review per 20 sections; editorial verification, не accuracy |
| Profile cost эскалация на больших корпусах | Cap `--max-profile-batch` (default 50), CLI `--no-profile` flag для skip, profile только при index, не при search |
| `md_refactor_candidates` outputs noise > signal | Stop rule P5: если editorial session показывает < 50% actionable, не deploy в production usage |
| Cross-runtime drift (Claude видит, Codex нет) | Один MCP сервер для обоих, registration через `claude mcp add` + `config.toml` уже сделано; текущая версия MCP `0.4.0` |
| 2-week refactor blocks других работ | Phase boundaries — каждая phase отдельный commit, можно paused между phases |
| User vision shift во время refactor | Stop rule explicit; escalate в `1strategy-docs` если goal/scope/done меняется |

## Open questions

- Cost real LLM profile run на `knowledge/` corpus (~300 sections) — нужен P4 spike перед commit к P5
- Должны ли `md_originality` / `md_owner_candidates` всё-таки expose'иться через MCP (как «advanced») или strictly internal? Defer до P5 implementation — посмотрим на real usage pattern
- Удалять ли `experiments/md-embedding-server/README.md` mention legacy MLX server (исторический artifact) — defer до P7

## Execution evidence — 2026-05-21

- Backend graph wrapper moved into repo: `experiments/md-embedding-server/scripts/md_graph.py` → `navigator/graph.py`; Codex `1md-graph` fallback symlink points to repo backend.
- Tier 1 MCP works: link counts, `md_importance`, `md_orient`, `md_edit_context`, `md_read_related mode`.
- Tier 2 MCP works: OpenRouter/heuristic section profiles, embedding-cosine originality, graph-aware owner candidates, `md_refactor_candidates`, `md_query_by_type`; helper signals remain CLI/internal.
- Verification passed: `npm run smoke` = 24 passed, 0 failed; `pytest experiments/md-embedding-server/tests` = 89 passed.
- LLM profile burn-in: `profile-sections knowledge --limit 20 --mode llm --json` completed with 20 profiled, 0 failed, estimated cost `$0.020`; unbounded full-corpus LLM profiling remains explicit because it is cost/time-bearing.
- Deferred: Claude-side `SKILL.md` edits are blocked for Codex by root instruction read-only boundary for Claude surfaces. P7 script removal is blocked until burn-in and explicit user confirmation.

## Anchors / Evidence

- Architecture discussion: `_ops/user-said/2026-05-21.md` (durable architecture decision)
- Adversarial review from external agent — captured в chat 2026-05-21 (this session), 8 of 9 points integrated
- Self-learning pattern: `_ops/self-learning/user-workflow-probe-skip-on-design.md`
- Current MCP version: 0.4.0 (`experiments/md-embedding-server/mcp/package.json`)
- Backend single source of truth (already): `experiments/md-embedding-server/scripts/md_navigator.py`
- Current graph location (to migrate): `~/.claude/skills/1md-graph/scripts/md_graph.py` (1446 LOC monolith)
- Spike outcome: `obsidiantools` mismatch с нашим mixed-link-style corpus — NetworkX напрямую правильный путь
