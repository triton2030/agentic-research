---
description: "Use after a Claude Premortem packet is frozen."
---

# Premortem

Вход: замороженный пакет панели или именованного Premortem. Выход: терминальный отчёт Codex или точный `blocker`.

1. Если Claude запущен из Codex, верни `premortem_skipped_recursive_parent` как точный `blocker`.
2. Иначе подготовь из замороженного пакета один запрос по `$1codex`; механика вызова принадлежит владельцу среды исполнения.
3. Не передавай нативные отчёты.
4. Попроси цепочку `achieved success → mechanism → harm`.
5. Попроси ранний `signal`, его адресуемый `state_today` и `guardrail` с ценой.
6. Потребуй первой строкой `fatal_signal_present`, `signal_watchable` или `story_unfalsifiable`.
7. Сохрани терминальный отчёт другой фактически выбранной модельной семьи или точный `blocker` без собственной подмены.
