---
эпик: "самостоятельный experiment: graphiti-codex"
состояние: в работе
обновлено: 2026-08-19
kind: status
---

# Статус — Graphiti + Codex

## Next

Заменить только транспорт `codex exec` на один тёплый `codex app-server` на
CLI-run, сохраняя новый ephemeral thread для каждого Graphiti LLM-call. Затем
повторить transport benchmark и реальную temporal-пару; при равной семантике
продолжить ordered DB порциями по 5 episodes.

## Свидетельства и статус

- Подтверждено: pinned Graphiti 0.29.3 работает через embedded FalkorDBLite,
  local multilingual-e5-small и Codex LLM seam.
- Подтверждено: current inventory — 117 tracked holders, 693 quotes:
  668 exact + 25 date-only, интерполированных по порядку между соседними
  session timestamps; diagnostics = 0.
- Подтверждено live: настоящий date-only record получил вычисленное
  `reference_time`, добавлен как 1 stock episode и дал 3 derived facts;
  public query не раскрыл quote/address.
- Остановлена: partial exact-only
  `owner-quotes-2026-08-04_2026-08-18-luna-low.db`; checkpoint сохранён как
  control, продолжать его нельзя. Full corpus пойдёт в новую ordered DB.
- Подтверждено: прежний writer мягко остановлен; checkpoint ordered DB после
  reopen содержит 109 episodes / 126 facts / 9 invalidated, BGSAVE status ok,
  unsaved changes 0. Schema/provenance errors отсутствуют; были transient
  `UnknownIssuer` и DNS transport errors.
- Подтверждено live: два одинаковых `--batch-size 1` запуска последовательно
  дали `skipped=1, added=1, remaining=1, complete=false`, затем
  `skipped=2, added=1, remaining=0, complete=true`.
- Повторяемый production ingest мягко остановлен после наблюдаемой порции:
  ordered DB содержит 149 episodes / 201 facts / 25 invalidated, remaining 544;
  BGSAVE ok, unsaved changes 0, writer/Codex/Redis процессов нет. Snapshot
  остаётся frozen на commit `692d894`: 117 holders / 693 records.
- Проверено изолированно на пяти реальных quotes: штатный Graphiti 0.29.3
  multi-episode combined extraction через Luna/max обработал все 5 episode
  indices и вывел 17 facts за 2 LLM turns, но занял 428.138 s. Luna/low на
  том же общем prompt превысила 300 s timeout. Ранняя позиция «решить потом»
  не получила `invalid_at` от более поздней коррекции внутри той же пачки.
  Поэтому multi-episode extraction не входит в production ingest: он не дал
  ускорения и не доказал intra-batch temporal invalidation.
- Проверено по совету Opus и official Codex runtime: один полный scratch
  `Graphiti.add_episode` занял 47.797 s и сделал 4 последовательных LLM turns
  (`ExtractedEntities`, `ExtractedEdges`, `EdgeTimestamps`,
  `SummarizedEntities`). Суммарный cold start до первого JSON event —
  1.064 s, а ожидание выхода процессов после уже полученного
  `turn.completed` — 8.284 s. Persistent `codex app-server` с новым ephemeral
  thread на каждый turn — подтверждённый официальный transport-кандидат, но
  ещё не принят без отдельного contract/performance proof.
- Подтверждено: Luna/low даёт schema-valid Graphiti extraction быстрее
  проверенного Luna/max; tools, skills, memory и write отключены.
- Проверено A/B на одной реальной temporal-паре `1000 → 2000` в чистых БД:
  Luna/low — 61.453 s, 5 edges, 1 invalidated; Luna/none — 33.374 s, но
  поздний episode дал 0 facts и оставил старый лимит актуальным; Terra/none —
  66.397 s, 4 edges, 1 invalidated. Поэтому отвергнута только Luna/none.
  Terra/none сохранила проверенную temporal semantics и на этой паре была
  практически равна Luna/low по скорости; общая quality parity не доказана,
  поскольку состав рёбер различается. До переключения нужен более широкий A/B.
- Решение владельца после A/B: оставить Luna/low — Terra/none дороже и не дала
  существенного выигрыша скорости
  (`_ops/chat-recall/2026-08-18-151822-codex-01a0145e.md`).
- Официальный Graphiti README рекомендует при медленном ingestion поднимать
  `SEMAPHORE_LIMIT` в пределах пропускной способности LLM-провайдера; официальный
  MCP server поясняет, что каждый episode вызывает несколько LLM-операций.
  Adapter уже допускает 4 параллельных Luna-turns внутри episode, но сохраняет
  последовательность episodes одного temporal corpus.
- GitHub issues `getzep/graphiti#1516` и `#1262` подтверждают наблюдаемый
  bottleneck: число extraction/dedup/resolution LLM-вызовов, умноженное на их
  latency и сериализацию. `skip_extraction` и bulk не подходят: первый убирает
  нужные facts/edges, второй официально не гарантирует edge invalidation.
- Изолированный transport A/B на текущем ChatGPT Codex binary, Luna/low и одном
  strict schema-answer: два холодных `codex exec` — 8.668/9.546 s
  (mean 9.107); один app-server + два новых ephemeral threads — startup 0.924 s,
  turns 8.480/6.068 s (mean 7.274; 7.736 с долей startup). Кандидат даёт
  примерно 15–20% транспортного выигрыша, не меняя Graphiti prompts или
  conversation semantics; real Graphiti proof ещё обязателен.
- Подтверждено: custom ontology, `RECORD_SCOPE`, `record_type` и relation
  filters удалены; episode — только `Owner:` и optional `Agent:` messages.
- Подтверждено: `uv run ruff check .` — pass; `uv run pytest -q` — 26 passed;
  `uv run graphiti-codex doctor` — ready.
- Подтверждено: live stock temporal pair добавила 2 episodes / 8 facts;
  старая связь получила `invalid_at=2026-08-08T09:05:14.733Z`, current
  вернул current-версию, historical — старую.
- Принятый предел stock Graphiti: `Agent:` context может создать
  дублирующий Agent-fact. JSON/inline-context не дали facts; свою
  post-processing семантику не добавляем.
- Старая Luna/max DB остаётся control snapshot; она не продолжается и не
  смешивается с новой Luna/low базой.
