---
эпик: "самостоятельный experiment: openviking-chat-recall"
план: "[[task|Batch compiler знаний из chat-recall]]"
состояние: 🔨 в работе
режим: Execution
вех-готово: 0
вех-всего: 5
обновлено: 2026-08-22
kind: status
---

# Статус — batch compiler знаний

## Next

Batch-002 принят как второй chronological checkpoint: 10 holders,
20 records, 9 active Wiki pages, 20/20 coverage, 8 index routes и blind
findability 4/4. Но Fresh Eyes и source-check нашли новый semantic
falsifier: source-backed строка может не отвечать на H1 страницы.
`method/global-skill-trigger.md` уже смешал цитаты про skill и
глобальную instruction. Механический model-check отдельно доказал, что
7/7 proposed files можно replay-ить детерминированно без Luna.

Единственный Next — завершить
[Wave 6f full-backfill transition](modules/wave-6f-full-backfill-transition.md).
Page-fit/split schema, deterministic materializer и chronological builder уже
реализованы; 13 targeted tests PASS, включая exact coverage/provenance
closure после independent implementation BLOCK. Frozen `batch-003-input.json` содержит
следующие 10 holders / 38 records и byte-identical проходит `--check`.
Осталось той же retained Luna починить найденное scope-mixing внутри v3
batch-003 draft, затем провести полный independent semantic audit и
детерминированно материализовать accepted bytes. После
этого full backfill идёт по одному reusable contract без новой permission-card
на каждые десять holders. Retained visible Luna Max task
`01a026fe-70a0-78d1-abad-12387192465e` не архивируется до terminal Wiki.

## Вехи

| Веха | Статус | Evidence |
| --- | --- | --- |
| 1. Контракты | в работе | Wave 4/4b accepted contracts; Wave 5 semantic contract принят, utility topology переносится после ingestion |
| 2. Compiler | в работе | F1–F3 приняты; F4 UNKNOWN; F4-R1 rejected; representative input-lock следующий |
| 3. Full build | ожидает | После sample gates и explicit frozen snapshot |
| 4. Normalize | ожидает | После coverage-complete full build |
| 5. Acceptance | ожидает | После frozen candidate Wiki |

## Текущая доказательная база

- Stock OpenViking runtime отклонен как рабочий route: health/resource import
  работали, но SDK skill upload и Compile расходились; receipt —
  experiments/openviking-chat-recall/artifacts/wave-3-receipt.md.
- Typed-evidence candidate 9319f71: 5/5 tests, byte-identical rebuild и exact
  count/first/latest на frozen records.
- Blind Luna Max reader восстановил exact recurrence и пять обязательств из
  трех Wiki pages; return — modules/return-wave-3-typed-evidence-probe.md.
- Владелец выбрал custom compiler: OpenViking prompts, IA и layers без stock
  runtime; holder указан в task.md.
- Поздняя коррекция владельца сняла chronology-heavy Wiki: источники сохраняют
  историю, Wiki хранит дистиллированные знания. Route записан в
  modules/_returns/fresh-eyes-distilled-knowledge.md.
