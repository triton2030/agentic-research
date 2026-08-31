# Open Opus Session

Вход: prepared advisor для новой управляемой консультации. Выход: один live
native `session_id` и typed initial state.

- Новую консультацию открой через `mcp__claude_mcp__claude_session` с
  `op: open_fresh`, `profile: opus_advisor`, prepared prompt, real `cwd` и
  prepared fresh effort; сохрани returned native `session_id`.
- Независимые advisors получают разные IDs; два live lease одного ID запрещены.
- Initial accepted state доказывает открытие, но не содержательный ответ.
