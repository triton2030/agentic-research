---
description: "Preview agent-skill lifecycle in active gh 2.97.0."
---

# GitHub CLI: skill

Момент: agent skill ищется, preview-ится, обновляется или готовится к publish.
Сверено 2026-08-19 с active `gh 2.97.0`; family помечена preview и меняется
быстро.

## Дельта

```bash
gh skill --help
gh skill search --help
gh skill preview --help
gh skill publish --dry-run
```

Family также имеет `install`, `list` и `update`; она работает со skills в GitHub
repositories. `publish --dry-run` валидирует skill до внешнего publish.
