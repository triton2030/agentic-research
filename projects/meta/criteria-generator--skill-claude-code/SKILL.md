---
name: criteria-generator
description: Use before executing any non-trivial or ambiguous task when Codex should first turn the user's request into the same request augmented with non-bypassable acceptance criteria. Recover intent from project context such as AGENTS.md, CLAUDE.md, GEMINI.md, README files, docs/, `_ops/`, project memory files, git state, and the instruction layer shaped by `system-architect` such as prompts, instructions, skills, hooks, or validators. When `_ops/1-NORTH-STAR.md` and `_ops/3-CURRENT-STRATEGY.md` exist, treat them as the upstream strategic map owned by `main-strategy`; read `_ops/2-RATIONALE.md` only when the why behind the strategy, rejected paths, or premortem materially changes the task contract. When that map or repo instructions already define canonical domains, let them route the next reads instead of broad generic scanning. Do not create or refresh operational files as part of criteria generation. Output only the augmented prompt and execution offer — never task implementation or operational scaffolding.
---

# Criteria Generator

Announce at the start with the active mode:

- Contract mode: "I'm using the criteria-generator skill to produce acceptance criteria."
- Strategy-trace mode: "I'm using the criteria-generator skill in strategy-trace mode."

## Role

You translate the global goal from `_ops/1-NORTH-STAR.md` and `_ops/3-CURRENT-STRATEGY.md` into local-task acceptance criteria that keep the execution agent aligned with the durable goal while doing this specific task.

Quality of downstream execution comes from constant focus on the global goal. A task contract without a North-Star anchor is weaker, even if it looks specific.

Reason wide, emit narrow. Use discovery, EVPI, adversarial pass, and the quality gate to decide what matters. Do not dump your reasoning trace into the visible contract. The visible criteria should be the smallest set of constraints that would materially prevent weak execution.

## Modes

Two modes, one owner:

- `contract` (default) — produce the thin augmented prompt used as a hard execution contract.
- `strategy-trace` (explicit-only) — run a compact read-only test of whether the current ask, plan, or draft still serves the global goal and active strategy.

Switch to `strategy-trace` only when the user explicitly asks for `strategy-trace`, a quick strategic-memory check, a drift check, or "just verify alignment" before execution. Do not silently replace normal contract generation with this mode.

This mode is not a substitute for a full trajectory audit or a durable architecture decision. If the real question is artifact-quality drift, use a trajectory-auditor-style pass when available. If the real question is where a durable rule should live, route to `system-architect`.

## Success Criteria For The Contract

Before emitting, verify every `Must` item passes all six checks:

1. **North-Star traceability** — an `Anchored in:` line points to a specific section of `_ops/1-NORTH-STAR.md`, `_ops/3-CURRENT-STRATEGY.md`, or (rarely) `_ops/2-RATIONALE.md`. If no strategic anchor applies, label the item `Anchored in: local-only — <reason>`. Silent absence is not allowed.
2. **Observable** — a reviewer inspects evidence, not a claim.
3. **Unambiguous** — two careful readers would judge it similarly.
4. **Non-bypassable** — a weak agent cannot pass it with shallow work.
5. **Minimal** — removing it would materially increase failure risk.
6. **Non-overlapping** — it is not already enforced elsewhere in the contract.

If `_ops/1-NORTH-STAR.md` is missing, mark the whole contract as **weak strategic grounding** and keep it thinner instead of inventing anchors. Do not hallucinate a North Star.

Drop or rewrite any criterion that fails one check. If two criteria guard the same failure mode, keep the shorter or stronger one.

## Success Criteria For Strategy-Trace Mode

Before emitting a trace result, verify it is:

1. **Chain-shaped** — it walks from global goal -> active strategic line or anti-goal -> local implication -> observed target.
2. **Anchored** — every chain step cites `_ops/` or the checked artifact. No free-floating claims.
3. **Compact** — usually 3-4 trace steps plus one verdict. Do not expand into a full criteria contract.
4. **Decisive** — return exactly one verdict: `aligned`, `partial`, `drift`, or `unknown`.
5. **Actionable** — name the smallest next move that would reduce drift or uncertainty.
6. **Read-only** — do not invent new strategy, architecture, or `Must` items while in this mode.

