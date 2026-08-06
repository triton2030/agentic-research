# Triggered Repository Rules

Project-owned cold rule directory вроде `_ops/rules/**` — допустимая
instruction surface, если правило устойчиво, нужно только в редкий наблюдаемый
момент и root может надёжно маршрутизировать этот момент.

- Always-on invariant остаётся в effective `AGENTS.md`; path-local правило — в
  subtree `AGENTS.md`.
- Root содержит только `observable trigger → exact RULE`; procedure и rationale
  живут в одном RULE.
- Каждый live RULE объявляет один information job, `read-when`, target
  act/result, owner/status и stop. Его steering cell реконструируется при
  authoring, но не сериализуется целиком без необходимости. RULE без root route
  — orphan; копия его procedure в root — competing owner.
- Читай RULE только после совпадения trigger, не загружай всю папку заранее.
- Если правило должно обнаруживаться skill runtime-ом в момент действия, а root
  route недостаточен, surface decision принадлежит `1skill-architect`; жанр
  project-local `2*` — `1local-rules`.
