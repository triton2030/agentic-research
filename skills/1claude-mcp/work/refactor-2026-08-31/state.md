# Состояние рефактора 1claude-mcp

## Текущее состояние

`рефактор завершён` — третий кандидат после двух loss-check corrections
сохранён в `skills/1claude-mcp/work/refactor-2026-08-31/draft/`, финальная карта
потерь записана в `skills/1claude-mcp/cut.md`.

Цепь израсходованных состояний: `нужен новый commander's intent` → `готово
новое намерение` → `ожидается смысловой черновик` → `нужен полный авторский
черновик` → `готов полный черновик`.

Первая проверка потерь вернула работу к `behavior-protocol.md`: named capability
в clean launch теперь требует exact owner/address в `Context`, а отправка prompt
и прочитанных материалов в Anthropic снова ограничена host approval. Оба
разрыва исправлены. Повторная проверка нашла потерянный unnamed-other-model
trigger и неполное представление действующего официального Opus prompting
contract; они возвращены в `skill-short-description.md` и
`behavior-protocol.md` и исправлены до финальной проверки потерь. Живой
tracked owner и установленная проекция до утверждения полного черновика не
меняются.

Финальная проверка потерь пройдена: функция, end states и требуемые способы
сохранены; state `рефактор завершён` передаёт кандидата в обязательный
`check-approve.md`. Установка всё ещё запрещена до безусловного «да» владельца.

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
