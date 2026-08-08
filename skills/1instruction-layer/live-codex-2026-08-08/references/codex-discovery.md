---
description: "Codex runtime facts: effective instruction chain, precedence, fallback и byte budget."
read-when: "Instruction repair зависит от того, что Codex реально загрузил или какой file wins."
---

# Codex Instruction Discovery

Открывай, когда audit/repair зависит от того, какие `AGENTS.md` Codex реально
загрузил, какой файл имеет precedence или куда положить durable rule. Это
runtime facts для Codex, не общий закон instruction architecture.

## Effective Chain

Codex строит instruction chain один раз при старте run / TUI session:

1. **Global:** в `$CODEX_HOME` (обычно `~/.codex`) берётся первый непустой
   `AGENTS.override.md`; если его нет — `AGENTS.md`.
2. **Project:** от project root (обычно Git root) до текущей рабочей директории
   Codex проверяет на каждом уровне `AGENTS.override.md`, затем `AGENTS.md`,
   затем configured `project_doc_fallback_filenames`. На один directory входит
   не больше одного файла.
3. **Precedence:** файлы объединяются root → cwd. Более близкая к cwd guidance
   появляется позже и перекрывает более широкую при конфликте.
4. **Budget:** пустые файлы пропускаются; chain обрезается после
   `project_doc_max_bytes` (по умолчанию 32 KiB).

После правки начни новый run/session, если нужно доказать именно runtime loading:
существующая session уже построила свою chain.

## Placement Consequences

- **Thread prompt:** одноразовое условие текущей задачи.
- **Global `~/.codex/AGENTS.md`:** личные cross-repo defaults.
- **Repo root `AGENTS.md`:** durable repo/team conventions, команды и review
  expectations.
- **Nested `AGENTS.md` / override:** distinct path responsibility или реальное
  локальное переопределение; сама папка не причина создать файл.
- **Fallback filename:** instruction surface только если имя реально включено в
  `project_doc_fallback_filenames`.
- **Hook/test/permission/config:** enforcement и runtime behavior, которые prose
  не может гарантировать.

`AGENTS.override.md` заменяет обычный файл на том же уровне; не считай их двумя
одновременно активными owners. Если chain достиг byte limit, перенос важного
правила вниз или добавление ещё одного файла не доказывает, что правило загрузится.

## Verify

Используй smallest check, который доказывает спорный слой:

```bash
codex --ask-for-approval never "Summarize the current instructions."
codex --cd path/to/subdir --ask-for-approval never \
  "Show which instruction files are active."
```

Для текущего harness можно дополнительно проверить model-visible prompt через
`codex debug prompt-input`; plaintext TUI/session logs используй только если они
включены и нужен точный loading trace.

## Source

- https://learn.chatgpt.com/docs/agent-configuration/agents-md
  Current discovery order, overrides, fallback names, byte budget и verification.
