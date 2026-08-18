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
- Последний подтверждённый reopen checkpoint ordered DB:
  195/693 уникальных episodes, 300 facts, 33 invalidated, remaining 498,
  duplicate names 0; BGSAVE `ok`, changes 0. Резервная копия до удаления старого
  concurrent-дубля:
  `.data/owner-quotes-2026-08-04_2026-08-18-luna-low-ordered.before-dedup-20260819T0110.db`.
- Последние полные пачки 5/5: 18 facts за 226.00 s, 10 facts за 193.23 s,
  8 facts за 201.46 s; observed range 38.6–45.2 s/episode.
- Luna/medium проверена изолированно на той же temporal control-паре, не в
  основной DB: 103.71 s против около 96.9 s у low, те же 5 facts и 2 invalidated,
  но medium инвалидировала две новые фразы об отмене и оставила старый лимит
  актуальным в current query. Поэтому default остаётся Luna/low.
- Первый probe двух одновременных turns в одном conversation thread был
  нерелевантен гипотезе владельца о последовательном reuse и не используется как
  verdict. Корректный A/B реализовал один thread на episode с lock для всех
  Graphiti turns и сравнил его с ephemeral-per-call на одинаковых clean DB.
- Sequential shared-thread был стабильно быстрее во всех трёх измерениях:
  57.095 vs 84.863 s, 49.281 vs 74.093 s на temporal-паре и 20.405 vs
  29.350 s на первой цитате; выигрыш около 30–34%, несмотря на сериализацию
  fan-out до 2–3 ожидающих turns.
- Ручная проверка raw Graphiti responses не приняла этот выигрыш: shared
  `ExtractedEdges` три раза из трёх потерял главное owner-правило «каждый файл
  не больше 2000 символов», хотя последующий `SummarizedEntities` его понимал;
  факт оставался summary узла, а не searchable edge. Ephemeral сохранил правило
  в 2/3 runs. На поздней цитате shared в 2/2 runs приписал отмену Agent и не
  создал historical old-rule edge; ephemeral правильно приписал отмену Owner
  в 2/2, хотя correct invalidation получил только 1/2 из-за model variance.
- Текущий production verdict: сохранять warm app-server + ephemeral thread на
  каждый Graphiti call. Thread-per-episode доказал speed potential, но на этом
  exact corpus-probe ухудшил fact recall, attribution и historical coverage;
  temporal correctness имеет приоритет над скоростью. Владелец закрепил выбор:
  `_ops/chat-recall/2026-08-18-151822-codex-01a0145e.md:67`.
- Повторный A/B на девяти других quotes проверил три независимых серии:
  эволюцию правил объяснений, разрешение quote + Agent context и алгоритм
  восстановления времени. Shared был 45.5% быстрее: 230.789 s / 35 LLM calls
  против ephemeral 423.236 s / 44 calls, но сохранил лишь 12 fact-edges против
  23 и снова предпочитал факты из Agent context словам Owner.
- Ручной semantic audit нового набора: shared потерял исходное правило финала
  и крупные заголовки; не сохранил финальное разрешение Owner передавать цитату
  вместе с Agent context; почти полностью потерял owner-алгоритм времени
  (порядок, соседние файлы, временное окно). Ephemeral сохранил эти owner-facts,
  но проявил stock Graphiti defects: чрезмерно инвалидировал правило длинных
  объяснений, не полностью снял старое сомнение о context и оставил рядом
  вытесненный вариант «полдень + source-order».
- Diverse-series probe подтверждает verdict уже вне сюжета 2000 символов:
  shared conversation ускоряет turns, но materially снижает owner-fact recall;
  ephemeral остаётся production transport, а несовершенная invalidation —
  наблюдаемый предел stock Graphiti/Luna, не повод добавлять свою семантику.
- Pinned retained task `01a01480-61ba-77b3-a876-01f3b50b15a5` активен и после
  чистого checkpoint 195/693 продолжает отдельными `batch-size 5`; runtime
  сильнее этого снимка, следующая сессия сначала читает сам task.
- Adapter теперь fail-closed при duplicate episode identity; `ruff` — pass,
  `pytest` — 26 passed. Live `doctor` — ready.