## When To Use

- Before executing a non-trivial task whose "done" state is not obvious.
- When the request is vague, high-stakes, easy to misread, or likely to invite shortcut behavior.
- Before handing work off for future execution or converting a request into a brief.
- When acceptance criteria are missing, soft, or easy to fake.
- Before major execution when task-level criteria should stay aligned with a strategic map in `_ops/1-NORTH-STAR.md` and `_ops/3-CURRENT-STRATEGY.md`.
- When the user explicitly wants a quick `strategy-trace` check to verify that the current ask, plan, or draft still follows the strategic map before committing to execution.

## When Not To Use

- Skip for trivial factual questions with no execution step.
- Skip for tiny obvious edits when the user already defined what success looks like.
- Skip when the user already supplied explicit, testable acceptance criteria.
- Skip `strategy-trace` when the user really needs a full artifact or trajectory audit with evidence from the work itself.
- Skip when the immediately previous turn already produced a criteria contract from this skill, the user explicitly approved execution, and the ask has not materially changed. In that case the correct next step is execution under the approved contract, not a second criteria pass.

If the skill was explicitly invoked on a trivial task, keep the result minimal instead of inflating the contract.

## Hard Gate

Do not implement the user's task while running this skill.

Do not create `_ops/`, do not create or refresh `_ops/1-NORTH-STAR.md`, and do not write any other support files while running this skill.

Treat `main-strategy` as the owner of the strategic map in `_ops/1-NORTH-STAR.md`, `_ops/3-CURRENT-STRATEGY.md`, and optional `_ops/2-RATIONALE.md`. This skill may read those artifacts as upstream truth when present, but does not author them.

Treat the durable instruction layer shaped by `system-architect` as the nearest upstream for task criteria. If owner, control-surface choice, or system shape is still unresolved or lives only in chat, stop and route the task back to `system-architect` before drafting criteria.

Begin execution only after the user agrees to use these criteria as a hard contract.

If the user approval arrives in a later turn and the ask has not materially changed, treat that reply as the execution handoff. Do not re-enter this skill just to restate the same contract.

`strategy-trace` is read-only. Do not emit `Must`, `Must not`, or a verification protocol there, and do not stretch this mode into a shadow trajectory audit or architecture review.

## Mode Selection

1. Use `contract` mode by default.
2. Switch to `strategy-trace` only on explicit user intent: `strategy-trace`, "check alignment", "quick drift test", "does this still follow the strategy", or equivalent.
3. If there is already substantial artifact evidence to audit, prefer a trajectory-auditor-style pass when available.
4. If the blocker is missing strategy or unresolved control-surface ownership, route to `main-strategy` or `system-architect` instead of stretching this skill.

## Contract Mode Process

Four checkpoints. Produce the artifact for each before moving on.

### 1. Capture

Quote the user's task verbatim.

Artifact: the exact task quote for the final `Original task` block.

### 2. Discover — global goal first, then local

Read the strategic map before local context.

1. `_ops/1-NORTH-STAR.md` and `_ops/3-CURRENT-STRATEGY.md` — mandatory unless missing. Translate only the parts that materially change the contract:
   - `Goal` and `Acceptance criteria` from `_ops/1-NORTH-STAR.md` — durable outcome and proof floor the task should serve
   - `Strategic Objective Now` from `_ops/3-CURRENT-STRATEGY.md` — calibrates what matters now vs later
   - `Working Hypothesis` — the active strategic bet the task should not quietly contradict
   - `Strategic Lines` and `Implications For Criteria Generator` — often become Must items or scope constraints
   - `Anti-goals` — often become Must-not items
   - `Unknowns` — feed EVPI questions or explicit assumptions
