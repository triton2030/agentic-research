# Multi-Stage Deferred Review

## Observation

Когда модель планирует работу как несколько stages (A → B → C) и
анонсирует план user-у, она воспринимает все stages как один логический
блок и откладывает `1work-review` до конца последней stage. Natural review
points между stages пропускаются.

Cumulative file count перешагивает порог stop hook (≥3 files / sensitive
surface) внутри stage B, хотя если бы review случился после stage A, текущий
ход касался бы только stage B и оставался под порогом.

Mechanism: planned multi-stage chain создаёт mental model «одна работа,
один closeout». Между stages нет user message, нет естественной паузы — а
review воспринимается как «отвлечение от плана».

Это пропускает реальный value review между stages: user может catch wrong
direction в UX (stage A) до того как модель добавит зависимость и схему
миграции (stage B). Cost ошибки в B значительно выше, чем в A — пропуск
A-closeout раздувает blast radius.

## Counter

- 2026-05-20 [Claude Opus 4.7]: spawned chain A (UX edits, 1 file) → B
  (stemming, 3 files + schema migration + new dep) → C (re-measure). После
  A не запустил review. На середине B stop hook сработал на cumulative
  4 файла. User явно flagged: «второй ход подряд с substantive write без
  `1work-review`». Natural review point после A был пропущен.

## Possible upgrade

В SKILL.md `1work-review`: добавить guidance, что multi-stage planned work
требует review **между stages**, не только в конце. Особенно когда:

- Stage A полностью закрывается и подлежит верификации user-ом до того,
  как stage B добавит cost (dep, migration, schema bump).
- Cumulative file count приближается к 3 в следующей stage.

В `1planning`: если task имеет explicit stages, оформлять каждую как
отдельный sub-task с собственным closeout, а не как один task с тремя
sequential edits.

Релевантно: любая планируемая multi-stage работа, особенно с возрастающей
ценой ошибки между stages.
