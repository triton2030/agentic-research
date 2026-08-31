# Две независимые проверки exact `candidate-v7`

Проверенный fingerprint:
`b6dd5b397cc78d49b6edd7212a48bb021a7c6b41b6feec359b81aaeaf378b1ee`.

Оба checker-а работали с `fork_turns=none`, не читали ответ друг друга, не
редактировали файлы и пересчитали fingerprint до и после review.

## Literal checker

- Fingerprint before/after: совпал с exact candidate.
- Full-file counts: root 16; scout 16; verification 27; Codex metadata 4.
- Active counts: trigger 1; ordinary authoring 15; clean scout 15;
  verification 20; install-only 20; Codex invocation 1.
- Verdict: `findings: none`.

## Trajectory checker

- Fingerprint before/after: совпал с exact candidate.
- Active counts: ordinary authoring 15; clean scout 15; verification 19;
  install-only 18; Codex invocation 1.
- Эталонная траектория совпала с commander intent: external truth/hard line
  достигает первого решения узким маршрутом; unknown edge получает clean
  scout; exact candidate проходит blind delayed/non-use proof; install возможен
  только owner-first при `pass` и exact approval того же identifier.
- Verdict: `findings: none`.

Для terminal отчёта приняты консервативные максимумы literal checker-а:
`15 / 15 / 20 / 20 / 1`. Расхождение атомизации не меняет gate: оба реальных
режима находятся в пределах двадцати и оба checker-а вернули пустой список
находок на одних байтах.
