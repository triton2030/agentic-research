# Авторские проверки — `1context-refactor`

## Цель

Зафиксировать author modes и изменения после двух checker rounds.

## Short description

`Use after session errors, rework, or needless searches recur.` — 61 символ,
одна English trigger-only фраза `Use after…`; функция, маршрут, результат и
exclusion отсутствуют. Use: повтор опровергнутого хода. Skip: будущий риск →
`1instruction-authoring`. Near-miss: первая дорогая находка → `1index`.

## Behavior protocol

Жёсткая процедура оставлена только для session-wide coverage, causal proof,
independent evidence gates, authority и replay. Дословного owner-порядка нет.

## Reference files и active set

После owner-критерия «не переусложнять» четыре промежуточных references
сначала стали двумя, но clean trajectory checker доказал, что оба всегда
читались и не давали progressive disclosure. Итоговый candidate полностью
self-contained; предварительный строгий active set — 20 единиц.

Остались только session-wide causal threshold, independent route/finding gates
и authority/replay для advice/repair. Их counterfactual harm записан в
`simplicity.md`; остальные fields/stages сняты.

## Agent defaults

Оставлены три исправляемых дефолта: последний source принять за причину;
catalog pattern принять за диагноз; автоматический trigger принять за write
authority. Owner-specific route/finding gates отделены от causal advice/repair.
