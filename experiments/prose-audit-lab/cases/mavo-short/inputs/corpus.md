---
description: "Declared MAVO corpus scope for prose-audit runs."
depends-on:
  - "[[experiments/prose-audit-lab/cases/mavo-short/README|MAVO case]]"
---

# Corpus

Target root: `/Users/triton/Documents/mavo-short/`.

## Primary current corpus

- `README.md`
- `AGENTS.md`
- `_ops/GOAL.md`
- `_context-base/*.md`
- `Данные_снаружи/*.md`
- `01_Описание_бизнеса/**/*.md`
- `02_Веб_приложение/**/*.md`
- `03_Создание_загрузка_дизайнов/**/*.md`
- `Бизнес_Анализ/**/*.md`

## Secondary / context-only

- `04_Доп_проекты/**/*.md`, except future-only material must not be promoted
  into current canon without an explicit current-owner anchor.

## Excluded from semantic verdicts

- `.git/`
- `.md-navigator/`
- `.serena/`
- `.obsidian/`
- `.claude/`
- `.codex/`
- `.ignore/`
- `_workspace/`
- `.DS_Store`
