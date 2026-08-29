---
description: "Repair one retained Claude lens without inventing a fresh vote."
---

# Steering

Вход: wrong premise или residual question той же линзе. Выход: repaired pass
или retained consultation с trace.

- Передай тому же Agent только fact, owner/source, scope, boundary или missing-evidence delta; не передавай conclusion и новый метод.
- Сохрани initial verdict, intervention и revised/unchanged verdict; один stream не становится несколькими голосами.
- Новый ordinary non-fork Agent нужен только при смене вопроса, линзы или scope, либо после leading/forked first pass.
- Follow-up не расширяет permissions и write scope.
- Stop, когда следующий follow-up не может назвать новый material evidence step, falsifier или сужение decision boundary.
