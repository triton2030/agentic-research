---
name: 1cli-tools
description: >
  Use when repo/tooling decisions need terminal evidence: exact text/path/ID/
  count/JSON, active binary owner, CLI flag/schema, update or security scan.
  Stable ID/table/raw block in Markdown is exact; prose body → 1md-read;
  unknown meaning → 1md-search; graph → 1md-graph.
---

# CLI Evidence

## Почему Это Выгодно

Один точный probe часто отменяет длинную ветку чтения, реализации или спора о
том, что «наверное» делает инструмент. Live schema дешевле отладки remembered
flag, а exact ID дешевле чтения многотысячной секции. Это не терминальная
церемония: используй CLI только там, где literal fact действительно сужает путь
к ответу пользователя.

## Результат

Для обычного узкого probe достаточно:

```text
claim → exact target/scope → observed fact → gap или side effect
```

Полный packet с command, active owner и evidence class нужен, только когда от
runtime, версии, риска или воспроизводимости materially зависит решение.

Команда доказывает только свой слой. Manager receipt не доказывает active
binary; text match не доказывает semantic owner; analyzer finding не даёт
permission на delete/rename.

## Рабочая Иерархия

| Момент | Лучший route | Почему |
| --- | --- | --- |
| Exact string/path/count/JSON | `rg` / `fd` / `wc` / `jq` | Literal answer за минимальный output |
| Stable ID, table row, raw block в Markdown | `rg`, затем delimiter-aware block extraction | Не загружает весь heading ради одной addressable записи |
| Неизвестный flag или JSON shape | `<tool> --help`; для `md` — `md tools <command> --json` | Live contract предотвращает ложный parse |
| Active binary/version влияет на вывод | `probe-tools.sh` + version | Доказывает реально исполняемый owner |
| Code syntax/analyzer candidate | exact/code reference | Даёт candidate, не semantic verdict |
| Update/security/supply-chain | профильная reference | Side effects и evidence bar отличаются |
| Известный Markdown heading/prose | `1md-read` | Heading-aware body сильнее line match |
| Неизвестный смысл/owner | `1md-search` | Exact text не заменяет discovery |
| Links, holders, impact | `1md-graph` | Graph relation не равна text occurrence |

Название команды не гарантирует read-only. `outdated`, `doctor`, `dry-run`,
`cache verify` и даже некоторые `list/root` могут обновить metadata, repair
cache или создать directories.

## Минимальный Контракт

1. Зафиксируй один claim, точный target и единицу измерения: files, matching
   lines, occurrences, JSON keys, runtime owner или test outcome.
2. Перед редким flag проверь `<tool> --help`; перед schema-dependent parsing —
   live keys/schema. Для `md` сначала:

   ```bash
   md tools <command> --json
   ```

3. Запусти самый узкий probe. Не превращай точный вопрос в inventory
   репозитория или машины.
4. Проверяй active binary owner только когда другой binary/version способен
   изменить вывод. Targeted owner probe:

   ```bash
   bash ~/.claude/skills/1cli-tools/scripts/probe-tools.sh md rg
   ```

   Для package CLI сначала предпочитай project-local `node_modules/.bin` /
   `pnpm exec`. `npm exec`, `npx` и `uvx` могут скачать package/cache.
5. Для delete/rename/codemod или другого high-risk действия добавь второй
   независимый signal либо runtime/test confirmation.
6. Сообщи фактические side effects, включая generated cache/index repair.

## Conditional References

- Exact strings/paths/counts/JSON, stable IDs, raw blocks, symbols и analyzers →
  [`references/exact-and-code-evidence.md`](references/exact-and-code-evidence.md).
- PATH owner, versions, update или machine-wide audit →
  [`references/runtime-ownership.md`](references/runtime-ownership.md).
- Secrets, vulnerabilities, SAST или native supply chain →
  [`references/security-scans.md`](references/security-scans.md).

## Evidence Classes

- `derived`: exact CLI fact (`rg`, `fd`, `sg`, parsed JSON field);
- `inferred`: analyzer/scanner candidate (`knip`, `depcruise`, SAST);
- `semantic`: ranked search candidate или `1md-search` packet;
- `runtime`: реально выполненная command/test/health check.

`inferred` и `semantic` требуют cross-check перед необратимым действием.
Secret-scanner finding остаётся candidate даже если verifier принял credential:
owner/scope и rotate/revoke — отдельные решения.

## Boundaries И Stop

- Browser interaction, screenshots и visual assertions → browser/frontend
  owner.
- Install/update, network probe, codemod, delete/move/rename, cache download и
  mutating LSP требуют явного покрытия запросом.
- Exact match отвечает только на literal claim; authority и meaning остаются у
  прочитанного owner-а.

Остановись, когда exact claim получил адресуемый ответ, scope и side effects
видны, а следующий CLI-вызов не способен изменить решение.
