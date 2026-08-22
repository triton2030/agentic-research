---
kind: module-card
wave: "6b"
state: superseded
role: representative-ingestion-utility-gate
system-owner: root
strategy-review: claude-opus-5
batch-model: gpt-5.6-luna
batch-thinking: max
description: representative post-ingestion utility gate before full semantic generation
---

# Модуль — representative ingestion utility gate

[parent: task.md](../task.md) · historical provider-dependent route ·
superseded for the live full backfill by Wave 6f; retained as experiment evidence]

## Contribution

Проверить пользу Wiki после настоящего representative ingestion. Этот gate
строит небольшой, но реальный end-to-end маршрут `L2 → L1 → L0`, а затем
сравнивает его с frozen holder route на одинаковых вопросах и source-bound
ожиданиях. Он закрывает разрыв между «валидаторы и projection выглядят
правильно» и «fresh agent действительно получает полезный финальный маршрут».

Это не новый semantic gold и не ещё один full-corpus build. Gate принимает
только уже принятый semantic contract, а utility измеряет фактически
построенную representative Wiki.

## Почему этот gate появился

Первый matched run Wave 5 — `FAIL`: один reader смешал пять cases, а token
экономия Wiki сопровождалась худшими `reader elapsed` и `evidence reads`.
Подробности и frozen hard failures остаются в
[Wave 5 matched grader](_returns/wave-5-matched-grader.md).

Незавершённый pre-build `operations-v2` rerun route из
[Wave 5 acceptance amendment](wave-5-acceptance-operations-amendment.md)
**superseded by this post-ingestion gate**. Его case isolation, arm-specific
reporting и измерительный контракт можно использовать как заранее объявленную
механику, но его rerun не является utility PASS и не открывает Wave 7.

Это не переписывает и не пересобирает frozen semantic gold v1: вопросы,
expected/forbidden criteria и hard failures остаются immutable.

## Entry contract

Wave 6b разделён на два неравноправных шага. Source-bound preflight/input-lock
разрешён после accepted F1–F3 и не вызывает модель. Semantic execution
`L2 → L1 → L0` разрешён только если дополнительно выполнены все условия:

- принят Wave 5 semantic/claim-currentness contract и immutable v1 semantic
  gold; принятие contract не означает utility PASS;
- deterministic F1–F3 завершены с `PASS` и выдали frozen source lock, records,
  coverage input и stable partitions; representative subset фиксирует
  preflight до первого candidate read;
- pinned OpenViking prompt/IA tuple и Context Layers prompt tuple имеют
  provenance, model/config/code digests и одну выбранную execution envelope;
- privacy/provider canary заранее доказал auth, egress, logging, retry, cost и
  secret-redaction contract;
- subset, case/arm route matrix, metrics и aggregation rule зафиксированы до
  первого чтения candidate Wiki или candidate answer.

Provider `UNKNOWN` блокирует semantic execution, но не source-bound input-lock.
Любой другой `UNKNOWN` на входе блокирует зависимый шаг. Live directory, dirty
snapshot, неприкреплённая prompt-версия или utility result Wave 5 не являются
заменой входному contract.

## Inputs

1. Accepted Wave 5 semantic contract и ровно тот же immutable
   `distilled-acceptance.json` v1. Gold читается как источник вопросов,
   semantic predicates, forbidden claims и hard failures; его копия с
   изменёнными формулировками запрещена.
2. Принятый Wave 6 deterministic output: explicit source lock, evidence
   records, coverage input, stable partitions и frozen representative subset.
   Membership subset определяется source/record/partition IDs и digest-ами до
   semantic generation; candidate answers не могут его расширить или сузить.
3. Pinned OpenViking LLM Wiki Skill и IA для L2, а также pinned Context Layers
   contract и semantic prompts для bottom-up L1/L0; каждый tuple имеет
   отдельный upstream provenance и digest.
4. Принятый privacy/provider canary и execution envelope: модель, provider,
   timeout, retry, logging, secret redaction и cost accounting.
5. До старта reader-ов — замороженная case/arm matrix для пяти v1 cases:
   stable knowledge, supersession/currentness, contested/scope,
   provenance/history route и no-gold abstain. Matrix фиксирует allowed
   surface, route expectation, must-report fields и budgets отдельно для Wiki
   и holder arm.

## Outputs

- Детерминированный `representative-utility/input-lock.json`: digests F1–F3,
  exact two-holder membership, record IDs/source addresses/content digests,
  selected-part map и digest immutable gold. Он не копирует full quotes и при
  provider `UNKNOWN` явно пишет `semantic_execution=blocked`.
- Реальный representative L2 tree, построенные из него bottom-up L1 overviews
  и L0 abstracts в dedicated artifact root; для каждого слоя есть topology,
  counts, digest и visible-text compression ratio против source quotes.
- Десять case-isolated packets: пять v1 cases × Wiki/holder arm, каждый с
  measured final route и физическими cost/evidence receipts.
- Unchanged-gold proof, isolation/privacy proof, nested-falsifier receipt и
  один root-owned `PASS | FAIL | UNKNOWN` utility verdict с per-case reasons.
