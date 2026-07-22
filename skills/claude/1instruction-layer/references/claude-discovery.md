---
description: "Claude Code runtime facts: CLAUDE.md, imports, path-scoped rules и skill loading."
read-when: "Instruction repair зависит от Claude Code load moment, import или path scope."
---

# Claude Code Discovery

Открывай, когда placement зависит от того, когда Claude Code загружает
`CLAUDE.md`, imports, path-scoped rules или skill metadata. Runtime facts ниже
не превращают одну repo convention в глобальный invariant.

## Что Грузится Когда

| Surface | Load moment | Use |
|---|---|---|
| `~/.claude/CLAUDE.md` | каждую Claude Code session | личный global context |
| project `CLAUDE.md` / `.claude/CLAUDE.md` | session start для project | team project instructions |
| nested `CLAUDE.md` | on demand при чтении subtree | folder-local context |
| `.claude/rules/*.md` без `paths` | project launch | topic rules |
| `.claude/rules/*.md` с `paths` | matching files read | path-scoped rules |
| Skill metadata | skill listing / discovery | routing only |
| Skill body/references | invocation / as needed | workflow depth |
| Hooks / permissions | runtime lifecycle | enforcement |

`CLAUDE.md` — context, не enforced configuration. Для block-before-action
используй permission/`PreToolUse` hook; для наблюдения discovery — live
`/memory` или `InstructionsLoaded` hook.

## `AGENTS.md` — Optional Shared Owner

Claude Code читает `CLAUDE.md`, не `AGENTS.md` напрямую. Если repo **уже
использует** `AGENTS.md` как cross-agent owner, `CLAUDE.md` может импортировать
его через `@AGENTS.md` и добавить только Claude-specific delta. Symlink тоже
возможен.

Это вариант совместного owner-а, не глобальный закон. Если live repo объявляет
`CLAUDE.md` canonical или держит другую policy, следуй ей. `depends-on`,
`related-when`, `veto-class` и shim conventions существуют только там, где их
задаёт project owner.

## Description Limits Зависят От Surface

- **Claude Code:** combined `description + when_to_use` в skill listing сейчас
  сокращается после 1,536 characters. Front-load use case; проверяй live docs,
  потому что runtime может измениться.
- **Portable Agent Skills / Claude Platform:** `description` max 1,024
  characters. Если один skill должен переноситься между surfaces, держи
  portable 1,024 ceiling.

Не приписывай превышению выдуманный failure mechanism вроде «skill точно не
найдётся». Валидируй фактический target surface и trigger behavior.

## Placement Rules

- Каждую session/весь project → root/project `CLAUDE.md`.
- Только при работе с path → nested instruction или `.claude/rules/` с `paths`.
- Только при повторяемом workflow trigger → skill.
- Длинное/редкое → owner file или conditional skill reference.
- Hard invariant → runtime enforcement, prose только объясняет.

Imports помогают поддерживать owner structure, но не экономят launch context:
imported content тоже загружается. Split ради файловой красоты не является
progressive disclosure.

## Проверка

1. Сначала назови target: Claude Code, portable Agent Skills или оба.
2. Проверь live repo owner policy и runtime discovery (`/memory` при доступности).
3. Для metadata измерь parsed description и проверь trigger near-misses.
4. Для root/subtree changes проверь conflicts и actual load moment.

Official runtime source:
`https://code.claude.com/docs/en/memory` и
`https://code.claude.com/docs/en/slash-commands`.
