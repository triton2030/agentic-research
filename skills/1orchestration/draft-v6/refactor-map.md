# Refactor map v6 — 1orchestration

## Функция

Перед любым поручением субагенту превратить работу в выполнимые когнитивные
наборы: root читает влияющие источники, формирует полный
`goal/done_when/read/delta` контракт, перечисляет активные единицы root и
исполнителей, делит только там, где следующий участник сможет отбросить часть
единиц, и принимает единый доказанный результат.

## Уникальный контекст

Поручение — временный слой инструкций поверх канонической правды. Только
оркестратор видит целую карту участников и может уменьшать их одновременную
нагрузку, сохраняя траекторию во внешнем владельце, а не в памяти одного окна.

## Цель владельца

Развивать когнитивную работу до выполнимого списка задач. Качество зависит не
только от субъективной сложности, но и от числа независимо удерживаемых
инструкций, критериев и знаний. Контракт адресует источники, сообщает
отсутствующую `delta` и получает вердикт нагрузки после формирования.

## Момент вызова

- Use: перед поручением любому субагенту, включая одного обычного исполнителя
  и управляемый фоновый тред.
- Use: когда root делит собственную перегруженную когнитивную работу.
- Специализированный контроллер сохраняет схему; сюда отдаёт только контракты
  и вердикты нагрузки своих исполнителей.
- Skip: локальная работа root без делегирования и признака перегруза.

Проверенные trigger-пробы:

- ordinary use: `Поручи субагенту проверить этот файл`;
- overloaded use: `Разбей сложную задачу между агентами`;
- managed use: `Вынеси анализ логов в фоновый тред`;
- specialized composition: `Проведи fresh-eyes аудит траектории проекта`;
- skip: `Исправь эту опечатку сам`.

## Три цели

1. Root прочитал полную карту источников.
2. Каждый исполнитель и root получили выполнимый когнитивный контракт.
3. Root закрыл одну оркестрацию доказанным результатом и актуальным состоянием.

## Карта стадий и active sets

Runtime body содержит 17 independently actionable units: unique context · три
цели · одиннадцать взаимоисключающих route decisions · две terminal branches.
На выбранной стадии применимы 5: context · goals · одна route. Description —
отдельное trigger decision до входа в protocol.

| Stage | Наблюдаемый выход | Ref units | Carried | Active total |
|---|---|---:|---:|---:|
| orient | прочитанная карта источников | 6 | 0 | 11 |
| brief | полный когнитивный контракт | 12 | 1 адрес карты | 18 |
| count | перечисленный реестр участника/root | 7 | 2 адреса источников и поручения | 14 |
| budget | `manageable|decompose` с основанием | 9 | 2 адреса реестра и точки решения | 16 |
| decompose | меньшие наборы либо названный перегруз | 11 | 2 адреса общей цели и источников | 18 |
| shape | `no-delegation|controller-handoff|own topology` | 9 | 1 набор вердиктов | 15 |
| map | видимая карта запуска | 10 | 1 решение о форме | 16 |
| carrier | адресуемый реестр восстановления | 10 | 1 адрес карты запуска | 16 |
| execute | следующий возврат либо blocker за барьером | 12 | 2 адреса запуска и состояния | 19 |
| accept | вердикт одного возврата | 11 | 2 адреса `done_when` и состояния | 18 |
| integrate | единый результат и финальный переход | 11 | 3 адреса приёмки, цели и состояния | 19 |

Past artifacts stay external. A stage keeps only named cursors and the current
unit/decision active; exclusion from simultaneous memory does not exclude any
task unit from its own count.

## Correspondence к прежнему live contract

