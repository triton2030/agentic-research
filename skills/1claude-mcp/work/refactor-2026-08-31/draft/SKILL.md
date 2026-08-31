---
name: 1claude-mcp
description: >-
  Use when work needs a Claude/Opus or unspecified-model opinion/review, an
  Opus-only boundary for non-Opus Claude, or inspection/control of a Claude
  session. Not for Claude facts or Gemini/Hermes.
---

# Claude Opus Advisor

## Уникальный Контекст

Opus — независимый советник. Подключай его потому, что уже можешь быть связан
собственными допущениями и выбранным маршрутом. Его ценность не в подтверждении
твоей позиции, а в самостоятельном профессиональном суждении, способном
изменить решение или результат. Clean launch не наследует инструкции проекта,
но Opus может читать релевантные материалы. Ты проверяешь claims и отвечаешь
владельцу.

## Твоя задача

Для advice/review получи от Opus полное разрешение исследовательского вопроса
либо содержательный review результата с достаточным контекстом и материалами.
Если владелец просит только inspection/control Claude session, выполни ровно
эту операцию.

## Твоя цель

Advice/review завершён законченным независимым заключением Opus: ясно, какое
решение лучше всего служит верхнеуровневой цели владельца, почему именно оно и
какие существенные риски или неизвестные способны его изменить. Используемые
claims проверены тобой. Inspection/control завершён его typed result.

## Маршрут

- Перед новым one-shot или управляемым advisor прочитай
  [prepare-advisor.md](references/prepare-advisor.md).
- Готовый blocking one-shot без полезной независимой работы выполни по
  [fresh-one-shot.md](references/fresh-one-shot.md).
- Готовый one-shot параллельно с полезной работой выполни по
  [parallel-one-shot.md](references/parallel-one-shot.md).
- Raw one-shot packet прими или отклони по
  [accept-one-shot.md](references/accept-one-shot.md).
- Новую управляемую консультацию открой по
  [session-open.md](references/session-open.md).
- Действие над live Opus session выполни по
  [session-action.md](references/session-action.md).
- Status/liveness либо ожидаемый содержательный ответ получи по
  [session-observe.md](references/session-observe.md).
- Список или видимую переписку active Claude sessions прочитай по
  [existing-sessions.md](references/existing-sessions.md).
- Session-specific typed failure обработай по
  [session-recovery.md](references/session-recovery.md).
- Typed failure обработай по [failure-recovery.md](references/failure-recovery.md).

## Стоп

Содержательный маршрут завершён только на validated Opus result и локальной
проверке используемых claims; явно запрошенное control/inspection action — на
его typed result. Не выводи завершённость из non-terminal evidence и не
подменяй отсутствующее мнение Opus выводом Codex.
