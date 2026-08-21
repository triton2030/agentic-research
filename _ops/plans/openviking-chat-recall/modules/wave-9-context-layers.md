---
kind: module-card
wave: 9
state: planned
role: bottom-up-context-layer-writers
model: gpt-5.6-luna
thinking: max
---

# Модуль — bottom-up L1 overviews и L0 abstracts

[parent: task.md](../task.md) · веха 4 · gate: Wave 8 PASS

## Contribution

Добавить к принятому L2 дереву экономные context layers: L1 для выбора нужной
ветви и deterministic L0 для быстрого route. Сами L2 pages не переписываются.

## Inputs

- validated L2 catalog/tree Wave 8;
- pinned `overview_generation.yaml`, official prompt provenance и digests;
- accepted Wave 4b contract: L1 semantic, L0 извлекается из Brief Description.

## Dependencies

Обход строго bottom-up и чередуется на каждом depth: leaf L1 → leaf L0 →
parent L1 с child L0 → parent L0. Parent L1 не строится до terminal L0 всех
непосредственных children.

## Ownership

- `scripts/build_l1_overviews.py`, `tests/test_l1_overviews.py` — один shared
  code owner; semantic writers получают по одной directory/depth zone.
- Каждый writer пишет только `.overview.md` внутри своей zone и receipt.
- `scripts/build_l0_abstracts.py`, `tests/test_l0_abstracts.py` — отдельный
  deterministic owner; пишет только `.abstract.md`.
- Root пишет layer manifest после завершения всех depths.

Каждый Luna Max writer запускает nested checker соседнего depth boundary.

## Layer contract

- L1 входы: summaries непосредственных L2 files и L0 дочерних directories;
  сама будущая L1/L0 не входит в собственный prompt.
- L1 содержит Brief Description и навигационные distinctions, достаточные для
  выбора следующего чтения, но не пытается заменить L2 evidence.
- L0 механически извлекается только из Brief Description принятого L1; без
  отдельного LLM-вызова и новых фактов.
- Одна directory/depth zone имеет одного writer. Self-cycle и двойной owner
  запрещены.
- Language, ordering и prompt tuple фиксируются до первого generation call.

## Falsifying checks

- self-inclusion/cycle и parent-before-child fail;
- L0, не совпадающий с Brief Description, fail;
- L1 source/link, отсутствующий в L2 catalog, fail;
- delete-and-rebuild с теми же digests byte-identical;
- synthetic directory fixture показывает, что агент выбирает правильного child
  по L0/L1 без чтения всей ветви.

## Return

На depth: commit SHA, owned directories, input/output digests, model/cost/retry,
tests и nested receipt. Root: layer manifest, coverage directories, unresolved
routes и общий verdict. Wave 10 закрыта при любом material UNKNOWN.

## Prohibitions

Не менять L2, canonical claims, evidence, holders, catalog или shared status;
не добавлять новые semantic facts в L0.
