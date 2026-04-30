# Gemini MCP Control Criteria

## Зона ответственности

Когда работа проектирует, настраивает или проверяет использование Gemini через
MCP, Codex skill, модельный default, reasoning/thinking controls или
prompt-reference для Gemini.

## Цель

Gemini в этом проекте должен работать как управляемый MCP-направление рядом с
`claude-mcp`: с актуальной сильной моделью, максимальным reasoning и
model-specific подсказками по промптингу.

## Критерии

Rule: Gemini MCP по умолчанию должен использовать `gemini-3.1-pro-preview`.
Why: Пользователь прямо задал Gemini 3.1 как рабочую модель для этого направления.

Rule: Gemini MCP по умолчанию должен включать максимальный доступный reasoning/thinking режим для этой модели.
Why: Пользователь прямо попросил самый мощный reasoning, а не быстрый или дешёвый режим.

Rule: Для Gemini должен существовать отдельный installed Codex skill `gemini-mcp`, сопоставимый по назначению с `claude-mcp`.
Why: Пользователь хочет вызывать Gemini через такой же явный skill-контракт, а не через разовый кодовый прототип.

Rule: `gemini-mcp` skill должен иметь reference-файл с лучшими prompting techniques именно для выбранной Gemini-модели.
Why: Пользователь попросил model-specific справку, чтобы будущие промпты не опирались на общий или устаревший Gemini-канон.

Rule: Отсутствие `GEMINI_API_KEY` / `GOOGLE_API_KEY` само по себе не считается поломкой Gemini MCP.
Why: Пользователь прямо поправил, что Gemini не должен спрашивать только ключ; будущая проверка должна различать API key, Vertex AI/ADC и явно выбранный локальный Gemini CLI backend.
