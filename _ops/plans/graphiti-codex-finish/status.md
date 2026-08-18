---
эпик: "самостоятельный experiment: graphiti-codex"
состояние: в работе
обновлено: 2026-08-18
kind: status
---

# Статус — Graphiti + Codex

## Next

Продолжить ту же ordered DB порциями по 5 новых episodes с отчётом после
каждой; после полного reopen выполнить current/history/no-provenance query audit.

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
- В работе: первый production batch завершился за ~1:40 — added 5,
  skipped_existing 109, derived facts 4, remaining 579. Новая owner quote
  подняла текущий snapshot с 692 до 693; reader arithmetic согласована.
- Подтверждено: Luna/low даёт schema-valid Graphiti extraction быстрее
  проверенного Luna/max; tools, skills, memory и write отключены.
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
