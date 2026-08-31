# Refactor map v6 — 1orchestration

## Функция

Перед любым поручением субагенту превратить работу в выполнимые когнитивные
наборы: root читает влияющие источники, формирует полный
`goal/done_when/read/delta` контракт, оценивает активные единицы root и
исполнителей, а при спорной нагрузке перечисляет их. Деление допустимо только
там, где следующий участник сможет отбросить часть единиц. Простая работа не
становится волной.

## Уникальный контекст

Поручение — временный слой инструкций поверх канонической правды. Только
оркестратор видит целую карту участников, требуемую схему и полномочия живых
владельцев. Он уменьшает их одновременную нагрузку, включая решения root, но
не создаёт control-plane там, где достаточно прямого назначения.

## Цель владельца

Развивать когнитивную работу до выполнимого списка задач. Качество зависит не
только от субъективной сложности, но и от числа независимо удерживаемых
инструкций, критериев и знаний. Контракт адресует источники и сообщает только
отсутствующую `delta`; после его формирования активный набор получает
пропорциональную оценку, а не безусловный ритуал.

## Момент вызова

- Use: перед поручением любому субагенту, включая одного обычного исполнителя
  и управляемый фоновый тред.
- Use: когда root делит собственную перегруженную когнитивную работу.
- Специализированный контроллер сохраняет схему; общий skill возвращает ему
  поручения и только уже нужные вердикты нагрузки.
- Skip: локальная работа root без делегирования и признака перегруза.

Проверенные trigger-пробы:

- ordinary use: `Поручи субагенту проверить этот файл`;
- overloaded use: `Разбей сложную задачу между агентами`;
- managed use: `Вынеси анализ логов в фоновый тред`;
- specialized composition: `Проведи fresh-eyes аудит траектории проекта`;
- skip: `Исправь эту опечатку сам`.

## Три цели

1. Доказуемый когнитивный контракт.
2. Выполнимый активный набор.
3. Доказанный результат в требуемой схеме полномочий.

## Карта стадий и active sets

Runtime body содержит 20 единиц: `C1` — траектория пользы к общей цели;
`G1–G3` — три цели; `R1` — stale-инвалидация; `R2–R16` — пятнадцать
взаимоисключающих route decisions.

На выбранной стадии активны `C1 + G1–G3 + R1 + одна R2–R16` = 6 единиц.
Description — отдельное trigger decision до входа. Повторяющий вход reference
совпадает с route и второй единицей не считается; локальная цель reference
заменяет выводимые инструкции, а не добавляется к их старому списку.

| Stage | Уникальные единицы reference | Ref | Carried | Total |
|---|---|---:|---:|---:|
| orient | `O1` локальная цель; `O2` карта адрес→влияние; `O3` root читает каждый адрес; `O4` blocker только при невозможном контракте; `O5` исследуемый gap входит в контракт | 5 | 0 | 11 |
| brief | `B1` локальная цель «контракт, не канон»; `B2` самодостаточный draft; `B3` goal; `B4` полный done_when из goal/sources/delta; `B5` evidence каждого и общей цели; `B6` read owner/task addresses; `B7` delta отсутствует в них; `B8` не пересказывать, кроме addressed live-owner exception | 8 | 1 | 15 |
| count | `C1` локальная цель спорной нагрузки; `C2` ledgers actor/root-point; `C3` independently forgettable unit; `C4` owner/delta units отдельно; `C5` склейка не уменьшает; `C6` total из entries | 6 | 2 | 14 |
| budget | `U1` локальная цель без hard cap; `U2` verdict+basis; `U3` число/coupling/horizon; `U4` ≤20 обычно manageable, но не магический предел | 4 | 2 | 12 |
| decompose | `D1` локальная цель boundary-drops-units; `D2` меньшие sets/принятый overload; `D3` dependencies→stages, independent→parallel; `D4` неразложимый risk→checks; `D5` reselect stage | 5 | 2 | 13 |
| handoff | `H1` specialized owner сохраняет topology/acceptance; `H2` resolved-load input; `H3` brief+verdict packet; `H4` owner выбирает boundaries/schema/acceptance; `H5` evidence каждого done_when | 8 | 1 | 15 |
| shape | `S1` minimal sufficient form; `S2` external ownership; `S3` direct-not-wave; `S4` resolved-load input; `S5` один исход формы; `S6` contract; `S7` explicit actor/topology constraints | 7 | 1 | 14 |
| assign | `N1` capable actor; `N2` live runtime owner; `N3` assignments+slots; `N4` root slot; `N5` direct actor slot; `N6` simple acceptance pipeline; `N7` no map/carrier; `N8` own slots; `N9` own→map | 9 | 1 | 16 |
| map | `M1` unambiguous launch; `M2` карта до launch; `M3` global owner; `M4` brief; `M5` actor; `M6` order; `M7` barrier; `M8` write owner; `M9` slot; `M10` return channel; `M11` acceptance owner | 11 | 1 | 18 |
| carrier | `K1` recovery, не canon; `K2` локальная цель; `K3` recovery ledger; `K4` gitignored carrier+address; `K5` map+transitions before dependent move; `K6` branch transition+basis+evidence | 6 | 1 | 13 |
| execute | `E1` локальная цель одного slot outcome; `E2` outcome с зависимым hold; `E3` runtime owner решает parallel/serial; `E4` conditional state transition before dependent move | 4 | 2 | 12 |
| verify | `V1` every-done_when goal; `V2` proven|terminal-blocker output; `V3` evidence каждого done_when; `V4` verifier by risk/contract; `V5` verifier not author; `V6` missing→blocker; `V7` else proven | 7 | 2 | 15 |
| accept | `A1` close-before-dependent goal; `A2` accepted|blocked output; `A3` proven closes accepted; `A4` blocker closes blocked; `A5` stop dependent branch; `A6` material-outcome invalidation; `A7` state before body | 7 | 2 | 15 |
| integrate | `I1` локальная цель общего результата; `I2` close orchestration; `I3` canonical evidence, не voting; `I4` chat map/evidence/gaps/next; `I5` conditional final state и durable truth to canon | 5 | 3 | 14 |

