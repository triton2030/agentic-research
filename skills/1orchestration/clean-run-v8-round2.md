# Clean-run v8 — второй кандидат

Exact manifest:
`faea1a13830f0a02fddbd3b7e030ab3975ab0e8c604031c3f51df96b0cf74c1b`.

Чистый исполнитель не читал predecessor/history и применил candidate к
read-only сравнению GOAL и project Frame.

- Brief содержал `outcome`, полный `done_when` с evidence, точный `read` и
  missing-only `delta`.
- Direct actor: `16`; root acceptance: `8`; root-work: `21`.
- Split отклонён, потому что не снимал source units и добавлял reconciliation.
- Actor capability change вызвал re-estimate; неспособный actor отклонён
  независимо от числа.
- Return «цели в целом согласуются» не прошёл coverage, addresses или evidence
  и не открыл dependency.
- Missing-only ответ назвал только coverage-index, address matrix,
  classification, gaps и no-write evidence; новый workflow не появился.
- Upstream change сделал затронутые brief/estimates/acceptance неактуальными.

Удалённые explicit accept/rework stages не понадобились. Наблюдаемых разрывов
в goals не найдено; exact trigger, Russian body, zero refs, soft `20`, harm gate
и authority прошли.
