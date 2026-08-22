---
kind: semantic-audit-verdict
batch: batch-001
attempt: 1
status: rejected
date: 2026-08-22
---

# Clean batch-001 attempt-001 — REJECTED

Candidate SHA-256:
`3e6a7088908b192d7373cbd31781469e5640444ea8d69be6b8d4c9ba87c35e98`.
Start/end SHA совпали. Deterministic `--check-only` прошёл: 10 active pages,
after-tree
`376fdc927850cab9c58c6a10997002dffc70c164419d341c13c7cb9af8adfaba`.
Это structural evidence, не semantic acceptance.

Independent source-bound audit дал FAIL:

- `cr-67b…`, `cr-3e2…`, `cr-7cb…`: Playwright, `1chat-recall` и другие named
  subjects слиты в общий cross-runtime claim;
- `cr-22ee…`, `cr-fc5…`, `cr-411…`, `cr-036…`: тематическая близость выдана
  за прямой ответ page H1;
- `cr-0c56…`, `cr-9e42…`, `cr-e0cc…`: `правило-кандидат` усилено до текущего
  правила на title/body/index surfaces;
- repetition groups инвертируют deterministic `first/latest` manifest order;
- reject `cr-1c066…` утверждает отсутствие skill/flag, хотя full holder их
  называет.

Опорные frozen holders:

- `_ops/chat-recall/2026-07-22-105500-claude-d8a832a4.md:24`;
- `_ops/chat-recall/2026-07-26-180518-claude-fa590eea.md:16-17`;
- `_ops/chat-recall/2026-07-26-163413-claude-2be60fdc.md:18,20`;
- `_ops/chat-recall/2026-07-25-134829-claude-d96a2888.md:2,6,15`.

Wiki и receipt не материализованы. Этот artifact — immutable failure evidence,
не semantic prior и не repair target. Следующая попытка обязана использовать
новый prompt SHA и новую Luna с чистым контекстом.
