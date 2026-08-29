---
description: "Run the fixed three native Codex panel profiles from frozen isolated packets."
---

# Native Panel Launch

Вход: frozen native packets и retained Premortem outcome. Выход: три terminal native reports плюс retained outcome.

1. Запусти `ladder`, `solvent`, `prospector` как новые streams с `fork_turns: "none"`.
2. Передай каждому stream только его packet; не передавай Premortem outcome.
3. При ограниченной capacity используй bounded waves и сохраняй готовые reports.
4. Недоступный профиль верни как точный blocker; не имитируй его другой ролью.
5. Не завершай стадию без terminal outcome каждой native линзы.
