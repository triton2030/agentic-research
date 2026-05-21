---
description: "Initial evidence map of current skills that use md_* capabilities."
read-before-edit:
  - "[[minimum-document-set.md]]"
edit-after-edit:
  - "[[full-functionality-contract.md]]"
  - "[[jobs-and-moments.md]]"
  - "[[public-capability-contract.md]]"
---
# Current Skill Usage Map

Первичный вывод: текущие `md_*` функции не являются мусором сами по себе.
Они используются разными скилами в разных рабочих моментах. Поэтому v2 должна
начинаться с capability design, а не с удаления команд по частоте.

Источник проверки:

```bash
rg -o 'md_[a-z_]+' /Users/triton/.codex/skills /Users/triton/.claude/skills \
  --glob 'SKILL.md' --glob 'references/**' --glob 'agents/**'
```

## Навигация И Чтение

- `md_orient`: `1md-navigator`, `1planning`, `1strategy`.
- `md_search`: `1md-navigator`, `1md-graph`, `1strategy`,
  `1planning`, `1ia-audit`, `1instruction-layer`, `1folder-contract`,
  `1skill-architect`, `1smart-simple`, `1work-review`.
- `md_extract`: `1md-navigator`, `1strategy`, `1planning`,
  `1ia-audit`, `1instruction-layer`, `1work-review`.
- `md_read_related`: `1md-navigator`, `1md-graph`, `1strategy`,
  `1ia-audit`, `1work-review`.
- `md_ls`: `1md-navigator`, `1planning`.
- `md_toc`: `1ia-audit`.
- `md_importance`: `1ia-audit`.

Вывод: чтение нельзя свести к одному search. Разные скилы требуют разные
формы ориентации: folder map, semantic search, related context, extraction,
importance and heading map.

## Graph И Радиус Последствий

- `md_edit_context`: `1md-graph`, `1md-navigator`, `1planning`,
  `1instruction-layer`, `1work-review`.
- `md_preflight`: `1md-graph`, `1strategy`, `1planning`,
  `1instruction-layer`, `1folder-contract`, `1work-review`.
- `md_impact`: `1md-graph`, `1strategy`, `1ia-audit`,
  `1instruction-layer`, `1folder-contract`, `1work-review`.
- `md_deps`: `1md-graph`, `1planning`, `1ia-audit`,
  `1instruction-layer`, `1folder-contract`.
- `md_section_blast_radius`: `1md-graph`, `1instruction-layer`.
- `md_changed`: `1md-graph`, `1planning`, `1instruction-layer`,
  `1folder-contract`, `1work-review`.
- `md_health`, `md_cycles`, `md_check`, `md_scan`: `1md-graph`,
  `1folder-contract`, `1work-review`, plus shape/audit skills.

Вывод: graph tools - не декоративная обвязка. Они закрывают разные риски:
pre-edit obligations, rename/delete impact, reverse edges, post-change review,
health and schema checks.

## Audit, IA И Повторяющиеся Идеи

- `md_audit`: `1md-navigator`, `1ia-audit`, `1instruction-layer`,
  `1smart-simple`, `1work-review`.
- `md_overlaps`: `1md-navigator`, `1ia-audit`, `1instruction-layer`,
  `1folder-contract`, `1skill-architect`, `1smart-simple`.
- `md_repeated_concepts`: `1md-navigator`, `1ia-audit`,
  `1instruction-layer`, `1folder-contract`, `1planning`.
- `md_refactor_candidates`: `1md-navigator`, `1ia-audit`.
- `md_query_by_type`: `1md-navigator`, `1strategy`, `1planning`.
- `md_profile_sections`: `1md-navigator`.

Вывод: audit/profile/refactor слой нужен не как "ещё функции", а как слой
сигналов для IA, planning, instruction cleanup and semantic review. В v2 его
нужно отделить от ядра, но не удалять без замены рабочего момента.

## Index, Mutations И Runtime

- `md_index`: `1md-navigator`, `1skill-architect`, `1smart-simple`,
  `1work-review`, `1folder-contract`.
- `md_status`: `1work-review`.
- `md_init`, `md_strip`: `1md-graph`, `1md-navigator`.
- `md_ping`: `1md-navigator`, `1md-graph`.

Вывод: stateful and mutating tools должны иметь отдельный admin/runtime
контракт. Их нельзя смешивать с read-only navigation, но нельзя и прятать так,
чтобы skill не видел cost, stale index or confirm-required behavior.

## Следствие Для v2

Не сокращать v2 через "оставить только часто используемые команды".

Особенно нельзя ломать привычные сценарии `1md-navigator`, `1md-graph` и
`1strategy`: это главные потребители, через которые остальные скилы получают
navigation, graph evidence and strategy ground-checks.

Правильный путь:

1. Сгруппировать функции по skill-моментам.
2. Описать полный функциональный контракт текущей поверхности.
3. Переписать backend так, чтобы текущие skill recipes не менялись.
4. Переключить ссылку на backend только после compatibility replay.
