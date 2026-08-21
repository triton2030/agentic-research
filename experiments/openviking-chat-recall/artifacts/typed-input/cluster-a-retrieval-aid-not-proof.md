# Typed evidence — Retrieval aid is not proof

This is a deterministic typed-evidence input. Exact count, first/latest and source provenance are gold facts; the LLM must not recalculate or replace them.

Probe claim: A search card or retrieval hit selects a holder for full reading; it does not prove the owner's position.

## Deterministic facts

- Exact source records: `4`
- First recorded occurrence: `2026-08-14T07:45:46.732000+00:00`
- Latest recorded occurrence: `2026-08-17T17:46:29+05:00`
- Source path: `_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md`
- Frozen provenance ref: `6d392ae^:_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md`
- Frozen source SHA-256: `501cad60b995a15ce2382ea1c4f264f4c3f22a0e1450dda2fbe4d891c58016ff`

## Gold assertions

### A-assertion-1

The retrieval aid helps locate the right conversation but does not replace the owner's quotes or count as the owner's truth.

Provenance records: `2026-08-14-124028-codex-019fff2e.md:20`

### A-assertion-2

A hit selects a holder for complete chronological reading and later checking; it does not prove the owner's position.

Provenance records: `2026-08-14-124028-codex-019fff2e.md:26`, `2026-08-14-124028-codex-019fff2e.md:31`, `2026-08-14-124028-codex-019fff2e.md:35`

## Exact owner records

### 2026-08-14-124028-codex-019fff2e.md:20

- Timestamp: `2026-08-14T07:45:46.732000+00:00`
- Kind: `selection`
- Type: `решение`
- Topic: `документация-и-знания`
- Source line: `20`
- Exact owner quote:
> У каждого файла цитат есть одна короткая, постоянно актуализируемая поисковая карточка сессии; она помогает найти правильный разговор, но не заменяет цитаты, не пересказывает решения и не считается правдой владельца.

### 2026-08-14-124028-codex-019fff2e.md:26

- Timestamp: `2026-08-14T20:50:44+05:00`
- Kind: `selection`
- Type: `решение`
- Topic: `документация-и-знания`
- Source line: `26`
- Exact owner quote:
> `session-context` остаётся отдельным полем `session_context` в JSON и `--show`. Обычный `records`-ranking ищет только по цитатам и `context-note`: BM25 допускает dense rerank, затем выдача схлопывается до одного кандидата на файл. Карточка индексируется отдельно — одна BM25-строка на файл — и никогда не смешивается с embeddings цитат. Если запрос содержит термин, отсутствующий во всём record-index, совпавшие карточки появляются отдельным top-5 маршрутом `session_candidates`, не переставляя `records`; если `records` пуст, тот же маршрут становится fallback-выдачей. В card-only fallback `--timeline` возвращает все записи найденных файлов. Карточка и rank выбирают только файл для полного чтения и не доказывают позицию владельца. `--json` даёт `address` для record-кандидатов и `session_candidates` для file-level маршрутов. При нуле и в record-index, и в карточках поиск честно возвращает пусто. Модель ставится один раз через `--prepare`; без неё `--lexical` сохраняет те же два раздельных lexical-маршрута. Acceptance этой возможности включает случай, где один существенный термин задачи отсутствует во всех цитатах и `context-note`, присутствует только в `session-context`, а default JSON показывает нужный файл в top-5 `session_candidates`, не меняя порядок `records`.

### 2026-08-14-124028-codex-019fff2e.md:31

- Timestamp: `2026-08-16T06:07:59+05:00`
- Kind: `not recorded`
- Type: `коррекция`
- Topic: `документация-и-знания`
- Source line: `31`
- Exact owner quote:
> Да но мы не должны удалять ту старую обязанность что агент должен читать не отдельные цитаты а весь файл ведь иначе он может не уловить контекст связи и флоу мои цитат по порядку а будет читать цитаты вне контекста

### 2026-08-14-124028-codex-019fff2e.md:35

- Timestamp: `2026-08-17T17:46:29+05:00`
- Kind: `selection`
- Type: `решение`
- Topic: `документация-и-знания`
- Source line: `35`
- Exact owner quote:
> 1chat-recall: первый запрос — естественная формулировка для BM25+E5 по цитатам; максимум один повтор — три-четыре отдельных wildcard-корня. Session-context остаётся отдельным BM25 file-route: прежний novel-term gate либо минимум два совпавших корня; карточка не входит в records, E5 карточки не ранжирует, card-only records пусты кроме timeline. Любой hit только выбирает holder: его читают от первой строки до последней и затем проверяют более поздние holder-ы по тому же claim.
