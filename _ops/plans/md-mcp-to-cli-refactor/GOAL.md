# GOAL — md-mcp → CLI Refactor

Outcome-first execution contract под `GPT-5.5` и `Claude Opus 4.7`. Самодостаточный документ для автономного исполнения 23 task-файлов от начала до closeout.

---

## Outcome

В конце работы:

1. **Node MCP server удалён**: `experiments/md-tools/mcp/` не существует. ~2228 LOC JavaScript удалены из репо.
2. **Python CLI `md` работает глобально**: `uv tool install` ставит binary в `~/.local/bin/`. Все 29 MCP tool names доступны как subcommands (`md orient`, `md search`, `md edit-context`, etc.).
3. **Library/CLI split реализован**: `experiments/md-tools/src/navigator/` — pure library (importable Python), `experiments/md-tools/src/md_cli/` — CLI слой с envelope + composites + transactions + dispatch.
4. **13 historical migration targets мигрированы** на CLI invocation syntax
   (Claude + Codex × {1md-navigator, 1md-graph, 1ia-audit,
   1instruction-layer, 1planning, retired approach/doc skills,
   1folder-contract, 1assumption-audit, 1work-review, 1skill-architect,
   1smart-simple, 1cli-tools}). Это snapshot исходного scope, а не live skill
   catalog. Skills остались **pure declarative** (SKILL.md + references/ +
   agents/openai.yaml).
5. **MCP registrations удалены** из всех конфигов (`~/.codex/config.toml` `[mcp_servers.md-mcp]`; Claude если есть).
6. **Cross-project smoke зелёный**: Claude и Codex sessions в как минимум 2-х разных репо успешно используют CLI через skills.

Live-surface caveat (2026-06-02): `1work-review` был частью исходного
migration scope, но сейчас не является installed Codex/Claude skill. Текущие
closeout-проверки держит execution owner через прямой evidence-closeout; этот
план не использовать как live skill catalog.

Главная инвариант: **внешний контракт для skills остался идентичным** — те же 29 tool names, та же envelope shape (`_envelope.{version, tool, corpus_root, corpus_state, lock, cost, size_estimate, next_step}`), тот же dry-run/confirm protocol. Skills получили только syntax replacement.

---

## In scope

- Создание Python пакета `md-tools` в `experiments/md-tools/`
- Удаление Node MCP server вместе со всеми его файлами
- Обновление 16 SKILL.md (13 skills × Claude/Codex минус 1cli-tools-Codex которая отсутствует или есть only references)
- Обновление `agents/openai.yaml.default_prompt` где он содержит MCP refs (на самом деле в большинстве yaml refs нет — только SKILL.md)
- Удаление MCP registration из `~/.codex/config.toml`
- Обновление repo docs: `CLAUDE.md`, `AGENTS.md`, `_ops/project-graph.md`, `experiments/md-tools/README.md`
- Pre-commit hook для code locality enforcement

## NOT in scope

- Backward-compatibility MCP wrapper (big-bang; user явно принял risk)
- Empirical SKILL.md trigger A/B testing до commit (user явно отказался; полагаемся на mechanical replace)
- Смена языка на Rust/Go/Bun (Python оставляем — pymorphy/NetworkX/markdown ecosystem one-way door)
- Изменение MCP envelope semantics (зеркальное копирование текущей shape)
- Добавление новых tools (refactor только формы, не функций)
- Правки `_ops/GOAL.md`, `README.md`, `_ops/PROJECT-ROADMAP.md` shape (это owner `1goal`)
- Перенос existing Codex `scripts/` папок других skills в repo (out of scope; только md-related, если найдутся)

---

## Constraints (invariants)

0. **4-layer architecture** (NEW — architectural review):
   - Layer 1: 24 atomic library functions в `src/navigator/*.py`, importable
   - Layer 2: 5 workflow functions в `src/navigator/workflows/*.py`, importable, compose atomic
   - Layer 3: 29 thin handlers в `src/md_cli/handlers/*.py`, return `ToolResult(payload, exit_code)`, NO JSON printing, NO envelope imports
   - Layer 4: central runner в `src/md_cli/runner.py` — single point JSON serialization + envelope wrapping + exit
   - One-way dependency: `md_cli` imports `navigator`. NEVER reverse.
   - Enforced через `tests/test_architecture_invariants.py`

1. **Code locality**. Весь executable код живёт только в `experiments/md-tools/`. Skill folders (`~/.claude/skills/**`, `~/.codex/skills/**`) — pure declarative. Whitelist для skill folders: `SKILL.md`, `references/*.md`, `agents/openai.yaml`, `assets/*.{png,jpg,svg,gif}`. Любой другой файл — нарушение.

