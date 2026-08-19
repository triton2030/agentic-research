---
description: "Active owner and joint-update route for conflicting terminal tools."
---

# Конфликт Версий И Update

Момент: две active terminal tools конфликтуют либо update не изменил active
binary. Сверено 2026-08-19; быстрее всего меняются manager dry-run/output.

## Active Owner

```bash
which -a TOOL
realpath "$(command -v TOOL)"
TOOL --version
```

Registry receipt без совпадающего active path не доказывает обновление.
Project-local binary имеет приоритет над global manager receipt.

## Совместное Обновление — Решение Владельца

Если конфликтуют две active версии, project pin не требует старую и managers
предлагают обновления обеих, один planned pass обновляет обоих участников до
текущих manager candidates. Затем повторяются обе версии и исходный failing
smoke. Основание — слова владельца
`_ops/chat-recall/2026-08-19-160259-codex-01a019a8.md`.

Homebrew direct targets не замораживают dependencies; точный plan виден до
mutation:

```bash
HOMEBREW_NO_AUTO_UPDATE=1 brew upgrade --dry-run --formula FORMULA...
```

`Would upgrade ... dependency` может принести major transition и относится к
тому же planned pass.
