# Cold → warm: восстановление записей

Корпус: `/private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/cold-after`. `AGENTS.md` разрешает индексировать и использовать для ответа только `docs/current/**`, обычный warmup и запросы к заданному синтетическому loopback. `.md-tools.toml` включает `docs/current/**` и исключает `docs/archive/**`. Действующее правило находится в [recovery.md](/private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/cold-after/docs/current/recovery.md:5).

## Задача 1

Вопрос: «Как продолжать работу после сбоя с завершёнными и незавершёнными записями?»

Фактические команды, по порядку:

```bash
MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md index /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/cold-after --dry-run --json
MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md index /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/cold-after --confirm --transaction-id txn_255331e3075bfbb8 --json
MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md search-read /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/cold-after --query 'Как продолжать работу после сбоя с завершёнными и незавершёнными записями?' --limit 5 --json
nl -ba /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/cold-after/docs/current/recovery.md
```

План dry-run содержал два фрагмента `docs/current/recovery.md` и не содержал архивного документа. Confirm встроил два фрагмента, вернул `FRESH`. Поиск вернул раздел `Resume records` (`docs/current/recovery.md:3`) с `engine.dense: true`, `dense_hits: 2`, фильтрами `docs/current/**` и `docs/archive/**`; прочитан сам файл. Ключевой текст строки 5: “Resume from the last committed checkpoint. Retry only unfinished records. Completed records must not run again.”

Ответ: после сбоя возобновить работу с последней зафиксированной контрольной точки; повторить только незавершённые записи. Завершённые записи повторно не запускать. Основание: [действующий документ, строка 5](/private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/cold-after/docs/current/recovery.md:5).

## Задача 2

Вопрос после первого ответа: «Найди по смыслу фрагмент, устанавливающий правило повторного запуска уже законченных записей, и приведи его основание».

Фактические команды этой задачи: дополнительных команд `md` и чтения не понадобилось; раздел уже найден семантическим поиском в задаче 1, а файл прочитан полностью. Ключевой фрагмент: “Completed records must not run again.” Его непосредственное основание в той же строке — восстановление с последней зафиксированной контрольной точки и повтор только незавершённых записей. Это текстовое обоснование правила, а не отдельное объяснение причин или гарантий реализации.

Ответ: правило находится в [recovery.md, строка 5](/private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/cold-after/docs/current/recovery.md:5): завершённые записи не запускать повторно. Документ задаёт продолжение с последней зафиксированной контрольной точки и повтор лишь незавершённых записей; иных оснований в прочитанном документе нет.

Ограничение обоих ответов: проверен только разрешённый текущий документ. Архив исключён политикой корпуса и не использовался как действующее основание.
