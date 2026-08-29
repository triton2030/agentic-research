# Named trial — round 1 — 2026-08-29

Clean Codex executor получил exact candidate и просьбу явно использовать
`auditor`. Он прочитал named route, запустил ровно один clean non-fork auditor,
не запустил panel roles и вернул native audit matrix без synthesis.

## Pass

- Explicit `auditor` routed to named mode.
- Spawned roles: exactly one `auditor`; panel roles: none.
- Native auditor product preserved unchanged.

## Findings

- `active set ≤20` failed на тогдашнем `named-packet`: auditor насчитал минимум
  26. Finding принят; версия заменена более глубоким `packet.md`, а не 19–23
  micro-stages.
- «Каждая stage обязана читать reference» failed только потому, что trial
  criterion был сформулирован слишком строго. Finding отклонён как invalid
  test: `1skill-creation` запрещает несколько simultaneous references, но не
  требует пустой файл для одношагового native handback. Этот ложный criterion
  не возвращается.

## Следующее evidence

Повторить clean named trial на упрощённой exact version и отдельно выполнить
panel trial; self-report controller-а не заменяет trace.
