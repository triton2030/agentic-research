# Состояние рефактора — 1orchestration

Состояние: `нужен полный авторский черновик` — смысловой черновик чистой
комнаты принят и сохранён в `clean-room-draft.md`: 13 самостоятельных единиц,
структура «мир → три цели → Разрез → Поручение → Командование → старшинство и
фальсификатор».

Цепь израсходованных состояний: `нужен новый commander's intent` → `готово
новое намерение` → `ожидается смысловой черновик` → `нужен полный авторский
черновик`.

Чистота комнаты: исполнителю ушли только Уникальный контекст, три цели и момент
вызова, плюс один разрешённый внешний файл
`science/how-to-command-agents-with-text.md`. Он сам раскрыл единственную
утечку: среда сессии автоматически показывает список доступных скилов, где есть
однострочный `description` живого `1orchestration`. Тело старого пакета он не
открывал и поиск по предмету не запускал. Утечка ограничена trigger-строкой и
формы старого текста не несёт. Разбор механики v10 остаётся у root в
`mechanics-map.md` и исполнителю не передавался.

## Почему новый круг, а не установка готового кандидата

`skills/1orchestration/draft-v12/` заморожен 2026-08-31 12:47 с вердиктом
`ready_exact_candidate; needs installation approval` и сегодня пересчитан
побайтово: манифест `7ae572d1c9cab1f6fa35c8dff817e1a52e47563f29e7f9c97c35590b590af0c4`
совпал. Но вердикт выдан под протоколом `1skill-creation`, которого больше нет:
`reviews-v12.md` записал его как `c2ca7634…`, живой сегодня — другой файл,
переписанный до v13 в 19:07. Доктрина композиции управляющего текста
`science/how-to-command-agents-with-text.md` создана в 19:14, ещё позже.
Поэтому v12 входит в этот круг как evidence, а не как форма и не как готовый
к установке пакет. Тот же ход уже применён к соседям: `1plan-task`,
`1plan-map` и `1planning` открыли круги `*-2026-08-31-doctrine` по этой же
причине.

## Источники старого пакета

Владелец пакета подтверждён `skills/shared/README.md`:

- owner: `skills/shared/1orchestration/portable/SKILL.md`
  (`0dab19d7bf285693f84f4eebac9ca2733698a9d0abb40fd604c61215a6edbf7e`);
- Codex UI metadata:
  `skills/shared/1orchestration/platforms/codex/agents/openai.yaml`;
- tracked projections: `skills/claude/1orchestration/`,
  `skills/codex/1orchestration/`;
- installed projections: `~/.claude/skills/1orchestration/`,
  `~/.codex/skills/1orchestration/` — совпадают с owner побайтово.

Живой пакет — v10. Кандидаты v11 (11:23) и v12 (12:47) не установлены ни в
одну из шести поверхностей.

## История

- `skills/1orchestration/origin.md` — происхождение правил v1–v5 с адресами
  слов владельца;
- `skills/1orchestration/cut.md` — карта потерь, последняя запись v12;
- `skills/1orchestration/evidence.md` — чем проверено, v1–v5;
- `skills/1orchestration/README.md` — карта владения и внешние швы;
- неустановленные кандидаты: `draft-v11/`, `draft-v12/` вместе с
  `refactor-v11.md`, `refactor-v12.md`, `reviews-v11.md`, `reviews-v12.md`,
  `product-frame-v11.md`, `product-frame-v12.md`.

## Новый вход стадии

- `1skill-creation` v13 — установленный протокол
  (`skills/shared/1skill-creation/portable/`);
- `science/how-to-command-agents-with-text.md` — доктрина композиции
  управляющего текста, выведенная 2026-08-31 и не существовавшая, когда
  писались кандидаты v11 и v12.
