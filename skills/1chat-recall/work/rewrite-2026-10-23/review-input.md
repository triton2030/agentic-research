# Вход проверки — переработка 2026-10-23

## Граница заказа

Полная переработка `SKILL.md` и `references/capture.md` скила `1chat-recall`
по поправке владельца: записывать только то, что изменит будущий выбор;
согласие с предложением агента записывать вместе с предложением; любая запись —
датированный контекст. Владелец просил переписать, а не дописывать правила.
Сюда же входят абзац Acceptance capture продуктовой рамки и абзац о записи
в глобальных инструкциях Claude и Codex. Retrieval, Integrity, search-mechanics
и helper не меняются.

## Что читать

- Замысел, источники и диагноз: `intent.md` рядом.
- Черновик: `draft/claude/SKILL.md`, `draft/claude/references/capture.md`;
  `draft/codex/` отличается двумя рантайм-строками.
- Прежняя редакция: `skills/claude/1chat-recall/SKILL.md`
  и `references/capture.md` (коммит `0f247a1c`, ещё не тронуты).
- Карта сохранённого и снятого: `cut.md` рядом.
- Продуктовая рамка: `skills/shared/1chat-recall/product-frame.md`
  (абзац Acceptance capture уже обновлён, незакоммичен — `git diff`).
- Глобальные инструкции: `skills/1instruction-authoring/work/claude-global-2026-10-23/`
  и `codex-global-2026-10-23/` — `original.md` и `after.md`.
- Слова владельца: `_ops/chat-recall/2026-10-22-195852-claude-code-83f01dd5.md`,
  записи от 2026-10-23.
- Применимый контракт: `~/.claude/skills/1skill-creation/SKILL.md`,
  `~/.claude/skills/1agent-steering/references/steering-science.md`.

## Evidence

Пробы свежими агентами — `probe-result.md` рядом.