- Только `PASS` несёт permission на Wave 7; `FAIL`/`UNKNOWN` возвращает
  исполнение к bounded repair/recheck, сохраняя deterministic Wave 6 output.

## Exact ownership

- **6b system owner** — root. Он единолично проектирует и собирает связанную
  representative utility implementation, её tests и input-lock в dedicated
  artifact root:
  `experiments/openviking-chat-recall/scripts/build_representative_utility.py`,
  `experiments/openviking-chat-recall/tests/test_representative_utility.py` и
  `experiments/openviking-chat-recall/artifacts/full-build/representative-utility/**`.
  Root не меняет source lock, Wave 6 partitions, v1 gold или Wave 7 outputs.
  После provider/privacy PASS root также владеет кросс-частным semantic layer:
  L1 overviews на каждой глубине, покрывающей больше одного `part-*`, включая
  корневой, и deterministic L0 extraction из Brief Description L1 по тому же
  pinned Context Layers tuple.
- **Strategy reviewer** — read-only Opus. До принятия system seam и terminal
  utility verdict он атакует связность архитектуры, privacy boundary и
  acceptance logic; self-report или совет Opus не заменяет исполняемые tests.
- **Luna Max batch writer** подключается только после accepted input-lock и
  provider/privacy PASS. Она получает замороженные prompt/schema и конкретный
  `part-*`, выполняет повторяемый quote-to-Wiki rewrite и пишет только L2 pages
  своего semantic-directory footprint. Она не пишет L1/L0 sidecars, не
  проектирует систему, не меняет shared files и не выносит gate verdict.
- **Wave 6 owner** сохраняет ownership frozen deterministic inputs. 6b читает
  их только по digest-у и не чинит их на месте.
- **Reader/grader owner** получает только заранее разрешённую surface и
  frozen gold; он пишет case packets/verdict evidence в dedicated
  representative-utility root, не в Wiki, holders или gold.
- **Root orchestrator** единолично принимает `PASS | FAIL | UNKNOWN`, открывает
  Wave 7 и при необходимости интегрирует shared plan/status. 6b writer не
  меняет shared plan/status.
- **Independent falsifier** — read-only Opus без writer transcript. Он не
  пишет файлов и возвращает atomic checks по circular-gate и
  semantic-acceptance risks.

## Bounded fan-out and isolation

- До semantic batch implementation и input-lock принадлежат root; один Opus
  проверяет системную границу. После accepted input-lock, provider/privacy PASS
  и frozen prompt/schema параллельные Luna writers разрешены только по
  непересекающимся `part-*`; exploratory fan-out запрещён.
- Ровно десять fresh reader runs: 5 cases × 2 arms. Каждый run получает новый
  context, один case, один arm и только его allowed surface. Никакой case не
  делит context, cache, discovery history или answer state с другим case.
- Wiki arm читает только реально построенные representative L0/L1/L2 и
  только заранее объявленный holder fallback для history/provenance route.
  Holder arm читает только frozen holders/evidence route и не видит Wiki.
- Grader не выбирает subset, prompts, thresholds или expected answers по
  packets; reader не видит gold, receipts или implementation transcript.

## Required execution

0. До model/provider call собрать source-bound input-lock из двух полных
   holders `_ops/chat-recall/2026-08-20-181330-claude-a7539038.md` и
   `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`. Accepted F2 должен
   дать ровно 24 `used` records, 0 diagnostics и 2 sessions; membership
   проверяется против F3 parts и всех holder routes frozen gold. Старый
   `artifacts/pilot-selection.json` запрещён. Full quotes в lock не пишутся.
   Если provider gate не `PASS`, output имеет состояние `prepared/blocked` и
   выполнение останавливается до шага 1.
1. После accepted provider/privacy PASS на frozen representative subset
   выполнить настоящий L2 semantic build по
   pinned Wiki Skill/IA. Writer видит только frozen quote records и не читает
   упомянутые в них project files. Generated pages адресуют source quotes и
   internal Wiki pages, но не project knowledge corpus; receipt не копирует
   private quotes.
2. Из полученного L2 дерева выполнить реальный bottom-up build: сначала L1
   overviews, затем L0 abstracts для тех же semantic directories. Sidecars
   строятся из фактически созданного дерева, а не из статического validator
   projection или hand-written fixture.
3. Опубликовать только dedicated representative artifact root с route/tree
   digests и запустить десять изолированных matched runs. Вопрос, model/system
   prompt, answer schema, timeout, retry и grading protocol совпадают; меняется
   только заранее объявленный Wiki-vs-holder route.
4. Снять физические receipts финального маршрута: typed reads,
   evidence reads, context/total tokens, reader elapsed, discovery operations,
   retries, cache/status и source IDs. Static validator PASS без fresh reader
   receipts не закрывает gate.
5. Независимо проверить каждый case/arm по immutable v1 gold и выдать один
   aggregate verdict, не скрывая case-level FAIL или UNKNOWN усреднением.

## Acceptance contract

`PASS` возможен только при всех условиях ниже:

- **Correctness/currentness non-inferior.** Wiki arm не хуже holder arm по
  correctness и currentness на каждом matched case и в заранее объявленном
  aggregate; все v1 semantic hard failures остаются hard failures.
