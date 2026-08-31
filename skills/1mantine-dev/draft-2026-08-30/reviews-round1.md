# Проверки черновика — round 1

## Траектория

Эталон: generic React/CSS или stale memory → installed cohort + официальный
source того же мажора → highest public handle → только более короткий и ясный
custom residue → материальный audit → наблюдаемая runtime-проверка.

Приняты и исправлены пять findings независимого trajectory-check:

- source priority при расхождении current docs и installed version;
- version-neutral resolver в always-on body;
- исключение по читаемости теперь проходит audit через «gap **или** цена»;
- audit-reference условен, а не обязателен для одиночной кнопки;
- trigger включает debugging/fixing, а годовой срез получил freshness-gate.

## Буквальные инструкции

Приняты и исправлены findings о source priority, freshness v9.5.2,
последовательности audit-шагов, trigger wording и длине near-miss.

Находка о составе references остаётся материальной: прежние
`help-center-map.md` + `placement.md` не возвращены; точное одобрение владельца
должно явно утвердить их замену на `audit.md` + `last-year.md`.

Находка о Product Frame отклонена: действующей skill-specific пары нет, а
корневая инструкция запрещает считать `skills/1<name>/product-frame*.md`
действующим owner-ом или создавать вторую правду в истории.

Первичный подсчёт literal-check (55/53/87) принят как доказательство, что
Markdown-маркеры нельзя считать единицами. Round 2 проверяет переписанную
семантическую карту: core 14; delta 16; audit 20.

## Clean run

Фактическая траектория сохранена в
[`receipts/clean-run-round1.md`](receipts/clean-run-round1.md). Прогон снял raw
grid, отдельные field states, homemade toast и wrapper 1:1 через public Mantine
handles; custom residue сохранился только по названной цене.
