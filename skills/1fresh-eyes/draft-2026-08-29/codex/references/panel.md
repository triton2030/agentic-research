---
description: "Run the fixed native Codex panel without leaking the Premortem report."
---

# Native Panel

Вход: frozen native packets и retained Premortem outcome. Выход: three terminal native reports плюс retained outcome.

1. Native panel — `ladder`, `solvent`, `prospector`.
2. Запусти каждый профиль как новый stream с `fork_turns: "none"` и только его packet.
3. Не передавай Premortem outcome native streams.
4. При ограниченной capacity используй bounded waves и сохраняй terminal reports.
5. Недоступный профиль верни как точный blocker без подмены.
6. Не переходи к handback без terminal outcome каждой native линзы.
