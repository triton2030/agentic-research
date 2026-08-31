# Fresh Opus One-shot

Вход: задача требует одного независимого Opus opinion/review, а brief уже
следует целям из тела скила. Выход: один terminal Opus result либо typed failure.

1. Подготовь реальный project/worktree `cwd` и prompt. Если outcome зависит от
   custom skill, MCP или named capability, включи её exact owner/address в
   `Context`: clean launch не загружает её автоматически.
2. Когда это материально, откалибруй visible length, progress cadence,
   deliverable size, narrow scope и stop; не добавляй generic double-check,
   verifier-subagent или automatic fan-out.
3. До dispatch следуй host approval: `claude_ask` отправляет Anthropic prompt и
   прочитанные материалы, а clean launch не является local sandbox.
4. Вызови `mcp__claude_mcp__claude_ask` ровно один раз с
   `profile: opus_advisor`, реальным `cwd` и без `session_id`. Оставь default
   `xhigh`; `max` выбирай только для оправданного свежего вызова.
5. Прими только terminal `structuredContent`: прочитай `text`, `session_id`,
   `requested_model`, `requested_effort`, `resolved_model` и `warnings`; отклони
   result без непустого `text`, `requested_model: opus` или
   `resolved_model`, начинающегося с `claude-opus-5`.
6. Проверь только используемые claims по task evidence и представь результат
   как мнение Opus; Codex владеет синтезом и финальным ответом.
