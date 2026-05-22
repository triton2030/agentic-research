# Semantic equivalence document: каждый skill и его CLI invocations

## Цель
Создать единый документ `experiments/md-embedding-server/docs/skills-semantic-equivalence.md`, который для каждого из **13 affected skills** доказывает что migration MCP → CLI **не ломает skill logic**. Это reference для всех migration tasks (301-305) и evidence для closeout.

Без этого документа migration — это «надеемся что find&replace ничего не сломал». С ним — explicit pre-flight verification что CLI покрывает все semantically important patterns of use.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)
- `_ops/project-graph.md`

## Зависимости
- task-000 закрыт (MCP signatures snapshot)
- task-001 закрыт (canonical CLI signatures)
- task-002 закрыт (framework decision — нужен правильный CLI syntax)

## Подшаги

- [ ] **Automation substep (audit cycle-2 Implementation G1)**: создать `experiments/md-embedding-server/scripts/extract-mcp-usages.py`:
  - Парсит все 26 SKILL.md (13 skills × 2 платформы Claude/Codex) regex'ом `md_[a-z_]+\(\{[^}]*\}\)`
  - Выгружает CSV с колонками: `skill | platform | tool | invocation_pattern | line_number`
  - Это input для manual review секций — без него equivalence doc пишется по «памяти» и пропускает edge cases
  - Output: `experiments/md-embedding-server/docs/mcp-usages-extracted.csv`

- [ ] Создать `experiments/md-embedding-server/docs/skills-semantic-equivalence.md`. Структура для каждого skill — одна секция с такими полями:

  ```md
  ## <skill-name>
  
  **Назначение**: <1-2 строки о цели skill>
  
  **Когда срабатывает**: <key trigger phrases / situations>
  
  **MCP usage сейчас**: <список tools + специфические patterns: thresholds, scopes, rerank, dry-run/confirm flows>
  
  **CLI invocations после migration**:
  | MCP call | CLI equivalent |
  |---|---|
  | `md_search({ corpus, query })` | `md search PATH "query" --json` |
  | ... | ... |
  
  **Semantic patterns preserved**:
  - <pattern 1>: например «threshold 0.85» — flag `--threshold 0.85` works
  - <pattern 2>: например «dry-run/confirm flow для md_index» — задокументирован в task-204
  
  **Что может сломаться (risk)**: <конкретные риски + mitigation>
  
  **Test plan**: <что покажет что skill работает после migration>
  ```

- [ ] Заполнить **13 секций**, по одной на skill:

  **Core (2):**
  1. `1md-navigator` — semantic reader для Markdown corpus; uses ~20 tools (search/overlaps/repeated-concepts/cluster/audit/read-related/map/headings/read/orient/etc.)
  2. `1md-graph` — frontmatter graph hygiene; preflight/impact/deps/health/cycles/check/scan/init/strip/changed

  **Extended (11):**
  3. `1ia-audit` — container-shape verdict для Markdown corpus; uses md_audit, md_search, md_repeated_concepts, md_overlaps, md_toc, md_extract
  4. `1instruction-layer` — language quality в AGENTS/CLAUDE; uses md_overlaps, md_repeated_concepts, md_audit, md_search (+rerank, +scope)
  5. `1planning` — recursive planning L1→L3; uses md_orient, md_ls, md_search, md_extract, md_query_by_type, md_preflight, md_edit_context, md_changed
  6. `1strategy` — momentum decision-thinking; uses md_search ('_ops' corpus), md_extract
  7. `1strategy-docs` — goal/scope/done/stop thinking; uses CLI-shaped `1md-navigator status _ops/`, `audit`, `repeated-concepts`, `overlaps`, `1md-graph preflight/changed`
  8. `1folder-contract` — folder graph + Owner Decision Map + Goal-цитата sync; uses md_changed (staged), md_search (scope=descriptions)
  9. `1assumption-audit` — semantic predicates; uses md_search (scope=descriptions, limit=3), md_overlaps (threshold=0.85), md_read_related
  10. `1work-review` — closeout / post-execution gate; uses md_changed, md_preflight, md_health, md_check, md_edit_context
  11. `1skill-architect` — skill design; uses md_index (~/.claude/skills, dry-run/confirm), md_search (scope, rerank, path_include), md_overlaps
  12. `1smart-simple` — prose density; uses md_search per span (limit=3), md_index dry-run/confirm для cold corpus
  13. `1cli-tools` (references только) — markdown-track, tool-map — упоминают MCP tools как options

