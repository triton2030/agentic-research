# Tool Fixture Side Effect

## Observation

При добавлении contract-check для tool/runtime модели легко назвать проверку
read-only, хотя внутри неё есть live mutating calls на fixture. Даже если
fixture временная и чистится, cwd-fixture создаёт шум для аудитора и портит
доверие к слову "read-only".

## Counter

- 2026-05-21 [GPT-5.5]: в ремонте `md-mcp 0.6.1` я добавил
  `mcp-contract-check` с live `md_init` / `md_strip` parity fixture сначала
  под package cwd. Subagent-аудит правильно отметил P3: проверка не выглядит
  read-only. Исправление: перенёс fixture в системный `/tmp` и оставил repo cwd
  чистым.

## Possible upgrade

Для contract/smoke тестов, которые называют себя read-only или wrapper-only:
temp roots по умолчанию только в `/tmp`; если нужен path-filter parity, делать
absolute glob через resolved temp path.