2. **Cross-platform symmetry**. Claude и Codex skills синхронны (за исключением AGENTS.md правила: Codex не правит Claude surfaces и наоборот). Любой intentional drift документируется в evidence file.

3. **Envelope shape immutable**. `_envelope` поля и их типы не меняются. Golden test (`tests/golden/envelope_shape.json`) гарантирует zero drift между MCP и CLI.

4. **Stateless transactions**. Mutating tools (md_init, md_strip, md_index) используют fingerprint-based dry-run/confirm. Cache в `~/.cache/md-tools/transactions/`. Никакого in-memory state.

5. **Lazy imports per subcommand**. `md status` не должен загружать NetworkX. `md --help` показывает все 29 subcommands без import handlers.

6. **Big-bang rollback safety**. Git tag `pre-mcp-refactor-2026-05-22` создан в task-000 как rollback point. Сохраняется минимум 1 месяц после Phase 5 deletion.

---

## Decisions already made (НЕ передумывать)

| Decision | Source | Rationale |
|---|---|---|
| Big-bang без MCP wrapper-моста | User explicit | Cross-project blast принят явно |
| Python (не Rust/Go) | 3-агентский audit cycle-1 | Pymorphy + NetworkX one-way door; русский lemmatizer без аналогов |
| 4-layer architecture (library / workflow / handler / runner) | Architectural review | Без workflow layer composite logic смешается с CLI; без central runner envelope drift по 29 файлам |
| Workflows в `navigator/workflows/`, не `md_cli/composites/` | Architectural review | Workflows — agent-facing logic, importable за пределы CLI |
| ToolResult dataclass pattern | Architectural review | Handlers thin (≤30 LOC), envelope owned by runner |
| catalog.py как single source of truth для 29 tools | Architectural review | Каждый tool: cli_name + category + library_function/workflow_function + handler_module + tests_module |
| Tool count: 24 atomic + 5 workflow = 29 (не «22+8=30») | Architectural review | Точная сверка с MCP `TOOL_ANNOTATION_ALLOWLIST` |
| `md_profile_sections` тоже cost-bearing (с md_init/md_strip/md_index) | Architectural review | LLM profiling stoит ~$0.0005/section |
| `uv tool install` distribution | Audit | Установил-раз-работает; isolated venv |
| Phase 5: smoke (501) до deletion (502) + clean install test | Audit cycle-1 Smith G9 + arch review | Reversibility + catches pyproject deps issues |
| task-305 primary target = SKILL.md, не `agents/openai.yaml` | Audit cycle-2 Codex G1 | Real grep показал refs только в SKILL.md |
| task-202a (navigator public API) — отдельный task до task-202 | Audit cycle-2 Implementation G7 | Hidden balloon разделён |
| CLI subcommands kebab-case (`md read-related`) | Audit cycle-2 Implementation G1 | Соответствует existing `md_navigator.py` + Unix CLI |
| 13 skills affected, не 2 | User correction + inventory | 11 extended consumers найдены grep'ом |
| No empirical SKILL.md trigger test до commit | User explicit | Доверяемся mechanical replace |

---

## Execution map

Фазы строго последовательны. Внутри фазы tasks параллелизуются по правилам Зависимости в каждом task-файле.

```
Phase 0 — Preflight (4 tasks, ~1 день)
  task-000 → task-001 → task-002 → task-003

Phase 1 — CLI foundation + architecture lock (6 tasks)
  task-101 → {task-102, task-103, task-104, task-105 — parallel} → task-106 (GATE)

Phase 2 — Tool migration (5 tasks, ordered)
  task-202a (FIRST: public navigator/* API) → {task-201, task-202, task-203 — parallel after 202a} → task-204

Phase 3 — Skills migration (5 tasks, ~1 день)
  task-303 wait for task-104
  {task-301 ∥ task-302} → {task-304 ∥ task-305} → task-303

Phase 4 — Repo migration (2 tasks, ~½ дня)
  task-401 → task-402

Phase 5 — Removal + closeout (2 tasks, ~½ дня)
  task-501 (smoke GO required) → task-502 (deletion + archive)
```

**Critical paths**:
- task-202a блокирует Phase 2 (`navigator/` public API нужен composites)
- task-003 (semantic equivalence) блокирует Phase 3 (skills migration uses doc as truth)
- task-501 — quality gate перед task-502 deletion

---

## Validation gates (между фазами)

Phase X не closed, пока gate не зелёный.

