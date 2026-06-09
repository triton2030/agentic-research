---
description: Refactor plan for md-mcp — scenario-driven strategy that drives live
  changes in md-embedding-server.
depends-on:
- '[[minimum-document-set.md]]'
- '[[current-skill-usage-map.md]]'
---
# md-mcp Refactor Plan

Папка держит проектную основу рефактора md-mcp. Изначально проектировалась
как docs-first v2 в `experiments/md-tools-v2/`. После scenario-walkthrough
(3 параллельных subagent, 6 живых сценариев каждый) выбран другой путь —
in-place hybrid рефактор без v2-as-replacement.

## Что Уже Сделано (live в `experiments/md-embedding-server/`)

1. **Split `graph.py` 1505 → 4 модуля** (commit `d2c1f57`). Foundation hygiene
   до того как трогать поведение: `graph_core.py` / `graph_edges.py` /
   `graph_reports.py` + thin facade `graph.py`. Public API без изменений.
2. **Response envelope skeleton** (Phase 1.1, commit `a4f75d8`). Каждый MCP
   reply теперь несёт `_envelope: {version, tool, corpus_root, corpus_state,
   lock, cost, next_step}`. Backward-compatible.
3. **Corpus state filling** (Phase 1.2, commit `7d90e32`). `md_status --json`
   возвращает structured state classification (FRESH/HEALTHY/NEEDS_WARMUP/
   NEEDS_REBUILD/NO_INDEX) + `recommended_action`. Envelope подключает это в
   каждый reply через 30s TTL cache.
4. **Edit transaction tokens** (Phase 2, commit `966d51a`). `md_init` /
   `md_strip` теперь dry_run → confirm с fingerprint verification. Drift
   между двумя calls обнаруживается structured `drift_detected` error.

## Что Отложено

- **Phase 3 — Saga collapse** (workflow tools: `md_find_and_read`,
  `md_warm_corpus`, `md_close_batch`). Частично уже решено через Phase 1.2
  `corpus_state.recommended_action` + envelope `next_step` — агент видит
  следующий шаг из любого reply без отдельного saga tool. Полный collapse
  отложен до пользовательской боли в проде.
- **Phase 4 — Cooperative locks** (`LOCK_NB` + holder identity). Требует
  Python work в `index_meta.py`. Lock contention сегодня cryptic (SQLite
  busy_timeout 30s → exit 1). Отложено до user signal что cross-skill races
  реально бьют в текущей работе.
- **md_index / md_profile_sections transaction tokens**. Per-corpus
  fingerprint over ~300 файлов в нашем knowledge corpus сделает dry_run
  тяжёлым. Пересмотреть когда появится session-scoped corpus cache.

## История Решения

Read in order:

1. `minimum-document-set.md` — какие документы обязательны и зачем.
2. `current-skill-usage-map.md` — какие текущие скилы используют какие
   `md_*` возможности (evidence, не вкус).
3. `full-functionality-contract.md` — весь функционал, который рефактор
   должен сохранить для текущих скилов без переписывания `SKILL.md`.
4. `jobs-and-moments.md` — рабочие моменты: когда агент зовёт tool, что
   хочет получить и какой риск закрывает.
5. `public-capability-contract.md` — публичные возможности на языке
   скилов.
6. `architecture-boundaries.md` — границы ядра, graph, search, audit,
   profiles, MCP adapter и CLI.
7. `state-and-cost-model.md` — индексы, кеши, ключи, внешние API,
   мутации, стоимость и режимы отказа.
8. `compatibility-and-migration.md` — что должно остаться совместимым с
   текущим `md-mcp`, CLI и installed skills.
9. `validation-and-release-gates.md` — какие проверки доказывают, что
   живой рефактор не сломал скилы.
10. `decision-log.md` — только решения, которые меняют контракт или
    архитектурную границу.

## Правило Разработки

Новая возможность не добавляется в код, пока для неё не названы:

- skill-момент;
- публичная capability;
- владелец состояния;
- стоимость или side effect;
- режим отказа;
- проверка совместимости.

Скилы не переписываются — backend меняется так, чтобы recipes остались
рабочими. Phase 1 envelope полностью backward-compatible (additive); Phase 2
transaction tokens добавляют новый аргумент `transaction_id` в schema
`md_init` / `md_strip` (optional при dry_run, required при confirm).
