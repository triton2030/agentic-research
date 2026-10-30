# Сырой receipt маршрутизации установленного скила

- дата: `2026-08-29`
- граница: проверка маршрутизации только для чтения; до выбора из перечисленных файлов установленных скилов были прочитаны только поля `name` и `description` во frontmatter. Тела `SKILL.md` не читались, во время прогона маршрутизации файлы не изменялись.

## Случаи

### use

- фраза: `Рефакторни этот модуль перед добавлением новой возможности.`
- выбран: `1readable-code`
- прочитанное `description`:

  > Use before writing or changing code. Contract choices use codebase-design in Claude or 1codebase-design in Codex.

- наблюдаемое основание маршрутизации: `description` предписывает использовать скил перед написанием или изменением кода; рефакторинг модуля изменяет код.

### skip

- фраза: `Исправь одну опечатку в тексте отчёта.`
- выбран: `none`
- учтённые прочитанные `description`: `1readable-code` срабатывает перед написанием или изменением кода; `1codebase-design` срабатывает при решении о контракте кода; `1context-refactor` срабатывает при повторно сделанной работе, лишнем чтении или рефакторинге инструкций либо контекста. Фраза не совпала ни с одним из этих наблюдаемых триггеров.

### near-miss

- фраза: `Выбери интерфейс адаптера между API и хранилищем.`
- выбран: `1codebase-design`
- прочитанное `description`:

  > Use when code work reaches a contract decision: choosing, reviewing, or changing an interface, seam, adapter, port, component boundary, dependency boundary, or test surface. Combine with 1domain-modeling when the contract carries a business rule; use 1readable-code when the contract stays stable.

- наблюдаемое основание маршрутизации: `description` прямо называет решение о контракте, связанное с интерфейсом или адаптером.

## Пути прочитанных frontmatter

- `/Users/triton/.codex/skills/1readable-code/SKILL.md`
- `/Users/triton/.codex/skills/1codebase-design/SKILL.md`
- `/Users/triton/.codex/skills/1context-refactor/SKILL.md`

## SHA-256 установленного артефакта

- точный установленный путь: `/Users/triton/.codex/skills/1readable-code/SKILL.md`
- команда: `shasum -a 256 /Users/triton/.codex/skills/1readable-code/SKILL.md`
- результат: `1bcb9e27fd2e355a2b74501063fec476c105bd2423cbefae5ad66438eda5a42a`
