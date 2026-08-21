---
эпик: "самостоятельный experiment: openviking-chat-recall"
план: "[[task|Batch compiler знаний из chat-recall]]"
состояние: 🔨 в работе
режим: Execution
вех-готово: 0
вех-всего: 5
обновлено: 2026-08-21
kind: status
---

# Статус — batch compiler знаний

## Next

Принять исправленный representative probe: закрыть symlink-containment и три
semantic corrections, затем независимо повторить 13+ tests, adversarial cleanup
и пять locked cases. Только accepted G0 открывает Wave 6.

## Вехи

| Веха | Статус | Evidence |
| --- | --- | --- |
| 1. Контракты | в работе | Wave 4/4b accepted contracts; Wave 5 repair проходит повторную приемку |
| 2. Compiler | ожидает | Подробные cards Waves 6–10 записаны; gate — accepted G0 |
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
- Probe commits ae3bd56 → 581e85c дали воспроизводимый frozen candidate;
  root clean-worktree run на 581e85c прошел 13/13 tests.
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
| 01a024c0-0f08-7870-85ef-d9d0b1784da5 | OpenViking: distilled probe | wave-5-distilled-probe.md | active repair after independent blockers |
| 01a024c0-0f10-7f02-b209-d0524247d432 | OpenViking: acceptance lock | wave-5-distilled-acceptance.md | terminal; integrated a77fc4c |
| 01a024c0-0f0e-7220-861e-aeb7f67e570d | OpenViking: contract red-team | wave-5-distilled-red-team.md | terminal read-only |

Все top-level задачи — gpt-5.6-luna/max с обязательным nested orchestration.
Inner-agent UNKNOWN не принят как evidence.

## Detailed-plan registry

| Task | Title | Scope | State |
| --- | --- | --- | --- |
| 01a0255d-8b25-7e13-85ee-a74fff61dc6a | OpenViking: full compiler plan | snapshot → L2/L1/L0 → receipts | terminal candidate; root-adapted |
| 01a0255d-8b20-7471-a0e1-2454629f3aa0 | OpenViking: full acceptance plan | blind audit → coverage/privacy → handoff | terminal candidate; root-adapted |

Оба треда были gpt-5.6-luna/max и запустили внутренний fan-out. Все шесть
внутренних agents остались UNKNOWN после bounded waits; их содержательные
выводы не использованы. Root проверил frozen counts и material gates напрямую.

Независимый plan-audit и root repairs записаны в
[detailed-plan-audit](modules/_returns/detailed-plan-audit.md); nested recheck
пока UNKNOWN.

## Планируемые волны

| Волна | Результат | Dependency | State |
| --- | --- | --- | --- |
| 6 | frozen snapshot, deterministic records, stable partitions, privacy fixture | accepted Wave 5 G0 | planned |
| 7 | semantic candidates и canonical current claims | Wave 6 pass | planned |
| 8 | typed L2 pages, per-part validation и root catalog | Wave 7 pass | planned |
| 9 | bottom-up L1 overviews и deterministic L0 abstracts | Wave 8 pass | planned |
| 10 | exhaustive coverage, resume/crash/delete-rebuild receipts | Wave 9 pass | planned |
| 11 | blind five-case probe + full matched comparator | Wave 10 frozen candidate | planned |
| 12 | fresh-agent route, rebuild handoff и independent completion audit | terminal Wave 11 verdict: pass or explicit rejection | planned |

## Блокеры

Owner-блокера нет.

Dependency blockers G0:

- generated-root cleanup обязан отклонять symlink escape и сохранять внешний
  sentinel;
- unresolved language route не может быть выдан как contested/current;
- historical subagent claim должен говорить только то, что есть в source;
- no-gold coverage gap ограничивается реально проверенными addresses.

Full build отдельно заблокирован до принятого privacy/provider fixture и нового
explicit corpus snapshot. Планировочный baseline a77fc4c содержит 180 holders /
1074 records; это не обещание, что финальный snapshot останется тем же.
