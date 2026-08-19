---
description: "Owner-preserving rebuild of an isolated CLI environment in active uv 0.12.5."
---

# uv tool Rebuild

Момент: изолированный Python CLI нужно пересобрать с изменённой dependency или
source. Сверено 2026-08-19 с uv 0.12.5; быстрее всего меняются install options.

## Дельта

Каждый `uv tool` имеет собственный environment и receipt. Команда
`uv tool install --reinstall` пересобирает его владельцем uv и принимает
dependency через `--with`, source и `--editable`:

```bash
uv tool list --show-paths
uv tool install --help
uv tool install --reinstall --with 'PACKAGE>=FIX' TOOL_OR_PATH
```

Внутренний `pip` меняет environment вне его manager receipt. `uv tool upgrade
--all` обновляет все tool environments, а не только один active command.
