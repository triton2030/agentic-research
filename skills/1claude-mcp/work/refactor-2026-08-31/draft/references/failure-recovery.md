# Claude Failure Recovery

Вход: exact typed failure packet. Выход: не более одной evidence-backed recovery
action либо честный stop.

- Сохрани исходные trust boundary и external identity; смена provider,
  credential, subscription route, model/profile, data scope или session ID —
  новый запрос, а не recovery.
- Не повторяй автоматически token-consuming или session-appending action.
- Missing/stale tool или schema — сохрани diagnosis, остановись и предложи
  владельцу fresh Codex task; сам task не создавай.
- Approval, auth, billing, unsupported model/profile или non-Opus evidence —
  назови точную границу и stop без substitution.
- Invalid path или permission исправляй только в прежнем approved scope.
- Busy/missing lease обрабатывай только на exact native ID: observe либо
  `open_resume` с известными `cwd`, новым prompt и affirmative Opus evidence.
- Timeout, cancellation, `max_turns`, malformed или non-terminal output не
  применяй; продолжение допустимо только при typed resumability и оправданном
  следующем turn.
- Если точная recovery не закрывает границу, назови failed layer, packet evidence
  и одно следующее действие владельца или системы.
