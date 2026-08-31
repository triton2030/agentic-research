# Clean-run v7 — первый кандидат

Чистый исполнитель не читал старый пакет, history, reviews или
`refactor-v7.md`. Он прочитал восемь файлов первого `draft-v7` и применил их к
read-only аудиту самого candidate.

Фактическая траектория:

`orient → brief → count → budget → direct-assignment → accept(rework)`.

- Полный source set: 8 файлов; 6 references.
- Actor active ledger: 17, `manageable`.
- Root next-decision ledger: 15, `manageable`.
- Shape: один read-only исполнитель; root сохранил приёмку.
- Return «Проверил: всё совпадает, все references имеют Цель» получил
  `rework`, потому что не содержал адресов и атомарных verdicts.
- Зависимый ход не открыт; недостающая `delta` названа точно.

Материальное расхождение: очевидный линейный аудит был обязан пройти полный
`count → budget`. Это стало evidence для условного ledger во второй версии.

Специфичный gap, не обобщённый в runtime: поскольку references были объектом
аудита, `orient` потребовал прочитать их все до стадийного использования.
