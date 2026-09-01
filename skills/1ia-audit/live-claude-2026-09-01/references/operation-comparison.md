---
description: "Detailed Gate 2-4 operations for reconstructing comparable baseline and candidate reader operations and proving their material delta."
read-when: "Read only after admission and authority are resolved; required before any IA repair or shape recommendation."
---

# Operation Comparison

Этот файл владеет детальными операциями Gate 2–4. Основной `SKILL.md` владеет
порядком фаз и stop-условиями.

## Содержание

- Gate 2 — current/baseline operation
- Gate 3 — candidate operation
- Gate 4 — material delta
- Контрастивные сцены

## Gate 2 — Восстанови Current/Baseline Operation

Не пиши общую фразу вроде «читатель находит информацию». Пройди только реально
нужные звенья одной операции:

1. Зафиксируй exact trigger/query, с которого начинается работа reader-а.
2. Покажи, как он обнаруживает confirmed owner, либо зафиксируй первый
   наблюдаемый wrong turn.
3. Назови minimum sufficient slice, без которого answer нельзя понять или
   применить.
4. Назови конкретный understand/use act: какое решение, действие или проверку
   выполняет reader.
5. Назови exact edit anchor, где меняется mutable answer.
6. Назови обязательные соседние edit hops; pointer/view не считай edit anchor-ом,
   если durable truth там не меняется.
7. Назови affected holders/dependent views только когда их действительно требует
   эта операция.
8. Назови bounded validation, доказывающую корректность после update.
9. Для каждого friction укажи адресуемое body/usage evidence: лишний hop,
   неполный slice, ambiguity, duplicate edit, conflict или oversized blast.
10. Для shallow/pass-through container проведи deletion test: его удаление
    убирает operation cost или только переносит её в соседей?
11. Если direct bodies недостаточны либо нужны semantic/exact/graph candidates,
    вернись к прямому route на `cli-evidence-tips.md` из основного `SKILL.md` и
    принеси фактический coverage/gap, не tool rank.

**Результат gate:** полный `current|smallest viable baseline trace`:
`trigger → owner discovery → slice → use → edit anchor/hops → dependents →
validation` плюс адресуемый friction или `none observed`. Пропущенное звено
пометь `not applicable|unknown`, не достраивай гладкой прозой.

## Gate 3 — Построй Candidate Operation Независимо

1. Выбери smallest viable candidate, который заявляет устранение конкретного
   current friction. Greenfield сравнивай с наименьшей рабочей формой, обычно
   одной section/file у live owner-а.
2. Запусти candidate с того же trigger/query и к тому же mutable answer; иначе
   сравниваются разные information jobs.
3. Восстанови owner discovery заново; не считай новую taxonomy автоматически
   более discoverable.
4. Назови candidate minimum slice и проверь, не потерялся ли необходимый context
   за новой seam.
5. Назови use act, edit anchor, edit hops, dependent views и validation теми же
   категориями, что в baseline trace.
6. Отметь каждый новый, удалённый или перемещённый hop; не сворачивай их сразу в
   итоговое число шагов.
7. Укажи, где живёт normative truth, а где navigation/teaching/generated view.
   Candidate с двумя independently editable truth surfaces не допускается.
8. Для split/merge/move повтори independence test: какая сторона получила
   отдельный reader, owner, lifecycle, update trigger или check?
9. Проверь reversibility и future constraint: какую следующую правку candidate
   делает дешевле, а какую необоснованно закрывает?
10. Если нужны формы для greenfield, второго reading axis или cross-cutting
    material, вернись к прямому route на `design-patterns.md` из основного
    `SKILL.md`; ladder не заменяет operation trace.

**Результат gate:** полный `candidate trace` на том же job и перечень `new /
removed / moved hops + truth/view direction + independent seam evidence`.
Candidate нельзя описать с той же конкретностью, что baseline → `unknown`, не
recommendation.

## Gate 4 — Докажи Material Delta

1. Сопоставь baseline и candidate звено к звену; не сравнивай один подробный
   trace с одной абстрактной фразой.
2. Для каждого отличия назови affected dimension:
   `retrieval | context completeness | comprehension | update locality |
   conflict surface | validation | edit blast radius`.
3. Припиши каждому delta адресуемое evidence либо `hypothesis`; ожидаемая
   «аккуратность» формы evidence не является.
4. Отдели signal от evidence. Length, headings, links, similarity, folder
   symmetry, search rank и template conformity только номинируют smell.
5. Counts вроде «пять шагов против трёх» допустимы лишь как summary уже
   прочитанных hops; число само не доказывает improvement.
6. Для каждого claimed gain проверь ближайшую потерю: split может сократить
   slice и добавить hops; merge может убрать hops и увеличить irrelevant context.
7. Если evidence изменило premise, owner или job, вернись к clean re-anchor и
   перестрой обе traces; не защищай preferred candidate.
8. Классифицируй итог как `material gain | material loss | trade-off |
   no material delta | unknown`. `Unknown` означает недостаток evidence;
   `no material delta` — доказанное отсутствие значимого различия.

**Результат gate:** `link-by-link delta table + dimension + evidence status +
net materiality`. Без material delta жанровая, таксономическая или эстетическая
разница не является IA-улучшением.

## Контрастивные Сцены

**Greenfield не получает бесплатную победу.** Предложен hub-and-spoke для двух
reading axes. Baseline — одна section у live owner-а, а не «никакой структуры».
Пока второй axis не создаёт регулярный independent reader path, hub добавляет
container и backlink obligations без material gain: recommendation остаётся
одной section.

**Антипример.** «Current path — пять шагов, candidate — три» без confirmed
owner-а, одинакового trigger, body evidence и названных changed hops — та же
metrics-as-verdict ошибка в новой форме. Operation pair ещё не построена.