2. `_ops/2-RATIONALE.md` — read only when `Chosen Path`, `Premortem`, or `Revisit Triggers` would materially change completion, forbidden shortcuts, or verification depth.
3. Local sources — read only what changes what "good" means for THIS task. Let the strategic map route the next folders: the nearest `projects/{category}/...` if a specific artifact line is implicated, then `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README*`, `docs/`, active instruction surfaces (system prompts, folder instructions, local skills, hooks, validators), recent git state. Reading everything "just in case" is a bypass.

If `_ops/1-NORTH-STAR.md` is missing, note it and continue with weaker strategic grounding — prefer a thinner contract to inventing anchors.

If only `_ops/1-NORTH-STAR.md` exists without `_ops/3-CURRENT-STRATEGY.md`, use the North Star cautiously and record that the task contract is missing a current-strategy layer.

Use [references/discovery-map.md](references/discovery-map.md) for extended routing by project type and task type. Do not treat generic folders like `docs/` or loose root notes as equal-priority substitutes when the repo already has stronger homes for the artifact type.

Produce, in the same step:

- A bullet list of `<source>: <one-line takeaway that changed your understanding>`.
- `Understood intent` — 1-3 sentences stating what the future agent must actually accomplish.
- `Unknowns` — missing facts that could materially change the criteria.

If the user proposed a solution path, classify it explicitly as `accept`, `narrow`, or `reject` based on current evidence. Do not silently inherit the proposed path as the task contract.

### 3. Draft → Adversarial → Gate (single loop)

Draft the smallest visible contract that still blocks bad work, then attack it, then run the Success Criteria check. Loop until it passes.

**Draft.** Three buckets:

- `Must`: conditions that block completion if missing. Every item carries `Evidence:` naming the observable artifact, and `Anchored in:` pointing to a strategic section (or `local-only — <reason>`).
- `Must not`: forbidden shortcuts that would make the work look done while staying poor. Add only when the bypass is both likely and not already blocked by a `Must`.
- `Verification protocol`: 1-3 concrete actions, ordered by highest-signal proof.

For code tasks, prefer behavior-first `Must` items: observable behavior change, regression proof, no-regression checks. Lock implementation details only when they are load-bearing and observable.

Keep each criterion short. Prefer one sentence before `Evidence:` and merge overlapping obligations. Default budgets: 2-4 `Must`, 0-2 `Must not`, 1-3 verification steps. Exceed only when a thinner contract would materially weaken correctness.

**Adversarial pass.** Act like a lazy agent trying to satisfy each criterion formally while doing poor work. For every bypass found, strengthen or merge criteria until the bypass is closed. Prefer one stronger criterion that closes several related bypasses over multiple narrow ones.

Use [references/failure-modes.md](references/failure-modes.md) to pick 2-5 modes relevant to the task type. Do not apply all 13.

**Gate.** Run every criterion through the six Success Criteria at the top of this file. Drop or rewrite any that fails. Drop any that duplicates a guard already present.

**EVPI — ask only when it materially changes the contract.** If one targeted question would materially change scope, acceptance threshold, or an irreversible decision, ask it now — prefer `AskUserQuestion` when available. Otherwise continue and record the unresolved point as an assumption prefixed with `[EVPI-would-ask]`.

Do not smuggle unresolved architecture into `Must` items. If the contract still depends on deciding whether the owner should be `AGENTS.md`, a local skill, a hook, a validator, or another control surface, stop and hand off to `system-architect` first.

Artifact: final criteria set passing all six Success Criteria, with either user answers captured or an `Assumptions` list finalized.

### 4. Emit

Return the augmented prompt in this shape and nothing outside it:

```md
## Original task
<verbatim quote>

## Understood intent
<1-3 sentences>

## Context anchors
- <source>: <why it changed the contract>

## Assumptions (not verified with user)
- ...

## Acceptance criteria

### Must (blocks completion)
- [ ] <criterion> — **Evidence**: <artifact>
  **Anchored in**: <_ops path + section | local-only — <reason>>

### Must not (anti-patterns)
- [ ] <forbidden shortcut> — **Why this would be bypassed**: <bypass mechanic>

### Verification protocol
1. <command or action>
   Expected: <observable output>
```

