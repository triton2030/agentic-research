---
description: "Get one independent Claude Premortem report from the frozen Codex packet."
---

# Cross-family Premortem

Вход: frozen Premortem packet. Выход: terminal Claude report или explicit skip.

1. Если текущий Codex запущен из Claude, верни `premortem_skipped_recursive_parent` с gap и не вызывай Claude обратно.
2. Иначе один раз вызови `claude_ask` с `profile: opus_advisor`, project `cwd` и `effort: xhigh`; не запускай polling или retry.
3. Prompt передаёт decision, success state, completed artifact state, horizon, exact paths и source-bound facts.
4. Prompt не передаёт интерпретацию main или native panel reports.
5. Попроси одну цепочку `achieved success → mechanism → harm`.
6. Попроси ранний signal, его адресуемый `state_today` и guardrail с ценой.
7. Потребуй первой строкой `fatal_signal_present`, `signal_watchable` или `story_unfalsifiable`.
8. Прими только terminal result другой resolved model family; иначе верни точный blocker без собственной замены.
