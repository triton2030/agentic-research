---
kind: history
project: openviking-chat-recall
through: 2026-08-22
---

# История OpenViking chat-recall

Этот файл объясняет, почему текущая система стала такой. Он не управляет
исполнением. Current contract — `task.md`, замысел — `context.md`, frontier —
`status.md`.

## 1. Stock runtime pilot

Изначально проект пытался использовать OpenViking почти целиком. Pinned
OpenViking 0.4.16 импортировал resources, но SDK skill upload и Compile/runtime
не образовали совместимый проверяемый путь. Stock route был отклонён, а его
receipts сохранены:

- `experiments/openviking-chat-recall/artifacts/receipt.md`;
- `experiments/openviking-chat-recall/artifacts/v2-receipt.md`;
- `modules/return-wave-2-v2-audit.md`.

## 2. Custom compiler и typed evidence

Владелец выбрал локальный batch compiler: OpenViking prompts, IA и context
layers без stock runtime. Frozen inventory, evidence records и stable
partitions были приняты как deterministic foundation:

- source lock: `modules/_returns/wave-6-f1-source-lock.md`;
- evidence layer: `modules/_returns/wave-6-f2-evidence-layer.md`;
- partitions: `modules/_returns/wave-6-f3-stable-partitions.md`.

Provider canary остался `UNKNOWN`; его repairs не были разрешением на full
semantic route. Chronological local Luna стал рабочим writer route.

## 3. Distilled knowledge вместо chronology report

Ранний дизайн пытался сохранять counts, first/latest, evolution и
contradictions внутри Wiki. Владелец уточнил границу: holders уже являются
историей, а Wiki должна хранить чистое актуальное знание. Exact repetition и
timestamps сохранились в evidence metadata, но не стали обязательной Wiki
прозой.

Опорные материалы:

- `modules/_returns/fresh-eyes-distilled-knowledge.md`;
- `modules/wave-5-distilled-probe.md`;
- `modules/wave-5-distilled-acceptance.md`.

## 4. Chronological pilot batch-001/002

Последовательные batches по десять holders дали полезную структуру и прошли
source/index checks. Batch-002 дошёл до 9 pages и blind findability 4/4:

- `modules/_returns/wave-6d-chronological-batch-002.md`;
- `modules/_returns/wave-6e-blind-findability.md`;
- `experiments/openviking-chat-recall/artifacts/chronological-pilot/`.

Позднее эти pages были понижены до historical evidence: универсальные
императивы превращали речь владельца в объективные правила. Их IA/findability
полезны как comparator, но их prose не является semantic prior новой chain.

## 5. Batch-003 repair loop

Rejected batch-003 несколько раз проходил mechanical checks, но independent
audits находили новые source-fidelity мутации на derived surfaces: page-fit,
description, body, source labels, coverage reasons и index cues. Repair той же
Luna переносил ошибку между surfaces и не доказывал повторяемый механизм.

Решение: остановить repair loop, создать один versioned prompt, новую Luna на
каждую clean attempt и candidate-first acceptance. Детали сохранены в
`modules/wave-6f-full-backfill-transition.md`; rejected candidate остаётся в
`artifacts/chronological-pilot/batch-003/` только как failure evidence.

## 6. Clean owner-attributed v1 chain

Prompt v1 сохранил OpenViking IA, но сделал source nature явной: все material
claims — third-person paraphrases того, что сказал владелец. Manifest v4,
changeset/receipt v5 и deterministic preflight связали prompt, output contract,
materializer, prior tree и exact source targets.

Checkpoint `9426db2d17c7823b603fe1b818387ab4211bbfad` открыл clean replay с пустого
batch-001 prior. Текущий artifact root —
`experiments/openviking-chat-recall/artifacts/chronological-v1/`.

## 7. Bounded prior-reading correction

Во время первой clean Luna владелец заметил будущий scaling risk: batch на
шаге 100 не должен перечитывать все прежние quotes. Текущий контракт поэтому
разделил inputs:

- source plane — только десять новых holders/records;
- knowledge plane — current Wiki;
- deterministic provenance — prior page IDs/hashes/source targets без чтения
  старых цитат;
- control plane — bounded named instructions, не Wiki evidence.

До batch-002 read-set audit и prior-page bindings стали обязательным gate.
Owner evidence: `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:71-73`.

## 8. Refactor control plane и первый clean attempt

Длинные `task/context/status` смешивали current execution с историей волн.
Live triad была пересобрана до одного contract/why/frontier, а прошлые pilots,
corrections и rejected routes вынесены в этот файл. Bounded fresh-agent probe
по одной triad восстановил batch inputs, gates, forbidden surfaces и terminal
outcome без чтения `HISTORY.md` или `modules/**`.

Первая clean Luna по prompt v1 вернула candidate SHA-256
`3e6a7088908b192d7373cbd31781469e5640444ea8d69be6b8d4c9ba87c35e98`.
Mechanical check прошёл, но independent semantic audit отклонил candidate:

- Playwright, `1chat-recall` и другие named subjects были слиты;
- тематически близкие records не отвечали точному H1;
- `правило-кандидат` стало текущей границей на derived surfaces;
- writer инвертировал deterministic `first/latest` order;
- reject reason противоречил полному holder context.

Exact rejected bytes и typed verdict сохранены в
`experiments/openviking-chat-recall/artifacts/chronological-v1/batch-001/attempt-001/`.
Туда же перенесены pinned v1 manifest и preflight; канонические batch-001 input
paths пересобраны только для новой попытки.

Wiki и receipt не материализованы; visible task архивирована. Candidate нельзя
ремонтировать. Следующий attempt начинается новой Luna и новым prompt SHA.
Fresh-eyes остановил дальнейшую полировку документации: ближайший результат —
чистый accepted batch-001. До первого `update/no-change` также добавлен gate:
новое изменённое знание должно появиться в answer-body, а не только в
description/provenance. После accepted batch-002 ранний matched comparator
проверит пользу до полного backfill.

Prompt v2 добавил наблюдаемый per-record `source_alignment`: named subject,
scope, modality и короткий exact quote fragment. Materializer проверяет, что
все supporting records прямо отвечают H1, фрагмент действительно входит в
`quote`, а repetition IDs следуют manifest order. Новый frozen input-lock:
prompt SHA `e5c4389374911239551f3157bce2b03e878dcd9981dae48a60831af856c8eeba`,
manifest SHA `1b7e51536b2b488ad2b8f4e16c4ab3ac47f1b72182e318bd2bcb1171951f32fc`.

## Подробный архив

`modules/**`, `modules/_returns/**`, ранние `artifacts/wiki*`,
`artifacts/distilled-*` и `artifacts/chronological-pilot/**` — подробный
addressable archive. Их назначение — объяснять прежний verdict или failure, а
не задавать следующий шаг.
