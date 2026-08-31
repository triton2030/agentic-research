---
description: "Create, defer, promote, reconcile и closeout planning contract."
---

# Жизненный Цикл Planning Contract

Contents: Create · Defer · Promote · Update · Mode Transitions · Review ·
Invalidation · Reconcile · Closeout.

Применяй после Gate из `SKILL.md`; schemas принадлежат
[`file-contracts.md`](file-contracts.md). Этот файл владеет только переходами
между live states, reconcile и closeout.

## Create Active

1. Найди active duplicate, исключая `/_archive/`.
2. Используй existing folder или flat `_ops/plans/`; новый workstream-folder
   требует отдельного owner/placement решения.
3. Выбери mode по current truth: Wayfinding, если destination принят, но
   material route ещё не ясен; Execution, если route достаточно ясен.
4. Зафиксируй compact `Decision Basis`; предложенный пользователем mechanism
   остаётся route candidate, пока owner/evidence не приняли его как premise.
5. Назови current `Reopen When`, а для выбранной mode — ровно один `Next`.
6. Создай common core и ровно один mode block из
   [`file-contracts.md`](file-contracts.md).

## Capture / Defer To Backlog

1. Найди duplicate среди plans и backlog.
2. Если backlog разрешён project owner-ом, создай/move один compact contract по
   [`file-contracts.md`](file-contracts.md).
3. При defer Execution сохрани только factual completed state/evidence и убери
   право stale milestones управлять execution.
4. При defer Wayfinding сожми принятые decisions в `Existing State / Evidence`,
   а unresolved questions/fog — в `Revalidate Before Start`; не переноси mode
   block или его Next в backlog.
5. В обеих mode перенеси current reopen signals в `Revalidate Before Start`;
   active `Reopen When` и `Next` в backlog не сохраняй.

## Promote From Backlog

1. Перечитай текущие GOAL, applicable instructions и source truth, способные
   изменить outcome/scope/Done.
2. Reconstruct Outcome/Scope/Decision Basis из current owner facts. Deferred
   route и assumptions считай candidates; reconcile stale premises,
   dependencies и duplicates. Invalid contract обнови, archive или верни
   owner-у.
3. Перемести один live file в `_ops/plans/`; не оставляй backlog-копию.
4. Выбери active mode заново: Wayfinding при material unresolved route либо
   Execution при ясном route. Не восстанавливай stale mode из deferred body.
5. Добавь current `Reopen When`, mode-specific `Next` и только decision map либо
   milestones/evidence/handoff выбранной mode.

## Update Active Or Deferred

Active task — current planning truth, не activity log. Current owner применяет
Steering Loop из `SKILL.md` на material boundary: resume, следующий independent
slice, milestone принят, evidence меняет frontier, появился blocker или
изменились verification/handoff. До действия перечитай anchor и его owner
pointers; после evidence запиши Steering Delta: evidence-state отдельно от
planning consequence. Один atomic evidence может закрыть несколько связанных
пунктов, но не копи известные изменения до финального closeout.

При `reframe` не патчь stale mode block. Сначала убери прежний `Next`, собери
current Decision Basis из owner facts + accepted evidence, заново выбери mode и
только затем создай decision map либо milestones. Completed factual evidence
сохрани; прежнюю route shape не используй как default.

В Wayfinding после каждого material answer перепиши decision map по
[`plan-as-prompt.md`](plan-as-prompt.md): resolution gist/pointer, оставшиеся
ready/blocked questions, ставший точным fog и один Next. В Execution обновляй
milestones/evidence/Next и не добавляй новый decision tree поверх старого route.

Перед каждой записью Execution пройди Planning Compression Gate. Удаляй
procedure detail, который competent executor восстановит из current contract;
старый большой plan не является формой, которую надо сохранять. Если следующий
route зависит от ещё не полученного empirical evidence, замени speculative
downstream steps одним prototype/benchmark `Next` и вернись после результата.

При delegation shared task пишет только orchestrator/root: worker возвращает
changes, адресуемый evidence, gaps и blockers; root принимает return и обновляет
task до следующего assignment. Task-level scope, Done и red lines не расширяй
по ходу в project plan.

Staged-run update/replanning выполняй только по
[`staged-runs.md`](staged-runs.md); worker не меняет planning-owned files.

Backlog обновляй, когда меняются устойчивый outcome, причина defer, activation,
stable scope, Done или revalidation anchor. Не превращай review в execution plan.

