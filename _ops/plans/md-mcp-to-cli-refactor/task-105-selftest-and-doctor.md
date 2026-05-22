# `md selftest` + `md doctor` — debug story replacement

## Цель
Заменить `npm run smoke` (37/37 MCP tests) на `md selftest`. Добавить `md doctor` для диагностики «не работает на моей машине». Без этого migration cost = потеря confidence (раunhinged by S3).

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-101 закрыт (есть dispatch)
- task-104 закрыт (есть catalog)
- task-102 закрыт (envelope) — selftest проверяет envelope shape

## Подшаги

- [ ] Дизайн `md selftest`:
  - `md selftest` — runs known-good corpus check для всех 29 tools (read-only там где возможно, mutating только в isolated tmpdir)
  - Output: PASS/FAIL таблица + summary `Pass: 35/37, Fail: 2`
  - Exit code 0 if all pass, 1 if any fail
  - `--corpus PATH` — explicit corpus override (default: `tests/fixtures/sample-corpus/`)
  - `--json` — structured output
  - `--tool <name>` — run single tool only

- [ ] Реализовать `src/md_cli/handlers/selftest.py` (audit Implementation #6 — in-process vs subprocess):
  - **Hybrid approach** (best of both):
    - **In-process** для 25 read-only tools — import handler module, вызов `run(args)` directly с captured stdout. ~10× faster startup (no subprocess), still exercises real handler code.
    - **Subprocess** для 4 mutating tools + 1 selftest entry — `subprocess.run(["md", tool, ...])` чтобы exercise full CLI dispatch + argparse + exit codes.
    - Total time target: <3s (was 29×150ms = 4.5s+ with all subprocess).
  - For each tool:
    - Choose representative invocation (atomic: simple call; composite: full path; mutating: dry-run only)
    - Run via in-process OR subprocess per category
    - Validate: exit 0 (or expected non-0 for tools with required corpus warmup), valid JSON, has `_envelope`
    - Record PASS/FAIL
  - Mutating tools run в `tmp/` copy of fixture corpus

- [ ] **Acceptance criterion (precise)** (audit Smith #4 — vague boundaries):
  - Pass = exactly **28/29 OK + 1 skip (md_audit)**, или **29/29 если SMOKE_AUDIT=1 set**
  - НЕ ambiguous «29 или 28+1»

- [ ] Portировать MCP smoke test fixtures:
  - `mcp/test/smoke.js` — source of truth для tool combinations
  - `experiments/md-embedding-server/tests/fixtures/sample-corpus/` — minimal corpus с indexed state
  - `experiments/md-embedding-server/tests/golden/selftest-expected.json` — expected outputs per tool (env-invariant fields)

- [ ] Дизайн `md doctor`:
  - Checks:
    - `md --version` matches expected
    - Python version >=3.11
    - Required deps installed (`networkx`, `requests`, etc.) — `importlib.metadata.version`
    - `OPENROUTER_API_KEY` set OR file key found (one of 6 lookup paths)
    - `~/.cache/md-tools/` writable
    - PATH includes `~/.local/bin/` or wherever `uv tool install` puts binary
    - Active skill paths: `~/.claude/skills/1md-{navigator,graph}/` существуют + `~/.codex/skills/...`
    - MCP server registration NOT present (post-removal check) — warning if found in legacy place
  - Output: human-readable table + suggestion for each fail

- [ ] Реализовать `src/md_cli/handlers/doctor.py`:
  - Каждый check — independent function
  - Returns: `(name, status, message)` — status: OK/WARN/FAIL
  - Aggregates → table output
  - `--json` для structured

- [ ] Tests `tests/test_selftest.py`:
  - test: selftest на fixture corpus → exit 0, ≥27/29 PASS (audit может быть skipped)
  - test: `--tool md_orient` → runs только orient, exit 0
  - test: `--json` → valid JSON shape (envelope + results array)

- [ ] Tests `tests/test_doctor.py`:
  - test: на текущей машине → ≥80% checks OK
  - test: `--json` shape

## Готово
- [ ] `src/md_cli/handlers/selftest.py` реализован
- [ ] `src/md_cli/handlers/doctor.py` реализован
- [ ] `tests/fixtures/sample-corpus/` создан с indexed state
- [ ] `tests/golden/selftest-expected.json` зафиксирован
- [ ] `md selftest` returns 0 на fixture corpus (28/29 минимум, audit может быть skip)
- [ ] `md doctor` runs, выводит понятный report
- [ ] `tests/test_selftest.py` — зелёный
- [ ] `tests/test_doctor.py` — зелёный

## Красные линии
- [ ] selftest не должен touch user's corpus или ~/.claude/. Только tmpdir + fixture.
- [ ] doctor — read-only, не fix-automatically.
- [ ] Не дублировать в Phase 5 — selftest mature к концу Phase 1, не позже.

## Проверка
1. `md selftest` → последняя строка "Pass: NN/29"
2. `md selftest --tool md_ping --json | jq '.results[0].status'` → "pass"
3. `md doctor` → table с проверками, status colored
4. `md doctor --json | jq '.checks[] | select(.status=="fail") | .name'` → пусто или с known issues
5. `cd experiments/md-embedding-server && uv run pytest tests/test_selftest.py tests/test_doctor.py -v` → all green