### Gate 0 → 1
- `tests/golden/mcp-responses/<tool>.json` — 29 фикстур существуют (task-000)
- `docs/cli-signatures-canonical.md` — таблица 29 tools с canonical CLI flags (task-001)
- `docs/cli-framework-decision.md` с явным verdict (task-002)
- `docs/skills-semantic-equivalence.md` — 13 секций; `_ops/findings/YYYY-MM-DD-equivalence-doc-review.md` с verdict от `1fresh-eyes` (task-003)
- git tag `pre-mcp-refactor-2026-05-22` создан

### Gate 1 → 2 (architecture lock — task-106 — GATE)
- `md --version` → "0.7.0"
- `md --help` показывает 29 subcommands без heavy imports (lazy imports verified)
- `md tools --json | jq '.tools | length'` → 29
- `md selftest --json | jq '.summary'` → pass (28/29 OK + 1 audit skip)
- `md doctor` без FAIL
- `tests/test_envelope_golden.py` зелёный
- **`tests/test_catalog_contract.py` зелёный** (catalog matches frozen snapshot, 29 entries)
- **`tests/test_architecture_boundaries.py` зелёный** (handlers без envelope/print/sys.exit; workflows без md_cli; runner единственный envelope owner; library без md_cli)
- **`tests/test_transactions_adversarial.py` зелёный** (8 scenarios: args mismatch, double confirm, concurrent, corrupt txn, etc.)
- **`tests/test_lazy_imports.py` зелёный** (6 scenarios: --help paths без heavy deps)
- `tests/golden/mcp-tool-snapshot.json` существует (frozen, 29 entries)

### Gate 2 → 3
- `tests/test_atomic_handlers.py` — 24/24 зелёные
- `tests/test_mcp_cli_parity.py` (snapshot-based) — 24/24 матчей (atomic). Composite/hybrid parity тесты — отдельно (5/5)
- `tests/test_composite_tools.py` + `tests/test_composite_mcp_parity.py` — 4/4 матчей
- `tests/test_hybrid_section_blast.py` зелёный
- `tests/test_mutating_handlers.py` — 12+ test cases зелёные
- Все 29 CLI subcommands работают через `md <tool> <args>` (24 atomic + 5 workflow)

### Gate 3 → 4
- `grep -rE "md_[a-z_]+\(\{" ~/.claude/skills/ ~/.codex/skills/` → 0 matches
- `grep -rE "mcp__md-mcp" ~/.claude/skills/ ~/.codex/skills/` → 0 matches
- `find ~/.claude/skills/1md-* ~/.codex/skills/1md-* -name "*.py" -o -name "*.sh"` → 0 (code locality)
- `~/.claude/skills/1md-navigator/references/tool-catalog.md` существует, mirror в Codex
- Evidence files в `_ops/findings/` для каждой skill migration task

### Gate 4 → 5
- MCP registration убран из `~/.codex/config.toml` (`grep "md-mcp" ~/.codex/config.toml` → 0 matches)
- `python3 -c "import tomllib; tomllib.loads(open('/Users/triton/.codex/config.toml').read())"` → ok
- `CLAUDE.md`, `AGENTS.md`, `_ops/project-graph.md`, `experiments/md-tools/README.md` обновлены (нет MCP wording)
- Pre-commit hook для code locality установлен

### Gate 5 (final, перед закрытием refactor)
- task-501 evidence файл содержит явный verdict "GO"
- `experiments/md-tools/mcp/` не существует
- `md selftest` зелёный после deletion
- `_ops/PROJECT-ROADMAP.md` — refactor в Archived
- git tag `mcp-removed-YYYY-MM-DD` создан
- Все 23 task-файла в `_archive/YYYY-MM-DD-<task-slug>/` capsules

---

## Stop rules (когда escalate to user, НЕ продолжать автономно)

1. **task-002 spike NULL verdict**: ни один framework не справляется с nested objects в `md_section_blast_radius` — escalate, possibly need different abstraction.
2. **task-501 smoke NO-GO**: cross-project verification упала. НЕ запускать task-502 deletion. Создать `_ops/findings/2026-MM-DD-pre-removal-blockers.md` со списком проблем. Escalate.
3. **Envelope drift detected**: `tests/test_envelope_drift.py` показывает divergence между CLI и MCP envelope shape. Это нарушение invariant — escalate перед continuing.
4. **Cross-project blast обнаружен в неожиданном месте**: если `grep "md_orient\|md_search\|..." /Users/triton/Documents/GitHub/<other-repo>/` показывает MCP refs которых не было в task-000 inventory — escalate, audit blast scope заново.
5. **Codex sandbox блокирует CLI binary access**: если `md` недоступен в Codex session, не путём sandbox config — escalate, это deeper Codex setup issue.
6. **Goal-цитата sync conflict**: если правки CLAUDE.md/AGENTS.md задевают hook-loaded Goal-цитату, передать в `1folder-contract` (NOT редактировать самостоятельно).
7. **Любое изменение `_ops/GOAL.md`**: это owner `1goal`, не этого refactor. Если что-то требует scope change — escalate.

