# Проверка скила `1planning` — роль instructions

## Контекст

Владелец — не программист; он строит продукт MAVO агентами и держит свои
глобальные скилы в этой мастерской (`/Users/triton/Documents/GitHub/agentic-research`).
Автор (Claude) переработал семью планирования: три скила — `1planning`,
`1plan-map`, `1plan-task` — сведены в один `1planning`. Файл задачи стал
«роутером»: цель, ссылки на места документации с пометкой «зачем», что не
входит, чеклист проверок готовности. Пересказ документации, отчёты,
доказательства, состояние и история решений из плана уходят. Это одобрил
владелец; его слова и одобренное предложение лежат в источниках ниже —
разговора с ним ты не видишь, поэтому опирайся на них, а не на пересказ автора.
Черновик ещё не установлен: твоя находка может изменить его до установки.

Ты — одна из трёх независимых ролей проверки по контракту владельца для
скилов; соседние роли проверяют другие оси, их ответов ты не видишь.

## Что читать

Черновик — объект проверки (пути от корня мастерской):
- `skills/shared/1planning/portable/SKILL.md`
- `skills/shared/1planning/portable/references/форма-планов.md`
- `skills/shared/1planning/portable/assets/` — шаблоны; `map/` — Bases без изменений
- `skills/shared/1planning/portable/scripts/check_plans.py` — механизм проверки формы
- `skills/shared/1planning/platforms/codex/agents/openai.yaml`

Прежние пакеты, для сверки потерь:
- `skills/1planning/versions/installed-2026-09-09/SKILL.md`
- `skills/shared/1plan-map/portable/` и `skills/shared/1plan-task/portable/` — SKILL.md, references, assets

Намерение, граница и карта потерь автора — `skills/1planning/work/router-2026-09-25/`:
`intent.md`, `cut.md`, `одобренное-предложение.md`. Это заявка автора, не evidence.

Слова владельца — первичка с датами:
- `/Users/triton/Documents/My_projects/mavo3/_ops/chat-recall/2026-09-25-130106-Claude-f6bca69a.md` — идея, одобрение, условие Bases, просьба о проверке Codex
- `/Users/triton/Documents/My_projects/mavo3/_ops/chat-recall/2026-08-24-130300-claude-7756c5b8.md` — прежние решения о форме задач; часть отменена 2026-09-25 записями с `supersedes`
- `_ops/chat-recall/2026-08-26-220614-claude-4ee6bbef.md` — раскрой на тройку и протокол владельца

Контракт скилов: `/Users/triton/.claude/skills/1skill-creation/SKILL.md`,
его `references/check-approve.md`, `references/agent-defaults.md` и файл твоей
роли (ниже). Наука управляющего текста —
`/Users/triton/.claude/skills/1agent-steering/references/steering-science.md`.

Evidence автора — `skills/1planning/work/router-2026-09-25/`: `evidence-checker.md`
(тесты механизма и прогон на живом проекте) и `evidence-probe.md` (свежий агент
собрал роутер по черновику в копии проекта; неподвижный снимок файла —
`probe-router-snapshot.md`, эпик — `probe-epic.md`, песочница — `/tmp/planning-probe`).

Живой проект-пример: `/Users/triton/Documents/My_projects/mavo3/_ops/plans/` —
файлы прежней формы и два Bases; `/Users/triton/Documents/My_projects/mavo3/AGENTS.md`.

## Цель

Проверь необходимость требований по роли `/Users/triton/.claude/skills/1skill-creation/agents/check-instructions.md`: лишние и повторные требования в теле, reference и шаблонах; потерянные существенные условия владельца и прежних пакетов (сверь с картой потерь `cut.md` — верно ли она описывает снятое и сохранённое); дорогие снятия без различающей пробы. Что здесь не выполнено и чем это видно?

## Границы

- Ничего не меняй в файлах; только чтение. Не вызывай инструменты claude-mcp —
  работай файлами и shell.
- Оцени только свою ось. Если вывод зависит от оси соседа, назови связанный
  вопрос одной строкой.
- Оправдательный вердикт допустим: держится — так и скажи, не придумывай находок.

## Готово, когда

Ответ строго по схеме:

```
## Вердикт
Одна-три фразы в границах роли.
## Находки
### N1 — короткое имя
- Место: файл:строка
- Наблюдение: что там (цитата до двух строк)
- Основание: слова владельца, контракт или наблюдение; догадка помечена «прогноз»
- Неверный выбор агента, который это вызывает
- Минимальная правка
## Что держится
## Непроверенное
```
