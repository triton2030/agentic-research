# Exact-version review — 1use-principles

Package hash:
`0e9e06f32b857ff179e8aba9c221ba5e9827dff8b4fa975c2daaa7e2b90674b5`.

`SKILL.md` hash:
`f3525c759e7b723b3c5792af3fe693b55826c627ec332c70b9c4a9584497cbf9`.

## Основание

- Текущий authoring source — `/Users/triton/.codex/skills/1skill-creation/SKILL.md`;
  `shasum -a 256 /Users/triton/.codex/skills/1skill-creation/SKILL.md` →
  `6e6b93e97eef2a31c8922ba8462a28a086c82ec80c6566c39ed63fc6bdc9f6a3`.
- Owner-evidence в
  `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md`: русский body и
  короткий English trigger — строки 20–21; единый адрес
  `<project-root>/_ops/product-frames/` — строка 30, timestamp
  `2026-08-30T19:20:11+05:00`; запрет переусложнения — строка 33; разрешение
  довести рефактор до готовности — строка 35.

## Независимые проверки

- Literal checker: `description 2 + context 1 + goal 1 + boundaries 16 = 20`;
  maximum active set `20`; hashes совпали; `findings: []`.
- Trajectory checker: ready-answer завершает выбор без вариантов, inference
  остаётся локальным и не меняет канон; `findings: []`.
- Clean probe: ready-answer и inference-ветки завершились ожидаемо; повторяемый
  пробел передан Creator без правки канона.

## Изоляция

Runtime references и стадии отсутствуют. Canonical resolver — только
`<project-root>/_ops/product-frames/`. Official owners, projections и live
packages не менялись.