## Active Mode Transitions

Mode transition меняет тот же active task и заменяет целый mode block.

- `Wayfinding → Execution`: Exit Gate пройден; classify каждый незакрытый
  вопрос, material blocker отсутствует, non-blocking handoff сохранён в
  `Stop / Handoff`; First-Action Probe не обнаружил material choice без
  owner/evidence. Затем перенеси load-bearing decision basis/pointers, создай
  current milestones/evidence/Next, перепиши reopen signals и удали map.
- `Wayfinding → close/handoff`: Outcome сам был decision/spec/map и Done
  достигнут либо downstream execution принадлежит другому owner-у.
- `Execution → Wayfinding`: evidence открыл material route decision; останови
  затронутые действия, замени milestones/Next на decision map, выбери primary
  decision и сохрани фактический completed evidence как basis.
- `Execution → Execution`: route остаётся ясным; replan milestones/Next и
  reopen signals без смены mode.

Не держи обе mode «для истории». История не управляет active contract.

## Refresh Project Status

Этот шаг существует только если effective project instructions явно
маршрутизируют compact `STATUS.md` к `1planning`.

Обнови snapshot после create/defer/promote/reconcile/close/archive, material
смены frontier/blocker или explicit status review. До записи:

1. осмотри все live plans/tasks, backlog и findings, исключая `/_archive/`;
2. не triage findings внутри refresh — отрази только число сигналов, требующих
   внимания, и material planning consequence, если оно уже известно;
3. замени net snapshot: кратко `done → now/next → gap`, live counts и нужные
   owner pointers; не переноси chronology, milestones, evidence tables или
   contracts;
4. соблюдай project size cap и проверь его на весь файл, включая frontmatter.

При delegation общий STATUS пишет только orchestrator/root. Finding capture,
worker и обычное execution без material planning delta его не меняют.

## Review Deferred

После revalidation выбери один исход:

- `promote` → move в plans по контракту выше;
- `remain deferred` → подтверди outcome/Why Later/scope/Done и обнови revisit
  anchor;
- `drop/supersede` → назови причину и archive;
- owner truth или полномочия неясны → handoff без execution.

Revisit condition — не scheduler: его наступление требует решения, но не делает
backlog item current execution owner-ом автоматически.

## Mid-Run Invalidation

После сработавшего `Reopen When` либо иного evidence, меняющего предпосылку
task, не выполняй stale `Next`. Сначала классифицируй evidence-state и planning
consequence, затем reconstruct Decision Basis из current owner facts и сверяй
Outcome/Scope/Done/red lines/authority:

- contract и route остаются достижимыми/ясными → продолжай Execution;
- Outcome остаётся принят, но route стал materially unclear → Wayfinding;
- contract стал ложным или требует новых полномочий → останови затронутую работу,
  update/replan task или верни handoff владельцу.

Не откладывай эту проверку до closeout.

В staged run сначала останови затронутые Modules и используй его отдельный
replanning contract.

## Reconcile Старого Task

- still active → обновить и продолжить;
- active с неясным material route → reconcile в Wayfinding;
- active с ясным route → reconcile в Execution;
- chosen but intentionally deferred → move/reconcile в backlog;
- backlog selected for current execution → revalidate и promote;
- backlog no longer wanted → reason + archive;
- superseded / descoped → записать причину и archive;
- independent outcome появился → sibling task текущего фронта;
- owner changed → handoff с owner/path;
- blocked → сохранить stop reason; inactive task не оставлять управляющим.

## Closeout

Каждый milestone должен быть classified: completed, descoped с причиной,
handed off с owner/path или blocked со stop reason. Зафиксируй только фактическое
evidence. Затем перемести task в ближайший durable `_archive/`, если он больше не
должен управлять execution.

Для Wayfinding closeout classify каждый precise decision: resolved, descoped,
handed off или blocked; `Not yet specifiable` должен быть пуст, out of scope либо
явно передан следующему owner-у. Если downstream execution остаётся частью того
же Outcome и Exit Gate пройден, closeout недопустим: выполни transition в
Execution. При material blocker оставь task active Wayfinding либо выполни
разрешённый defer/owner handoff; не переходи в Execution и не архивируй active
blocked work как завершённое.

Staged Task закрывается по archive routes из
[`archive-and-folders.md`](archive-and-folders.md).

Backlog не является closeout: он сохраняет выбранную deferred работу. Archive
означает inactive, не автоматически successful.
