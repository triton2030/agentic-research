---
эпик: "самостоятельный experiment: graphiti-codex"
состояние: в работе
обновлено: 2026-08-18
kind: status
---

# Статус — Graphiti + Codex

## Next

Дождаться фонового sequential ingest 692 цитат; после reopen снять
authoritative counts и выполнить current/history/no-provenance query audit.

## Свидетельства и статус

- Подтверждено: pinned Graphiti 0.29.3 работает через embedded FalkorDBLite,
  local multilingual-e5-small и Codex LLM seam.
- Подтверждено: current inventory — 117 tracked holders, 692 quotes:
  667 exact + 25 date-only, интерполированных по порядку между соседними
  session timestamps; diagnostics = 0.
- Подтверждено live: настоящий date-only record получил вычисленное
  `reference_time`, добавлен как 1 stock episode и дал 3 derived facts;
  public query не раскрыл quote/address.
- Остановлена: partial exact-only
  `owner-quotes-2026-08-04_2026-08-18-luna-low.db`; checkpoint сохранён как
  control, продолжать его нельзя. Full corpus пойдёт в новую ordered DB.
- В работе: одна команда без `--limit` пишет все 692 records в новую
  `owner-quotes-2026-08-04_2026-08-18-luna-low-ordered.db`; reader передал
  117 holders, 667 exact + 25 interpolated, diagnostics = 0.
- Подтверждено: Luna/low даёт schema-valid Graphiti extraction быстрее
  проверенного Luna/max; tools, skills, memory и write отключены.
- Подтверждено: custom ontology, `RECORD_SCOPE`, `record_type` и relation
  filters удалены; episode — только `Owner:` и optional `Agent:` messages.
- Подтверждено: `uv run ruff check .` — pass; `uv run pytest -q` — 25 passed;
  `uv run graphiti-codex doctor` — ready.
- Подтверждено: live stock temporal pair добавила 2 episodes / 8 facts;
  старая связь получила `invalid_at=2026-08-08T09:05:14.733Z`, current
  вернул current-версию, historical — старую.
- Принятый предел stock Graphiti: `Agent:` context может создать
  дублирующий Agent-fact. JSON/inline-context не дали facts; свою
  post-processing семантику не добавляем.
- Старая Luna/max DB остаётся control snapshot; она не продолжается и не
  смешивается с новой Luna/low базой.
