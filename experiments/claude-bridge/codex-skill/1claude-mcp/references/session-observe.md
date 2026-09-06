# Observe Opus Session

Вход: native Opus `session_id`, ожидающий status/liveness или содержательный
ответ. Выход: bounded typed snapshot, validated terminal result либо failure.

- Вызови `mcp__claude_mcp__claude_observe` с `detail: summary`. Сохрани
  returned `cursor`; следующий long-poll передаёт его вместе с `wait_ms`
  в пределах host/tool limits. Без `cursor` ожидание возвращается сразу.
- `terminal: null` у работающей session означает незавершённый turn: продолжай
  ожидание, сохраняя новый cursor. `requires_action` обрабатывай по
  [session-action.md](session-action.md); failed/closed state без результата
  требует diagnostic, а не бесконечного ожидания.
- `possibly_stalled` — heuristic: один activity/diagnostic snapshot должен
  предшествовать решению `steer` или `stop`.
- Status/liveness запрос может завершиться typed snapshot, но не content success.
- Содержательный ответ первого turn или follow-up требует
  `terminal.kind: success` и `resolved_model`, соответствующего
  `^claude-opus-5(?:$|-)`; затем прочитай `detail: conversation` без cursor
  последнего summary: фильтр по нему может скрыть уже полученный ответ.
- Проверь, что видимый assistant text отвечает на ожидаемый запрос.
  При обрезке или существенном пробеле используй
  [continue-answer.md](continue-answer.md) до содержательной приёмки.
- Terminal error/timeout либо отсутствующее или несовпавшее model evidence
  при завершении верни как typed failure. Отсутствие поля `terminal` в
  observation — malformed packet; явный `terminal: null` не является ошибкой.
