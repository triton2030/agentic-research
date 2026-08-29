---
description: "Repair one retained Codex lens without manufacturing another vote."
---

# Steering

Вход: wrong source-bound premise или residual question той же линзе. Выход: repaired report.

1. Running target получит delta через `send_message`; idle target — через `followup_task`.
2. Передай retained stream только fact/source/scope/boundary/missing-evidence delta.
3. Не передавай conclusion или новый метод.
4. Сохрани initial verdict, intervention и revised/unchanged verdict.
5. Новый `fork_turns: "none"` stream используй только при смене question/lens/scope или после leading/inherited first pass.
6. Follow-up не расширяет permissions или write scope.
7. Остановись, когда следующий ход не называет новый material evidence step, falsifier или сужение decision boundary.
