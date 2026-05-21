# Observable Trace Not Chain Of Thought

## Observation

Пользователь хочет видеть, что делают долгие внешние агенты: какие инструменты
они вызывают, какие файлы читают, где застряли и когда их стоит остановить.
Фраза "ход мышления" в таком контексте означает operational visibility, а не
запрос на приватную chain-of-thought.

## Counter

- 2026-05-20 [GPT-5.5]: во время cross-review Claude/Gemini MCP пользователь
  уточнил, что для часовых задач надо видеть trajectory и tool use, чтобы
  остановить или проверить направление. Правильная реализация — `activity`,
  `observe`, logs, tool/file trace, cursor и kill hint; не пытаться показывать
  внутренние рассуждения модели.

## Possible Upgrade

Когда пользователь просит "видеть ход мыслей" у агента/tool-run, отвечать
через observable trace: visible updates, tool calls, files, commands, logs,
warnings, elapsed time, stop control. Явно отделять это от private reasoning.
