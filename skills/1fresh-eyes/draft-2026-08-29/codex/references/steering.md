---
description: "Repair one retained Codex lens without inventing a fresh vote."
---

# Steering

Вход: wrong premise или residual question той же линзе. Выход: repaired pass
или retained consultation с trace.

- Running target получит delta через `send_message`; idle target — через `followup_task`.
- Исправляй только fact, owner/source, scope, boundary или missing evidence; не передавай conclusion и новый метод.
- Сохрани initial verdict, intervention и revised/unchanged verdict; один stream не становится несколькими голосами.
- Новый `fork_turns: "none"` stream нужен только при смене вопроса, линзы или scope, либо после leading/inherited first pass.
- Follow-up не расширяет permissions и write scope.
- Stop, когда следующий follow-up не может назвать новый material evidence step, falsifier или сужение decision boundary.
