---
эпик: "самостоятельный experiment: openviking-chat-recall"
план: "[[task|Библиотека знаний из chat-recall]]"
состояние: 🔨 в работе
режим: Execution
вех-готово: 0
вех-всего: 5
обновлено: 2026-08-22
kind: status
---

# Статус — библиотека знаний из chat-recall

## Next

Root независимо проверяет terminal candidate SHA
`5b6d2a0e12df4f4a55273640b6f33621100cd8e718b67db7d3c84da2459f7701`,
frozen provenance и materializer `--check-only`. Затем свежий read-only auditor
сверяет все 32 records с десятью полными holders. Любой semantic FAIL отклоняет
весь кандидат; только полный PASS разрешает materialization, receipt и commit.

## Свидетельства и статус

- Frozen corpus: commit `6f98fcccdbf4b4de45ef787239ad101f70d106e2`,
  184 holders; evidence commit
  `ea569e2bf84377b17be9177065d5fb9172d26d39`, 1101 records.
- Rejected semantic prompt:
  `experiments/openviking-chat-recall/prompts/wiki-writer.v1.md`, SHA-256
  `3fd3ff7748c71f2e6d8e8cc06aebd898b1992c3c6a242bb021fe3f1ff08897d3`.
- Current semantic prompt:
  `experiments/openviking-chat-recall/prompts/wiki-writer.v2.md`, SHA-256
  `e5c4389374911239551f3157bce2b03e878dcd9981dae48a60831af856c8eeba`.
- Current batch-001 manifest: 10 holders / 32 records, SHA-256
  `1b7e51536b2b488ad2b8f4e16c4ab3ac47f1b72182e318bd2bcb1171951f32fc`;
  preflight PASS; prior Wiki tree empty.
- Pipeline checkpoint `9426db2d17c7823b603fe1b818387ab4211bbfad` pushed to
  `origin/main`; targeted suite 22/22 PASS.
- Luna terminal candidate SHA-256
  `3e6a7088908b192d7373cbd31781469e5640444ea8d69be6b8d4c9ba87c35e98`;
  rejected bytes сохранены в
  `experiments/openviking-chat-recall/artifacts/chronological-v1/batch-001/attempt-001/changeset.json`;
  independent materializer `--check-only` дал PASS, 10 active pages и tree
  `376fdc927850cab9c58c6a10997002dffc70c164419d341c13c7cb9af8adfaba`.
- Independent semantic audit дал FAIL: слиты разные named subjects, тематическая
  близость выдана за H1 answer, потеряна candidate modality, инвертированы
  `first/latest` IDs и reject reason противоречит full holder. Candidate не
  принят и не материализован; visible Luna task архивирована.
- Fresh-agent cold start после обновления frontier восстановил новый exact
  Next, inputs, gates, forbidden surfaces и terminal outcome без
  неоднозначности.
- Новый owner rule: batch N читает только свои десять holders и current Wiki.
  До batch-002 builder должен передавать deterministic prior-page record/link
  bindings, а read-set audit — доказать отсутствие reread старых quotes.
- Owner blocker отсутствует. Текущий gate внутренний: новый prompt SHA и чистый
  batch-001 attempt должны закрыть пять semantic failure classes.
- Prompt v2 требует per-record `source_alignment`; strict v5 проверяет, что
  каждый supporting record прямо отвечает H1, а короткий `supporting_words`
  буквально входит в exact quote. Repetition order теперь проверяется по
  manifest, не по lexical timestamp tie.
- Prompt v2 и strict gates находятся в pushed commit
  `fc287ecf22834593c1a82b4b2a4445273e6ac377`; Opus cold-start после исправления
  manifest и literal alignment вернул `READY_FOR_FRESH_ATTEMPT`.
- Чистая Luna v2 завершила candidate
  `artifacts/chronological-v1/batch-001/changeset.json`, SHA-256
  `5b6d2a0e12df4f4a55273640b6f33621100cd8e718b67db7d3c84da2459f7701`;
  её builder и materializer `--check-only` дали PASS и after-tree
  `5439df57ebf0cbfbe22b87610bb5ef57c06ba481405ebdf8f0953a2016ec4381`.
  Это self-report исполнителя: root check и независимый semantic audit ещё не
  получены, receipt и Wiki не созданы.
- Targeted current/legacy suite 21/21 PASS; полный experiment suite 87/87 PASS.
- До первого update в batch-002 validator обязан отклонять changed knowledge,
  которое выросло только в provenance/description, но не появилось в body.

Исторические pilot results, rejected routes, tasks и audit packets вынесены в
`HISTORY.md`; они не являются текущим статусом.
