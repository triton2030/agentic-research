# Состояние рефактора — 1orchestration

Состояние: `установлено`. Владелец безусловно утвердил точную версию
(`_ops/chat-recall/2026-08-31-222311-claude-a7a340d8.md`, запись
2026-08-31T23:38:26 «Да, устанавливай как есть»), и пакет
`83db2e5dda2fb64aedb220ad04c31e9291f9b57b53b5d9719016c97cd682f744` записан в
шесть поверхностей: tracked owner `skills/shared/1orchestration/`, проекции
`skills/claude/1orchestration/` и `skills/codex/1orchestration/`, живые пакеты
`~/.claude/skills/1orchestration/` и `~/.codex/skills/1orchestration/`. Хэши
сверены после записи: `SKILL.md 018693ff…` везде, `openai.yaml 179adf85…` в
четырёх местах, где он предусмотрен.

Цепь израсходованных состояний: `нужен новый commander's intent` → `готово новое
намерение` → `ожидается смысловой черновик` → `нужен полный авторский черновик`
→ `готов полный черновик` → `готово обновлённое намерение` → `готов полный
черновик v2` → `рефактор завершён` → `установлено`.

Кандидат v1 (`draft/`, 18 нумерованных единиц) остаётся в этой папке как
альтернатива, которую владелец не выбрал.

**Открытые расхождения, принятые владельцем при утверждении:** три блока держат
2187 знаков против названной им тысячи (`D7`); три его дословные цитаты сняты из
тела (`D2`); по собственному мерилу скила читатель удерживает около 31 вещи при
объявленном пороге около 20.

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
