---
description: "Run the fixed four Claude panel profiles from frozen isolated packets."
---

# Panel Launch

Вход: четыре frozen packets. Выход: четыре terminal native reports.

1. Запусти новые ordinary non-fork `Agent` streams профилей `ladder`, `solvent`, `prospector`, `premortem`.
2. Передай каждому stream только его packet; роль читает raw sources своей зоны.
3. При ограниченной capacity используй bounded waves и сохраняй готовые reports.
4. Недоступный профиль верни как точный blocker; не имитируй его другой ролью.
5. Не завершай стадию без terminal outcome каждой линзы.
