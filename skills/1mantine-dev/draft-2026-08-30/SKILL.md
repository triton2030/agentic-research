---
name: 1mantine-dev
description: >-
  Use when building, debugging, reviewing, or upgrading Mantine components or
  forms.
---

# Mantine

## Контекст

Generic React/CSS prior агента может обойти существующий public-механизм Mantine
или применить API другой версии.

## Цель

Получать соответствующую текущей официальной документации Mantine реализацию,
которая полно использует релевантные public-компоненты и возможности, сокращает
объём кода и остаётся понятной для изменения.
Mantine не самоцель: читаемый локальный custom допустим только когда
public-механизм повышает совокупную сложность.

## Порядок

1. Зафиксируй task packet и определи `cohort` как одну exact resolved version,
   одинаковую для всех затронутых `@mantine/*`; если lockfile, package metadata
   или public types не дают такую версию, выведи `cohort: unknown`, остановись до
   обоих gate и не выбирай API.
2. При version uncertainty выполни [`references/last-year.md`](references/last-year.md);
   при audit uncertainty выполни [`references/audit.md`](references/audit.md);
   если неопределённости совместны, заверши version gate до audit и передай дальше
   неизменные packet, cohort и result.
3. После применимых gate сначала проверь public handle; оставляй local custom
   только если Mantine повышает совокупную сложность и custom остаётся читаемым.
