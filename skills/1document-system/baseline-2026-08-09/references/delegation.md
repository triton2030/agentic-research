# Adaptive Delegation

Не используй subagents как generic quality ritual. Direct mode по умолчанию
остаётся у root.

## Fan-Out Gate

Делегируй только когда есть независимые evidence streams или непересекающиеся
corpus slices и fan-out уменьшает root context/latency. Один итоговый файл из
сотни sources уже может требовать System mode; число outputs не является gate.

## Staged DAG

1. Root фиксирует outcome, scope, mode и write boundaries.
2. Первая волна независимо собирает inventory shards и, если future меняет
   taxonomy, future-scenario evidence.
3. Root строит candidate type/authority map и spot-checks source addresses.
4. IA reviewer проверяет уже предложенную shape; не запускай его до evidence.
5. Root выбирает templates, разрешает conflicts и синтезирует результат.
6. Metadata audit проверяет уже созданный artifact/map.

Template selection, conflict resolution и final integration не делегируй.
Независимую экспертную критику уже собранной архитектуры передавай
`1fresh-eyes`; inventory worker не должен незаметно становиться reviewer-ом.

## Worker Return Contracts

- **Inventory:** examined/uncovered scope, `path#heading`, observed purpose,
  explicit authority evidence, conflicts, gaps; без финального IA verdict.
- **Future scenarios:** actor/reader, lifecycle change, information obligation,
  pressure on types/topology, evidence vs assumption, activation trigger.
- **IA review:** `pass/risky/fail/unknown`, owner evidence, false seams,
  smallest repair or alternative.
- **Metadata audit:** artifact path, core fields, lifecycle/authority result,
  hard edges, missing sections, not-checked.
- **Compaction verifier** (когда исполняется рез по target map): утверждения
  прошлой ревизии, которых нет ни в новой версии, ни у названного owner-а, —
  цитата, адрес, причина невыводимости; отдельно потери в контрактах неактивных
  сущностей и в адресуемых ID; вердикт по каждому: сохранено / выводимо (адрес)
  / потеряно. Работает от ревизии до реза, не видит самоотчёт исполнителя и не
  совпадает с ним в одном агенте. Полный контракт —
  [compaction-safety.md](compaction-safety.md).

Давай worker-у exact paths и minimum task-local context, не весь чат и не весь
template library. Root ждёт все обязательные shards, признаёт uncovered scope
и не маскирует конфликт голосованием.

