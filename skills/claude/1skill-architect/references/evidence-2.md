## Evidence — продолжение

Для routing нужны use/skip/near-miss cases против живых соседей. Для operational
claim — точный tool output, воспроизводимый прогон или проверяемое преимущество.
Для distribution — фактический runtime и metadata/projection sync.

Сила evidence растёт вместе с широтой, частотой, риском, credential/network
effects, trigger collision и историей regressions. Не прогоняй фиксированный
ритуал всех проверок; выбирай evidence, которое различает именно заявленные
риски.

Перед добавлением нового правила проведи delete-first pass: убери obsolete
scaffolding, повторы, generic brevity и строки без action-changing Delta. Не
удаляй causal explanation или thought demonstration, если без них controller
снова превращается в произвольную команду.

Дословно из `local-skill-contract` (Validation) и каталога провалов:

- For a probability-shift claim, register the bypass prediction first, then use
  matched repeated runs of the same fork and count the target first act.
- Test proxy, objective, phase, anchor, and form claims separately when the
  design relies on them.
- **Elastic defense**: a failed run is rescued by a post-hoc explanation when no
  bypass prediction and revision criterion were recorded before it.
- **No mechanism ablation**: a central explanation or example is assumed to
  cause the effect without testing whether behavior survives its removal or
  replacement when the claim is material.
