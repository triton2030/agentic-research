# Кнопка запуска 1claude-mcp

## Имя

`1claude-mcp` сохраняется. Корпус не содержит решения владельца о переименовании
в `1opus` или `1opus-advisor`; устойчивое употребление связывает существующее
имя с Claude/Opus advisor. Миграция имени не требуется для исправления trigger.

## Description — 195 символов

> Use when work needs a Claude/Opus or unspecified-model opinion/review, an Opus-only boundary for non-Opus Claude, or inspection/control of a Claude session. Not for Claude facts or Gemini/Hermes.

## Trigger probes

| Фраза | Решение |
| --- | --- |
| «Попроси Opus посмотреть архитектуру» | use |
| «Что нового в Claude Opus 5?» | skip |
| «Дай второе мнение Gemini» | neighbor: `1gemini` |
| «Продолжи ту Claude-сессию» | use |
| «Запусти Fable» | use для явной Opus-only границы |
| «Спроси другую модель, что она думает» | use через Opus |
| «Продолжи эту Sonnet-сессию как советника» | use для Opus-only stop |
| «Покажи активные Claude-сессии» | use для read-only inspection |

Trigger не является поздним: наблюдаемый запрос к модельному мнению или session
control присутствует до выбора скила, поэтому повторная проверка mid-trajectory
не нужна.
