# v6 round 2 — clean check record

Дата: 2026-08-29. Этот раунд проверял промежуточную cognitive-decomposition
версию до structural correction, описанной ниже; он не является approval
evidence следующей версии.

## Instruction checker — findings и решения

1. Заявленные counts считали bullets, а active sets доходили до 33.
   Принято: runtime body сокращён до 17 units; flow пересобран, refs и carried
   sets пересчитаны по independently actionable predicates.
2. Description мог читаться как trigger только при уже замеченном overload.
   Принято: `Use before root assigns any subagent or splits cognitive work`.
3. `repair` мог читаться одновременно с execute.
   Принято структурно: отдельный repair controller снят; runtime owner владеет
   lifecycle, orchestration — semantic barrier.
4. Dependency-bearing refs были unordered checklists.
   Принято: cognitive stages используют numbered order; schemas остаются fields.
5. State сохранялся только после integration.
   Принято: execute и accept append transition до следующего dependent move;
   carrier — recovery ledger, не второй lifecycle owner.
6. Completion смешивал no-delegation и launched topology.
   Принято: две terminal branches названы отдельно.
7. `cut.md` направлял root recovery в отсутствующий `repair.md`.
   Принято: история теперь называет plan/carrier transition state и runtime seam.
8. Actual trigger probes и full executor trace отсутствовали.
   Принято как pending evidence для финального clean round, не закрыто текстом.

## Trajectory checker — minimum structural corrections

| Finding | Решение |
|---|---|
| `no-delegation` недостижим | `shape` выбирает cheapest manageable topology, включая root. |
| Specialized controller получает вторую topology | `controller-handoff` возвращает contracts/verdicts и terminal до map/execute. |
| Budget есть только у worker | `count` строит ledger каждого actor-а и каждого root decision point. |
| Capability отсутствует в feasibility | `shape` требует evidence достаточной способности; exact runtime implementation остаётся live owner-у. |
| Carrier устаревает до integration | execute/accept append recovery-bearing transitions до dependent move; integrate пишет terminal transition. |

Ни одно finding не превращено в отдельный checklist-патч: первые четыре
поглощены одной стадией `shape` и actor-wide count, пятое — сменой carrier model.

## Clean executor — actual trajectory промежуточной версии

Кейс: один ordinary read-only worker проверяет `references/brief.md` против двух
owner ranges. Executor прочитал candidate и project owners, построил source map,
brief и active ledger. Монолит получил `34 ±2`; staged same-window phases дали
примерно `20 → 18 → 19 → 10`, поэтому verdict стал `manageable, staged` без
лишнего fan-out. Launch map была готова, actual spawn не выполнялся.

Trajectory: quick one-worker prompt → mandatory owner map and budget → monolith
rejected → same-window staging → launch boundary. Gaps: no actual return,
acceptance or integration; counts approximate. Это доказало cognitive split, но
не полный launched lifecycle.

## Новая owner-граница после раунда

`_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:17` требует строгости без
вредного буквализма. Поэтому `20` остаётся attention budget с overload escape,
а findings исправлены owner-seams, не новыми ритуалами.

`_ops/chat-recall/2026-08-29-160553-claude-0bee3f3d.md:19` прямо отказывает
runtime skill-у в дословных owner-цитатах. Цитаты удалены из candidate body и
сохранены в history/evidence; behavior order остался.

## Вердикт раунда

Промежуточная версия отклонена. Следующая версия требует финального повторного
instruction check, trajectory check, actual routing probes и clean execution.
