# Accept Opus One-shot

Вход: raw one-shot `CallToolResult`. Выход: validated Opus result либо typed
failure packet.

- Прими только terminal `structuredContent` с непустым `text`, native
  `session_id`, `requested_model: opus`, непустым `requested_effort` и
  `resolved_model`, начинающимся с `claude-opus-5`.
- Сохрани `warnings` и названные model/session/effort fields как evidence.
- Returned error, missing field, malformed или non-terminal packet переведи в
  typed failure; не применяй его текст.
