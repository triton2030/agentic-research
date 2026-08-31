# Terminal clean acceptance probe

## Verdict

**PASS.** Исполнитель читал только три exact candidate `SKILL.md` и ничего не
менял.

1. Root и nested rule прочитаны до planning decision после major error.
2. Planning не принимает неполный handoff; named book+method trace меняет один
   task slice.
3. Карта с overlap, отсутствующими order/dependency/proof остановлена до
   ремонта; после ремонта становится входом task.
4. Новый writer перечитывает task+epic, называет next/stop и получает authority
   только явной передачей; defer сохраняет reason.
5. При прежнем result, но изменённых boundary/proof/surprise resume остановлен
   и возвращён в `1planning` до execution.
6. Runtime не требует schema, status catalog или reference; около `20` остаётся
   бюджетом упаковки, а не основанием урезать результат.

Фальсификаторы не сработали: partial approval, invalid map, dual writer,
unreasoned defer, stale resume и hard-cap reading каждого разрушают маршрут.
