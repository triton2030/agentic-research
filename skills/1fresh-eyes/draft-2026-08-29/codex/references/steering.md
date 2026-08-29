---
description: "Repair one retained Codex lens without manufacturing another vote."
---

# Steering

Вход: wrong source-bound premise или residual question. Выход: repaired report.

1. Running target получит fact/source/scope/boundary/missing-evidence delta через `send_message`; idle target — через `followup_task`.
2. Не передавай conclusion или новый method.
3. Сохрани initial verdict, intervention и revised/unchanged verdict.
4. Новый `fork_turns: "none"` stream используй только после смены identity вопроса/линзы/scope или contaminated first pass.
5. Не расширяй permissions или write scope.
6. Остановись без нового evidence step, falsifier или сужения decision boundary.
