---
description: State, cost and side-effect model for md-tools-v2.
depends-on:
- '[[architecture-boundaries.md]]'
---
# State And Cost Model

v2 должна явно различать чтение, ленивую запись, стоимость и разрушительные
действия. Иначе агенты будут видеть одинаковые tools, но не будут понимать
риск.

## Категории Действий

| Категория | Пример | Требование |
|---|---|---|
| read-only | map, toc, extract, check existing graph | не пишет файлы, index или reports |
| lazy-write | search with small auto-embed, audit report, profile cache | явно объявляет side effect |
| cost-bearing | embedding, rerank, LLM profile | dry-run or visible estimate where possible |
| mutating | init, strip | `dry_run` first, `confirm` for live run |
| destructive | remove fields, remove sections | explicit confirm and affected files list |

## State Surfaces

- Markdown source files.
- `.md-navigator/` index and generated reports.
- SQLite schema and migrations.
- Embedding model metadata.
- Profile cache.
- API key lookup.
- MCP tool registry.

## Не Решено

- Нужно ли v2 читать старые `.md-navigator/index.sqlite`.
- Как хранить generated reports, если audit станет optional layer.
- Какие operations должны быть unavailable через MCP и доступны только CLI.
