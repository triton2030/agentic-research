---
description: "Verify panel reports and return one owner decision without voting."
---

# Synthesis

Вход: three native reports plus Claude verdict or explicit recursive-parent
skip. Выход: next, alternative или unchanged.

Классифицируй сверху вниз; первый применимый label побеждает:

1. `invalid-test` — brief был leading/inherited, спрашивал не того actor-а либо reports повторяют method, source и consequence.
2. `rejected` — source противоречит finding или finding вне scope.
3. `needs verification` — decision зависит от claim без direct/source-supported evidence.
4. `incomplete` — supported objection не даёт alternative или smaller probe.
5. `deferred` — finding поддержан, но не нужен текущему decision.
6. `accepted` — evidence и alternative меняют текущий decision.

Citation не support сама по себе; проверь, что source говорит именно то, что
claims finding.

Для каждой доступной линзы сохрани native verdict, falsifier, source anchor и
отдельное следствие для решения.

Одинаковый итог допустим при разных evidence paths.

Группируй findings по source, label и severity; raw output не переноси молча в canon.

Не голосуй и не усредняй; выбери по конечному результату.

Верни next · nearest alternative · unchanged · почему выбранный лучше обеих.

Честный `satisfied` / `architecture_ok` завершает линзу без повторного запуска.
