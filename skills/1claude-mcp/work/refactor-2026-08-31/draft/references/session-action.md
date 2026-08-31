# Act on Live Opus Session

Вход: live native Opus `session_id`, typed current state и запрошенное действие.
Выход: raw typed action packet либо маркер ожидаемого содержательного ответа.

- В `idle` используй `mcp__claude_mcp__claude_session` с `op: send`; в active
  state используй `op: steer` только для материальной коррекции.
- `requires_action` требует одного diagnostic и осознанного `steer` или `stop`;
  в `closing` не отправляй и не переоткрывай.
- `stop` завершает exact live lease по просьбе владельца или когда follow-up
  больше не оправдан.
- Status/steer/stop-only запрос заканчивается typed state запрошенного action.
- Follow-up с ожидаемым ответом после accepted `send`/`steer` переходит в
  session observation; accepted operation содержательным успехом не является.
