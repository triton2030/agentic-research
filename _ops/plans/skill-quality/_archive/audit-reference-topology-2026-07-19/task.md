---
description: "Восемь глобальных skill-пакетов имеют lean reference topology без дублей и ложных маршрутов чтения."
kind: task
---

# Аудит reference topology восьми skills

## Outcome

`1ia-audit`, `1md-graph`, `1planning`, `1cli-tools`, `1fresh-eyes`,
`1readable-code`, `1instruction-layer` и `1break-down` оставляют будущей
GPT-5.6 / Claude Opus 4.7 только нужный для их рабочего хода контекст: каждый
reference имеет отдельную функцию, условие чтения и не конкурирует с
`SKILL.md` или соседним reference.

## Scope

- In: `SKILL.md`, `references/**`, `scripts/**` и `agents/openai.yaml` восьми
  пакетов в `/Users/triton/.codex/skills/`; этот task и его Module briefs.
- Out: остальные skills, общий knowledge-canon, новые control surfaces,
  machine-wide tooling audit и изменения runtime configuration.

## Red Lines

- Не сокращать ради метрики: удалять только generic competence, obsolete
  scaffolding, повторы, ложные variants и материал вне главного workflow.
- Не превращать reference в второй owner правил из `SKILL.md`.
- Не смешивать write ownership между параллельными исполнителями.
- Не принимать similarity, размер или зелёную link-check за IA-verdict без
  чтения bodies.

## Milestones

- [x] Зафиксирован полный inventory файлов, размеров, route links и исходный
  structural health.
- [x] Каждый пакет прочитан и исправлен в своём write boundary.
- [x] Root синтезировал межпакетные дубли, routing collisions и owner seams.
- [x] Независимые structural и acceptance lenses приняли итоговые артефакты.

## Done

- [x] Все восемь `SKILL.md` и все их references прошли direct body review.
- [x] Каждый оставшийся reference прямо маршрутизирован из `SKILL.md` с
  понятным условием чтения; orphan и broken local links отсутствуют.
- [x] Повторы между body/reference и соседними references удалены либо имеют
  доказанно разную функцию.
- [x] Самые длинные references либо сокращены, либо их длина оправдана
  самостоятельной task-local функцией и навигацией.
- [x] `quick_validate.py` проходит на всех восьми пакетах; изменённые scripts
  имеют targeted runtime check.
- [x] Strict gate пройден для каждого глобального skill: 8 should-trigger + 8
  should-not near-miss prompts, output assertions и metadata regression.
- [x] Финальный отчёт отделяет проверенное, принятые IA-решения и residual risk,
  включая before/after размеры.

## Closeout Evidence

- Initial root inventory before edits: 44 Markdown-файла = 8 `SKILL.md` + 36
  references, 4 959 строк. Крупнейшие references —
  `1cli-tools/references/tool-map.md` (375 строк),
  `1ia-audit/references/design-patterns.md` (203),
  `1fresh-eyes/references/brief-templates.md` (202),
  `1break-down/references/decomposition-failures.md` (187).
- Final live `find ... -name '*.md' | xargs wc -l`: 38 Markdown-файлов = 8
  `SKILL.md` + 30 references, 2 808 строк; delta −6 files / −2 151 lines
  (−43.38%). Крупнейшие references теперь: `file-contracts.md` (144,
  schema owner + Contents), `staged-runs.md` (124, staged protocol + Contents),
  `semantic-edge-audit.md` (114, edge admission + Contents),
  `task-file-lifecycle.md` (106, lifecycle owner + Contents).
- Eight `qv-skill` runs: `Skill is valid!`; eight scoped `md scan` runs: zero
  issues; offline `lychee`: 51 links, 50 OK, 0 errors, 1 excluded external.
- Orphan check, retired-route search and exact Markdown hash check returned no
  findings. `probe-tools.sh`: `bash -n`, `shellcheck`, found/miss smoke and
  invalid-handle exit all passed.
- Semantic overlap after final FRESH index: seven candidates at threshold 0.78;
  direct body review classified them as router→full contract or explicit
  schema→protocol seam, not competing obligations.
- `architecture-critic` found one real blocker: `1readable-code` created an
  architecture truth owner and instruction route. Root removed that authority;
  follow-up verdict `architecture_ok` confirmed owner placement now routes to
  `1ia-audit` and instruction routing to `1instruction-layer`.
- Write provenance: `audit_ia_instructions` менял только `1ia-audit/**` и
  `1instruction-layer/**`; `audit_graph_cli` — только `1md-graph/**` и
  `1cli-tools/**`; `audit_planning_decomposition` — только `1planning/**` и
  `1break-down/**`; root — `1fresh-eyes/**`, `1readable-code/**` и последующие
  cross-package fixes. Worker returns и live paths не показывают пересекающихся
  writes; Module briefs остались неизменными.
- Strict gate: два blind cross-evaluators обменялись unlabeled cases и
  классифицировали только по восьми live descriptions. Каждый skill: 8/8
  should-trigger и 8/8 should-not near-miss; общий результат 128/128, exact
  failures none. Для каждого skill representative output regression прошёл
  4/4 assertions: observable result, boundary/handoff, stop и metadata/default
  prompt alignment. Статический `plugin-eval analyze` после metadata/body fixes
  дал всем восьми grade A; у пяти остался non-blocking token-budget warning.
- Во время eval в live `1planning` появился дополнительный cadence-contract для
  active task/root-worker updates в `SKILL.md`, `task-file-lifecycle.md` и
  `staged-runs.md` (mtime 22:23:17), не заявленный текущими read-only
  evaluators. Он сохранён как внешний concurrent delta, directly reviewed,
  получил `Contents` после роста lifecycle reference >100 строк и повторно
  включён в validation; assigned worker boundaries не пересекались.
- Final `auditor` verdict: `pass`; strict gate, disjoint write provenance,
  external planning delta, current totals и final validations приняты;
  blocking findings отсутствуют.
- Runtime/schema facts for Codex, Claude Code and `md-tools` were checked against
  current official/live surfaces. Networked update/security commands were not
  executed because this audit did not authorize their side effects; their
  references were checked against live help only.

## Continuity

- Active frontier: все milestones и Done приняты; task больше не управляет
  execution.
- Accepted evidence: package, link, graph/schema, script, semantic overlap and
  independent architecture/acceptance checks above are green.
- Next bounded action: move whole Task directory to the nearest durable
  `_archive/`; next execution owner отсутствует.

## Stop / Handoff

- Blocker: reference содержит live runtime/schema fact, который нельзя
  подтвердить локально и удаление изменит контракт — оставить факт как
  residual risk, не угадывать.
- Root владеет конфликтами между пакетами, итоговым diff, graph/link closeout,
  fresh-eyes synthesis и архивированием этого task после завершения.
