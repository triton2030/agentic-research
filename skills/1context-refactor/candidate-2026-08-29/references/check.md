# Проверка поведенческого claim

## Цель

Отличить возможность выполнить новый текст от изменения поведения.

1. Зафиксируй resolved execution environment проверяемого эпизода.
2. Выбери один matched comparator: routing — применимый и неприменимый случаи;
   изменение — тот же случай old/new; сохранение — holdout с шумом;
   placement — none/always/selective; projection — validator и parity.
3. Наблюдай цепочку `текст достигнут → решение изменилось → эффект дожил до
   завершения`.
4. Самоотчёт и один удачный output доказывают только возможность; вероятностный
   claim требует повторов в том же environment.
5. Если comparator зеленеет без заявленной правки, claim остаётся candidate.
6. Не устанавливай спорные проекции до различающего verdict.

Верни `claim · comparator · наблюдение · verdict · residual risk`.
