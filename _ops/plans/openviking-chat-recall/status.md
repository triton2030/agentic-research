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

Запустить F2 evidence-layer writer из принятого F1 source lock. F2 читает Git
objects exact corpus commit `6f98fcccdbf4b4de45ef787239ad101f70d106e2`,
не live holders, и адресует все 1101 parsed records и 34 diagnostics. Frozen
semantic gold остаётся неизменным. Следующий utility verdict снимается только
с настоящего representative L2/L1/L0 route, и его PASS откроет full semantic
Wave 7.

## Вехи

| Веха | Статус | Evidence |
| --- | --- | --- |
| 1. Контракты | в работе | Wave 4/4b accepted contracts; Wave 5 semantic contract принят, utility topology переносится после ingestion |
| 2. Compiler | в работе | F1 source lock принят; F2 deterministic evidence следующий |
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
PASS.

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

F1 return —
[wave-6-f1-source-lock](modules/_returns/wave-6-f1-source-lock.md). Root
подтвердил 24/24 tests и byte-identical fresh rebuild; независимый auditor
`/root/f1_acceptance` вернул PASS по 16 условиям. Nested checker writer-а
остался UNKNOWN и не использован как evidence.

## Планируемые волны

| Волна | Результат | Dependency | State |
| --- | --- | --- | --- |
| 6 | frozen snapshot, deterministic records, stable partitions, privacy fixture | accepted Wave 5 semantic contract + explicit corpus commit | active: F1 PASS, F2 next |
| 6b | representative L2/L1/L0 ingestion + matched final-route utility | Wave 6 pass | accepted card; execution waits for Wave 6 |
| 7 | semantic candidates и canonical current claims | Wave 6b utility PASS | planned |
| 8 | typed L2 pages, per-part validation и root catalog | Wave 7 pass | planned |
| 9 | bottom-up L1 overviews и deterministic L0 abstracts | Wave 8 pass | planned |
| 10 | exhaustive coverage, resume/crash/delete-rebuild receipts | Wave 9 pass | planned |
| 11 | blind five-case probe + full matched comparator | Wave 10 frozen candidate | planned |
| 12 | fresh-agent route, rebuild handoff и independent completion audit | terminal Wave 11 verdict: pass or explicit rejection | planned |

## Блокеры

Owner-блокера нет.

Закрытые semantic defects G0:

- generated-root cleanup обязан отклонять symlink escape и сохранять внешний
  sentinel;
- unresolved language route не может быть выдан как contested/current;
- historical subagent claim должен говорить только то, что есть в source;
- no-gold coverage gap ограничивается реально проверенными addresses.

Wave 6 source snapshot выбран: `6f98fcc`, 184 holder files и 1101 parsed
records. Из них 34 имеют diagnostics; compiler не удаляет их молча, а обязан
выдать явный rejected/skipped disposition. Перед передачей реальных holders
semantic provider-у отдельно остаётся обязательным privacy/provider fixture.
