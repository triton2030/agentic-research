# Аудит B — соответствие черновика 1chat-recall протоколу и словам владельца

## Контекст
Claude переписал глобальный скил `1chat-recall` по новым словам владельца: скил — про понимание владельца как личности (намерения, чувства, отношение), а корпус читает только отдельный агент-психолог с готовым промптом в `agents/`; в Claude — повторно опрашиваемый субагент на сессию, в Codex — фоновый тред на проект. Черновик прошёл две волны проверки субагентами Claude; владелец считает, что соответствие скилов протоколу проверяет именно Codex, «с точки зрения агента, который бы это использовал». Ты — Codex; проверь как агент, который получит этот текст промптом.

Первичные артефакты (read-only):
- Черновик (Claude-вариант — основной): /Users/triton/Documents/GitHub/agentic-research/skills/1chat-recall/work/owner-picture-2026-09-08/draft/claude/ — SKILL.md, agents/psychologist.md, references/retrieval.md, references/capture.md, references/integrity.md. Codex-вариант: .../draft/codex/ (отличия: allowed-tools, ROOT, раздел «Психолог», Контекст роли, agents/openai.yaml).
- Прежний установленный пакет: /Users/triton/Documents/GitHub/agentic-research/skills/claude/1chat-recall/.
- Слова владельца сегодня: /Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-09-08-161113-claude-4c325be0.md (весь файл; строки 18–24). Ранее: /Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md:33,37; /Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-13-120315-claude-8e9d58e3.md:21; /Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-09-030700-codex-019fe36a.md:22,28.
- Протокол создания скилов владельца: ~/.codex/skills/1skill-creation/SKILL.md и references/ (в частности refactor.md «Адресная правка намерения», skill-short-description.md, behavior-protocol.md, reference-files.md), и его наука управления текстом: ~/.codex/skills/1agent-steering/references/steering-science.md.
- Product owner скила: /Users/triton/Documents/GitHub/agentic-research/skills/shared/1chat-recall/product-frame.md.
- Материалы автора (маршрут, допуск, потери, решения по находкам): /Users/triton/Documents/GitHub/agentic-research/skills/1chat-recall/work/owner-picture-2026-09-08/intent.md, reviews.md, verification.md; верхний раздел /Users/triton/Documents/GitHub/agentic-research/skills/1chat-recall/cut.md.

## Цель
Найти, что в черновике не выполняет протокол `1skill-creation`, науку `1agent-steering` или слова владельца, и чем это видно: (1) неназванные владельцем части должны быть сохранены дословно — где они изменены без его слов; (2) у каждой строки Контекста/Задачи/Цели тела, retrieval.md и роли — источник; (3) в каждом условном наборе не больше семи инструкций, у каждой — причина; совместная нагрузка в момент Retrieval; (4) роль психолога самостоятельна: агент с одной ролью и корнем проекта может работать, форма ответа проверяема; (5) «сломанный джин»: где буквальное выполнение оставляет владельца без желаемого — портрет без адресов, «прямые слова» вместо вывода, «ни опор» после пары запросов по фразе, вывод психолога, перебивающий цитату, лишние вопросы владельцу; (6) description ≤ 200 символов по форме «Use when …». Судить надо также решения автора из intent.md «Авторские решения к показу владельцу»: где они расходятся со словами владельца.

## Границы
Read-only: ничего не изменяй; не вызывай инструменты claude-mcp и `claude_ask` — работай файлами и shell. Аудит, не переделка: минимальная правка в находке, не новый текст скила. Право сказать «держится» по любому пункту есть; выдуманные находки хуже пустого списка. Дословные слова владельца к переписыванию не предлагай.

## Готово, когда
Один ответ по схеме: первая строка — «Вердикт: годен к предъявлению владельцу / годен с правками / не годен» с одной фразой основания; затем список находок, каждая — `адрес (файл:строка) → нарушенное требование точной цитатой из протокола или слов владельца → чем видно в байтах → минимальная правка`; затем блок «Держится» по пунктам 1–6; в конце — «Расхождения с решениями автора» из intent.md, если есть.
