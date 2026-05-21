---
description: Tool surface и tool descriptions у агента — почему меньше инструментов лучше, и какой description реально триггерит правильно.
---

# Agents — Tool Design

Снимок на 20 мая 2026. Снято с `wisdom-agents.md` при function-split refactor.

Здесь принципы про дизайн tool surface агента: размер, описание, fallback
на базовые примитивы. Runtime-слой и anti-loop — `runtime-layer.md`.
Skill authoring canon — `knowledge/practical-guides/how-to-write-skills/`.

## Проверено

- Активный набор инструментов должен быть маленьким и управляемым. Избыточный tool set повышает шум, drift и число ошибочных ходов.
- Tool surface: радикальное сокращение (классический кейс — 17 узких инструментов → 2 примитива над файловой системой) обычно повышает качество выбора. Перед добавлением tool в скилл — проверить, не делается ли это уже базовыми примитивами.
- Tool description (frontmatter скилла, MCP tool) валиден, если отвечает на 4 вопроса: что делает, когда применять, что вернёт, чем отличается от соседнего. Без этого триггеры конфликтуют.
- Для большого tool surface использовать narrow descriptions и tool search / deferred discovery, а не грузить весь каталог в основной контекст. Model-specific детали — `knowledge/wisdom-gpt-5.5.md`, `knowledge/wisdom-claude-opus-4.7.md`.

## Опоры

- https://developers.openai.com/api/docs/guides/structured-outputs
  Schema-constrained outputs как форма контракта инструмента.

- `/knowledge/practical-guides/how-to-write-skills/authoring-canon.md`
  Authoring canon для skill description и triggering surface.
