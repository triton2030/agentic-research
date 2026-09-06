# Accept Opus One-shot

Вход: raw one-shot `CallToolResult` и исходный call envelope. Выход: validated
Opus result, необходимость дополнить ответ либо typed failure packet.

- Прими только успешный `CallToolResult` с непустым `structuredContent.text`,
  native `session_id` и `resolved_model`, соответствующим
  `^claude-opus-5(?:$|-)`. One-shot возвращается после завершения; отдельного
  поля `terminal` в его success schema нет.
- Для fresh envelope требуются `requested_model: opus` и
  `requested_effort: xhigh | max`, совпадающий с запросом (default `xhigh`).
  Для envelope с `session_id` ответ должен вернуть тот же ID и оба requested
  fields как `null`: продолжение сохраняет модель и effort native session.
- Сохрани `warnings` и названные model/session/effort fields как evidence.
- Returned error, missing field, malformed или non-terminal packet переведи в
  typed failure; не применяй его текст.
- `result_truncated_at:*` или маркер пропущенного текста означает неполное
  заключение, даже при техническом успехе. Перед содержательной приёмкой получи
  недостающие выводы по [continue-answer.md](continue-answer.md).