If `Context anchors`, `Assumptions`, or `Must not` would be empty, omit that heading.

Default visible limits: up to 3 `Context anchors`, up to 3 `Assumptions`, 2-4 `Must`, 0-2 `Must not`, 1-3 verification steps. Go above these only when a shorter contract would materially weaken correctness.

Prefer one-line criteria. Avoid multi-clause bullets and mini-essays.

After emitting, ask exactly one question:

`Acceptance criteria generated. Want me to execute the task using these criteria as a hard contract?`

If the user says yes, stop this skill and continue the task under the generated contract.

Artifact: the full augmented prompt plus the execution offer.

## Strategy-Trace Mode

Use this explicit-only mode for a compact upstream-alignment test.

### Read Path

1. Quote the concrete target being checked: the current ask, plan, draft, or short artifact summary.
2. Read `_ops/1-NORTH-STAR.md` and `_ops/3-CURRENT-STRATEGY.md`.
3. Read `_ops/2-RATIONALE.md` only if a rejected path, premortem, or revisit trigger is needed to decide between `partial`, `drift`, and `unknown`.
4. Read only the local artifact being checked. Do not widen into a repo scan.

### Emit

Return this shape and nothing outside it:

```md
## Trace target
<verbatim quote or named artifact>

## Strategic chain
1. Goal: <durable outcome that matters here>
   **Anchored in**: <_ops path + section>
2. Active line: <current bet, line, or anti-goal that matters>
   **Anchored in**: <_ops path + section>
3. Local implication: <what this target must do or avoid if it is aligned>
   **Anchored in**: <_ops path + section | local artifact>
4. Observed target: <what the ask, plan, or draft is actually trying to do>
   **Anchored in**: <user quote | artifact>

## Verdict
<aligned | partial | drift | unknown>

## Why
- <1-2 evidence-backed bullets>

## Do now
- <one short next move>
```

If step 4 adds no information beyond `Trace target`, omit it.

If `_ops/1-NORTH-STAR.md` or `_ops/3-CURRENT-STRATEGY.md` is missing, say so explicitly and default to `unknown` unless the missing layer truly does not change the call.

Default visible limits: 3-4 chain steps, up to 2 `Why` bullets, 1 `Do now`.

Do not emit `Must`, `Must not`, or a verification protocol in this mode.

After emitting, ask exactly one question:

`Strategy trace checked. Want me to turn this into a hard execution contract?`

## Red Flags

- "The task is obvious; I can skip discovery." No. Wrong criteria almost always start there.
- "Adversarial pass is overkill." No. This skill exists for that step.
- "I can say something was verified without naming the artifact." No. Evidence must be explicit.
- "Thin context means I should improvise." No. Thin context is why the EVPI gate exists.
- "The evidence is implied by the criterion." No. LLMs skip implied obligations.
- "Adding more constraints always makes the output safer." No. Over-constraint is its own bypass.
- "I found six plausible risks; I should list all six." No. Compress to the few constraints that materially change execution.
- "The Must item is obviously related to the goal — no need to anchor it explicitly." No. Make the anchor explicit, or mark `local-only` with a reason.
- "I can use `strategy-trace` as a cheap full review." No. It checks alignment memory, not artifact quality.
- "I can call something aligned without quoting the chain back to `_ops/`." No. A verdict without anchors is theatre.

## Output Constraint

Produce only the mode-appropriate artifact and its single follow-up question. No `_ops/` support files, no task code, no partial task implementation, no side work.

## References

- Use [references/discovery-map.md](references/discovery-map.md) when the default discovery pass needs adaptation by project type or task type.
- Use [references/failure-modes.md](references/failure-modes.md) during the adversarial pass.
- Use [references/format-examples.md](references/format-examples.md) to match the output shape without copying the content.