| Старый смысл | Текущий owner |
|---|---|
| General wave trigger | Broadened by 2026-08-29 owner correction to every subagent prompt. |
| Ordinary one-worker skip | Removed; `shape` can still return no-delegation. |
| Specialized controller exclusion | Recast as `controller-handoff`, not a second topology. |
| Root direct owner-reading | `orient`. |
| Work + instruction-load allocation | `brief → count → budget → decompose`. |
| Model/cognitive suitability | `budget` and capability gate in `shape`; no static model table. |
| Minimal windows and dependent stages | `decompose` and `shape`. |
| Chat map, ownership, barrier, return, acceptance owner | `map`. |
| Evidence before synthesis, verifier only by risk/contract | `accept`. |
| Root conflict/claim/integration/chat proof | `integrate`. |
| Conditional no-plan carrier and decision registry | `carrier` as transition ledger. |
| Stalled wait/follow-up/retry lifecycle | Live runtime owner; orchestration retains semantic barrier only. |
| Root recovery | Live plan/carrier transition history; no separate procedural controller. |

## Agent-default chains для добавок

| Добавка | default → mechanism → decision → harm without → price |
|---|---|
| `no-delegation` in shape | Invoked orchestration tends to launch → work already spent on a brief → compare cognitive gain with handoff → needless worker ceremony → root may retain a manageable task. |
| Specialized handoff | General protocol tends to finish its own wave → nearby topology feels complete → return contracts to live controller → duplicated barriers/acceptance → general skill cannot redesign specialized roles. |
| Capability gate | Low count looks sufficient → budget ignores domain ability → prove actor sufficiency before assignment → manageable but incapable worker fails → runtime keeps freedom to choose exact implementation. |
| Scope change invalidates contract | Started work tends to continue → sunk trajectory masks new owners/units → re-enter cognitive stages → stale brief or hidden overload → reshaping costs another pass. |
| Soft threshold escape | `20` looks like enforcement → numeric gate invites harmful splitting → allow named overload when no honest boundary shrinks units → goal mutilation or infinite split → accepted lower adherence needs checkpoints. |
| Pre-integration state append | Agents defer bookkeeping to the end → integration feels like natural save point → append recovery transition before dependent move → root break replays action or loses acceptance → more state writes during a wave. |
| Runtime owns lifecycle | Barrier semantics resemble wait/retry mechanics → closest instruction takes over tool behavior → orchestration stops at semantic state; runtime launches/waits/repairs → invalid polling/retry/archive → another live owner must be read. |
| Auditable count | Agent estimates a plausible number → a bare total looks sufficient → total must equal separately listed entries → hidden overload passes budget → a longer external ledger. |

Owner-exact rules — every subagent trigger, root owner-reading, address+delta,
brief-before-count and cognitive threshold — do not need agent-default invention.
Scoped `1plan-task` exception may carry a few owner-addressed critical excerpts;
each remains an active unit.

## Протокол поведения

| Likely misread | Gap / price | Structural correction |
|---|---|---|
| Split first, inspect owners later | Every child inherits hidden load. | `orient → brief → count → budget` precedes decomposition. |
| Count prompt lines | Independent obligations disappear syntactically. | `count` requires separate entries and derives the total from them. |
| More agents always lower load | Handoff and shared owners can increase it. | Boundary must let the next actor drop units; `shape` prices handoff. |
| Only worker needs a budget | Root becomes the overloaded CTO bottleneck. | `count` names root at each decision point. |
| Specialized wave continues through general execute | Two controllers own topology. | `controller-handoff` is terminal after shape. |
| Conditional carrier becomes mandatory | Cheap work creates bookkeeping or cannot finish. | State writes are conditional in execute/accept/integrate and completion. |
| Save carrier after synthesis | Root break loses launch/acceptance state. | execute/accept append before dependent moves. |
| Progress means accepted | Synthesis consumes an unproved return. | `accept` is a separate evidence gate. |
| First return triggers synthesis | Later mandatory packets are skipped. | Body cycles execute → accept until every return has a verdict. |

## Принципы

- `agentic-research:P-002` — active set and capability, not agent count, choose form.
- `agentic-research:P-003` — latest owner corrections broaden trigger but reject
  harmful literalism and runtime owner quotes.
- `agentic-research:P-005` — proof is actual ledger, verdict, trajectory,
  evidence acceptance and state transition.
- `agentic-research:P-007/P-008` — canonical owners keep truth, specialized
  controllers keep topology, runtime owners keep lifecycle.
