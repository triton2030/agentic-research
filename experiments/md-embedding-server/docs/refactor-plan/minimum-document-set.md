---
description: Minimum documentation set required before building a complex Markdown
  tools backend.
depends-on:
- '[[README.md]]'
---
# Минимальный Набор Документов

Сложное программное решение нельзя начинать с файлов кода, если оно уже
обслуживает несколько скилов, runtime-поверхностей и режимов риска. Перед
реализацией v2 нужен минимум документов ниже.

## 1. Usage Map

Файл: `current-skill-usage-map.md`.

Задача: показать, где текущие `md_*` возможности используются в Codex и
Claude skills. Это защищает от ложного вывода "функция редко нужна, значит
лишняя".

Готово, когда у каждой публичной возможности есть один из статусов:
`used by skill`, `internal only`, `compatibility only`, `delete candidate`.

## 2. Full Functionality Contract

Файл: `full-functionality-contract.md`.

Задача: описать весь функционал, который текущие skills ожидают от backend,
MCP tools и CLI fallback. Это главный контракт v2: скилы не переписываются,
меняется код и backend-ссылка.

Готово, когда каждая текущая `md_*` возможность имеет назначение, потребителей,
side effects, compatibility requirement and validation gate.

## 3. Jobs And Moments

Файл: `jobs-and-moments.md`.

Задача: описать рабочие моменты агента: найти смысл, выбрать файл, проверить
граф, оценить дубли, понять радиус правки, закрыть работу.

Готово, когда каждая возможность связана не с названием команды, а с моментом
работы и риском, который она закрывает.

## 4. Public Capability Contract

Файл: `public-capability-contract.md`.

Задача: определить публичный язык v2. Capability не равна внутренней функции.
Один public tool может оркестрировать несколько backend primitives.

Готово, когда публичная поверхность объясняется через намерения скилов, а не
через структуру модулей.

## 5. Architecture Boundaries

Файл: `architecture-boundaries.md`.

Задача: разделить ядро и расширения:

- Markdown parsing and section model;
- index and search;
- graph obligations;
- audit and IA probes;
- profile/classification;
- MCP adapter;
- CLI/debug/admin.

Готово, когда понятно, где живёт состояние, кто владеет side effects и что не
может импортировать что.

## 6. State And Cost Model

Файл: `state-and-cost-model.md`.

Задача: описать `.md-navigator/`, SQLite, embedding model, API keys,
OpenRouter calls, profile cache, generated reports, dry-run and confirm
guards.

Готово, когда каждое действие помечено как read-only, lazy-write, mutating,
cost-bearing или destructive.

## 7. Compatibility And Migration

Файл: `compatibility-and-migration.md`.

Задача: зафиксировать, что нельзя сломать при v2:

- installed Codex/Claude skills;
- MCP tool names or compatibility aliases;
- output shapes, где на них завязаны скилы;
- exit codes and error classes;
- old indexes and migration behavior.

Готово, когда есть explicit compatibility matrix: keep, alias, replace,
remove with migration.

## 8. Validation And Release Gates

Файл: `validation-and-release-gates.md`.

Задача: определить, какие проверки доказывают готовность v2.

Минимальные gate-классы:

- unit tests for parser/search/graph primitives;
- contract tests for public capabilities;
- smoke tests through MCP;
- compatibility replay against current skill workflows;
- fixture corpus tests for Russian and English Markdown;
- failure-mode tests for missing key, stale index, broken links and
  confirm-required mutations.

Готово, когда v2 можно сравнить с текущим backend по наблюдаемому поведению.

## 9. Decision Log

Файл: `decision-log.md`.

Задача: хранить только решения, которые меняют контракт, границу или
миграционный путь.

Готово, когда будущий агент видит, почему v2 устроена так, а не просто что
было сделано.
