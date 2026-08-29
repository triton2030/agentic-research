---
description: >-
  Use when an existing project-local 2* rule has an approved absent state and
  must be removed from its owner and both runtime copies.
---

# Снятие

## Цель

Полностью сними устаревший `2*`, не оставив активной проекции.

1. Разреши owner и точные runtime-пути либо объявленный проектом механизм
   удаления/check; сохрани исходное состояние пакета.
2. Удали owner и обе runtime-проекции.
3. Прими результат только когда project check подтверждает отсутствие всех
   трёх поверхностей.
4. При сбое восстанови исходное состояние и верни blocker; при успехе верни
   адресное доказательство отсутствия owner↔Claude↔Codex.
