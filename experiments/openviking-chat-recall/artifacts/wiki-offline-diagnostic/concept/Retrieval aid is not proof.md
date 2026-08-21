---
type: concept
title: Retrieval aid is not proof
description: A chat-recall search card or hit selects a holder for full reading but does not prove the owner's position.
tags: [chat-recall, retrieval, provenance, evidence]
---

# Retrieval aid is not proof

A search card, rank or retrieval hit is a wayfinding aid. The evidence-bearing operation is complete chronological reading of the selected holder, followed by a later-holder check for the same claim.

## Deterministic facts

- Exact source records: **4**.
- First recorded occurrence: **2026-08-14T07:45:46.732000+00:00**.
- Latest recorded occurrence: **2026-08-17T17:46:29+05:00**.
- Frozen source path: `_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md`.
- Frozen Git provenance: `6d392ae^:_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md`.
- Frozen source SHA-256: `501cad60b995a15ce2382ea1c4f264f4c3f22a0e1450dda2fbe4d891c58016ff`.

These values are deterministic gold facts. They are not recomputed by the Wiki layer.

## Evidence boundary

The source records establish three linked boundaries:

1. A session card helps locate the right conversation; it does not replace quotes, retell decisions, or become owner truth.
2. A card and rank select a file for full reading; they do not prove the owner's position.
3. The full holder must be read in order, and later holders must be checked for the same claim.

## Exact owner evidence

The four selected records remain addressable by source line and preserve the owner's wording:

### `2026-08-14-124028-codex-019fff2e.md:20`

Timestamp: `2026-08-14T07:45:46.732000+00:00`; kind `selection`; type `решение`; topic `документация-и-знания`.

> У каждого файла цитат есть одна короткая, постоянно актуализируемая поисковая карточка сессии; она помогает найти правильный разговор, но не заменяет цитаты, не пересказывает решения и не считается правдой владельца.

### `2026-08-14-124028-codex-019fff2e.md:26`

Timestamp: `2026-08-14T20:50:44+05:00`; kind `selection`; type `решение`; topic `документация-и-знания`.

> `session-context` остаётся отдельным полем `session_context` в JSON и `--show`. Обычный `records`-ranking ищет только по цитатам и `context-note`: BM25 допускает dense rerank, затем выдача схлопывается до одного кандидата на файл. Карточка индексируется отдельно — одна BM25-строка на файл — и никогда не смешивается с embeddings цитат. Если запрос содержит термин, отсутствующий во всём record-index, совпавшие карточки появляются отдельным top-5 маршрутом `session_candidates`, не переставляя `records`; если `records` пуст, тот же маршрут становится fallback-выдачей. В card-only fallback `--timeline` возвращает все записи найденных файлов. Карточка и rank выбирают только файл для полного чтения и не доказывают позицию владельца. `--json` даёт `address` для record-кандидатов и `session_candidates` для file-level маршрутов. При нуле и в record-index, и в карточках поиск честно возвращает пусто. Модель ставится один раз через `--prepare`; без неё `--lexical` сохраняет те же два раздельных lexical-маршрута. Acceptance этой возможности включает случай, где один существенный термин задачи отсутствует во всех цитатах и `context-note`, присутствует только в `session-context`, а default JSON показывает нужный файл в top-5 `session_candidates`, не меняя порядок `records`.

### `2026-08-14-124028-codex-019fff2e.md:31`

Timestamp: `2026-08-16T06:07:59+05:00`; kind not recorded; type `коррекция`; topic `документация-и-знания`.

> Да но мы не должны удалять ту старую обязанность что агент должен читать не отдельные цитаты а весь файл ведь иначе он может не уловить контекст связи и флоу мои цитат по порядку а будет читать цитаты вне контекста

### `2026-08-14-124028-codex-019fff2e.md:35`

Timestamp: `2026-08-17T17:46:29+05:00`; kind `selection`; type `решение`; topic `документация-и-знания`.

> 1chat-recall: первый запрос — естественная формулировка для BM25+E5 по цитатам; максимум один повтор — три-четыре отдельных wildcard-корня. Session-context остаётся отдельным BM25 file-route: прежний novel-term gate либо минимум два совпавших корня; карточка не входит в records, E5 карточки не ранжирует, card-only records пусты кроме timeline. Любой hit только выбирает holder: его читают от первой строки до последней и затем проверяют более поздние holder-ы по тому же claim.

## Sources

- [Typed Cluster A input](viking://resources/chat-recall-typed-probe/cluster-a-retrieval-aid-not-proof/cluster-a-retrieval-aid-not-proof.md)
