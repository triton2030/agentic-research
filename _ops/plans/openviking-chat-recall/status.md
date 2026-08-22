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

Поднять отложенный allocation gate вместо третьего полного changeset.
Порядок одного batch становится: (1) root пересобирает manifest — materializer
SHA изменился после ремонта `_validate_coverage`; (2) новая visible Luna Max
выдаёт только claim -> page allocation без прозы; (3) независимый аудит
принимает или отклоняет карту; (4) вторая Luna Max пишет прозу и index,
связанные с accepted allocation SHA; (5) полный semantic audit сохраняется.

Prompt-only route опровергнут: attempt-001 и attempt-002 упали в один
родительский класс S1 (page-allocation instability), поэтому stop rule
`task.md` запрещает третий полный changeset без изменения механизма.
Attempt-001 и attempt-002 запрещены как semantic input.

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
- Attempt-001 отклонён (слияние named subjects, тематическая близость вместо
  ответа, усиление модальности, инверсия first/latest, reject против holder):
  `experiments/openviking-chat-recall/artifacts/chronological-v1/batch-001/attempt-001/REJECTED.md`.
- Attempt-002 отклонён, SHA-256
  `5b6d2a0e12df4f4a55273640b6f33621100cd8e718b67db7d3c84da2459f7701`; веер из
  шести независимых Codex-осей дал шесть FAIL; вердикт и классы S1-S4 —
  `.../batch-001/attempt-002/REJECTED.md`, бриф `.../batch-001/audit/BRIEF.md`,
  полные пакеты `_workspace/codex-artifacts/20260822T0907*`.
- Канонический `batch-001/changeset.json` освобождён; ни одна Wiki не
  материализована, `current/wiki/` пуста.
- Механический дефект M1 исправлен: `used` coverage без `page_path` больше не
  проходит `--check-only`; прямой прогон исправленного валидатора против
  attempt-002 даёт `used coverage is missing page_path for cr-07c5570aa291ce00`.
  Регрессия — `test_used_coverage_requires_matching_page_path`; targeted suite
  22/22 PASS. Materializer SHA изменился, поэтому любой новый manifest обязан
  получить новый binding.
- Диагностика объёма attempt-002: 10 079 байт цитат -> 27 379 байт кандидата
  (x2,72). Не acceptance gate; сигнал направления.
- S2: заявлена одна repetition group на 32 записи, аудит нашёл ещё три. До
  следующего batch решить, как повторы попадают в поле зрения писателя.
- Owner blocker отсутствует. Открытые владельцу вопросы: параллельность Лун,
  allocation как постоянный шаг или разовый пробник, размер batch.

Исторические pilot results, rejected routes, tasks и audit packets вынесены в
`HISTORY.md`; они не являются текущим статусом.