`controller-handoff` заканчивает общий skill после `orient → brief → estimate →
handoff`; специализированный владелец принимает результат своей схемой.
`direct-assignment` и `no-delegation` идут через `shape → assign → execute →
verify → accept → integrate`, но не создают `map` и `carrier`. Past artifacts
остаются внешними адресами; carried-колонка считает только курсор текущего
решения.

## Correspondence к прежнему live contract

| Старый смысл | Текущий owner |
|---|---|
| General wave trigger | Broadened by 2026-08-29 owner correction to every subagent prompt. |
| Ordinary one-worker skip | Removed; `shape` can still return no-delegation. |
| Specialized controller exclusion | `handoff` возвращает brief/verdict владельцу topology. |
| Root direct owner-reading | `orient`. |
| Work + instruction-load allocation | `brief → lightweight estimate`; спорное → `count → budget → decompose`. |
| Model/cognitive suitability | `budget` and capability goal in `assign`; no static model table. |
| Minimal windows and dependent stages | `shape`; при перегрузе — `decompose`. |
| Chat map, ownership, barrier, return, acceptance owner | `map`. |
| Evidence before synthesis, verifier only by risk/contract | `verify → accept`. |
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
| Auditable count | Agent near threshold estimates a plausible number → a bare total looks sufficient → conditional ledger derives total from entries → hidden overload passes budget → спорная ветвь получает более длинный trace. |

Owner-exact rules — every subagent trigger, root owner-reading, address+delta,
brief-before-count and cognitive threshold — do not need agent-default invention.
Scoped `1plan-task` exception may carry a few owner-addressed critical excerpts;
each remains an active unit.

## Протокол поведения

| Likely misread | Gap / price | Structural correction |
|---|---|---|
| Split first, inspect owners later | Every child inherits hidden load. | `orient → brief` precedes any split; спорная нагрузка проходит `count → budget`. |
| Count prompt lines | Independent obligations disappear syntactically. | `count` requires separate entries and derives the total from them. |
| More agents always lower load | Handoff and shared owners can increase it. | Boundary must let the next actor drop units; `shape` keeps the minimum form. |
| Only worker needs a budget | Root becomes the overloaded CTO bottleneck. | `count` names root at each decision point. |
| Specialized wave continues through general execute | Two controllers own topology. | `controller-handoff` is terminal after `handoff`. |
| Simple brief becomes a wave | One worker pays for ledgers, map and carrier. | Light estimate skips count-ledger, `map` and `carrier`, but retains exact acceptance. |
| Conditional carrier becomes mandatory | Cheap work creates bookkeeping or cannot finish. | State writes are conditional in execute/accept/integrate and completion. |
| Save carrier after synthesis | Root break loses launch/acceptance state. | execute/accept append before dependent moves. |
| Progress means accepted | Synthesis consumes an unproved return. | `verify` is a separate evidence gate before closure. |
| First return triggers synthesis | Later mandatory packets are skipped. | Body cycles `execute → verify → accept` until every slot is closed. |

## Принципы

- `agentic-research:P-002` — active set and capability, not agent count, choose form.
- `agentic-research:P-003` — latest owner corrections broaden trigger but reject
  harmful literalism and runtime owner quotes.
- `agentic-research:P-005` — proof follows the selected path: actual ledger only
  on the disputed-load branch; evidence acceptance and state transition when
  their branches exist.
- `agentic-research:P-007/P-008` — canonical owners keep truth, specialized
  controllers keep topology, runtime owners keep lifecycle.
