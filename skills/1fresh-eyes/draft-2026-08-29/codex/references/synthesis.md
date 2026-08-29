---
description: "Verify panel findings and return one owner decision without voting."
---

# Synthesis

Вход: terminal reports. Выход: проверяемый owner decision либо native product
одиночного исключения.

- Critic finding: `accepted` только при direct/source-supported evidence и альтернативе; иначе `rejected`, `deferred`, `needs verification` или `incomplete`.
- Citation не support сама по себе: проверь, что source говорит именно то, что claims finding.
- Для каждой panel lens сохрани native verdict, falsifier, source anchor и отдельное следствие для решения.
- Одинаковый итог допустим при разных evidence paths; одинаковый метод, источник и следствие — `invalid-test`, а не консенсус.
- `auditor` сохраняет матрицу pass/fail/unknown, `md-scout` — packet coverage/gaps; не нормализуй их в critic classification.
- Не голосуй и не усредняй. Проверь material claims, сохрани расхождения и выбери по конечному результату.
- Верни: следующий ход · ближайшая альтернатива · продолжить без изменений · чем выбранный лучше обеих.
- Честный `satisfied` / `architecture_ok` завершает линзу; не покупай повтор без нового material reason.
