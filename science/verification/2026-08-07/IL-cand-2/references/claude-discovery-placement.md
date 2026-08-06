# Claude Code Discovery — Limits, Placement, Проверка

Открывается из [`claude-discovery.md`](claude-discovery.md).

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
