---
description: "Active global TypeScript 7.0.2 compiler defaults."
---

# TypeScript 7 Defaults

Момент: глобальный `tsc` запускается вне проекта с собственным local TypeScript
и `tsconfig`. Сверено 2026-08-19 с active TypeScript 7.0.2; быстрее всего
меняются compiler defaults.

## Дельта

Active `tsc --help` объявляет:

- `strict: true`;
- `target: es2025`;
- `esModuleInterop: true`;
- `--ignoreConfig` для явного отключения найденного config.

Это отличается от defaults, привычных по старым TypeScript. Канонический
владелец текущих значений:

```bash
tsc --version
tsc --help --all
tsc --showConfig
```
