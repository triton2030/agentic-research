---
description: "Canonical search, scan and outline routes in active ast-grep 0.45.1."
---

# ast-grep 0.45.1

Момент: выбирается structural code search/rewrite. Сверено 2026-08-19; быстрее
всего меняются subcommands и outline views.

## Дельта

- `ast-grep run` — канонический разовый search/rewrite.
- `ast-grep scan` — config-driven rules.
- `ast-grep test` — тесты повторяемых rules.
- `ast-grep outline` — symbols, imports, exports и members без отдельного
  parser-а; имеет `--items`, `--view` и JSON styles.
- `sg` остаётся в PATH, но печатает deprecation warning; новое каноническое имя
  — `ast-grep`.

```bash
ast-grep outline PATH --items exports --view signatures --json=compact
ast-grep COMMAND --help
```
