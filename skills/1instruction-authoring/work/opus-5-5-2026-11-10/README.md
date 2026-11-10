# Доставка AGENTS.md и осадок осторожности — 2026-11-10

Адресная правка. Снимок — [`versions/v21/`](../../versions/v21/portable/SKILL.md).
Владелец одобрил пакет предложения: «Да, внеси все эти поправки»
(сессия Claude Code `4ab2091c-fb00-4f6d-beaf-4c58eff3642c`).

| Где | Было | Стало | Основание |
|---|---|---|---|
| `SKILL.md`, доставка | `CLAUDE.md` отключает только папочные `AGENTS.md`; строки одного Claude — в `CLAUDE.md` | любой `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` в рабочей папке и выше отключает все `AGENTS.md`; строки одного Claude — в `.claude/rules/` или в `CLAUDE.md`, начинающемся с `@AGENTS.md` | code.claude.com/docs/en/memory, раздел «AGENTS.md», прочитан 2026-11-10 |
| `SKILL.md`, нужна ли строка | — | абзац об осадке осторожности: область, причина и исключение внутри правила; снятие запрета с ушедшей причиной | Prompting Claude Fable 5.2 |
| `SKILL.md`, раскладка | «необратимая граница стоит заметно» | отдельной строкой без капса; неизгибаемую держит хук | Claude Code best practices |
| `verification.md` | — | `/doctor prompt-audit` до проверяющих | code.claude.com/docs/en/memory, «Audit your instruction files» |
| `discovery.md`, шаг 2 | читатель на каждую отслеживаемую папку | каждая папка прочитана целиком; малые root читает сам, читатель — где объём засорит окно | Claude Code best practices: защита окна больше не главный довод; Fable 5.2 о постоянном делегировании |

В этом репо рядом лежат `_ops/chat-recall/CLAUDE.md` (`@AGENTS.md`)
и `AGENTS.md`: по новому правилу это верная форма, правка не нужна.

Проверка: установка в Claude и Codex сверена `--check`. Проб не было.
