# Prepare Opus Advisor

Вход: body выбрал нового advisor. Выход: approved advisor artifact для one-shot
или управляемой session.

- Попроси исследовать задачу и дать мнение, не изменяя внешнее состояние.
- Если outcome зависит от custom skill, MCP или named capability, включи её
  exact owner/address в `Context`: clean launch не загружает её автоматически.
- Откалибруй границы deliverable и verification/delegation effort к задаче; не
  добавляй generic rechecking или fan-out.
- До dispatch следуй host approval: prompt и прочитанные материалы уходят в
  Anthropic, а clean launch не является local sandbox.
- Для one-shot envelope укажи `mcp__claude_mcp__claude_ask`,
  `profile: opus_advisor`, готовый prompt, реальный `cwd` и без `session_id`.
- Оставь default `xhigh`; `max` выбирай только когда цена решения оправдывает
  более долгий свежий вызов.
