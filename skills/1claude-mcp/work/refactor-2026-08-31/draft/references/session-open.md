# Open Opus Session

Вход: prepared advisor для новой управляемой консультации либо известные native
ID, project `cwd`, новый prompt и affirmative Opus evidence для lost lease.
Выход: один live native `session_id` и typed initial state.

- Новую консультацию открой через `mcp__claude_mcp__claude_session` с
  `op: open_fresh`, `profile: opus_advisor`, prepared prompt, real `cwd` и
  prepared fresh effort; сохрани returned native `session_id`.
- Lost lease продолжай через тот же tool с `op: open_resume`, известными
  `session_id`, project `cwd` и новым prompt только при сохранённом
  `resolved_model`, начинающемся с `claude-opus-5`.
- Без affirmative Opus evidence не используй resumed session как advisor.
- Независимые advisors получают разные IDs; два live lease одного ID запрещены.
- Initial accepted state доказывает открытие, но не содержательный ответ.
