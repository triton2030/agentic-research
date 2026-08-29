---
description: "Verify and classify Codex panel findings into one evidence ledger."
---

# Classification

Вход: three native reports плюс Claude report или explicit skip. Выход: evidence ledger.

Каждый material finding классифицируй сверху вниз; первый применимый к нему label побеждает:

1. `invalid-test` — brief был leading/inherited или повторил method, source и consequence другой линзы.
2. `rejected` — source противоречит finding или finding вне scope.
3. `needs verification` — decision зависит от claim без direct/source-supported evidence.
4. `incomplete` — supported objection не даёт alternative или smaller probe.
5. `deferred` — finding поддержан, но не нужен текущему decision.
6. `accepted` — evidence и alternative меняют текущий decision.

Проверь, что source поддерживает decision-changing claim; citation сама по себе не support.
Сохрани для каждой доступной линзы native verdict, falsifier, source anchor и отдельное decision consequence.
Одинаковый итог допустим при разных evidence paths.
Сгруппируй ledger по source, label и severity; raw output не переноси в canon.
