---
description: "Условные правила размещения файлов, папок, разделов и знаний без второго source of truth."
depends-on:
  - "[[AGENTS.md]]"
  - "[[_ops/AGENTS.md]]"
  - "[[_ops/GOAL.md]]"
---

# Placement Rules

Trigger: создаёшь, двигаешь, переименовываешь или делишь файл, папку, раздел,
правило, заметку, задачу или знание.

Owner: container shape, split/merge/move, file-vs-folder и truth-vs-view держит
`1ia-audit`; folder criteria и формулировку инструкции держит
`1instruction-layer`; GOAL/README shape держит `1goal`.

Check: один owner truth, понятный retrieval path, нет второго source of truth,
нет нового файла без функции.

## Минимальный След

- Сначала обновляй существующий owner-файл.
- Новый файл создавай только после названной функции, reader-а, owner-а и check.
- Side-doc, summary, handoff note или explainer не создавай без явного запроса.
- Retired/superseded artifacts не храни ради архива; важный урок переноси в
  правильный owner.

## Куда Класть

- Общие выводы для агентов, skills, LLM или платформ -> `knowledge/`.
- Короткие практические гайды -> `knowledge/practical-guides/`.
- Канонические guides/playbooks/pattern studies -> `knowledge/guides/`.
- Эталонные артефакты -> `knowledge/examples/`.
- Категорийные learnings/inventories -> `knowledge/research/{business,design,dev,meta}/`.
- Reader on-ramp -> `README.md` через `1goal`.
- Scope, NOT in scope, definition of done, stop rules -> `_ops/GOAL.md` через
  `1goal`.
- Текущая рамка движения -> `_ops/PROJECT-ROADMAP.md` через `1planning`.
- Активная сложная задача -> `_ops/plans/**` через `1planning`, только когда
  task-файл реально нужен.
- Актуальная проблема до решения -> `_ops/findings/**` через `1findings`.
- Длинный сбор ответов пользователя -> `_ops/interviews/**` через
  `1interview-tool`.
- Длинные слова пользователя -> не автозаписывать; существующий
  `_ops/user-said/YYYY-MM-DD.md` обрабатывать только manual, отдельным проходом.

## Folder Shape

- В корне `knowledge/` держать только `wisdom-*.md`.
- Новые подпапки в `knowledge/guides/` не создавать.
- Новые подпапки в `knowledge/research/{category}/` не создавать.
- `_ops/` — не склад заметок, идей, research или backlog.
- `INTERVIEW.md`, `LEARNINGS.md` и `projects/` не восстанавливать как живые
  поверхности.
- Новый project shape не собирать глобальным bootstrap-скриптом: GOAL/README/ROADMAP
  маршрутизировать через `1goal`, graph/frontmatter — через
  `1md-graph`, локальный project-owned bootstrap использовать только если
  он уже есть.
