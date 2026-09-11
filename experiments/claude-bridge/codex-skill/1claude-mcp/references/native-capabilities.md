# Дополнительные возможности Claude

Этот справочник нужен, когда задаче тесно в обычном one-shot или текущем
наборе MCP-операций. Наличие функции в Claude SDK не означает, что одноимённое
поле принимает MCP: точный доступ проверяется по callable schema или API
установленного SDK. Список ниже не является ограничением доступных функций.

## Что уже доступно через мост

Claude использует штатный набор локальных tools: читает и изменяет файлы,
исполняет команды, исследует материалы и может пользоваться встроенными
субагентами. Конкретный набор зависит от Claude Code и модели. Native history,
resume, follow-up, steer, stop и параллельные отдельные разговоры поддержаны
операциями из [справочника моста](tools-and-sessions.md).

Clean launch отключает автоматическую загрузку локальных settings, skills,
hooks, MCP и auto-memory. Это характеристика текущего подключения, а не
утверждение, что эти возможности отсутствуют у Claude.

## Когда полезны native API вне текущей MCP-схемы

Проверено по Claude Agent SDK 0.3.268 / Claude Code 2.1.268, 2026-09-12.

| Возможность | Когда полезна | Native API и существенная особенность |
| --- | --- | --- |
| Каталог моделей и effort | Появилась новая модель или неизвестна доступность в аккаунте | `Query.supportedModels()`: aliases, `resolvedModel`, поддерживаемые effort; доступность строки не заменяет успешный model call |
| Заполнение контекста | Длинная работа, выбор продолжения или нового разговора | `Query.getContextUsage({detail: 'summary'})` получает usage и локальные оценки без per-category token-count API calls; `full` делает дополнительный подсчёт |
| Смена модели и effort | Другой этап той же работы требует другой модели | `Query.setModel()` и `applyFlagSettings({effortLevel: ...})`; смена сохраняет разговор, поэтому не создаёт независимое мнение |
| Fork | Нужно исследовать альтернативу из той же истории | `forkSession()` или `forkSession` при resume; native SDK владеет копированием и новым ID |
| Структурированный ответ | Результат потребляет программа | `outputFormat` с JSON Schema; форматирование имеет собственные ошибки/retry limits |
| File checkpointing | Задача предполагает редактирование с возможностью отката | `enableFileCheckpointing` + `rewindFiles()`; это откат отслеженных файлов, не транзакция внешних действий |
| Подробности лимитов | Нужно различить плановые окна и текущую нагрузку | `usage_EXPERIMENTAL_MAY_CHANGE_DO_NOT_RELY_ON_THIS_API_YET({skipBehaviors:true})`; API явно нестабилен, версия существенна |
| Hooks, MCP, skills и subagents | Нужна конкретная интеграция или специализация | Native SDK options подключают их к сессии; текущий clean MCP-маршрут не принимает произвольные SDK options |
| Управление отдельной фоновой задачей | Требуется остановить подзадачу, сохранив основную сессию | `Query.stopTask(taskId)`; общее `stop` моста закрывает весь lease |

Native API применяются через доступный SDK/CLI, когда выбран такой способ
решения; расширение MCP нужно только если задача требует именно этого
интерфейса. Установка иной схемы или изменение global configuration — отдельное
действие, не эффект чтения справочника.

## Источники

- [TypeScript SDK](https://code.claude.com/docs/en/agent-sdk/typescript) и
  `sdk.d.ts` установленной версии — точные API и ограничения.
- [Changelog SDK](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md) — изменения поведения по версиям.
- [Модели и effort](https://code.claude.com/docs/en/model-config) — доступность,
  aliases, большой контекст и fallback.
- [Системные промпты](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts) — штатный preset, custom prompt и загрузка проекта.
