# Cross-project smoke БЕФОРЕ removal

## Цель
**Verify что без MCP всё работает** — на полностью мигрированном но не удалённом MCP. Это поглощение: skills уже на CLI, MCP ещё стоит как fallback. Если smoke падает — есть chance fix without rollback. Только после green smoke — переходим к task-502 (deletion).

**Audit fix (Smith #9 + Implementation #7):** Раньше removal был перед smoke — one-way door. Сейчас swap: smoke первый, deletion после.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-301 + task-302 + task-303 + task-304 + task-305 + task-402 закрыты (skills + docs migrated)
- task-401 (registration removal) — **может быть закрыт ДО ИЛИ ПОСЛЕ task-501** (audit cycle-2 Smith G1):
  - Если ДО: smoke на полностью clean state (skills через CLI, MCP server даже не зарегистрирован). Чище gate, но rollback требует re-register.
  - Если ПОСЛЕ: smoke с standing-by MCP fallback. Reversible если CLI ломается.
  - **Decision**: task-401 ДО task-501. Если smoke fails — explicit rollback procedure (см. ниже).
- MCP server folder **ещё не удалён** (task-502)

## Rollback procedure (audit cycle-2 fix)

Если smoke NO-GO **после** task-401:
1. `git revert <task-401 commit>` — восстанавливает MCP registration
2. Скилы стянут MCP tools обратно в deferred list через restart Claude/Codex
3. Diagnostic side-by-side: одна skill prompts тестируется через CLI и через MCP
4. Fix CLI issue → re-apply task-401 → re-run task-501

Это accepted cost reversibility: одноходовый rollback потерян, но gate cleaner.

## Подшаги

- [ ] **Verify parity tests already snapshot-based** (conversion owned by Phase 2 tasks, not by deletion gate):
  - В `experiments/md-embedding-server/tests/test_*_mcp_parity.py` нет live MCP subprocess/client calls
  - Tests load golden JSON fixtures from `tests/golden/mcp-responses/`
  - Golden fixtures были созданы в task-000 + task-106
  - Run `uv run pytest tests/test_*_mcp_parity.py -v` → all green БЕЗ Node MCP standing by
  - Это **prerequisite** для smoke и deletion — если conversion не сделан раньше, вернуться в Phase 2, а не чинить в task-501

- [ ] **Pre-flight check (architectural review — clean install test, не editable)**:
  - **Clean install test** (NOT editable repo install):
    ```bash
    TEMP_HOME=$(mktemp -d)
    cd /tmp  # cwd outside repo
    HOME="$TEMP_HOME" uv tool install /Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server --force
    HOME="$TEMP_HOME" PATH="$TEMP_HOME/.local/bin:$PATH" md ping --json
    HOME="$TEMP_HOME" PATH="$TEMP_HOME/.local/bin:$PATH" md status . --json
    HOME="$TEMP_HOME" PATH="$TEMP_HOME/.local/bin:$PATH" md tools --json
    HOME="$TEMP_HOME" PATH="$TEMP_HOME/.local/bin:$PATH" md selftest --json
    ```
  - Это catches missing dependencies в pyproject (которые editable mode не ловит)
  - Это catches PATH issues (binary actually installed правильно)
  - Это catches cwd-relative assumptions (CLI работает вне repo)
  - **All 4 commands должны быть зелёные** перед continue
  - Cleanup: `rm -rf "$TEMP_HOME"`

- [ ] **Standard pre-flight**:
  - `md selftest --json | jq '.summary'` → all OK (или audit-skip)
  - `md doctor` → no FAIL
  - `md --version` → 0.7.0
  - All parity tests (`tests/test_*_mcp_parity.py`) — already snapshot-based (from task-201/202/203), passing without live MCP

- [ ] **Claude smoke в agentic-research repo**:
  - Запустить fresh Claude session в `/Users/triton/Documents/GitHub/agentic-research/`
  - Дать 3 трigger prompts:
    1. «о чём папка `knowledge/`?» → skill `1md-navigator` сработает, использует `md orient` через Bash
    2. «расскажи статус moego corpus в `_ops/`» → uses `md status _ops/`
    3. «есть ли open questions в репо?» → uses `md query-by-type _ops --types open-question`
  - Verify:
    - Skill triggers (deferred tools НЕ содержат `mcp__md-mcp__*`)
    - First tool call — Bash `md ...`
    - Output содержит `_envelope`
    - Answer relevant

- [ ] **Claude smoke в другом repo**:
  - Запустить fresh Claude session в `/Users/triton/Documents/GitHub/civicchain-v2/` (или другой репо с .md content)
  - Тот же тип prompts на их corpus
  - Verify: skill работает cross-project

- [ ] **Codex smoke в agentic-research repo** (audit cycle-2 Codex G7 — explicit commands):
  - Запустить Codex session: `codex` в директории `/Users/triton/Documents/GitHub/agentic-research/`
  - Prompt 1 (core skill): «о чём папка `knowledge/`?» → должна activate `1md-navigator`, использовать `md orient` или `md search`
  - Prompt 2 (extended skill): «какие открытые вопросы в `_ops/`?» → активирует `1planning` или `1strategy`, использует `md query-by-type ... --types open-question`
  - Verify:
    - Output содержит JSON с `_envelope`
    - No errors about MCP / md_navigator.py / MD_NAVIGATOR_SCRIPT
    - `ps aux | grep md-mcp` (в другом terminal) — нет запущенных Node процессов (Codex G5)
  - Save trace в evidence file

- [ ] **Codex smoke в другом repo**:
  - Open Codex session в другом проекте (например `/Users/triton/Documents/GitHub/civicchain-v2/`)
  - Тот же type prompt (адаптировать под content of that repo)
  - Same verifications

- [ ] **Mutating tools smoke** (isolated):
  - Создать tmpdir с sample corpus
  - Запустить через Claude: «обнови frontmatter описания в `/tmp/test-corpus/`» → skill triggers `md init` dry-run → confirm flow
  - Verify dry-run/confirm/fingerprint chain работает

- [ ] **Performance smoke**:
  - `time md status _ops/` — должно быть <500ms cold
  - `time md selftest` — должно быть acceptable (in-process target <2s)
  - Если cold startup >1s — investigate lazy imports

- [ ] **Evidence**:
  - Создать `_ops/findings/2026-MM-DD-pre-removal-smoke.md`:
    - Каждый smoke прогон: timestamp, project, exact prompt, first CLI command, exit status, evidence что envelope corrent
    - Summary: GO/NO-GO для deletion (task-502)

- [ ] **Если smoke failed**:
  - НЕ переходить к task-502
  - Создать `_ops/findings/2026-MM-DD-pre-removal-blockers.md` со списком проблем
  - Маршрутизировать в соответствующие fix tasks (re-open task-301/302/304/305 или ранее)
  - Re-run smoke после fix

## Готово (с explicit quorum — audit cycle-2 Smith G2)

GO verdict требует **все** следующие:
- [ ] Claude smoke в agentic-research: **3/3** prompts work
- [ ] Claude smoke в одном другом repo: **1+** prompt works
- [ ] Codex smoke в agentic-research: **2+** skills work (один из core 1md-navigator + один из extended 1planning или 1assumption-audit) — Smith G5
- [ ] Codex smoke в одном другом repo: **1+** skill works
- [ ] Mutating tools dry-run/confirm flow verified (Claude + Codex)
- [ ] Performance: cold `md status` <500ms **OR** degraded GO с recorded performance finding (не блокер)
- [ ] Codex restart verification — `ps aux | grep md-embedding-server` не показывает MCP server процессы (Codex G5)
- [ ] Evidence file `_ops/findings/2026-MM-DD-pre-removal-smoke.md` exists с GO verdict

**Partial pass (4/5 prompts ok)** → NO-GO. Любой fail в первых 4 пунктах = NO-GO. Performance может быть degraded GO с явным noting.

## Красные линии
- [ ] НЕ начинать task-502 если smoke NOT GO. Это критичный gate.
- [ ] Не deduplicate с task-105 selftest — smoke это реальные skill sessions, не unit tests.
- [ ] Не trust «вчера работало» — smoke сейчас на current state.
- [ ] Не пропускать Codex smoke (равноценный consumer).

## Проверка
1. `cat _ops/findings/2026-MM-DD-pre-removal-smoke.md | grep "GO/NO-GO"` → есть verdict "GO"
2. Каждый smoke прогон документирован: project + prompt + first CLI command
3. No MCP errors в Codex logs во время smoke
4. Manual verification: deferred tools в Claude session — `mcp__md-mcp__*` absent (assuming task-401 done)
