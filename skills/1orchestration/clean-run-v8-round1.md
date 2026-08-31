# Clean-run v8 — первый кандидат

Exact manifest:
`56c0fa9901264bbe7ecf216b70d4c667eb27d1dc54a6198aeae92523e971fe8e`.
Чистый исполнитель прочитал только два runtime-файла candidate и task owners.

Случай: один read-only actor сравнивает `GOAL.md` и project Frame.

- Форма: direct; actor `18`, root next-decision `11`.
- Split отклонён: оба actor-а сохранили бы те же source units, а root получил
  бы reconciliation.
- Capability-change actor-а до запуска вызвал новый выбор и re-estimate.
- Слабый return без адресов и clause-map получил fail; dependency осталась
  заблокированной.
- Смоделированный upstream-change увеличил оценки до `19/12`; пересобраны
  только затронутые brief/evidence units, новый control-plane не создан.
- Trigger use/skip/near-miss, exact metadata parity, Russian body, zero refs,
  soft `20`, harm gate и authority boundary прошли.

Наблюдаемые, но не материальные gaps: skill не задаёт универсальный конец
source-discovery и точную весовую нормализацию units. Оба намеренно оставлены
вне runtime по причинам в `reviews-v8.md`.
