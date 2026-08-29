---
description: "Get one independent Claude Premortem report from the frozen Codex packet."
---

# Premortem

Вход: frozen Premortem packet. Выход: terminal Claude report или explicit skip.

1. Если Codex запущен из Claude, верни `premortem_skipped_recursive_parent` с gap.
2. Иначе один раз вызови `claude_ask` с `opus_advisor`, project `cwd` и `xhigh`; не запускай polling или retry.
3. Передай только frozen packet; не передавай native reports.
4. Попроси цепочку `achieved success → mechanism → harm`.
5. Попроси ранний signal, его адресуемый `state_today` и guardrail с ценой.
6. Потребуй первой строкой `fatal_signal_present`, `signal_watchable` или `story_unfalsifiable`.
7. Прими только terminal result другой resolved model family; иначе верни точный blocker без собственной замены.
