---
description: "Validation gates required before md-tools-v2 can replace current backend behavior."
read-before-edit:
  - "[[compatibility-and-migration.md]]"
  - "[[state-and-cost-model.md]]"
edit-after-edit:
  - "[[decision-log.md]]"
---
# Validation And Release Gates

v2 готова не когда код написан, а когда доказано, что она держит реальные
skill workflows.

## Gate Classes

| Gate | Что доказывает |
|---|---|
| unit tests | primitives work locally |
| contract tests | public capabilities держат schema and output shape |
| MCP smoke | agent transport works end-to-end |
| skill workflow replay | текущие Codex/Claude recipes still work |
| fixture corpora | RU/EN Markdown, broken links, duplicate concepts, warm-index clusters, stale index |
| failure-mode tests | missing key, API failure, stale index, confirm required |
| migration tests | aliases and old index behavior work or fail clearly |

## Minimum Green Baseline

Перед любым switch:

- current v1 baseline green;
- v2 baseline green;
- compatibility matrix updated;
- known deviations listed in decision log;
- rollback path named.

## Priority Skill Gates

Эти gate обязательны до замены backend-ссылки:

| Skill | Replay must prove |
|---|---|
| `1md-navigator` | привычные navigation/search/read/audit recipes работают без правки `SKILL.md` |
| `1md-graph` | graph action labels and blockers читаются так же, как в текущем skill |
| `1strategy` | ground-check calls stay cheap, bounded and decision-oriented |

Если любой из этих трёх требует переписать skill body, v2 migration считается
не готовой.

## Не Решено

- Где хранить replay fixtures.
- Какие real session traces можно использовать без лишнего шума.
- Должен ли `md_audit` быть release gate or optional slow gate.
