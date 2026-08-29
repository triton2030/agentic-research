---
description: "Get one independent Claude Premortem report from the frozen Codex packet."
---

# Premortem

Вход: frozen panel или named Premortem packet. Выход: terminal Claude report или exact blocker.

1. Если Codex запущен из Claude, верни `premortem_skipped_recursive_parent` как exact blocker.
2. Иначе подготовь из frozen packet один prompt по `$1claude-mcp`; call mechanics принадлежат этому runtime-owner.
3. Не передавай native reports.
4. Попроси цепочку `achieved success → mechanism → harm`.
5. Попроси ранний signal, его адресуемый `state_today` и guardrail с ценой.
6. Потребуй первой строкой `fatal_signal_present`, `signal_watchable` или `story_unfalsifiable`.
7. Сохрани terminal report другой resolved model family или точный blocker без собственной замены.
