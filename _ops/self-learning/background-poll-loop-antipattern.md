# Background poll-loop antipattern

## Observation

Когда нужно подождать long-running background job (LLM corpus profile, build, deploy), я запускаю `until ! pgrep ...; do sleep 5; done` shell loop. Пользователь прерывает через несколько минут — UX неприятный (chat "застрял", непонятно что происходит, прерывание выглядит как отказ).

Прямая инструкция из system prompt:
> «If waiting for a background task you started with `run_in_background`, you will be notified — do not poll. Long leading sleep commands are blocked.»

То есть **архитектура harness уже даёт notification** на background completion. Poll loop — это **дублирование уже существующей механики**, плюс блокирует chat, плюс выглядит как hang.

## Counter

- 2026-05-21 [Claude Opus 4.7]: сессия про md-tools refactor verification. Запустил `profile-sections --mode llm --force` в background через Bash (`run_in_background: true`). Потом сделал отдельный `until ! pgrep ...; do sleep 5; done` чтобы подождать finish. Пользователь прервал на 30 секунде. Через 5 минут попробовал снова в другом синтаксисе — пользователь снова прервал, сказав «опять застряли». Только после **второго** прерывания понял что должен был просто **продолжать другую работу** — notification придёт автоматически.

## Possible upgrade

**ВСЕГДА** для long-running background job:
1. Запустить через `Bash` с `run_in_background: true`
2. **НЕ запускать poll loop** в follow-up
3. Continue к другой полезной работе (не блокированной этим job)
4. Когда придёт system notification (task-id + status), use Read на output file
5. Если другой работы нет — просто закончить ход и подождать notification в следующем сообщении пользователя

Detection rule: если я collapse'ю в «нужно подождать пока завершится X» — это сигнал что хочу запустить poll. STOP. `run_in_background` + continue. Notification — не запрос; это **сам механизм синхронизации**.

Related: poll loops также anti-pattern по causes контекстных issues — burn cache tokens на repeat-shell-launch overhead.
