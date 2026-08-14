---
name: 1claude-mcp
description: >-
  Когда пользователь просит Claude, Opus или Fable, мнение другой model family
  либо работу с уже запущенной Claude session — подключи Opus advisor. Не для
  справочных вопросов о Claude; native Codex review → `1fresh-eyes`.
---

# Claude Advisor

## Результат

Получить компактное, проверяемое мнение Claude перед работой, параллельно с ней
или как ревью результата. Для одного ответа по умолчанию используй blocking
`claude_ask`; transient session остаётся opt-in для параллельной работы и
follow-up. Codex владеет scope, проверкой, синтезом и ответом пользователю;
Claude советует, но не принимает результат.

## Основной Маршрут

1. Используй только `opus_advisor` (`claude-opus-5`). Если запрос назвал
   Fable, до вызова назови Opus-only границу и маршрутизируй работу в Opus,
   не подменяя модель молча.
2. Передай реальный project/worktree `cwd` и короткий самодостаточный brief:
   цель и проблему; текущее состояние; известные owner-файлы и URLs, а если
   точного адреса нет — корень исследования; существенные границы; критерий
   успеха и evidence; форму и длину ответа. Описывай необходимый результат, а
   не шаги: Claude сам выбирает дополнительные файлы, инструменты и подход. Не
   копируй сырой chat dump.
3. Оставь `xhigh`; выбери `effort: max` только для свежего вызова, когда цена
   решения оправдывает более долгую максимально глубокую работу.
4. Вызови один blocking `claude_ask`. Он может работать несколько минут;
   продолжай тот же host call, не запускай polling или параллельный повтор.
5. Прочитай `requested_model`, `requested_effort`, `resolved_model`, `warnings`
   и `session_id`. `unsupported_profile` или `unsupported_model` — fail-closed:
   не повторяй через Fable и не выдавай вызов за завершённый. `warnings` может
   компактно показать нативный model-refusal fallback, subscription
   overage/credits или имя отклонённого инструмента, но не его arguments/output.
6. Проверь существенные утверждения локально и представь ответ как мнение
   Claude, а не как собственный доказанный вывод.

## Внешние Данные И Оплата

`claude_ask` отправляет в Anthropic переданный prompt и прочитанные материалы.
Следуй host approval; не обходи его, но и не изобретай дополнительный запрет на
локальные файлы и файлы проекта после разрешения scope.

Инструкция исследовать и не изменять состояние — поведенческая, а не read-only
sandbox.

Не подставляй API key/token/provider/base URL ради восстановления. При auth или
billing ошибке читай единственный owner-файл
[`subscription-billing.md`](/Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/docs/subscription-billing.md)
— не загружай его в обычный advisor call.

## Условные Маршруты

- Когда качество Opus review зависит от роли, sources или формы ответа:
  [opus-agent-prompting.md](references/opus-agent-prompting.md).
- Конкретный Claude `Skill`, MCP capability, subagent, monitor или workflow:
  [claude-native-tools.md](references/claude-native-tools.md).
- Совет фоном, пока Codex продолжает работу; продолжение по `session_id`,
  follow-up, steer, проверка живости или stop:
  [session-adapter.md](references/session-adapter.md).
- Необязательный read-only список активных локальных Claude sessions или чтение
  видимой переписки известной active session:
  [existing-sessions.md](references/existing-sessions.md).
- Tool missing/stale, approval, auth, malformed output или cancellation:
  [mcp-failure-handling.md](references/mcp-failure-handling.md).

## Стоп

Остановись после bounded terminal result и локальной проверки существенных
утверждений. Закрой transient session, когда follow-up больше не нужен. Не
объявляй Claude review выполненным по progress snapshot без terminal result.
