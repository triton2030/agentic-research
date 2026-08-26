# Проверка и сдача

До проверки назови support envelope: target model, harness, tools, reasoning и
горизонт автономной работы.

## Falsifier по claim

| Claim | Минимальная проверка |
| --- | --- |
| routing или context delivery | применимая и неприменимая задачи без подсказки о своде |
| behavior изменён | тот же случай без инструкции или с меньшим вмешательством |
| behavior сохранён в заявленном горизонте | matched holdout с ожидаемыми phase changes, tool noise и compaction boundaries |
| resident placement полезен | none · always-on · selective на target model |
| structure/distribution | validator и projection sync |

Проверяй отдельно:

- достижение — текст попал в контекст;
- применение — решение изменилось;
- завершение — обязательство дожило до конца заявленного горизонта, а не
  только изменило первый ответ.

Самоотчёт, заполненный checklist и один удачный output доказывают не больше,
чем возможность. Claim о вероятностном улучшении требует повторов на том же
resolved model и settings.

Если зелёный сигнал можно получить без заявленной работы, проверка не различает
claim. Непроверенное остаётся candidate.

Сдача: итоговый свод · изменившиеся решения · закрытые пути · comparator ·
удалённое · residual candidate claims.
