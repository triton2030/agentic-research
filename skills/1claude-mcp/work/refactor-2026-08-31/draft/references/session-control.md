# Opus Session Control

Вход: нужен follow-up, steer, status/liveness или stop известной Opus session.
Выход: одно адресуемое действие и typed state/result того же native ID.

- `mcp__claude_mcp__claude_session` с `op: open_resume` принимает известные
  native `session_id`, тот же project `cwd` и новый prompt только при сохранённом
  affirmative Opus model evidence.
- Без `resolved_model`, начинающегося с `claude-opus-5`, не используй session
  как advisor и не приписывай ей мнение Opus.
- Независимые advisors получают разные IDs; два live lease одного ID запрещены.
- `mcp__claude_mcp__claude_observe` с `detail: summary` — default bounded
  snapshot; используй один `wait_ms` long-poll только когда действительно ждёшь.
- Activity, conversation или diagnostic читай только когда они меняют
  следующее действие.
- В `idle` используй `send`; в активном состоянии используй `steer` только для
  материальной коррекции.
- `requires_action` требует одного diagnostic и осознанного steer/stop;
  в `closing` не отправляй и не переоткрывай.
- `possibly_stalled` — heuristic: один activity/diagnostic snapshot должен
  предшествовать steer/stop.
- `idle` с `terminal.kind: success` и affirmative Opus evidence разрешает один
  bounded conversation read; отсутствие или несовпадение model evidence идёт в
  typed failure и завершает этот режим.
- После локальной проверки сделай `stop`, если follow-up больше не оправдан.
- Успех доказывают тот же `session_id`, ожидаемый `accepted_op`, `state`,
  `cursor`, terminal metadata и affirmative Opus evidence; tool/activity label
  или progress содержательную работу не доказывают.
