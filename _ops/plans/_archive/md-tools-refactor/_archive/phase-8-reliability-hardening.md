# Phase 8 — Reliability hardening

**Estimated cost**: ~2.5 часа
**Depends on**: P5 (Tier 2 capabilities done)
**Created**: 2026-05-21 (surfaced during audit + external library-spec review)

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md`.

## Цель

Закрыть **observed reliability gaps** найденные в audit + library-spec review другим агентом:

1. F1 LLM profile-sections run hung 10+ min (`_ops/findings/2026-05-21-...-36c3e6b6.md`)
2. SQLite "database is locked" race condition между profile-sections и md_search
3. Heuristic classifier даёт wrong types для значительной части корпуса (md_query_by_type returns project-guide sections как "open-question")
4. MCP tools без host UX annotations (readOnlyHint, destructiveHint)
5. spawnPython без output cap (memory risk на больших audit runs)

## In scope

### 1. SQLite timeouts (#8 от review)
- Add `timeout=30.0` parameter ко всем `sqlite3.connect()` calls в `navigator/index_meta.py` и `navigator/section_profile.py`
- Add `PRAGMA busy_timeout = 30000` после connect
- Reduces "database is locked" failures когда profile-sections и md_search competing

### 2. OpenRouter retry — 429 + completion (#6)
- В `navigator/embeddings.py`:
  - Apply existing retry pattern (5xx + backoff) к `completion()` method (currently no retry)
  - Add 429 to retried codes (currently only 5xx)
  - 529 already covered (5xx)

### 3. spawnPython output caps (#4)
- В `mcp/src/subprocess.js`:
  - Add `maxStdoutBytes` / `maxStderrBytes` options (default 5MB)
  - Truncation envelope: при превышении — keep first/last portions с marker `[TRUNCATED: N bytes elided]`

### 4. Tool annotations (#2)
- Все 19 MCP tools получают:
  - `readOnlyHint: true` для read-only (все наши кроме `md_audit` который пишет audit.md в `.md-navigator/`)
  - `destructiveHint: false` для всех
  - `openWorldHint: true` для tools которые dyrgay OpenRouter (`md_search`, `md_audit`, `md_refactor_candidates`)

### 5. Version bump 0.4.0 → 0.5.0
- `mcp/package.json` + `mcp/src/server.js` md_ping response

## NOT in scope

- #1 structuredContent + outputSchema (отдельный future task, ~3 часа refactor)
- #5 uv lock (polygon flexibility prevails)
- #7 JSON Schema для section profile (defer до next iteration)
- #9 NetworkX edge weights (defer)
- #10 README library-contract checklist (low value)

## Definition of done

- `profile-sections --mode llm` on full corpus completes без hang (verified by re-running F1)
- Profile state ≥80% LLM (анти-heuristic-fallback)
- `md_search` параллельно с `profile-sections` НЕ throws "database is locked" (retries within 30s window)
- spawnPython truncates output at 5MB с marker
- listTools shows annotations через MCP client check
- Smoke 24/24 still passes (no regression)
- Version 0.5.0 reflected в md_ping response

## Stop rules

- Backend fix breaks smoke — rollback, investigate
- F1 retry hangs again — investigate более глубоко (TLS handshake bug в urllib?)
- Annotations break MCP client — revert to plain registerTool

## Anchors / Evidence

- Audit finding: `_ops/findings/2026-05-21-Claude Opus 4.7-36c3e6b6.md`
- External library-spec review by agent (2026-05-21, captured в chat)
- High-level контракт: `task-001-md-tools-unified-backend.md`
- Self-learning: `_ops/self-learning/background-poll-loop-antipattern.md` (avoid poll loops during F1 retry)
