# Opus Session Recovery

Вход: exact typed session failure. Выход: одна evidence-backed action на том же
native ID либо честный stop.

- Busy session сначала observe; второй identity для той же conversation запрещён.
- Missing lease продолжай через `mcp__claude_mcp__claude_session` с
  `op: open_resume`, известными `session_id`, project `cwd` и новым prompt только
  при сохранённом `resolved_model`, начинающемся с `claude-opus-5`.
- Timeout или cancellation не повторяй автоматически.
- `max_turns` продолжай только при typed resumability и оправданном следующем
  turn.
- Если точная recovery не закрывает границу, назови packet evidence и одно
  следующее действие владельца или системы.
