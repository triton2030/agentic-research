# Inspect Existing Claude Sessions

Вход: владелец просит список активных Claude sessions или видимую переписку
известной session. Выход: один read-only bounded result без advisor attribution.

- `mcp__claude_mcp__claude_sessions` с `op: list_active` возвращает metadata;
  optional `cwd` только сужает список.
- `op: read` принимает известный active `session_id` и возвращает bounded
  visible user/assistant text, но не hidden reasoning, system или tool I/O.
- Active session нельзя одновременно брать через `open_resume`: текущий Claude
  process уже владеет ею.
- Non-Opus session можно показать как найденную Claude session, но нельзя
  использовать как advisor или приписывать ей мнение Opus.
