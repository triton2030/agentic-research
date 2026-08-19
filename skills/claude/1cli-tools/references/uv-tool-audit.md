---
description: "Vulnerability audit of isolated CLI environments in active uv 0.12.5."
---

# uv tool audit

Момент: проверяются vulnerabilities зависимостей изолированного Python CLI.
Сверено 2026-08-19 с uv 0.12.5; быстрее всего меняются audit service и formats.

## Дельта

`uv tool audit` проверяет отдельные tool environments через OSV и имеет text,
JSON и SARIF output:

```bash
uv tool audit TOOL --output-format json
uv tool audit --all --output-format sarif
uv tool audit --help
```

Это отдельная поверхность от project dependency audit: `<NAME>...` выбирает
environments, установленные владельцем `uv tool`.
