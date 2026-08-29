---
description: >-
  Use after a present 2* candidate has behavioral proof and must be installed
  with matching Claude and Codex projections.
---

# Установка

## Цель

Установи доказанный кандидат из одного owner-а без расхождения проекций.

1. Разреши owner и точные runtime-пути либо объявленный проектом механизм
   sync/check; сохрани исходное состояние пакета.
2. Запиши кандидат только в owner и выполни установку обеих проекций.
3. Прими результат только при успешной project check: различия разрешены лишь
   там, где их требует формат runtime.
4. При сбое восстанови исходное состояние и верни blocker; при успехе верни
   адресное доказательство owner↔Claude↔Codex.
