---
description: Public capability contract for md-tools-v2 before implementation.
depends-on:
- '[[jobs-and-moments.md]]'
- '[[current-skill-usage-map.md]]'
- '[[full-functionality-contract.md]]'
---
# Public Capability Contract

v2 не должна требовать переписывания скилов. Значит текущие public tool names,
ключевые args, output families и cost/safety semantics считаются
compatibility contract.

Новый design может быть чище внутри, но снаружи должен быть совместимым.

## Начальные Capability Группы

| Capability | Назначение | Возможные backend primitives |
|---|---|---|
| `orient` | Быстро понять Markdown-папку | map, status, importance |
| `search` | Найти смысловую секцию или файл | index, BM25, dense, rerank, extract |
| `read-context` | Собрать контекст вокруг файла/секции | read, extract, related |
| `edit-context` | Подготовить правку `.md` | preflight, related, semantic radius |
| `graph-check` | Проверить graph/schema/link health | check, scan, cycles, deps, impact |
| `audit` | Найти IA-проблемы корпуса | overlaps, repeated concepts, clusters (`md_cluster` when standalone) |
| `admin` | Управлять index/profile/frontmatter state | index, status, init, strip, profile |

## Правило

Backend primitive может быть отдельной функцией, но не обязан быть публичным
MCP tool. Публичным становится только то, что нужно агенту как самостоятельный
рабочий выбор.

Для v2 это правило применяется к новым внутренностям. Уже существующие public
`md_*` tools сначала сохраняются или получают compatibility alias.

## Не Решено

- Какие outputs являются строгим compatibility contract.
- Какие CLI fallback commands должны остаться по старым именам.
- Какой минимальный link switch нужен: MCP server path, env vars or shim.
