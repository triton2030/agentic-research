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

Перед возобновлением full backfill убрать пять уже наблюдаемых классов сбоя:

1. source-backed claim попадает в близкую страницу, но supporting quote не
   отвечает на её H1-вопрос;
2. semantic writer вручную материализует пути и bytes из accepted
   changeset, хотя это детерминированная работа;
3. локальное решение про named skill/artifact переписывается как универсальный
   метод, либо неподдержанное обобщение остаётся в prose вне typed claims.
4. typed claim остаётся source-faithful, но description, body, `Check`, source
   label, coverage reason или index cue добавляет новую modality/relationship.
5. owner quote переписывается как объективный факт или универсальный императив,
   хотя evidence устанавливает только то, что владелец сказал о предмете.

Результат перехода — один versioned semantic-will prompt, его path/SHA binding,
reusable full-run contract, узкий deterministic replay route, clean
owner-attributed rebaseline batch-001/002 и чистый batch-003 verdict.
Хронологический размер десять holders, current-only rewrite и exact-one record
coverage не меняются. Retained writer route отменён: каждая clean attempt
получает новую visible Luna task.

## Frozen boundary

- corpus commit: `6f98fcccdbf4b4de45ef787239ad101f70d106e2`;
- evidence commit: `ea569e2bf84377b17be9177065d5fb9172d26d39`;
- accepted batch-002 commit: `ade7d0583930495479f3739a6db54cb47003b7fb`;
- accepted current Wiki tree: `71bc5b917ffdef9feeb26831efe3cfbf801a8a1e36ef460ed14427390b8cbfe0`;
- failed retained writer evidence: `01a026fe-70a0-78d1-abad-12387192465e`.

Batch-001/002 commit и tree остаются immutable historical evidence, но после
owner-correction не являются semantic prior нового writer route.

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
- OpenViking page type остаётся предметным, но claim/title/H1/description/body/
  source label/index cue сохраняют owner attribution и modality. Страница
  сообщает, что владелец сказал о concept/entity/method, а не выдаёт его речь
  за независимо проверенный факт проекта или мира.
- Independent audit сравнивает с evidence весь `proposed_content`, а не только
  `material_claims`: typed table не считается полным представлением prose.
- До prose writer перечисляет все serialized surfaces страницы. Каждая
  material surface несёт source record ID или выводится из named claim; для
  неё отдельно проверяются actor, subject, scope, modality и relation.
- Обратная проверка называет точный source span и каждое слово/отношение без
  соответствия в нём. Несоответствие удаляется либо явно становится
  inference/uncertainty; source preference/question не превращается в settled
  capability/rule.
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

### T3 · Clean owner-attributed rebaseline

- Deterministic builder
  `experiments/openviking-chat-recall/scripts/build_chronological_batch.py`
  сформировал `batch-003-input.json` SHA-256
  `02e36c2a5636a19c24633149cb81b082c6d5edb14c247b773a4f67821ff9e4c4`:
  следующие десять целых holders, 38 records, UTC boundary
  `2026-08-01T12:22:41.874000+00:00`.
- Cumulative run-state явно разделяет 183 record-bearing holders и один
  no-record holder; нулевому holder не выдумывается timestamp или semantic
  batch.
- Старые batch-001/002 current pages не переписывать вручную. После prompt
  approval новая Luna строит batch-001 из первых десяти frozen holders и
  пустого Wiki; independent audit проверяет source → claim → third-person
  prose и index-first findability. PASS материализует новый baseline.
- Следующая новая Luna строит batch-002 поверх accepted нового baseline; только
  его PASS открывает batch-003. Старые accepted artifacts не используются как
  semantic source, но доступны root как comparator формы/findability.
- Candidate SHA
  `b1001021bb4011cec1504f75b1cc35d8c9e809b4e60ac82874058ca4ec77f808`
  остаётся rejected failure evidence: он добавил `comments separately` и
  превратил proposal рассмотреть filtering/sorting в added capability на
  derived surfaces. Его не ремонтировать и не материализовать.
- После exact owner approval создать
  `experiments/openviking-chat-recall/prompts/wiki-writer.v1.md`. Prompt —
  единственный owner writing rules; Wave 6f владеет acceptance и stop-rule, но
  не копирует его prose.