- [ ] Для каждого skill — **verify** что CLI поддерживает все semantic patterns:
  - Сверить с `docs/cli-signatures-canonical.md` (task-001 output) что **все flags существуют** в CLI versions
  - Если flag отсутствует — добавить в task-201/202/203/204 как gap
  - Если pattern имеет implicit assumption (например «`md_index` для ~/.claude/skills работает с symlinks») — задокументировать в risk section

- [ ] Особое внимание паттернам которые могут сломаться:
  - **Threshold/limit defaults** — должны быть identical (флаги с default values match MCP defaults)
  - **dry-run/confirm flow** — multi-call pattern сохраняется через fingerprint transactions (task-103)
  - **Path-filter behavior** — multiple flags vs comma-separated (task-001 decision применяется)
  - **JSON output schema** — envelope shape (task-102) идентичен MCP envelope (golden test)
  - **Exit codes** — 0/1/2/3/4 mapping одинаковый (task-201)
  - **rerank flag** — `md_search` поддерживает rerank? Если нет — task-201 gap
  - **scope=descriptions** — для уровня файлов; flag works?

- [ ] **Cross-platform проверка** в каждой секции:
  - «Claude usage» pattern и «Codex usage» pattern — могут различаться (Codex использует `default_prompt` для tool invocation guidance)
  - Document any platform-specific nuances

- [ ] **Section: «Что добавляется» (новое поведение)**:
  - Для каждого skill — что после migration **становится возможным** что не было раньше? (например `md tools --json` discovery)
  - Это не required, но useful для product perspective

- [ ] Cross-reference в migration tasks (task-301/302/304/305):
  - Каждая migration task должна цитировать соответствующую секцию equivalence doc
  - Acceptance criterion: skill после migration ведёт себя как описано в equivalence doc

- [ ] Final review: запустить `1fresh-eyes` subagent с независимым взглядом для верификации:
  - «Прочти `docs/skills-semantic-equivalence.md` + 3 случайных skills из live `~/.claude/skills/`. Найди skills, где CLI invocation НЕ покрывает MCP usage pattern. Найди missing flags. Найди assumed-but-not-documented behaviors.»
  - **Save output в `_ops/findings/2026-MM-DD-equivalence-doc-review.md`** (audit cycle-2 Smith G4 + Implementation G6 — evidence path)
  - **Pass criterion**: findings list (может быть empty). Все non-empty findings либо resolved правкой equivalence doc, либо записаны как accepted gaps в task-201/202/203/204 substeps. Без этой routing — task-003 не закрывается.

## Готово
- [ ] `docs/skills-semantic-equivalence.md` существует
- [ ] Все 13 skills имеют секции с 6 полями каждая
- [ ] Каждая секция cross-references task-201/202/203/204 для импленментации flags
- [ ] Identified gaps (если есть) добавлены как substeps в task-201/202/203/204
- [ ] Independent subagent review confirms нет missing patterns

## Красные линии
- [ ] Не делать секции «generic» (общие фразы). Каждая section — about specific tool calls с specific parameters skill уже использует.
- [ ] Не пропускать `1cli-tools` references (тоже affected, хоть references-only).
- [ ] Не предполагать «migration mechanical» без verification per-skill semantics.
- [ ] Не writing документ как marketing material — это engineering doc, для будущей verification.

## Проверка
1. `cat experiments/md-embedding-server/docs/skills-semantic-equivalence.md | grep "^## " | wc -l` → 13 (one per skill)
2. `grep -c "MCP usage" experiments/md-embedding-server/docs/skills-semantic-equivalence.md` → 13
3. `grep -c "Semantic patterns preserved" experiments/md-embedding-server/docs/skills-semantic-equivalence.md` → 13
4. Independent subagent review проведён, findings отражены в task-201/202/203/204 если нашли gaps
