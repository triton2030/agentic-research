---
эпик: "самостоятельный experiment: graphiti-codex"
состояние: в работе
обновлено: 2026-08-19
kind: status
---

# Статус — Graphiti + Codex

## Next

Продолжать frozen corpus в той же ordered DB короткими пачками по 5 episodes:
один тёплый `codex app-server` на запуск, новый ephemeral thread на каждый
Graphiti LLM-call, максимум 4 Luna-turn внутри episode, сами episodes строго
последовательны. После 693/693 — current/history query audit и финальная сдача.

## Свидетельства и статус

- Принята и реализована финальная архитектура: stock Graphiti 0.29.3,
  embedded FalkorDBLite, local multilingual-e5-small, Luna/low; один persistent
  Codex app-server на CLI-run, один ephemeral thread на каждый LLM-call.
- Episodes одного owner corpus остаются последовательными; внутри episode
  допускаются максимум 4 параллельных Luna-turn. `add_episode_bulk` и custom
  multi-episode extraction не используются, поскольку не сохраняют доказанную
  temporal invalidation семантику.
- Подтверждено: current inventory — 117 tracked holders, 693 quotes:
  668 exact + 25 date-only, интерполированных по порядку между соседними
  session timestamps; diagnostics = 0. Snapshot frozen на commit `692d894`.
- Изолированный transport A/B на текущем ChatGPT Codex binary, Luna/low и одном
  strict schema-answer: два холодных `codex exec` — 8.668/9.546 s
  (mean 9.107); один app-server + два новых ephemeral threads — startup 0.924 s,
  turns 8.480/6.068 s (mean 7.274; 7.736 с долей startup). Transport принят.
- Live Graphiti control-пара через app-server: старая связь получила
  `invalid_at=2026-08-08T09:05:14.733Z`; current query исключил её, historical
  до границы вернул. Отдельная пара `1000 → 2000` не была семантически
  распознана моделью и не дала invalidation: temporal filter гарантирует
  исключение уже инвалидированных рёбер, но не гарантирует распознавание каждой
  коррекции stock Graphiti.
- Ordered DB после последней полной пачки и штатного удаления одного старого
  concurrent-дубля: 175/693 уникальных episodes, 266 facts, 31 invalidated,
  remaining 518. Резервная копия до удаления:
  `.data/owner-quotes-2026-08-04_2026-08-18-luna-low-ordered.before-dedup-20260819T0110.db`.
- Последние полные пачки 5/5: 18 facts за 226.00 s, 10 facts за 193.23 s,
  8 facts за 201.46 s; observed range 38.6–45.2 s/episode.
- Luna/medium проверена изолированно на той же temporal control-паре, не в
  основной DB: 103.71 s против около 96.9 s у low, те же 5 facts и 2 invalidated,
  но medium инвалидировала две новые фразы об отмене и оставила старый лимит
  актуальным в current query. Поэтому default остаётся Luna/low.
- Adapter теперь fail-closed при duplicate episode identity; `ruff` — pass,
  `pytest` — 26 passed. Live `doctor` — ready.