- Builder фиксирует `prompt_path` и `prompt_sha256`; changeset и receipt обязаны
  воспроизвести binding. Ручные follow-up инструкции writer-у запрещены.
- Новая visible Luna с чистым context получает frozen batch input, accepted
  prior Wiki текущей новой цепочки и exact prompt SHA; пишет только новый
  changeset. Mechanical
  `--check` выполняется до independent non-writer semantic audit всех affected
  pages и всех serialized surfaces.
- PASS разрешает deterministic materialization. FAIL отбрасывает candidate:
  root + Opus классифицируют класс сбоя, новая prompt version получает новый
  SHA, а следующая новая Luna повторяет batch с нуля. Repair output той же Luna
  запрещён.
- Два последовательных FAIL одного owner/scope/modality/relation класса после
  prompt bump останавливают backfill и опровергают prompt-only route. До
  пересмотра размера batch, model route или claim-derived surfaces batch-004 не
  запускается.
- Full semantic audit сохраняется на каждом batch. Exception-based route не
  открывается, пока два последовательных batch не пройдут clean candidate-first
  audit; deterministic gates и exact coverage остаются на каждом batch.

### T4 · Отложенный allocation prototype

- Реализованный allocation-v4 seam остаётся не принятым optional prototype и
  не блокирует batch-003/004. Наблюдавшиеся terminal defects требовали полного
  holder context и prose audit; отдельная allocation phase пока не доказала
  снижения ошибки или стоимости.
- Вернуться к allocation можно после двух clean batch либо после prompt-only
  defeater. Тогда отдельный falsifying probe должен показать, что sidecar ловит
  material defect до prose дешевле полного candidate audit.
- До такого evidence рабочая схема остаётся changeset v3 плюс обязательный
  prompt path/SHA binding. План не требует allocation v1 или v4 для batch-004.

## Full-run checkpoints

- Один cumulative run-state хранит cursor, processed holder/record IDs, prior/after
  tree digests и exception status. Отдельная permission-card на каждые десять
  holders не нужна.
- Blind index-first reader запускается после каждых пяти batch, при
  material index/page split и на terminal full-corpus boundary.
- Final acceptance проверяет complete frozen coverage, currentness, page-fit,
  index-first findability, source links, rebuild/replay и matched reading cost.
  Размер Wiki — diagnostic only.

## Acceptance

Wave 6f accepted, когда:

- batch-002 page-fit repair принят отдельной непишущей рукой;
- replay helper и его falsifying tests доказывают fail-before-write и exact
  replay для `create | update | supersede`; named split кодируется
  как `update|supersede + create` с общим `split_group_id`;
- exact owner-approved prompt и его path/SHA binding воспроизводятся из input
  manifest в changeset и receipt;
- clean batch-001/002 rebaseline и batch-003 имеют exact coverage, accepted
  semantic drafts, deterministic receipts и independent verdicts без repair
  candidate;
- batch-004 запускается только после batch-003 PASS; allocation-v4 не является
  gate без отдельного falsifying evidence;
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
  Batch-003 candidate `b1001021…f808` проходит mechanical dry-run, но terminal
  semantic audit отклонил его из-за unsupported relation и proposal-modality на
  derived surfaces; materialization до `status: accepted` fail closed.

## Principles trace

Direct owner answers сохраняют OpenViking IA, full backfill, десять holders,
current-only rewrite, source links и отсутствие size gates, но требуют, чтобы
знания оставались third-person paraphrases owner quotes; новый prompt исполняют
новые Luna (`_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:25-27,35,40-66`).
P-003 снимает repair loop, который больше не служит полной Wiki; P-004/P-005
требуют clean-run observable gate вместо принятия self-report или manually
repaired output; P-007 правит существующие task/context/status/Wave 6f вместо
параллельной карточки. Выведено: clean replay batch-001/002 сильнее глобального
rewrite заражённого prior, потому что отдельно доказывает новую семантику.
Контрось по Frame, всем Principles и GOAL назвала только цену повторной
обработки первых 20 holders; она не переворачивает P-004/P-005, а GOAL отдельно
запрещает второй source of truth.
