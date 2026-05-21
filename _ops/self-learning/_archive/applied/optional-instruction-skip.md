# Optional Instruction Skip

## Observation

Когда инструкция в SKILL.md помечает шаг как «опционально, не выдумывай ради ритуала, пустой ход норма» — агент по дефолту **пропускает** шаг даже когда есть что записать. Default-skip побеждает default-write. Anti-ritual framing создаёт over-cautious threshold для opt-in actions; нет explicit user-facing failure → нет stress → пропуск.

## Counter

- 2026-05-19 [Claude Opus 4.7]: первая итерация Self-Learning секции в `1work-review`. Tone был «опционально, не выдумывай»; два subsequent агента (closeouts в этой сессии) записали ноль observations. Пользователь дал явный feedback «писать смелее, относитесь как к свалке».
- 2026-05-20 [GPT-5.5]: после closeout по Claude/Gemini MCP user спросил, не хочу ли я что-то исправить в агентской среде через самообучение. Я увидел self-learning candidate, но вместо записи начал спрашивать уровень исправления. User прервал и ткнул в `1work-review`: self-learning должен default-to-write, а не default-to-ask.

## Possible upgrade

Для opt-in actions в SKILL.md (не только self-learning): если хочешь чтобы агенты выполняли — tone «делай смело, default to action, ничего не сломаешь» вместо «не выдумывай ради ритуала». Список positive triggers «когда делать» с низким bar лучше disclaimer «когда не делать». Anti-ritual framing нужен только для actions с реальным cost (write canonical text, modify runtime); для cheap reversible writes (папка-свалка) — наоборот, нужно push.

Релевантно: любые optional steps в SKILL.md (не только self-learning).
