# Clean-run v8 — terminal candidate

Exact manifest:
`304feb88f1842b04fbe93af4cddf859df28c17620383941e5399cbaa51390074`.

Чистый read-only executor прочитал только candidate и governing task sources.

- Case: proposal-only изменение root route по GOAL и project Frame.
- Brief: `outcome`, пять `done_when` с evidence, точный `read`, missing-only
  `delta`.
- Direct actor: `21`; root acceptance: `10`.
- Предварительный split отклонён: оба actor-а повторяли owners, root получал
  merge; direct на `21` остался manageable, soft `20` не стал hard cap.
- Capability/configuration change вызвал повтор обеих оценок.
- Weak return прошёл `4/5`; failed behavioral evidence удержал dependency.
- После точечного evidence-return all-pass открыл dependency без отдельной
  rework-стадии.
- Upstream change повторно закрыл gate и пересобрал только затронутые
  brief/estimates/acceptance.
- Tiny case выбрал root-work без actor-а.

Удалённые impact-map, gap, references и rework-stage не понадобились.
Неблокирующий пробел: recovery после fail выводим, но не назван явно.

Отдельный trajectory residue, не проявившийся в этой clean-пробе: абстрактное
«все применимые критерии» допускает неполный source-derived `done_when`.
