---
name: 1claude-mcp
description: >-
  Use when invoking Claude/Opus/Fable for research, review, coding or another
  task, seeking an unspecified-model second opinion, or inspecting and
  controlling Claude sessions. Provides model,
  prompting and tool knowledge; not general Claude product support.
---

# Claude

Мост подключает Claude Code через Claude.ai-подписку. Claude получает штатный
системный промпт и native tools; роль, результат и допустимые изменения задаёт
переданный запрос. Поэтому один и тот же инструмент подходит для независимого
мнения, исследования, работы с документами и исполнения кода.

Этот скил сообщает особенности подключения и моделей. Выбор функций,
организация работы и проверка результата остаются у вызывающего агента.

## Выбор модели

Предпочтения владельца применяются в порядке таблицы; явный выбор для
конкретного вызова имеет приоритет.

| Когда | Модель | Параметры свежего вызова |
| --- | --- | --- |
| Умная или важная работа, включая документы и код | Fable 5.1 Medium | `profile: fable_advisor`, `effort: medium` |
| Работа с кодом | Opus 5 Max | `profile: opus_advisor`, `effort: max` |
| Документы и остальные случаи по умолчанию | Opus 5 High | `profile: opus_advisor`, `effort: high` |

`claude-opus-5-high` — модель `claude-opus-5` с отдельным `effort: high`.
Fable закреплён на `claude-fable-5-1`. Имена профилей с суффиксом `_advisor`
сохранены для совместимости: профиль выбирает модель, а не роль.

## Знание по ситуации

| Когда сведения нужны | Где они находятся |
| --- | --- |
| Составляешь запрос Claude: исполнение, исследование или независимое мнение | [Особенности промптов](references/prompting.md) |
| Выбираешь one-shot, несколько параллельных Claude-агентов, продолжение, управление или просмотр сессий | [Инструменты и сессии](references/tools-and-sessions.md) |
| Разбираешь результат, обрезку, ожидание, ошибку или несовпадение модели | [Результаты и ограничения](references/results-and-recovery.md) |
| Задаче нужны дополнительные возможности Claude Code или SDK | [Native-возможности](references/native-capabilities.md) |

Свежий процесс не подхватывает пользовательские и проектные инструкции,
скилы, hooks, MCP и auto-memory автоматически. `cwd` и файлы доступны Claude:
нужные правила проекта и материалы можно передать адресами в запросе.
Продолжение сохраняет разговор native session. Вызов может менять файлы и
внешнее состояние; read-only характер исследования задаётся конкретной задачей.
