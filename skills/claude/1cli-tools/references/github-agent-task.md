---
description: "Preview GitHub agent sessions in active gh 2.97.0."
---

# GitHub CLI: agent-task

Момент: создаётся или читается GitHub agent session. Сверено 2026-08-19 с
active `gh 2.97.0`; family помечена preview и меняется быстро.

## Дельта

```bash
gh agent-task --help
gh agent-task create --help
gh agent-task list --help
gh agent-task view --help
```

Task адресуется pull request number, session ID или URL. Для non-interactive
`view` точный session ID избегает disambiguation при нескольких sessions у PR.
