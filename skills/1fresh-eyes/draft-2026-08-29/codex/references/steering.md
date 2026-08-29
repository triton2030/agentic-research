---
description: "Repair facts or continue one retained Codex lens without inventing a fresh vote."
---

# Steering

Вход: terminal/running report с неверной premise либо остаточный вопрос той же
линзе. Выход: repaired pass или retained consultation с явным trace.

- Передай running target короткий delta через `send_message`; idle target продолжи через `followup_task`.
- Исправляй только fact, owner/source, scope, boundary или missing evidence; не передавай желаемый вывод и новый метод.
- Сохрани initial verdict, intervention и revised/unchanged verdict; один stream не становится несколькими голосами.
- Новый `fork_turns: "none"` stream нужен только при смене вопроса, линзы или scope, либо если первый brief был leading/inherited.
- Follow-up не расширяет исходные permissions и write scope.
- Два хода без сужения evidence, альтернативы или decision boundary — stop.
