# Remove MCP folder + final closeout

## Цель
Удалить `experiments/md-embedding-server/mcp/` целиком (~2228 LOC JS). Archive task capsules. Update ROADMAP. Final tag. Это последний шаг — выполняется **только после** task-501 smoke GO verdict.

**Audit fix:** Раньше smoke был в task-502; теперь task-501 — smoke (gate), task-502 — deletion + closeout.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-501 закрыт с **GO verdict** (cross-project smoke pass)
- Backup tag `pre-mcp-refactor-2026-05-22` существует

## Подшаги

- [ ] **Verify GO from task-501**:
  - `cat _ops/findings/2026-MM-DD-pre-removal-smoke.md | grep "GO/NO-GO"` → "GO"
  - Если "NO-GO" — не запускать дальше

- [ ] **Verify backup tag**:
  - `git tag | grep pre-mcp-refactor-2026-05-22` → exists
  - Если нет — abort, создать tag и потом продолжить

- [ ] **Verify parity tests already snapshot-based** (conversion owned by Phase 2; task-501 verified it):
  - `cat tests/test_*_mcp_parity.py | grep -E "subprocess|live"` → 0 hits (no live MCP)
  - `uv run pytest tests/test_*_mcp_parity.py -v` → all green
  - Если что-то всё ещё references live MCP → task-501 не закрыт правильно; вернуться

- [ ] **Удалить директорию**:
  - `git rm -rf experiments/md-embedding-server/mcp/`
  - Это удалит: src/ (server.js, envelope.js, paths.js, subprocess.js, transaction.js, tools/), test/, package.json, package-lock.json, node_modules/, README.md, _ops/

- [ ] **Cleanup Node-specific artifacts**:
  - `find experiments/md-embedding-server -name "package*.json" -not -path "*/mcp/*" 2>/dev/null` — должно быть пусто
  - `find experiments/md-embedding-server -name "node_modules" -type d 2>/dev/null` — должно быть пусто
  - Удалить .DS_Store если затронут

- [ ] **Verify nothing broken**:
  - `cd experiments/md-embedding-server && uv run pytest tests/` → all green (включая converted parity tests)
  - `md selftest` → all green
  - `cd experiments/md-embedding-server/scripts && bash run-tests.sh` → green

- [ ] **Repo cleanup scan**:
  - `grep -rln "experiments/md-embedding-server/mcp" /Users/triton/Documents/GitHub/agentic-research --include="*.md" | grep -v "_ops/plans/_archive"` → 0 active refs

- [ ] **Commit**:
  - `git add -A experiments/md-embedding-server/`
  - Commit: «Phase 5: remove MCP server (Node) — superseded by md CLI»
  - НЕ push automatically

- [ ] **Update PROJECT-ROADMAP.md**:
  - Снять `md-mcp-to-cli-refactor` из «Текущие активные фронты»
  - Добавить в Archived:
    ```md
    **Archived 2026-MM-DD**:
    - `md-mcp-to-cli-refactor` — Refactor complete: Node MCP removed (~2228 LOC), 29 tools mapped to Python CLI `md`, library/CLI split (navigator/ + md_cli/), envelope golden test, stateless transactions, 13 skills migrated (Claude + Codex). См. `_ops/findings/2026-MM-DD-mcp-refactor-closeout.md`.
    ```

- [ ] **Final closeout summary**:
  - Создать `_ops/findings/2026-MM-DD-mcp-refactor-closeout.md`:
    - Summary: что закрыто
    - Goals достигнуты per `_ops/GOAL.md` definition of done
    - LOC stats: 2228 JS removed, ~X Python added
    - 13 skills migrated (list)
    - Known limitations / deferred items
    - Backup tag rollback path

- [ ] **Archive task capsules**:
  - Каждый из 23 task-файлов → `_archive/YYYY-MM-DD-<task-slug>/` capsules
  - Структура capsule: task-file + evidence files если были created в этой task
  - Pattern: `_archive/2026-MM-DD-blast-scope-and-snapshot/`, `_archive/2026-MM-DD-cli-framework-spike/`, etc.

- [ ] **Final tag**:
  - `git tag mcp-removed-YYYY-MM-DD HEAD`
  - НЕ push automatically

- [ ] **Optional: archive whole domain folder через 1-2 недели** (не immediate):
  - Если ничего не всплыло — `_ops/plans/md-mcp-to-cli-refactor/` (целиком) переехать в `_ops/plans/_archive/YYYY-MM-DD-md-mcp-to-cli-refactor-final/`
  - Defer до next session

- [ ] **Cleanup backup tag через 1 месяц** (defer):
  - Через ~30 дней — `git tag -d pre-mcp-refactor-2026-05-22`
  - Не immediate

## Готово
- [ ] `experiments/md-embedding-server/mcp/` не существует
- [ ] Parity tests are snapshot-based, all green
- [ ] `md selftest` зелёный
- [ ] `git log --oneline -1` показывает commit «Phase 5: remove MCP server»
- [ ] `_ops/PROJECT-ROADMAP.md` обновлён (фронт → archived)
- [ ] `_ops/findings/2026-MM-DD-mcp-refactor-closeout.md` написан
- [ ] Все 23 task-файла в `_archive/YYYY-MM-DD-<task-slug>/` capsules
- [ ] `git tag | grep mcp-removed` → создан
- [ ] Backup tag `pre-mcp-refactor-2026-05-22` сохранён минимум 1 месяц

## Красные линии
- [ ] НЕ удалять backup tag сразу.
- [ ] НЕ начинать deletion без GO от task-501.
- [ ] НЕ пушить tag automatically — пользователь решает.
- [ ] НЕ удалять `_ops/plans/_archive/` или historical findings — они часть истории.
- [ ] НЕ забыть convert parity tests **ДО** deletion (или они сломаются после).

## Проверка
1. `ls experiments/md-embedding-server/` → нет `mcp/`
2. `git log --oneline -1` → «Phase 5: remove MCP server»
3. `md selftest --json | jq '.summary.pass'` → equals total
4. `cd experiments/md-embedding-server && uv run pytest tests/ -v` → all green
5. `git tag | grep mcp-removed` → tag exists
6. `git tag | grep pre-mcp-refactor` → backup tag still exists
7. `ls _ops/plans/md-mcp-to-cli-refactor/_archive/` → 23 dated capsules
