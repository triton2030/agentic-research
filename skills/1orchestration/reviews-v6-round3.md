# Reviews v6 — round 3 (second repeat, terminal residue)

Проверяемая версия: `draft-v6/**` после пяти trajectory findings round 2.
По `1skill-creation/references/check-approve.md:18–19` после второго повтора
правки не продолжаются молча: остаток назван, live/projections не меняются.

## Пять исходных trajectory findings

| Finding round 2 | Minimum structural correction | Evidence | Вердикт |
| --- | --- | --- | --- |
| `no-delegation` недостижим | `shape` выбирает форму до launch и может закончить `no-delegation` | naked skip probe | закрыт |
| Specialized controller получает вторую topology | `controller-handoff` terminal после `shape`; general skill возвращает только contracts/verdicts | fresh-eyes и managed probes | закрыт |
| Budget есть только у worker | `count` требует ledger каждого actor-а и root в следующей decision point | executor различил root/worker, но не перечислил units | структура закрыта, behavioral proof неполон |
| Capability отсутствует в feasibility | `shape` отделяет active-load verdict от capability sufficiency | executor назвал capability basis до assignment | закрыт |
| Carrier обновляется после synthesis | `execute` и `accept` пишут transition до зависимого хода; `integrate` — final transition | executor carrier: launch → return-held → accepted → integrated | carrier-ветвь закрыта; no-carrier ветвь имеет новый residue |

Снятые пути: отдельная managed topology, always-on carrier, static model table,
hard cap `20`, общий wait/retry controller. Поэтому candidate структурно проще
прежнего v6-кандидата, хотя ещё не готов к approval.

## Clean executor

Lifecycle исполнен настоящим nested worker-ом и сохранён в
`executor-carrier-v6.md`. Root не пересёк barrier до return и независимой
проверки; carrier обновлялся до каждого зависимого хода.

Executor не выполнил `count.md:6–9`: вместо внешних ledgers показал только
`14/18`, тогда как return содержит 27 source-specific rows. Это nonadherence
однозначному кандидату; новое дублирующее правило сознательно не добавляется.
Clean-executor proof остаётся неполным и требует повтора на следующей версии.

Scoped вывод executor-а, будто один `brief.md` обязан содержать стадии count,
budget и decompose, не принят: весь package распределяет их по routed owners.

## Final trajectory checker

Эталон: owners → полный contract → отдельные active ledgers → честная
decomposition → minimum capable topology → evidence acceptance → state до
integration.

Принятые findings:

1. `brief.md` не требует полноты owner-derived `done_when`; `accept` может
   корректно принять неполный contract. Minimum: полный набор критериев и
   addressable evidence для каждого.
2. Carrier условен, но `execute`, `accept`, `integrate` и completion безусловно
   требуют append/sync. Minimum: эти операции условны существованием созданного
   state owner-а.

## Final literal checker

Принятый residue candidate/history:

1. `brief.md` должен адресовать также доступные релевантные task inputs, а
   `delta` — отсутствовать во всех адресованных sources.
2. `decompose.md` должен позволять отбросить любые `active units`, не только
   `owner units`.
3. `map.md` должен адресовать global goal / trajectory owner.
4. `accept.md` должен явно относить blocker к недоказанному `done_when`.
5. Execute/accept требуют однозначного цикла по одному mandatory return;
   integration — только после обработки всех.
6. Scope change должен помечать затронутые artifacts stale и возвращать к
   самой ранней затронутой cognitive stage.
7. `origin.md` содержит устаревшие historical addresses; их надо исправить либо
   честно пометить недоступными.
8. После исправлений нужен новый полный clean executor с перечисленными
   worker/root units.

Не принято как правка candidate: буквальные owner-цитаты в runtime. Checker
нашёл конфликт `1skill-creation/references/behavior-protocol.md:6–7` с прямым
owner-запретом. В этой версии победила более свежая owner-boundary: quotes
остаются в history, runtime несёт смысл без verbatim. Возможная upstream-правка
`1skill-creation` вне scope этого refactor-а.

## Terminal verdict

Status: `candidate`, not approved. Пять исходных findings получили minimum
structural corrections, но final check-approve не чист: восемь candidate/history
residues и один неполный executor proof. По лимиту двух повторов работа
останавливается на адресуемом residue; installation запрещена.
