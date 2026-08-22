---
kind: module-card
wave: 8
state: planned
role: l2-page-writers-and-catalog-owner
system-owner: root
boundary-review: claude-opus-5
batch-model: gpt-5.6-luna
batch-thinking: max
---

# Модуль — typed L2 knowledge library

[parent: task.md](../task.md) · вехи 2–4 · gate: Wave 7 PASS

## Contribution

Материализовать accepted canonical claims в navigable typed L2 pages по
OpenViking IA, проверить каждую partition и атомарно собрать root catalog.

## Inputs

- frozen canonical claims/rejections/index Wave 7;
- pinned OpenViking Wiki Skill и разрешённые типы: entity, concept, justified
  method, comparison, analysis, summary;
- accepted language route; unresolved route не подменяется default-решением.

## Dependencies

Parallel render per part → validation per part → root-only catalog/index. Ни
одна L2 partition не открывается Wave 9 до общего catalog PASS.

## Ownership

- Shared code owner: `scripts/render_l2_pages.py`, `tests/test_l2_pages.py`.
- Каждый Luna Max writer пишет только
  `artifacts/full-build/wiki-l2/part-*/**` и свой receipt.
- Read-only validators используют `scripts/validate_l2.py`; validation result
  хранится рядом с part, но writer не принимает сам себя.
- Root-only owner: `scripts/build_l2_catalog.py`,
  `artifacts/full-build/wiki-l2/index.md`, `catalog.json` и
  `page-provenance.json`.
- L2 writers никогда не пишут `.overview.md` или `.abstract.md`.

Каждый writer проходит deterministic проверку source-quote membership и link
boundary; системную границу независимо проверяет root/Opus, не writer.

## Page contract

- Одна страница владеет одной понятной knowledge unit и имеет stable slug/type.
- Body содержит только distilled final statement, applicability, uncertainty и
  точные адреса supporting chat-recall quotes. Полные цитаты и chronology
  остаются в holders.
- Count/first/latest/full evolution не печатаются как default knowledge.
- Superseded/non-current/uncertain claims не появляются как current; contested
  допускается только при evidence обеих позиций и явной scope boundary.
- Source quote IDs разрешаются только из accepted claim membership. Internal
  Wiki links и catalog entries разрешаются; ссылки на project knowledge files,
  URLs или иные источники запрещены. Writer не открывает упомянутые в цитатах
  project files.
- `page-provenance.json` зеркалит только проверяемый page/claim/record mapping и
  не является вторым владельцем claim text.

## Falsifying checks

- full quote/history leakage fail;
- unknown claim/source ID, duplicate slug или wrong type fail;
- project-corpus link, source lookup вне frozen quote input или invented
  knowledge fail;
- prior superseded claim отсутствует в default body;
- delete-and-render part byte-identical;
- root catalog строится только из terminal validated parts и публикуется
  атомарно после проверки completeness.

## Return

Part writer возвращает commit SHA, footprint, page/type counts, validation и
nested receipt. Catalog owner возвращает global counts, orphan/link/source
checks, catalog digest и unresolved gaps. FAIL/UNKNOWN оставляет Wave 9 закрытой.

## Prohibitions

Не менять canonical claims, evidence, holders, prompts или shared plan/status;
не создавать общий hot file из parallel writers.