- **Efficiency.** По пяти matched cases есть не менее **25% improvement** в
  `context tokens` **или** `evidence reads`. Ни один другой material cost
  dimension не регрессирует более чем на **10%**: измеряются как минимум
  `typed reads`, tokens/total tokens и `reader elapsed`. Пропущенная метрика —
  `UNKNOWN`, а не ноль.
- **Route safety.** Historical/provenance вопрос адресно уходит к holders;
  no-gold вопрос abstain-ит или следует за frozen route expectation.
  Historical/no-gold confident answer из Wiki, invented provenance,
  superseded claim как current или scope-overclaim — hard `FAIL`.
- **Size is diagnostic only.** Visible representative Wiki/source ratio
  измеряется, но не ограничивает число страниц, длину файлов или общий объём и
  не участвует в PASS/FAIL. Completeness и отсутствие filler проверяются
  семантически независимо от размера.
- **Measured final route.** Вердикт опирается на десять fresh runs и их
  receipts, а не на длину файлов, static validator, byte parity, prompt
  inspection или writer self-report.
- Все cost thresholds, semantic predicates и aggregation rule были pinned до
  candidate read и не выведены из candidate answers, packets или observed
  winner.

`25%` и `10%` применяются к predeclared matched aggregation, а не к удобному
послефактум среднему. Любой выбранный aggregation должен быть тем же для
обоих arms и быть указан в input receipt до запуска readers.

## Falsifiers

Следующее атомарно falsifies gate или делает его `UNKNOWN`:

- Wave 6b использует Wave 5 utility PASS, pre-build rerun или candidate answer
  как permission/input — circular gate;
- subset, prompt, IA, model, budgets, thresholds или arm expectations меняются
  после чтения Wiki, reader packets или candidate answers;
- v1 gold, expected/forbidden criteria или hard failures изменены, даже если
  semantic output становится зелёным;
- L2/L1/L0 не построены end-to-end, sidecar подменён static validator или
  readers не прошли весь final route;
- case context, cache, allowed files, reader history или answer state
  пересекаются между cases/arms;
- Wiki/holder arm оценивается по чужому budget или обязательное поле нельзя
  получить из его allowed surface;
- historical/no-gold/superseded route нарушен, даже если средний score вырос;
- Wiki содержит link на project knowledge file, claim из прочитанного вне
  frozen quote input, chronology/evolution prose или superseded остаток;
- missing knowledge либо filler обнаружены semantic/coverage audit независимо
  от `wiki/source` ratio;
- context-token/read economy достигается ценой >10% regression в другом
  material cost dimension, скрытой orchestration latency или отсутствующего
  receipt;
- provider canary, privacy boundary, source digest или nested falsifier receipt
  отсутствует.
- source-bound preflight переиспользует старый six-holder pilot, меняет subset
  после candidate read, не совпадает с F1–F3 digests или пишет semantic claims,
  Wiki pages либо full private quotes;

## Receipts

Return обязан содержать:

- commit SHA и exact changed paths 6b implementation/tests/artifacts;
- input-lock state, source/record/subset counts и digests, Wave 6 lock, v1 gold,
  prompt/IA/model/config/code и provider-canary receipts;
- L2/L1/L0 output topology, counts/digests и proof, что sidecars построены
  bottom-up из фактического L2; source/Wiki text counts и compression ratio;
- десять case/arm packets с route, allowed surface, typed reads,
  evidence reads, context/total tokens, reader elapsed, retries/status,
  cited source IDs, gaps, hard-failure flags и grader result;
- unchanged-gold proof, no-candidate-derived-threshold proof, case-isolation
  proof и nested falsifier receipt;
- один `PASS | FAIL | UNKNOWN` с причиной по каждому criterion и final route.

Receipts не содержат полные private quotes, holder dumps, provider
transcripts, secrets или незаявленные absolute paths.

## Gate outcome

- `prepared/blocked` принимает только immutable representative input-lock. Это
  не utility verdict, не Wiki и не permission на semantic execution.
- **PASS** открывает Wave 7 full semantic generation. Wave 7 получает именно
  accepted 6b receipt и тот же pinned tuple; usefulness не переоценивается по
  гладкости candidate tree.
- **FAIL** или **UNKNOWN** блокирует full semantic backfill и не меняет
  deterministic Wave 6 snapshot. Root сохраняет receipt и причину; повтор
  возможен только с тем же immutable gold или с отдельно принятым новым
  snapshot, без молчаливой правки исторического evidence.
- Ни один 6b result не разрешает full build сам по себе и не становится заменой
  Wave 11 blind acceptance для полного candidate.

## Prohibitions

Не менять `_ops/chat-recall/**`, Wave 5 v1 gold, Wave 6 frozen foundation,
shared `task.md`/`status.md`, Wave 7+ artifacts, full Wiki или acceptance
thresholds. Не возобновлять незавершённый pre-build operations-v2 rerun как
отдельное разрешение. Не добавлять extra agents, extra cases или extra
questions после pinning. Не считать self-report, lint, static projection или
один положительный prompt доказательством utility.