---

## Failure recovery procedures

### Если CLI ломается во время Phase 2
- Skills ещё на MCP (Phase 3 не начата) — продолжить development normally
- Не committing partial CLI state в master до Phase 2 gate green

### Если skill migration не работает (Phase 3)
- Skills хотя бы временно — re-revert SKILL.md из git
- Investigate в isolated tmpdir copy
- Fix CLI или semantic equivalence doc, retry migration

### Если task-501 smoke fails после task-401
- `git revert <task-401 commit>` — восстанавливает MCP registration
- Restart Claude/Codex
- Side-by-side diagnostic (один и тот же prompt через CLI и через MCP)
- Fix CLI issue → re-apply task-401 → re-run task-501

### Если task-502 deletion проходит но что-то ломается через неделю
- `git checkout pre-mcp-refactor-2026-05-22 -- experiments/md-tools/mcp/`
- Reinstall Node deps: `cd experiments/md-tools/mcp && npm install`
- Re-register MCP в `~/.codex/config.toml`
- Investigate root cause, fix, retry phase 5

---

## Reference paths

### Read first
- `experiments/md-tools/README.md` — package overview
- `experiments/md-tools/scripts/navigator/` — existing library (которая move в `src/`)
- `experiments/md-tools/mcp/src/envelope.js` — current envelope shape (source for task-102)
- `experiments/md-tools/mcp/src/transaction.js` — current transaction logic
- `experiments/md-tools/mcp/src/tools/*.js` — current 29 tool definitions
- `~/.claude/skills/1md-navigator/SKILL.md` — current Claude skill shape
- `~/.codex/skills/1md-navigator/SKILL.md` — current Codex skill shape

### Write only here
- `experiments/md-tools/src/**` — new code
- `experiments/md-tools/tests/**` — new tests + golden fixtures
- `experiments/md-tools/docs/**` — new documentation
- `experiments/md-tools/pyproject.toml` — package config
- `~/.claude/skills/1*/{SKILL.md, references/*.md}` — declarative migration
- `~/.codex/skills/1*/{SKILL.md, references/*.md, agents/openai.yaml}` — declarative migration
- `_ops/findings/2026-MM-DD-*.md` — evidence files
- `_ops/plans/md-mcp-to-cli-refactor/_archive/YYYY-MM-DD-<task-slug>/` — closed task capsules

### Never write
- `_ops/GOAL.md` — owner `1goal`
- `_ops/PROJECT-ROADMAP.md` (кроме task-502 archive update — content update is `1planning` owner)
- `README.md` корневой — owner `1goal`
- Hook-loaded Goal-цитаты в `CLAUDE.md` / `AGENTS.md` — sync через `1folder-contract`

---

## Per-task workflow

Для каждой task:

1. **Read** `task-NNN-*.md` целиком + все файлы из `Зависимости` если ещё не closed
2. **Read** `Применимые инструкции` (typically `AGENTS.md` + subtree)
3. **Apply** все Подшаги по порядку
4. **Verify** все пункты в `Готово`
5. **Verify** все пункты в `Красные линии` не нарушены
6. **Run** все команды из `Проверка`
7. **Если всё ок**: переместить task в `_archive/YYYY-MM-DD-<task-slug>/` capsule, добавить evidence files если были созданы
8. **Если проблема**: записать в `_ops/findings/`, оценить — fix локально или escalate per Stop rules

---

## How to verify "почти готово" vs "готово"

«Готово» = все 4 категории закрыты:
- Все Подшаги выполнены
- Все Готово пункты verified
- Все Красные линии не нарушены  
- Все Проверка команды зелёные

Если хоть одна категория не закрыта — не moveть task в archive. Continue work.

---

## Final closeout signal

Refactor closed когда:
- 22 task капсул в `_ops/plans/md-mcp-to-cli-refactor/_archive/`
- `_ops/PROJECT-ROADMAP.md` показывает refactor в Archived
- `_ops/findings/2026-MM-DD-mcp-refactor-closeout.md` написан
- git tag `mcp-removed-YYYY-MM-DD` создан
- Backup tag `pre-mcp-refactor-2026-05-22` сохранён (удалять через 1+ месяц)
- Cross-project smoke по умолчанию работает

После этого — `_ops/plans/md-mcp-to-cli-refactor/` целиком может переехать в `_ops/plans/_archive/YYYY-MM-DD-md-mcp-to-cli-refactor-final/` (defer 1-2 недели на проявление потенциальных issues).
