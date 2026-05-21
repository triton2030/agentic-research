# MCP Transport Vs Agent Tail

## Observation

Модель и субагенты смешали два разных хвоста: внешний агентский процесс
(`agy`, `gemini`, `claude`, `tmux`) и долгоживущий `node .../src/server.js`,
который Codex app-server держит как stdio MCP transport. Из-за этого рабочий
Gemini MCP несколько раз получал fail на cleanup, хотя модельный запуск уже
закончился.

## Counter

- 2026-05-20 [GPT-5.5]: при переводе `gemini-mcp` на Antigravity CLI финальные
  аудиторы подтвердили Gemini 3.5 Flash, чтение, web, запись и safety gate, но
  считали `node .../experiments/gemini-mcp/src/server.js` под Codex app-server
  runaway tail. Пришлось уточнить contract: проверять `agy`/legacy `gemini`/
  `tmux`; Codex-held MCP server — active tool transport.
- 2026-05-20 [GPT-5.5]: при обновлении Claude Bridge тот же риск повторился
  уже на `claude-bridge`: `ps` показывал несколько `server.js` под Codex
  app-server, но живых `claude` model-run процессов не было. Урок закреплён в
  `claude-mcp` skill/reference и README: tail check должен искать внешний
  модельный процесс, а не убивать transport.
- 2026-05-20 [GPT-5.5]: при одновременном bug hunt через Claude/Gemini MCP
  старый tool transport вернул `Transport closed`, а ручной `pkill server.js`
  не восстановил callable tools в текущем окне. Следующий раз сначала
  различать: чиню live MCP transport или сразу иду в repo runner fallback;
  не тратить круги на перезапуск stdio tools, если Codex already cached them.

## Possible upgrade

В acceptance briefs для MCP сразу разделять: **model/run tails** запрещены,
**tool transport processes** допустимы, если parent — Codex app-server. Перед
fail по `node server.js` смотреть parent command и активный transport context.
