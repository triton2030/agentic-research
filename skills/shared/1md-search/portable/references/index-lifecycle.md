# 1md-search — Жизненный Цикл Индекса

## Содержание

- Owner и scope
- States и default recovery
- Delta, cleanup и conflicts
- Transaction contract

Vector index лежит в `<corpus>/.md-navigator/index.sqlite`: один generated
index на один corpus root. Вложенные indexes не сужают поиск; они создают
shadowed ownership и `INDEX_CONFLICT`.

## Owner И Scope

`md` индексирует только Markdown. Постоянные границы покрытия принадлежат
корневому `.md-tools.toml`:

```toml
[index]
include = []
exclude = ["_workspace/**", "drafts/**"]
```

Config задаёт baseline. CLI `--path-include` / `--path-exclude` добавляют
operation scope; excludes применяются после includes. Command include может
объединиться с config include по OR и не сузить corpus.

Для внешнего corpus используй абсолютный root и сначала прочитай его
`AGENTS.md` / `.md-tools.toml`. Не создавай отдельный index внутри уже
индексируемого subtree.

До первой semantic command effective project instructions или явное current
user approval должны разрешать передачу in-scope Markdown/query внешнему
provider-у и изменение generated index/cache. Сам запрос «найди по смыслу»
такого разрешения не создаёт. Без него не запускай `search`, `search-read`,
auto-embed или warmup; вернись к filesystem/exact route либо запроси согласие на
точный scope.

Default ignored parts: `.git`, `.github`, `.claude`, `.codex`,
`.md-navigator`, caches, virtualenvs, `node_modules`, build outputs,
`_archive`. Live `.md-tools.toml` остаётся owner-ом дополнительных границ.

## States И Default Recovery

Если local project не требует status перед каждой semantic command, сначала
запусти исходный search: его envelope уже несёт corpus state и exact recovery.
После material corpus edits либо при explicit index question сначала выполни:

```bash
md status CORPUS --json
```

States:

- `FRESH` — pending changes отсутствуют.
- `HEALTHY` — small delta; search может auto-embed inline.
- `NEEDS_WARMUP` — large delta; search возвращает
  `index_warmup_required`, partial search не выполняется.
- `NEEDS_REBUILD` — schema/model/integrity mismatch.
- `NO_INDEX` — index ещё не создан.

Required recovery:

```bash
md index CORPUS --dry-run --json
md index CORPUS --confirm --transaction-id TRANSACTION_ID --json
md status CORPUS --json
# replay original query with the same filters
```

Если envelope предлагает parent corpus или filters в
`_envelope.next_step.args`, используй их as-is. При нулевых pending/cleanup
confirm не нужен.

## Delta, Cleanup И Conflicts

- Small delta может быть auto-embedded во время `search`/`search-read`.
- Large delta требует explicit dry-run/confirm.
- Removed sections/files и stale config rows чистятся generated index route;
  source Markdown не меняется.
- `semantic-neighbors` при nested indexes возвращает `INDEX_CONFLICT`, а не
  выбирает nearest index.
- Для диагностики roots:

  ```bash
  md corpus-scan CORPUS --json
  ```

- `cleanup-shadowed`, `vacuum`, ручное удаление SQLite/WAL/SHM и forced rebuild
  не входят в ordinary warmup. Делай их только после отдельного основания и
  dry-run.
- Schema/model/backend mismatch определяется из stored metadata и требует
  rebuild через normal index transaction.

## Transaction Contract

Confirm всегда использует `transaction_id` или `fingerprint` **из того же
dry-run**. Ищи их в:

- `_envelope.lock.transaction_id`;
- `_envelope.lock.fingerprint`;
- `_envelope.next_step[].args`.

Никогда не запускай bare `--confirm`.

`transaction_not_found` означает expired/replaced lock, а не автоматически
сломанный corpus. Если error envelope уже показывает `FRESH`, другой writer
завершил warmup — replay query. Иначе выполни новый dry-run и confirm его id.

Query pack по одному corpus сериализуй, чтобы агенты не перехватывали общий
lock. Independent corpus roots можно обрабатывать параллельно.

Если effective owner authorization покрывает ordinary warmup и передачу
in-scope Markdown configured embedding provider, она всё равно не покрывает
profile generation, cleanup/vacuum, manual rebuild или расширение scope.
