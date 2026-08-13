# Origin

## Владелец

Source root: `/Users/triton/Documents/My_projects/mavo-assets`.

- `_ops/chat-recall/2026-08-13-153357-codex-019ffa9f.md:21-25` — цель,
  global `Workspace/Recraft`, prompt provenance, прямой Recraft trigger, охват
  всех инструментов.
- `_ops/chat-recall/2026-08-13-153357-codex-019ffa9f.md:26-29` — дневная папка
  без года, парные PNG/Markdown, запрет short-prompt exploration, V4.1 default.
- `_ops/chat-recall/2026-08-13-154355-Codex-019ffa9f.md:19` — после каждой
  генерации сообщать остаток кредитов.
- `_ops/chat-recall/2026-08-13-154355-Codex-019ffa9f.md:20` — выбран один
  результат на вызов по умолчанию; native vector сохраняется как SVG.
- `_ops/chat-recall/2026-08-13-154355-Codex-019ffa9f.md:21-22` — owner brief не
  копируется в prompt: количественное требование сначала переводится в слова,
  вызывающие нужный визуальный эффект.

## Recraft

- Официальная MCP-документация: <https://www.recraft.ai/docs/mcp-reference/tools>
- Официальное семейство V4.1: <https://www.recraft.ai/docs/recraft-models/recraft-v4-1>
- Официальный prompt guide: <https://www.recraft.ai/docs/prompt-engineering-guide/prompting-with-recraft-v4>
- Официальный universal template: <https://www.recraft.ai/docs/prompt-engineering-guide/prompt-templates/universal>
- Live remote MCP schema, fresh Codex probe 2026-08-13: 21 tools; current
  `generate_image` enum includes `recraftv4_1` and `recraftv4_1_pro`, but not
  Utility/Vector ids.

## Field evidence

- <https://ropewalk.ai/blog/recraft-v4-pro-svg-guide-2026> — independent June
  2026 tests; used only for vector prompt habits, not as API truth.
