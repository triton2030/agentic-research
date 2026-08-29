---
description: "Obtain the fourth panel report from Claude without a recursive family loop."
---

# Cross-family Premortem

Вход: decision packet и три native reports. Выход: terminal Claude verdict или
явный recursive-parent skip.

Если текущий Codex сам запущен из Claude, не вызывай Claude обратно: верни
`premortem_skipped_recursive_parent` и синтезируй три native reports с явным gap.

Иначе вызови один `claude_ask` по `$1claude-mcp`; не запускай polling или
параллельный повтор.

Передай decision, source-supported rationale, success state, completed work,
horizon и exact paths без гипотезы провала.

Попроси одну цепочку `achieved success → mechanism → harm`.

Попроси один ранний наблюдаемый signal, его `state_today` с адресом и
guardrail, сохраняющий success, с ценой.

Bad implementation или omitted work не являются Premortem story.

Первая строка: `fatal_signal_present` · `signal_watchable` ·
`story_unfalsifiable`.

Проверь `resolved_model`, warnings и terminal result другой семьи.

Bridge недоступен — верни точную ошибку; своей историей чужую не подменяй.
