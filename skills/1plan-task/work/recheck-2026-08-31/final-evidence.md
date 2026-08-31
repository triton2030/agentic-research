# Финальное evidence — 1plan-task

## Проверки и решения

- Волна 1: приняты goal, состав approved packet, положительная обязанность
  повторить редкие critical lines, state/evidence и map handoff.
- Fresh Eyes: снят глобальный first-epic gate; task следует принятому map
  contract и не пересекается с соседней задачей.
- Волна 2: приняты budget non-split, durable completion traces и общий handoff
  human-visible task-state владельцу карты.

## Trigger

- use: «Отложи этот утверждённый task-файл» → `1plan-task`;
- skip: «Перестрой карту эпиков проекта» → `1plan-map`;
- near-miss: «Реши, какую работу утвердить следующей» → `1planning`.

Frontmatter и `agents/openai.yaml` дают тот же выбор.

## Active set

Консервативный статический recount: create `40`, continue `39`, handoff `38`,
defer/close `31`. Mixed-run прошёл все lifecycle falsifiers с family peak `18`;
self-replay финальной дельты даёт `20`. Разница возникает потому, что
статический счёт включает каждое поле контракта, а исполнитель в одном ходе
держит только текущий route и адресует остальное в task-файле. Это остаточный
риск, а не заявленный hard pass бюджета.

## Falsifiers финальной дельты

- 21-я единица не разделила единый результат автоматически;
- create записал полный task-файл;
- continue обновил state/evidence/Next;
- handoff записал единственного writer;
- defer передал dashboard-visible state карте;
- close прошёл только по whole-result proof.

## Exact candidate

SHA-256 package fingerprint:
`5fe51a22e11650c0d180a7f6f66fbed7c780a51903e0d8470d546c85cee35403`.
