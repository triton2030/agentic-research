# Clean-run 1orchestration v9

Manifest:
`e92af4190ce42843eb5c47a2f2a6099cbb5f68305dee783d5799d14926a48acd`.

Чистый executor видел только candidate и project AGENTS/GOAL/Frame/Principles.
History, owner quotes и checker outputs не читались.

Case: решить, нужен ли постоянный root-rule читать каждую skill-specific
Product Frame в любой задаче.

Наблюдаемое поведение:

- root прочитал все влияющие источники до brief;
- brief сохранил scoped outcome, complete done/required-evidence, exact read и
  missing delta;
- actor/root оценены отдельно;
- split отклонён как лишний handoff при выполнимом direct/root наборе;
- weak return без current evidence не открыл dependency;
- изменение source вернуло только затронутую цепочку к первому stale result.

Mode counts terminal clean case с task/source units:

`prepare 6 · root-work root 13 · direct actor 11 / root 11 · split actors 8+8 /
root 13 · accept root 6 · upstream root 5`.

Verdict: `behavior_pass`.
