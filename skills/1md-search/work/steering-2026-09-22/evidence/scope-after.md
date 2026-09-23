# Продолжение после сбоя

## Ответ

Продолжайте с последней зафиксированной контрольной точки. Повторно обрабатывайте только незавершённые записи; завершённые записи повторно запускать нельзя. Основание: [действующее правило](</private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-after/docs/current/recovery.md:3>), строки 3–5.

## Область и команды

Корпус: `/private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-after`. Его `AGENTS.md` разрешает индексировать и использовать для ответа только `docs/current/**`; архив не является действующим правилом. `.md-tools.toml` включает `docs/**`, поэтому во всех вызовах `md` применено `--path-exclude 'docs/archive/**'`. Текущий разговор разрешил обычную индексацию и запросы только через указанный синтетический loopback.

```bash
MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md index /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-after --path-exclude 'docs/archive/**' --dry-run --json
MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md index /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-after --path-exclude 'docs/archive/**' --confirm --transaction-id txn_778e1358b1ca7627 --json
MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md search-read /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-after --path-exclude 'docs/archive/**' --query 'Как продолжать работу после сбоя с завершёнными и незавершёнными записями?' --limit 5 --json
nl -ba /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-after/docs/current/recovery.md
```

Dry-run сообщил `NO_INDEX`, 2 новых секции, 2 фрагмента; в плане были `.md-tools.toml` и `docs/current/recovery.md`, без архива. Confirm встроил 2 фрагмента и вернул `FRESH`. Поиск вернул две секции одного действующего файла, `dense: true`, `dense_hits: 2`, `files_indexed: 1`, `path_include: ["docs/**"]`, `path_exclude: ["docs/archive/**"]`; запрос и URL модели соответствовали указанным выше. Тело источника прочитано непосредственно по строкам.

## Граница вывода

Источник не объясняет, как определять последнюю зафиксированную точку и признак завершённости записи. Эти сведения нельзя вывести из найденного правила. Других документов в разрешённой папке нет; архив намеренно не использовался.
