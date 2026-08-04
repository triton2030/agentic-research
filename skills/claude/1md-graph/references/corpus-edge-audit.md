---
description: "Bounded cohort audit for semantic integrity of many cross-file Markdown edges."
---

# Corpus Edge Audit

## Boundary

Это редкий route для явного corpus-wide или cohort-wide вопроса. Он применяет
те же edge verdicts, что edit-time audit, но требует отдельного denominator,
coverage accounting и stop.

Не расширяй обычную правку в corpus campaign из-за большого reverse graph.

## Choose The Cohort

Выбери один режим:

- **exhaustive cohort** — все существующие cross-file edges в конечном
  file/folder/type set;
- **risk cohort** — все edges выбранного hub, relation job, artifact type или
  changed owner chain;
- **sampled diagnostic** — стратифицированная выборка для оценки failure
  pattern; никогда не даёт corpus closure.

Denominator должен перечислять link dialects и metadata relations. Tool output,
который теряет holder context, exact fragment или часть dialects, не является
полным inventory.

## Baseline

До verdicts зафиксируй:

- corpus root, includes/excludes и effective instructions;
- количество existing edges по relation/link class;
- unread denominator;
- known hubs и SCC review cohorts;
- named seeds для missing-edge probes;
- structural state отдельно от semantic state.

Broken paths/anchors и cycles — signals. Они не заменяют чтение edge bodies и
не определяют semantic verdict.

## Audit Order

1. **Owner/conflict signals.** Сначала пары, где два artifacts претендуют на
   один invariant, каждый делегирует его другому или link direction расходится
   с body authority.
2. **High-consequence hubs.** Затем owners, изменение которых затрагивает
   customer promise, money, rights, state, delivery или большой reverse set.
   Centrality выбирает порядок, не verdict.
3. **Anchored prose edges.** Проверяй holder attribution против exact target
   section; technically valid anchor может быть semantic `retarget`.
4. **Hard dependencies.** Для каждого `depends-on` назови X/Y и
   `sound/reclassify/remove/conflict`.
5. **Navigation/provenance.** Удали только edge без различимой information job;
   optional reader value может быть sound.
6. **Missing edges.** Запусти seeded route из
   [`missing-edge-discovery.md`](missing-edge-discovery.md) только после
   existing-edge cohort, чтобы не смешивать closed и open sets.

Каждая строка verdict-а следует
[`semantic-edge-audit.md`](semantic-edge-audit.md). File-level batch verdict
без body attribution запрещён.

## Measurement

Для exhaustive/risk cohort сообщи:

- denominator existing edges;
- `sound`, `retarget`, `reclassify`, `remove`, `conflict`, `unread`;
- delta impacts, если audit связан с change;
- missing probes, candidates и named open remainder;
- structural findings отдельно.

Для sampled diagnostic дополнительно назови selection method и не экстраполируй
проценты на corpus без defensible sampling contract.

## Stop

Exhaustive cohort закрыт, когда каждый existing edge denominator получил
verdict, `unread` пуст или передан, conflicts имеют owner handoff, а
missing-edge вывод ограничен seeds и searched scope.

Sampled diagnostic закрыт после выбранной sample и failure-pattern verdict; он
не разрешает фразы `corpus audited`, `graph clean` или `no missing edges`.
