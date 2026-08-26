---
name: 1claude-mcp
description: >-
  Use when the user asks for Claude, Opus, Fable, an unnamed other-model-family
  view, or an existing Claude session. Not for Claude facts; route Gemini and
  Hermes to their own skills.
---

# Claude Advisor

## Результат

Получить компактное, проверяемое мнение Claude перед работой, параллельно с ней
или как ревью результата. Для одного ответа по умолчанию используй
`claude_ask`: напрямую, когда до ответа нет полезной независимой работы, или
через yielded one-answer route ниже, когда она есть. Transient session остаётся
opt-in только для follow-up, mid-turn correction, progress, liveness или
explicit stop. Codex владеет scope, проверкой, синтезом и ответом пользователю;
Claude советует, но не принимает результат.

## Основной Маршрут

1. Используй только `opus_advisor` (`claude-opus-5`). Если запрос назвал
   Fable, до вызова назови Opus-only границу и маршрутизируй работу в Opus,
   не подменяя модель молча.
2. Передай реальный project/worktree `cwd` и полную спецификацию задачи upfront
   как самодостаточный XML-brief. Каждый prompt обязательно содержит `<goal>` — желаемое
   верхнеуровневое конечное состояние и зачем оно нужно, не локальную операцию;
   `<context>` — текущую сцену, состояние, известные owner-файлы/URLs, evidence
   и существенные gaps; и `<task>` — конкретный требуемый результат. Добавляй
   `<constraints>`, `<success_criteria>` и `<output>` только когда в них есть
   материальное содержание; пустые секции запрещены.
   Во всём brief допускается не больше десяти самостоятельно исполнимых
   обязательств: действий, ограничений, границ и правил вывода вместе; заголовки
   и фактический контекст не считаются. Если кандидатов больше, оставь десять
   наиболее важных для верхнеуровневой цели и observable done; veto-class
   границы важнее частых, но дешёвых деталей. Описывай outcome, не маршрут:
   Claude сам выбирает дополнительные файлы, инструменты и подход; не копируй
   сырой chat dump или instruction stack.
3. Оставь `xhigh`; выбери `effort: max` только для свежего вызова, когда цена
   решения оправдывает более долгую максимально глубокую работу.
4. Вызови один `claude_ask`. Для независимого совета не передавай `session_id`;
   resume используй только как сознательное продолжение уже выбранного советника.
   Для yielded one-answer route запусти Promise того
   же вызова внутри одной `functions.exec` cell: сначала верни короткую запись
   `family: claude, phase: started`, затем вызови `yield_control()` и дождись
   Promise внутри cell. Каждая yielded cell вызывает ровно один финальный
   `notify()`: returned `CallToolResult` сохраняется под task-scoped
   `result_ref`, а уведомление несёт только `bridge: returned` и opaque-ссылку.
   После wake загрузи результат и примени действующий failure/result contract.
   Пойманный отказ cell или transport до returned result сохраняет diagnostic
   под `failure_ref` и уведомляет `observer: failed`, `bridge: unknown`,
   `external: unknown`; автоматический повтор запрещён. Это прямой внешний
   вызов, не нативный Codex-субагент. Не запускай polling, параллельный повтор
   или transient session только ради фона.
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
- Продолжение по `session_id`, follow-up, steer, user-visible progress, проверка
  живости или stop:
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
