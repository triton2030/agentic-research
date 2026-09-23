# Поиск правила восстановления: baseline

Корпус: `/private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-before`. `AGENTS.md` разрешает для этой задачи только `docs/current/**` и обычный warmup через указанный synthetic loopback. Конфигурация включает `docs/**`, поэтому все операции записи и поиска ограничены `--path-exclude 'docs/archive/**'`.

Фактические команды и краткие ответы:

| Команда | Ответ |
| --- | --- |
| `MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md index --help` | Подтверждены `--dry-run`, `--confirm`, `--transaction-id`, `--path-exclude`. |
| `MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md index /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-before --path-exclude 'docs/archive/**' --dry-run --json` | `NO_INDEX`; 2 секции и 2 чанка из `docs/current/recovery.md`; `transaction_id=txn_7ae40add04a11c60`. |
| `MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md index /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-before --path-exclude 'docs/archive/**' --confirm --transaction-id txn_7ae40add04a11c60 --json` | Созданы 2 эмбеддинга; ответ `FRESH`. |
| `MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md status /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-before --json` | Общий scope конфигурации: `include=[docs/**]`, `exclude=null`; `HEALTHY`, 1 ожидающий чанк архива. Архив не индексировался. |
| `MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md search-read --help` | Подтверждён `--path-exclude` для поиска. |
| `MD_EMBEDDING_API_URL=http://127.0.0.1:51528/v1 MD_EMBEDDING_MODEL_ID=test/steering-synthetic md search-read /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-before --path-exclude 'docs/archive/**' --query 'Как продолжать работу после сбоя с завершёнными и незавершёнными записями?' --limit 5 --json` | `FRESH`, `dense=true`, 2 попадания из одного файла `docs/current/recovery.md`; фильтр ответа `path_exclude=[docs/archive/**]`, `files_indexed=1`. |
| `nl -ba /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-steering-proof-u9gips2o/scope-before/docs/current/recovery.md` | Строка 5 прочитана в исходнике: продолжать с последней зафиксированной контрольной точки, повторять только незавершённые записи, завершённые не запускать снова. |

Ответ: продолжить с последней зафиксированной контрольной точки; повторить только незавершённые записи; завершённые записи не запускать повторно. Источник: `docs/current/recovery.md:5`. Непокрытых разрешённых файлов нет: в `docs/current` найден только этот документ.
