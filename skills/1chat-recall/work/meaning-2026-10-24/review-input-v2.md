# Вход проверки — поправка о наборе контекста, 2026-10-24

Владелец (`_ops/chat-recall/2026-10-22-195852-claude-code-83f01dd5.md#recall-d0d531162ac9441cb4c1f80c4e79c2db`):
набирать контекст из цитат — главное в скиле, в том числе во время обсуждения,
чтобы не начинать с нуля; агент помнит, что это прошлое, скорее всего
устаревшее, но оно помогает понять намерения и желания.

Правки:

- `skills/{claude,codex}/1chat-recall/SKILL.md` — «Why this exists» и режим
  Retrieval (`git diff`): снят запрет искать во время обсуждения;
- глобальные инструкции: `skills/1instruction-authoring/work/claude-global-2026-10-24-v2/`
  и `codex-global-2026-10-24-v2/` — `original.md` против `after.md`;
- `skills/shared/1chat-recall/product-frame.md` — «Цель» и строка истории (`git diff`).

Остальной скил (`references/retrieval.md`, `capture.md`) не менялся.
Контракт: `~/.claude/skills/1skill-creation/SKILL.md`.
