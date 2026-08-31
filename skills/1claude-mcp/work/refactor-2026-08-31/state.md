# Состояние рефактора 1claude-mcp

## Текущее состояние

`ожидается безусловное утверждение` — повторно проверенный кандидат после двух
loss-check и двух reviewer-волн сохранён в
`skills/1claude-mcp/work/refactor-2026-08-31/draft/`. Живой пакет не менялся.

Цепь израсходованных состояний: `нужен новый commander's intent` → `готово
новое намерение` → `ожидается смысловой черновик` → `нужен полный авторский
черновик` → `готов полный черновик`.

Loss-check вернул named capability exact owner/address, Anthropic data boundary,
unnamed-other-model trigger и current Opus prompting deltas. Wave 1 исправила
tool/model evidence, session Opus gate, recovery scope и неверные evidence
addresses. Wave 2 обнаружила завышенную когнитивную нагрузку и потерянные
`open_fresh`/follow-up seams; финальная версия разделена на короткие стадии.

После второй terminal wave владелец уточнил условие blocking режима:
`_ops/chat-recall/2026-08-31-212001-Codex-01a0589c.md:18`. Router теперь выбирает
blocking one-shot, когда полезной параллельной работы нет, и yielded route —
только когда она есть. Причинно затронутые байты и semantic evidence повторно
проверены root; receipt сохранён в `validation-evidence.md`, новые reviewers
запрещены протоколом. Затем владелец выбрал задачу и цель вместо мысленного
протокола — там же, `:20-21`; это инвалидировало прежнее утверждение. Новый
exact receipt сохранён в `validation-evidence.md`. Установка всё ещё запрещена
до безусловного «да» владельца.

## Основание решения

Из GOAL, Product Frame и P-003/P-007 выведено: короткий запрос владельца
означает clean-room рефактор всей функции, но история не становится вторым
runtime owner. Поэтому долговечный результат будет записан только после
утверждения, а эта папка хранит состояние, evidence и карту потерь.

## Источники старого пакета

Владелец пакета подтверждён `experiments/claude-bridge/AGENTS.md` и разделом
Change Rule в `experiments/claude-bridge/README.md`:

- `experiments/claude-bridge/codex-skill/1claude-mcp/SKILL.md`;
- `experiments/claude-bridge/codex-skill/1claude-mcp/agents/openai.yaml`;
- `experiments/claude-bridge/codex-skill/1claude-mcp/references/claude-native-tools.md`;
- `experiments/claude-bridge/codex-skill/1claude-mcp/references/existing-sessions.md`;
- `experiments/claude-bridge/codex-skill/1claude-mcp/references/mcp-failure-handling.md`;
- `experiments/claude-bridge/codex-skill/1claude-mcp/references/opus-agent-prompting.md`;
- `experiments/claude-bridge/codex-skill/1claude-mcp/references/session-adapter.md`.

Истории до этого файла не существовало. Принятые смыслы и буквальные цитаты
сохранены в `skills/1claude-mcp/origin.md`; финальный `cut.md` записан после
проверки потерь.
