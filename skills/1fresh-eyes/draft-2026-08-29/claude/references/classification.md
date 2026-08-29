---
description: "Verify and classify Claude panel findings into one evidence ledger."
---

# Classification

Вход: четыре terminal native reports. Выход: evidence ledger.

Каждый material finding классифицируй сверху вниз; первый применимый к нему label побеждает:

1. `invalid-test` — brief был leading/forked или повторил method, source и consequence другой линзы.
2. `rejected` — source противоречит finding или finding вне scope.
3. `needs verification` — decision зависит от claim без direct/source-supported evidence.
4. `incomplete` — supported objection не даёт alternative или smaller probe.
5. `deferred` — finding поддержан, но не нужен текущему decision.
6. `accepted` — evidence и alternative меняют текущий decision.

Проверь, что source поддерживает decision-changing claim; citation сама по себе не support.
Сохрани для каждой линзы native verdict, falsifier, source anchor и отдельное decision consequence.
Одинаковый итог допустим при разных evidence paths.
Сгруппируй ledger по source, label и severity; raw output не переноси в canon.