- Последняя коррекция владельца уточнила topology и lifecycle: Wiki ссылается
  на quotes, но не на project knowledge files; хранит только переписываемый
  актуальный итог. Число страниц, длина файлов и compression ratio не имеют
  лимитов или targets; 5–10× остаётся только наблюдаемым ожиданием после полного
  backfill. Главный semantic gate — claim-level source support без
  неподтверждённых фактов, causality, scope, status или recommendations. Holder —
  `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.
- Chronological batch-002 принят: 10 holders, 20 records, 3 update, 4 create,
  1 reject; current Wiki — 9 pages. Root и independent auditor подтвердили
  changeset replay, receipt/provenance, frozen source targets и index integrity.
  Return —
  [wave-6d chronological batch-002](modules/_returns/wave-6d-chronological-batch-002.md).
- Acceptance lock интегрирован commit a77fc4c: пять cases и hard failures
  зафиксированы до принятия candidate Wiki.
- Probe chain ae3bd56 → f2ca300 дал воспроизводимый frozen candidate;
  root main и clean detached run на f2ca300 прошли 16/16 tests.
- Независимая техническая приемка 581e85c нашла symlink escape при cleanup
  generated root. Семантическая приемка нашла unsupported contested status,
  один overstated prior claim и corpus-wide wording при двух checked addresses.
  Точный return —
  [wave-5-repair-audits](modules/_returns/wave-5-repair-audits.md).

## Wave 4 registry

| Task | Title | Card | Worktree | State |
| --- | --- | --- | --- | --- |
| 01a0248f-9a1b-71d0-ac76-9c9247e0d23d | OpenViking: карта корпуса | wave-4-corpus-map.md | 25bc | terminal candidate |
| 01a0248f-9a14-7a53-877a-56a4f0acb12a | OpenViking: seam компилятора | wave-4-compiler-seam.md | 1b54 | terminal candidate |
| 01a02490-90e6-7a71-8120-8451f7ad4016 | OpenViking: prompt и IA | wave-4-openviking-ia.md | 93c9 | terminal candidate |
| 01a0248f-9a1b-71d0-ac76-9c52161efcf2 | OpenViking: LLM route | wave-4-llm-route.md | 2901 | terminal candidate |
| 01a0248f-9a14-7a53-877a-568219d57716 | OpenViking: acceptance contract | wave-4-acceptance.md | 2e80 | terminal candidate |
| 01a0248f-9a1b-71d0-ac76-9c7d8ac02686 | OpenViking: privacy и recovery | wave-4-privacy-operations.md | b2e6 | terminal candidate |

Wave 4 закончена как contract evidence, не как permission на full build.

## Wave 4b registry

| Task | Title | Card | Worktree | State |
| --- | --- | --- | --- | --- |
| 01a024a2-245a-7a91-95c2-d5cacb530c76 | OpenViking: L0 L1 prompts | wave-4b-context-layer-prompts.md | a5dc | terminal candidate |
| 01a024a2-245a-7a91-95c2-d58e0db293a2 | OpenViking: layered seam | wave-4b-layered-seam.md | aa2d | terminal candidate |
| 01a024a2-245a-7a91-95c2-d5aeba7a18cc | OpenViking: generation execution | wave-4b-generation-execution.md | 57af | terminal candidate |

Root подтвердил: L1 использует overview_generation.yaml; L0 извлекается из
Brief Description L1; L2 writer не пишет sidecars. Accepted contract —
modules/_returns/wave-4b-contracts.md.

## Wave 5 registry

| Task | Title | Card | State |
| --- | --- | --- | --- |
| 01a024c0-0f08-7870-85ef-d9d0b1784da5 | OpenViking: distilled probe | wave-5-distilled-probe.md | terminal candidate f2ca300; behavior pending |
| 01a024c0-0f10-7f02-b209-d0524247d432 | OpenViking: acceptance lock | wave-5-distilled-acceptance.md | terminal; integrated a77fc4c |
| 01a024c0-0f0e-7220-861e-aeb7f67e570d | OpenViking: contract red-team | wave-5-distilled-red-team.md | terminal read-only |

Все top-level задачи — gpt-5.6-luna/max с обязательным nested orchestration.
Inner-agent UNKNOWN не принят как evidence.

Blind arms Wiki `01a02587-f765-7ae3-8382-7d64283388ed` и holders
`01a02587-f16a-7a82-9fd7-c75281594395` terminal. Independent matched verdict —
FAIL: один five-case session нарушил per-case budgets/reporting; raw packets —
`modules/_returns/wave-5-blind-reader-packets.json`, verdict —
`modules/_returns/wave-5-matched-grader.md`.

Pre-build repair card
[wave-5-acceptance-operations-amendment](modules/wave-5-acceptance-operations-amendment.md)
остановлена после Fresh Eyes: её case-isolation сохраняется как требование, но
utility нельзя принимать до ingestion настоящего representative route.

## Detailed-plan registry

| Task | Title | Scope | State |
| --- | --- | --- | --- |
| 01a0255d-8b25-7e13-85ee-a74fff61dc6a | OpenViking: full compiler plan | snapshot → L2/L1/L0 → receipts | terminal candidate; root-adapted |
| 01a0255d-8b20-7471-a0e1-2454629f3aa0 | OpenViking: full acceptance plan | blind audit → coverage/privacy → handoff | terminal candidate; root-adapted |
| 01a025ae-59cf-7883-976b-1449e19e5439 | OpenViking: post-ingestion pilot gate | representative L2/L1/L0 → matched utility | terminal; integrated 7a6cdf5 |

Оба треда были gpt-5.6-luna/max и запустили внутренний fan-out. Все шесть
внутренних agents остались UNKNOWN после bounded waits; их содержательные
выводы не использованы. Root проверил frozen counts и material gates напрямую.

Независимый plan-audit и root repairs записаны в
[detailed-plan-audit](modules/_returns/detailed-plan-audit.md); nested recheck
пока UNKNOWN.

Fresh Eyes trajectory correction и четыре разные опоры записаны в
[fresh-eyes-post-ingestion-gate](modules/_returns/fresh-eyes-post-ingestion-gate.md).
Wave 6b writer запустил nested Luna Max auditor
`01a025b5-e79a-7c81-a2c5-261ac06be8ff`; circular gate и semantic acceptance —
исторический PASS прежней role-map, не evidence для текущего terminal gate.
Перед terminal verdict independent falsifier выполняет Opus без writer
transcript.

Source-frontier task `01a025bb-e6d4-7c00-94ce-bafd7bb932e1` доказал, что
предыдущий `HEAD` терял 26 parsed records. Все восемь holder overlays сохранены
без изменения текста в explicit source commit `6f98fcc`; точные counts и
diagnostics — [wave-6-source-frontier](modules/_returns/wave-6-source-frontier.md).
Nested denominator checker остался terminal UNKNOWN и не использован как
evidence.

## Wave 6 registry

| Task | Stage | Ownership | State |
| --- | --- | --- | --- |
| 01a025ca-3714-7082-be9f-27ece6673e54 | F1 frozen source lock | freeze script/test + frozen manifest/lock | accepted `acb3def` + `31c8a4f` |
| 01a025ef-35d5-7791-a2c8-323259126faa | F2 deterministic evidence | evidence script/test + records/coverage | accepted `ea569e2` |
| 01a02629-b1e2-71d2-949f-9a605f686b8b | F3 stable partitions | partition writer/test + manifest/8 parts | accepted `c5bbe41` |
| 01a02657-d943-7013-b1a6-36be71b59b68 | F4 provider canary | writer/test + public UNKNOWN receipt | accepted `UNKNOWN` on `c7ceed0`; no retry |
| 01a02681-32dd-7de1-8d4c-014972769587 | F4-R1 provider repair | three-path candidate + separate v2 receipt | rejected by final audit; commits not integrated; terminal `UNKNOWN` |
| 01a026cd-2baf-7982-ac1f-303b04c29302 | P-1 representative input-lock | system design + implementation | stopped before writes; clean worktree; archived after owner model-role correction |

F1 return —
[wave-6-f1-source-lock](modules/_returns/wave-6-f1-source-lock.md). Root
подтвердил 24/24 tests и byte-identical fresh rebuild; независимый auditor
`/root/f1_acceptance` вернул PASS по 16 условиям. Nested checker writer-а
остался UNKNOWN и не использован как evidence.

F2 return —
[wave-6-f2-evidence-layer](modules/_returns/wave-6-f2-evidence-layer.md).
Root подтвердил 32/32 tests, committed `--check` и exact-one JSON audit. Первый
auditor дал FAIL из-за неоднозначного dirty-live bullet; второй independent
Luna Max audit доказал, что rejection принадлежит F1, а F2-owned invariant —
byte-identical output независимо от live holder tree. Карточка уточнена.

F3 return —
[wave-6-f3-stable-partitions](modules/_returns/wave-6-f3-stable-partitions.md).
Root подтвердил два fresh public-CLI build, exact F2 equality и 43/43 tests;
independent Luna Max auditor вернул PASS. Semantic utility не выводится из
balance и остаётся отдельным Wave 6b gate.

F4 return —
[wave-6-f4-provider-canary](modules/_returns/wave-6-f4-provider-canary.md).
Одна real synthetic попытка дошла до local artifact writer, который упал на
absolute/relative containment до долговечной записи результата. Повтора не
было; usage/model/nonce не восстановлены и terminal verdict остаётся UNKNOWN.
Current fix прошёл 59/59 tests и root full-pipeline fake preflight. Отдельная
repair card —
[wave-6-provider-canary-repair](modules/wave-6-provider-canary-repair.md).
Independent Luna Max runtime audit принял UNKNOWN receipt, но запретил retry
до code repair: all-model drift, required run address и явные provider/retry
policy поля пока не имеют fail-closed contract.

F4-R1 return —
[wave-6-f4-r1-provider-canary](modules/_returns/wave-6-f4-r1-provider-canary.md).
Root подтвердил 32/32 targeted и 75/75 full tests, но independent final audit
нашёл два новых false-PASS: null usage при addressable status и два real
requests. Candidate `84cda7f → 5bfbffb → 9b1cdaf` не интегрирован; дальнейший
provider repair снят с текущей траектории после Fresh Eyes.

## Планируемые волны

| Волна | Результат | Dependency | State |
| --- | --- | --- | --- |
| 6 | frozen snapshot, deterministic records, stable partitions; provider gate separate | accepted Wave 5 semantic contract + explicit corpus commit | deterministic F1/F2/F3 PASS; provider F4 UNKNOWN; F4-R1 rejected |
| 6c | first chronological serial changeset + candidate Wiki checkpoint | accepted F1–F3 + explicit owner authorization | owner-liked Wiki `6ab9cb9`; root structural/provenance PASS |
| 6d | second chronological draft/materialization checkpoint | batch-001 accepted + owner-authorized next 10 holders | accepted: 10 holders / 20 records; 3 update + 4 create + 1 reject; tree `71bc5b…` |
| 6e | blind index-first findability | current Wiki frozen before batch-002 draft | PASS: [wave-6e return](modules/_returns/wave-6e-blind-findability.md); task `01a02750…` archived |
| 6f | page-fit/split + deterministic replay + shadow batch-003 | accepted batch-002 + Fresh Eyes/model-check | **Next: ready** |
| 6b | historical representative/provider route | F1–F3 | superseded as pre-backfill permission route; input-lock evidence retained |
| 7 | historical parallel semantic candidates route | Wave 6b utility PASS | superseded by chronological fold |
| 8 | historical parallel L2 build route | Wave 7 pass | superseded by chronological fold |
| 9 | terminal L1/L0 projection over complete L2 | full chronological L2 Wiki | deferred until complete L2; not a batch blocker |
| 10 | exhaustive coverage, resume/crash/delete-rebuild receipts | Wave 9 pass | planned |
| 11 | blind five-case probe + full matched comparator | Wave 10 frozen candidate | planned |
| 12 | fresh-agent route, rebuild handoff и independent completion audit | terminal Wave 11 verdict: pass or explicit rejection | planned |

## Блокеры

Owner-блокера нет. Full backfill разрешён ранним owner-decision
после успешного pilot; текущий blocker внутренний — Wave 6f transition.

Закрытые semantic defects G0:

- generated-root cleanup обязан отклонять symlink escape и сохранять внешний
  sentinel;
- unresolved language route не может быть выдан как contested/current;
- historical subagent claim должен говорить только то, что есть в source;
- no-gold coverage gap ограничивается реально проверенными addresses.

Wave 6 source snapshot выбран: `6f98fcc`, 184 holder files и 1101 parsed
records. Из них 34 имеют diagnostics; compiler не удаляет их молча, а обязан
выдать явный rejected/skipped disposition. Source-bound input-lock разрешён,
но перед передачей реальных holders semantic provider-у обязателен новый
accepted provider/privacy PASS. F4/F4-R1 `UNKNOWN` не являются permission на
semantic Wave 6b.
