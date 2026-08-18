---
эпик: "самостоятельный experiment: graphiti-codex"
состояние: в работе
обновлено: 2026-08-18
kind: status
---

# Статус — Graphiti + Codex

## Next

В существующей фоновой задаче запустить один последовательный ingest
648 цитат в новую Luna/low DB.

## Свидетельства и статус

- Подтверждено: pinned Graphiti 0.29.3 работает через embedded FalkorDBLite,
  local multilingual-e5-small и Codex LLM seam.
- Подтверждено: Luna/low даёт schema-valid Graphiti extraction быстрее
  проверенного Luna/max; tools, skills, memory и write отключены.
- Подтверждено: custom ontology, `RECORD_SCOPE`, `record_type` и relation
  filters удалены; episode — только `Owner:` и optional `Agent:` messages.
- Подтверждено: `uv run ruff check .` — pass; `uv run pytest -q` — 24 passed;
  `uv run graphiti-codex doctor` — ready.
- Подтверждено: live stock temporal pair добавила 2 episodes / 8 facts;
  старая связь получила `invalid_at=2026-08-08T09:05:14.733Z`, current
  вернул current-версию, historical — старую.
- Принятый предел stock Graphiti: `Agent:` context может создать
  дублирующий Agent-fact. JSON/inline-context не дали facts; свою
  post-processing семантику не добавляем.
- Старая Luna/max DB остаётся control snapshot; она не продолжается и не
  смешивается с новой Luna/low базой.
