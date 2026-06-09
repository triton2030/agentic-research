---
description: Decision log for md-tools-v2 architecture and compatibility choices.
depends-on:
- '[[minimum-document-set.md]]'
- '[[compatibility-and-migration.md]]'
---
# Decision Log

Здесь фиксируются только решения, которые меняют архитектурную границу,
публичный контракт или миграционный путь.

## D-001 - Начать v2 с docs-first папки

Дата: 2026-05-22.

Решение: создать отдельную папку `experiments/md-tools-v2/` и сначала описать
минимальный набор документов для разработки сложного Markdown tools backend.

Причина: текущие `md_*` функции реально используются разными скилами в разных
моментах. Задача v2 - не удалить функции, а спроектировать более ясную систему
возможностей, границ, состояния и совместимости.

Следствие: код v2 не пишется, пока docs не закрывают usage map, jobs,
public capability contract, architecture boundaries, state/cost,
compatibility and validation gates.

## D-002 - Не переписывать skills как часть v2

Дата: 2026-05-22.

Решение: v2 переписывает backend-код так, чтобы текущие Codex/Claude skills
продолжили работать. Миграция должна сводиться к замене backend-ссылки,
MCP registration path, env vars or compatibility shim.

Причина: текущие skills используют `md_*` инструменты в разных рабочих
моментах. Переписывание skills смешает две задачи: улучшение backend
архитектуры и изменение agent workflows.

Следствие: перед кодом нужен `full-functionality-contract.md`, который
описывает весь функционал, ожидаемый текущими skills.

## D-003 - Приоритетная совместимость navigator / graph / strategy

Дата: 2026-05-22.

Решение: `1md-navigator`, `1md-graph` и `1strategy` являются priority
consumers v2. Их привычные workflows должны работать после замены backend
ссылки без правки skill bodies.

Причина: эти три скила задают основные способы использования Markdown tools:
navigation/search, graph evidence and strategy ground-check. Если они требуют
переучивания, v2 не является совместимой заменой.

Следствие: validation gates должны включать отдельный replay для этих трёх
скилов до любого runtime switch.

## D-004 - Agent feedback class 2026-05-23: probe-first, без четвёртого contract document

Дата: 2026-05-23.

Решение: отвергли создание нового `docs/llm-cli-contract.md` с 7 правилами
(stream / budget / projection / schema / confirm / naming / default brief);
приняли расширение существующих owner-surfaces (`cli-conventions.md`,
`schemas.py`, `architecture-lock.md`) + bilateral mention в SKILL.md обоих
skills + cross-project hygiene fixes. Probe-first вместо spec-first.

Причина: внешний агент дал 7 жалоб на md-tools UX/API плюс 4 жалобы на
discipline gaps. Independent critics (developer / architecture / trajectory)
указали три риска первоначального плана: (а) `ownership_leak` с существующими
contract surfaces (`cli-conventions.md` владеет CLI shape, `schemas.py`
владеет JSON shape, `architecture-lock.md` владеет boundary invariants);
(б) `method_as_goal` — 7 точек данных компактуются в spec до того, как
probe подтвердил наличие класса; (в) compliance harness c xfail-списком
становится cargo-cult и Hyrum-контрактом одновременно.

Probe-первый показал, что три жалобы из семи не bug:
жалоба «stderr leak в stdout» = harness artifact (caller мерджит
дескрипторы; `embeddings.py:105` уже `file=sys.stderr`); жалоба «mixed
int/list types in md health» = schema misunderstanding (counter vs list of
objects — два разных поля по природе); жалоба «old changed-file helper showed
4 vs 11» = discoverability gap (default-excludes silently dropped `_archive/` и
`runs/`, contract правильный, но не документирован в `--help`). Это
сильный сигнал, что **discoverability ценнее compliance enforcement**:
fix через `--help`, SKILL.md recipe и docstrings, не через новый
contract document.

Следствие: закрыты конкретные bugs и UX issues без widening canon:
sentinel-before-apply (finding #18) — `restore_transaction_claim` в
`transactions.py`, exit-code-aware finish в `_generic.py:138-140`;
`cycles_count: int` additive в `health_report` для UX однородности с
counter-полями; default-excludes были документированы в help старого helper;
`envelope.derive_next_step` выдаёт narrowing `next_step` для large reply
(лечит #4/#6/#7 одной точкой без запроса большего текста);
`md impact --help` объясняет
`dependent_breaks` vs `body_wikilink_refs` vs `body_markdown_refs`; новая секция `## Schema Vocabulary` в
`cli-conventions.md` фиксирует reverse-relationship словарь и
companion `_count` field rule; 4 SKILL.md (Claude + Codex, navigator +
graph) получили pre/post-action discipline (semantic-search-first перед
structural diagnosis; `md cycles` после frontmatter edits) и stream
hygiene (stdout = data only). Compliance test harness как класс не
создаётся; точечные probe-tests в существующем `tests/` стиле.

Следствие за пределы класса: `_path_passes` / default-excludes silently
dropping non-dot folders — паттерн, который вероятно проявится в
жалобах на `md scan`, `md check`, `md health`, `md preflight`, `md impact`
тоже. Future probe — добавить такие же `--help` notes этим командам,
либо emit warning при значительной части скрытых файлов. Не делается
сейчас по EVPI: один feedback round пока не оправдывает sweep.

## D-005 - `md` не владеет git-diff selection

Дата: 2026-05-29.

Решение: убрать публичную git-diff based changed-file review команду из
installed `md` path. Callers and skills own file selection; `md` принимает
явные paths/scopes и возвращает graph/index evidence через `preflight`,
`check`, `health`, `status` and related tools.

Причина: рабочая среда часто живёт с грязным git tree and GitHub используется
как backup, not collaboration flow. Команда, которая притворяется canonical
diff owner-ом, создаёт шум и подталкивает agents к git/GitHub-dependent
логике вместо явного локального scope.

Следствие: `md_cluster` занимает освободившееся место в catalog-driven CLI как
самостоятельный read-only IA/topology tool. Legacy graph wrappers remain only
for compatibility; `navigator.api` imports graph primitives directly and does
not depend on legacy `navigator.graph`.
