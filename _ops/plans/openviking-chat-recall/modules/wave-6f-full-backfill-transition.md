---
kind: module-card
wave: "6f"
state: in-progress
role: full-backfill-transition
system-owner: root
semantic-writer: gpt-5.6-luna/max
---

# Модуль — full-backfill transition

[parent: task.md](../task.md) · один переход от двух accepted probes к
reusable chronological fold]

## Outcome

Перед batch-003 убрать три уже наблюдаемых класса сбоя:

1. source-backed claim попадает в близкую страницу, но supporting quote не
   отвечает на её H1-вопрос;
2. semantic writer вручную материализует пути и bytes из accepted
   changeset, хотя это детерминированная работа;
3. локальное решение про named skill/artifact переписывается как универсальный
   метод, либо неподдержанное обобщение остаётся в prose вне typed claims.

Результат перехода — один reusable full-run contract, узкий
deterministic replay route и batch-003 shadow verdict. Хронологический размер
десять holders, retained visible Luna, current-only rewrite и exact-one
record coverage не меняются.

## Frozen boundary

- corpus commit: `6f98fcccdbf4b4de45ef787239ad101f70d106e2`;
- evidence commit: `ea569e2bf84377b17be9177065d5fb9172d26d39`;
- accepted batch-002 commit: `ade7d0583930495479f3739a6db54cb47003b7fb`;
- accepted current Wiki tree: `71bc5b917ffdef9feeb26831efe3cfbf801a8a1e36ef460ed14427390b8cbfe0`;
- retained visible writer: `01a026fe-70a0-78d1-abad-12387192465e`.

`HEAD`, live holders и project files, упомянутые в quotes, не становятся
silent fallback или semantic input.

## Transition work

### T1 · Page ownership

- Проверить каждый material claim в затронутых batch-002 pages вопросом:
  «supporting quote сама отвечает на H1 этой страницы?»
- Changeset обязан адресно обосновать `page_fit` для каждого claim.
- Holder scene, `context-note` и named owner ограничивают subject/H1: перенос
  `1html`, `1index` или конкретного каталога на весь класс skills/Wiki/interfaces
  является новым claim, а не дистилляцией.
- Independent audit сравнивает с evidence весь `proposed_content`, а не только
  `material_claims`: typed table не считается полным представлением prose.
- Не подходящий соседний предмет требует `create` или named `split`;
  existing page не растёт только по semantic proximity.
- Первая repair-цель: `method/global-skill-trigger.md`; source records
  про global instruction не смешиваются с H1 про skill.

### T2 · Deterministic replay

- Semantic Luna пишет только typed changeset; current Wiki и receipt она не
  материализует.
- Runtime owner —
  `experiments/openviking-chat-recall/scripts/materialize_chronological_changeset.py`;
  он принимает только `chronological-wiki-changeset.v3`. Claim хранит exact H1
  в `page_fit.page_question`, непустой subset
  `page_fit.answering_record_ids` и короткий `page_fit.reason`.
- Current-batch `record_ids` semantic operations должны точно совпадать с
  union `material_claims.supporting_record_ids`; formal `used` без
  claim-ответственности fail closed.
- Replay helper до записи проверяет schema, prior tree/page SHA, разрешённые
  operations и path boundary; после записи — exact proposed bytes/SHA, active tree,
  coverage, links и receipt.
- Mismatch останавливает batch до partial write либо включает явный
  rollback к prior digest. LLM-generated patch не является fallback.

### T3 · Shadow batch-003

- Deterministic builder
  `experiments/openviking-chat-recall/scripts/build_chronological_batch.py`
  сформировал `batch-003-input.json` SHA-256
  `02e36c2a5636a19c24633149cb81b082c6d5edb14c247b773a4f67821ff9e4c4`:
  следующие десять целых holders, 38 records, UTC boundary
  `2026-08-01T12:22:41.874000+00:00`.
- Cumulative run-state явно разделяет 183 record-bearing holders и один
  no-record holder; нулевому holder не выдумывается timestamp или semantic
  batch.
- Возобновить retained Luna на Phase A с новым page-fit contract.
- Root и independent non-writer повторно проверяют все affected pages, а не
  только mechanical invariants. Accepted draft материализует replay helper.
- Если independent audit находит material page-fit/currentness defect, который
  не вызвал stop, full semantic audit сохраняется на каждом batch.
- Наблюдавшийся scope/prose FAIL оставляет full semantic audit на каждом batch.
  Exception-based route не открывается, пока исправленный batch-003 и следующий
  batch подряд не пройдут чистый candidate-first audit; deterministic gates и
  exact coverage остаются на каждом batch.

## Full-run checkpoints

- Один cumulative run-state хранит cursor, processed holder/record IDs, prior/after
  tree digests и exception status. Отдельная permission-card на каждые десять
  holders не нужна.
- Blind index-first reader запускается после каждых пяти batch, при
  material index/page split и на terminal full-corpus boundary.
- Final acceptance проверяет complete frozen coverage, currentness, page-fit,
  index-first findability, source links, rebuild/replay и matched reading cost. Размер
  Wiki — diagnostic only.

## Acceptance

Wave 6f accepted, когда:

- batch-002 page-fit repair принят отдельной непишущей рукой;
- replay helper и его falsifying tests доказывают fail-before-write и exact
  replay для `create | update | supersede`; named split кодируется
  как `update|supersede + create` с общим `split_group_id`;
- batch-003 имеет exact coverage, accepted semantic draft, deterministic receipt
  и independent shadow verdict;
- plan/status хранят один full-run frontier, а completed batch artifacts остаются
  immutable evidence.

## Current evidence

- `tests/test_build_chronological_batch.py` воспроизводит holder slices
  batch-001/002, exact batch-003, timezone normalization, shuffled JSONL,
  no-record accounting, prior commit pin и check mode.
- `tests/test_materialize_chronological_changeset.py` проверяет exact bytes,
  machine receipt, v3/page-fit, path/prior/content SHA, named split, source-only
  links, full-quote guard, symlink boundary и existing-receipt stop.
- 15 targeted tests PASS. Provenance closure отдельно доказывает, что
  `reject|skipped` record нельзя материализовать, а старый support разрешён
  только через exact source-link принятой prior Wiki, а `used` record не может
  остаться без material-claim support. Full suite: 76 tests, только прежние
  2 failures + 3 errors `test_freeze_corpus` из-за dirty live `_ops/chat-recall`.
  Batch-003 проходит mechanical dry-run, но его source-scope repair и новый
  blind verdict ещё не приняты; materialization до `status: accepted` fail closed.

## Principles trace

Direct owner answers сохраняют full backfill, одну chronological Luna, десять
holders, current-only rewrite, source links и отсутствие size gates
(`_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:25-27,35,40-57`).
P-003 снимает process, который больше не служит полной Wiki; P-004/P-005
сохраняют semantic falsifier и observable replay gate; P-007 правит этот
plan owner вместо параллельного plan. Выведено: после одного shadow PASS
routine semantic audit может сузиться до exceptions; прямого owner-answer
на эту степень автоматизации нет.
