# Reviews — round 1

Проверена неизменная версия candidate после clean-room и loss-map.

## Trajectory

Находок нет. Реалистичный сценарий регрессии подтвердил цепочку
`локальный patch → pre-action provenance + probe → causal delta → исправление →
исходный DoD → продолжение`; декоративная цитата, post-hoc claim и блокировка
из-за proof gap закрыты.

## Literal findings и решения root

1. **Источник методов не закреплён за живой корневой инструкцией — принято.**
   Исправлена первая цель; каталог книг в скилл не дублирован.
2. **`полностью выполни` конфликтует с post-action сверкой — принято.**
   Сессионный route теперь явно начинается до действия и завершается сверкой
   после действия.
3. **Узкая pre-action граница запрещала проверку цитаты — принято.**
   До действия отдельно разрешена source verification.
4. **Новая работа той же сессии не re-anchor’илась — принято.**
   Добавлен re-anchor без переоткрытия завершённой задачи.

Контрольный recount checker-а до правок: `SKILL.md` 29,
`activation.md` 61, `session-fork.md` 82; active sets 76 / 85 / 100.
После локальных правок materially changed только route/source/re-anchor clauses;
rich-output exception остаётся явным.
