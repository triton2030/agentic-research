---
name: 1claude-mcp
description: >-
  Use when work needs a Claude/Opus or unspecified-model opinion/review, an
  Opus-only boundary for non-Opus Claude, or inspection/control of a Claude
  session. Not for Claude facts or Gemini/Hermes.
---

# Claude Opus Advisor

## Уникальный контекст

Для владельца Claude/Opus — советник или ревьюер до работы, параллельно с ней
и после неё. Он запускается максимально чистым, без автоматически подмешанных
глобальных, project и local инструкций, но вправе сам читать нужные файлы.
Prompt строится от верхнеуровневой цели, контекста и проблемы, а не указывает
модели, как думать.

## Цели владельца

- Мнение Opus появляется до закрытия решения или как независимый review
  результата; позднее подтверждение уже принятого вывода и выдача совета за
  доказанный факт успехом не считаются.
- Opus получает достаточный task context и доступ к нужным файлам, сохраняя
  независимость clean launch; загрузка всего instruction stack или искусственный
  запрет читать релевантные источники успехом не считаются.
- Brief содержит верхнеуровневую цель и контекст, выбирает не более десяти
  важнейших ограничений или границ и оставляет Opus выбор способа работы;
  процедурное управление мышлением успехом не считается.

## Маршрут

- Перед первым Opus advice/review в задаче прочитай
  [owner-protocol.md](references/owner-protocol.md).
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
