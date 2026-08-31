# Observe Opus Session

Вход: native Opus `session_id`, ожидающий status/liveness или содержательный
ответ. Выход: bounded typed snapshot, validated terminal result либо failure.

- Вызови `mcp__claude_mcp__claude_observe` с `detail: summary`; один `wait_ms`
  long-poll допустим только когда действительно ждёшь.
- `possibly_stalled` — heuristic: один activity/diagnostic snapshot должен
  предшествовать решению `steer` или `stop`.
- Status/liveness запрос может завершиться typed snapshot, но не content success.
- Содержательный follow-up завершён только на `terminal.kind: success` и
  `resolved_model`, начинающемся с `claude-opus-5`; затем прочитай одну bounded
  visible conversation.
- Отсутствующее или несовпавшее model/terminal evidence верни как typed failure.
- Сохрани raw identity, state, cursor и terminal evidence; activity label или
  progress содержательную работу не доказывают.
