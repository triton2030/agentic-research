---
description: "Run the fixed Claude panel from four frozen isolated packets."
---

# Panel

Вход: four frozen panel packets. Выход: four terminal native reports.

1. Панель — `ladder`, `solvent`, `prospector`, `premortem`.
2. Запусти каждый профиль в новом ordinary non-fork `Agent` stream только с его packet.
3. При ограниченной capacity используй bounded waves и сохраняй terminal reports.
4. Каждая линза читает raw sources своей зоны.
5. Недоступный профиль верни как точный blocker без подмены.
6. Не переходи к handback без terminal outcome каждой линзы.
