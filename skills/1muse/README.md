---
description: "История скила 1muse: вызов Muse Wonder из Claude Code через Muse Code."
---

# 1muse

Эта папка хранит историю `1muse` и не является пакетом скила.

Живой владелец для Claude Code — `skills/claude/1muse/`; установленная копия
лежит в `~/.claude/skills/1muse/`. У Codex такого скила нет.

Заказ владельца —
`_ops/chat-recall/2026-10-13-134632-claude-bee1af57.md#recall-1091394493d54b9fb038c0ef5d7b932c`.
Образец формы — `1gemini`, история в `skills/1gemini/`.

- `work/probes-2026-10-13.md` — замеры поведения `muse exec`, из которых
  выведена форма скила, и проба черновика свежими агентами.
- `versions/draft-2026-10-13/` — первый установленный снимок пакета.
- `versions/draft-2026-10-13-v2/` — снимок после переноса идей `1codex`;
  что перенесено и чем проверено — `skills/1muse/work/codex-ideas-2026-10-13.md`.
- Вопрос к владельцу о том, какую работу отдавать Muse, лежит в общем файле
  `skills/1gemini/work/roster-2026-10-13.md`.
- `versions/draft-2026-10-13-v3/` — снимок после пробы исполнителей на HTML-странице:
  `skills/1muse/work/html-writer-2026-10-13.md`.
- `versions/draft-2026-10-13-v4/` — умолчание сменено владельцем на `muse-wonder-full-1.0` + `xhigh`:
  `_ops/chat-recall/2026-10-13-134632-claude-bee1af57.md#recall-64f041739dc045febe04fb9dd65c9410`.
- `versions/draft-2026-10-13-v5/` — после аудита самим Muse:
  `work/audit-2026-10-13.md`.
- `work/steer-probe-2026-10-14/` — рабочие клиенты протокола `muse serve`: `probe_echo.py`
  на бесплатном эхо-провайдере и `probe_live.py` с репликой в идущий ход.
- `work/t3-probe-2026-10-14.md` — проба Muse и Gemini через MCP-сервер T3 Code
  на одной задаче; итоги — в справках обоих скилов.
