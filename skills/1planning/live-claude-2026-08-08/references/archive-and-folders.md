---
description: "Folder placement и durable archive для plans/backlog."
---

# Archive И Папки

Planning surfaces создаются лениво под принятую active или deferred работу.

## Placement

- Есть подходящая task-folder → используй её.
- Одна bounded работа без устойчивого workstream → flat task в `_ops/plans/`.
- Одна выбранная deferred работа → flat task в `_ops/backlog/`.
- Нужная planning surface отсутствует → создай её вместе с первым принятым
  contract, не заранее пустой. Решение относится к принятию active/deferred
  работы, а не к созданию стандартной директории. Если меняется project scope,
  сначала `1goal`.
- Нужен новый устойчивый workstream/owner boundary → сначала `1ia-audit`, затем
  минимальная folder shape.
- Large-run Gate выполнен → используй
  `_ops/plans/<stage>/<task-slug>/task.md`; Stage только группирует sibling Tasks
  по смыслу и не получает собственного файла или lifecycle.

Не вызывай IA-аудит только ради обычного task-файла или технического
`_archive/` рядом с уже выбранной plans/backlog surface.

## Durable Archive

- Closed, dropped, descoped или superseded contract уходит в ближайший archive
  своей surface; paths с `/_archive/` никогда не live.
- Новая plans/backlog folder следует существующей project convention для
  `_archive/`; переход и factual closeout принадлежат
  [`task-file-lifecycle.md`](task-file-lifecycle.md).
- Пустая директория не является durable artifact в Git: используй уже принятую
  project placeholder convention или создавай archive вместе с первым content.

Archive capsule нужен, когда рядом с contract есть действительно полезное
evidence:

```text
_archive/YYYY-MM-DD-<task-slug>/
├── task-*.md
└── <только retrieval-useful evidence>
```

## Staged-Run Routes

- inactive Module brief → `<task-slug>/_archive/<module-slug>.md`;
- closed/dropped/superseded Task directory → `<stage>/_archive/<task-slug>/`;
- live `modules/` и оба `_archive/` создаются лениво, только с первым artifact;
- archive не читается как active frontier и не участвует в worker assignment.
