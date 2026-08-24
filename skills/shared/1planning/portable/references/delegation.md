# Delegation — work wider than one context

A staged run is a shape for recovery and delegation, not a third mode: it
carries Wayfinding or Execution and does not change the task's Outcome.

## When

Exact recovery across a session boundary · several independent
context/write slices · a worker fleet. Do not open a staged shape because
of size, a standalone question, or a blocker — a sibling task appears only
for an independently closeable Outcome.

## Delegation contract

- **Plan files are written only by the orchestrating window.** Workers and
  subagents do not write to the map or the task files; their write rights
  are the epic's `_evidence/**` and their own working footprints outside
  the map. Hooks and the project instrument enforce the ban mechanically; a
  migration exception is enabled only by the owner's word.
- **A worker brief is ephemeral**: it lives in the orchestrator's run_dir
  outside the map, together with the wave's file footprint ("who writes
  where"). Brief composition: contribution (into which subtask and with
  what) · sources (exact addresses; the requirement list is verified by the
  derivation act from [contract](contract.md), not replaced by it) ·
  boundaries (read · write: the exact files) · equipment (skills the worker
  must load) · budget (N steps; "enough when …") · orchestrator checks
  (what accepts the result) · prohibitions. The worker sees no chat. The
  brief is immutable: a clarification is a message marked "amendment",
  accounted for in the return.
- **File-disjoint:** every worker gets a non-overlapping file footprint.
  Overlap means clobbered edits — the most expensive fleet failure.
- **A worker's return** is a file in the epic's `_evidence/` (placed before
  the barrier — a crash at the barrier does not lose the wave's evidence):
  status success|blocked|split-proposal · changes · evidence · gaps ·
  equipment: loaded/not + reason · principles trace (decision + names).
  Having accepted a return, the orchestrator in the same move writes a line
  into the subtask report and refreshes the counters via the instrument.
- Wave order, barriers and parallelism limits — `1orchestration`; a heavy
  subtask carries a layout line in its report:
  `волна: чтение <zones> · запись <footprints> · проверка <lenses>`.

## Verifying workers

A worker's self-report is not evidence. Verify with a fresh run against the
original criteria and paths: `git diff`, tests, consumer acceptance of the
seam. The executor's transcript is material for diagnosis, not for
acceptance.

The wait/probe/repair protocol for a stalled worker is owned by
`1orchestration`; planning's delta is one line: the outcome of every
probe/repair lands as a line in the affected subtask's report — `UNKNOWN`
and blockers too; a final blocker that needs the owner's word goes through
[questions](questions.md).

## Recovery after a break

A wave is the unit of autonomy: a break costs one wave, not the work. A
worker is not restored from plan files — the wave is reissued whole.

- Cold start, reading budget: epic folder → epic folder note → task file →
  the wave's `_evidence/` → exact source anchors. Verify `эпик-снимок` at
  once; stale → re-verify the task against the epic in the same move,
  before reissuing (copy of the [contract](contract.md) gate — edit
  together). The archive, backlog and neighboring tasks are not preloaded.
- Before reissuing — reconcile "what is already done": git status/diff
  against the subtask reports. An external action is never repeated blind:
  a repeat fleet over already-applied edits means clobbered edits and
  double commits.
- A pause is a state: open owner questions live as question notes
  ([questions](questions.md)); another window may accept the answer.
- Reports diverge from git → trust git, fix the report, then continue: a
  checkpoint that lies is worse than none.

## Invalidation

An upstream artifact or a seam contract changed → downstream proofs are
void: re-verify the affected tasks; do not trust their old "done".
