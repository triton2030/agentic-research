# Claude Failure Recovery

Вход: фактический typed error/result packet. Выход: одна допустимая recovery
action либо честный stop с failed layer и evidence.

- Tool или schema отсутствуют/stale — сохрани diagnosis, остановись и предложи
  владельцу повторить из свежей Codex task; сам task не создавай.
- External-data approval отклонён — назови, что не было отправлено; повторяй
  только после явного открытия scope владельцем.
- Auth или billing failure — сохрани subscription-only route, сообщи typed
  failure и stop; не подставляй credential, provider, base URL или model alias.
- Unsupported profile/model или non-Opus `resolved_model` — stop без fallback и
  без заявления, что review завершён.
- Invalid path — назови exact input/OS denial и исправляй только в прежнем scope.
- Invalid session или missing lease — `open_resume` допустим только с известными
  native `session_id`, `cwd`, новым prompt и affirmative Opus evidence.
- Native tool permission denial — используй typed tool-name warning и запроси
  разрешённую альтернативу либо stop; не auto-approve.
- Busy/capacity — observe или stop exact lease; второй identity запрещён.
- Timeout, cancellation, SDK failure или session-appending turn — сохрани typed
  code и не повторяй автоматически.
- Resumable `max_turns` продолжай только когда ещё один turn оправдан задачей;
  не скрывай failure повышением лимита.
- Malformed, truncated или non-terminal output не применяй и не называй
  завершённым мнением Opus.
- Если exact recovery оставляет ту же границу, остановись и назови failed layer,
  packet evidence и одно следующее действие владельца или системы.
