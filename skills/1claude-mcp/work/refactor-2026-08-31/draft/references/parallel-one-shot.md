# Parallel Opus One-shot

Вход: тот же готовый brief, но после запуска остаётся полезная независимая
работа Codex. Выход: terminal result того же вызова либо один typed diagnostic.

1. До dispatch следуй host approval: вызов отправляет Anthropic prompt и
   прочитанные материалы, а clean launch не является local sandbox.
2. В одной `functions.exec` cell запусти Promise ровно одного
   `mcp__claude_mcp__claude_ask` с `profile: opus_advisor`, реальным `cwd`, без
   `session_id` и с default `xhigh`; `max` допустим только для оправданного вызова.
3. Верни короткую запись `family: claude, phase: started`, вызови
   `yield_control()` и продолжи полезную локальную работу в root.
4. Внутри той же cell дождись исходного Promise. Не открывай transient session,
   не polling-уй и не запускай второй advisor ради одного ответа.
5. Returned `CallToolResult` сохрани под task-scoped opaque `result_ref`; один
   финальный `notify()` сообщает только `bridge: returned` и ссылку.
6. Если cell или transport отказали раньше, сохрани diagnostic под
   `failure_ref`; один финальный `notify()` сообщает `observer: failed`,
   `bridge: unknown`, `external: unknown`. Автоматический повтор запрещён.
7. После wake загрузи ровно один result/diagnostic. Для success прочитай `text`,
   `session_id`, `requested_model`, `requested_effort`, `resolved_model` и
   `warnings`; отклони packet без непустого `text`, `requested_model: opus` или
   `resolved_model`, начинающегося с `claude-opus-5`.
8. Проверь используемые claims по task evidence. При failure верни сохранённый
   diagnostic как выход режима; recovery начинается отдельным решением root.
