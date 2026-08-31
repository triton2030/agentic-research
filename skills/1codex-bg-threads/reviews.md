# Check-approve reviews

## Новый authoring cycle — terminal exact version

После owner-authorized semantic compression первый formal repeat exact hash
`041bc3a60a2bae4257723f9cd098b166bca3fc26f2c96903deac6a46e6093d4c`
вернул active-set overflow и четыре trajectory seams. Они были приняты и
исправлены без новых references, стадий или typed machinery.

Второй и последний repeat проверил exact manifest
`10c8e8776634ac1058e7a442811e45986828d11a54a8c316567f5ea35c97e7e4`:

- Literal checker: `NO_FINDINGS`, active sets `13–20`.
- Trajectory checker: `NO_FINDINGS`.
- Новый clean-window behavioral probe: `BEHAVIOR_OK`.

Terminal verdict: `EXACT CANDIDATE READY FOR OWNER APPROVAL`. Official/tracked
и live не изменены.

## Superseded previous cycle по baseline 9bf11f64

Ниже сохранена история прежнего blocked hash; terminal verdict находится выше.

Clean-room reimplementation началась от заново сформулированного FAST, не от
старого package. После полного draft старый package использован как loss
oracle. Первый checker round вернул controller/receiver, managed/launch-only и
persisted-lifecycle seams. Затем owner correction отменила typed card/status
машину и потребовала простой Markdown brief для умного receiver-а.

Zero-based candidate сократила runtime с восьми файлов до четырёх и заменила
шесть процедурных references двумя самостоятельными surfaces:
`receiver-message.md` и `codex-native.md`. После второго round исправлены
launch-only ordering, точный запрет recursive controller invocation, Luna gap,
terminal wait, ready `threadId` reuse и exact English trigger.

Финальный exact manifest:
`c4152786d04537e376e985fd89bb2e8919dbbd8e7627f3c26d08efd336a58249`.

- Trajectory checker: `NO_FINDINGS`.
- Behavioral probe exact hash: `BEHAVIOR_OK`; новый clean-window не доказан,
  потому что runtime разрешил только reuse существующего agent slot.
- Literal checker: один residual blocker — минимум `23` core predicates при
  контракте `≤20`.

По `check-approve.md` два repeats исчерпаны. Новый rewrite не начат: exact
candidate остаётся `NOT APPROVED`, official/live не изменён, а следующий ход
требует нового authoring cycle, который снимет минимум три core obligations без
возврата state-machine или механического умножения references, после чего
нужна exact probe в новом clean-window.

Адреса verdicts и фактического trace находятся в
[`receipts-2026-08-30/`](receipts-2026-08-30/).

## Round 1

Literal checker нашёл восемь defects: actionable-card ambiguity, потерянное
nested-subagent право, неполный unpinned invariant, неоднозначный bounded
archive, потерянный implicit invocation, заниженный instruction count,
раздутый Unique Context и несохранённый behavioral trace.

Trajectory checker нашёл два departures: общий `1orchestration` оставлял
`no-delegation` как допустимый путь вопреки цели минимальной работы root, а
жёсткое `architecture → xhigh` заменяло разрешённый профессиональный выбор
между Sol medium и xhigh.

Все находки приняты по буквальным словам владельца либо фактическому dry-run и
исправлены в полном кандидате. Round 2 обязан повторить оба checker-а и probe с
чистыми окнами.

## Round 2

Literal checker нашёл controller/receiver ambiguity, слишком широкий
independent-proof goal, укрупнённый recount и отсутствие сохранённого probe
новой версии. Trajectory checker нашёл потерянный retained receiver route и
terminal archive зонтичной retained-service.

Все шесть находок приняты. Body стал stage-router; environment вынесен в
отдельный reference; references переписаны по predicate-level единицам;
retained receiver re-resolves sources, а umbrella acceptance архивирует
specialist. Следующий прогон — второй и последний repeat, разрешённый
`check-approve.md`.

## Final allowed repeat

Behavioral trajectory сохранила technical-director, Luna/Sol, Local,
verification и bounded archive. Trajectory checker нашёл три reachability
seams: controller retained reuse, umbrella retained archive и receiver
`THREAD_DONE` schema. Literal checker подтвердил последние два, уточнил
full-card receiver condition и не принял predicate-level budget.

Reachability seams и full-card condition исправлены. Бюджет дополнительно
сокращён через более короткие Unique Context и цели, но новый checker не
запущен: два repeats исчерпаны. Остаток — независимое доказательство exact
post-fix версии и спор о том, считать ли каждую причинную часть контекста
отдельным активным обязательством.
