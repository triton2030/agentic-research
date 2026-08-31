# 112 learning mode — clean-room semantic draft

state: `semantic draft; not an official skill or authoring pass`

source boundary: only `../intent.md`

## Purpose

After an explicit invocation, add a session-wide learning overlay to the work
already in progress. At every substantial fork, the overlay must make the
chosen method, its book provenance, its concrete operation, and its causal
effect public before the resulting work action. The overlay teaches through
the real work and must not replace, pause, or silently broaden that work.

The public report is a forcing function, not a retrospective explanation. A
method is not proved merely because the result resembles it, its name appears
in a later summary, or a quotation is placed next to an already-made choice.

This draft deliberately does not name any book, method, author, or quotation.
The input supplies no such catalogue, and inventing one would violate the
provenance requirement the mode exists to enforce.

## Semantic contract

### Invariants

While the mode is active:

1. The original objective, scope, authority, definition of done, current
   position, and pace remain the governing work contract.
2. The mode is an overlay on that contract, not a replacement task.
3. Every substantial fork receives a public proof packet before the work
   action that commits the resulting choice.
4. The packet identifies a relevant method and exposes a real operation, not
   merely a label or analogy.
5. Literal quotation and source address are provenance evidence. Paraphrase,
   memory, or an unverified source is a proof gap.
6. Causal influence is evidenced by a visible difference between the question
   before the operation and the decision after it. Similarity alone is not
   evidence of influence.
7. A packet written after the committing action is a missed-method repair. It
   can improve the work, but it can never retroactively become pre-fork proof.
8. A proof gap limits the claim about method use; it does not by itself grant,
   revoke, or change authority over the original work.
9. After each packet or repair, the agent performs the next authorized step of
   the original work without waiting for a new command.
10. One successful packet does not end the mode. The latch remains active
    until the current session ends.

### Working terms

- **Original work**: the task underway at invocation, including its objective,
  scope, authority, DoD, current evidence, and next authorized step.
- **Substantial fork**: a point where choosing among live alternatives could
  materially affect the outcome, scope, authority, DoD, cost, reversibility,
  evidence standard, or next major step.
- **Work action**: the action that commits or materially expresses a choice in
  the original work. Thinking and the method's diagnostic operation happen
  before this action.
- **Public proof packet**: a chat-visible, addressable record of the fork,
  provenance, operation, result, causal delta, and continuation.
- **Verified literal quotation**: exact source wording whose identity and
  address have been checked. A remembered sentence or paraphrase does not meet
  this term.
- **Proof gap**: a visible declaration that one or more proof conditions are
  absent. It forbids a claim of proved method use; it does not authorize a
  fabricated substitute.
- **Miss**: a substantial fork whose committing work action occurred without a
  valid pre-fork packet while the mode was active.

The intent uses “substantial fork” but does not define its threshold. The
definition above is a provisional operationalization, not recovered owner
policy. The traceability section records this uncertainty.

## Activation

### Trigger

The mode transitions from `inactive` to `active for this session` only after an
explicit invocation. It must not be inferred merely from the user's interest
in learning, a request for explanation, or the presence of methodological
language.

### Activation handoff

Activation performs a small handoff rather than starting a new task:

1. Record that the session latch is active.
2. Re-anchor the original work contract: objective, scope, authority, DoD,
   current position, and next authorized step.
3. Identify the next likely substantial fork.
4. If the current work state exposes an earlier missed opportunity, classify
   it either as a pre-activation learning opportunity or a post-activation
   breach; do not confuse the two.
5. Continue the original work immediately. If the next step is a substantial
   fork, run the pre-fork protocol first; otherwise perform the step directly.

Activation never implies permission beyond the authority already present in
the original work.

### Duration

The latch survives individual answers, completed proof packets, repaired
misses, and completion of one intermediate step. It ends only at the boundary
of the current session. Completion of the original task may occur before that
boundary; if the conversation continues in the same session, the overlay is
still active for subsequent work.

## Session-wide cadence

The cadence alternates between ordinary execution and explicit fork handling:

1. **Continue** the next authorized step of the original work.
2. **Watch** for a substantial fork before committing a choice.
3. **Open the fork** by stating the unresolved decision and the thinking
   weakness or uncertainty it presents.
4. **Select and verify** the most relevant available method and its provenance.
5. **Publish and apply** the proof packet before the committing work action.
6. **Execute** the resulting next step in the original work.
7. **Verify** that step against the original work's own criteria.
8. **Repair immediately** if a missed packet is discovered.
9. Return to **Continue** without requesting another command.

Routine mechanical steps do not require a packet merely to keep the mode
visible. When the significance of a fork is genuinely uncertain, the safe
provisional rule is to treat it as substantial and expose the judgment. This
fallback protects the forcing function but may be too verbose; it requires
owner calibration rather than being treated as settled policy.

The mode must not batch all methods into a closing list. A final summary may
count packets, misses, and gaps, but it cannot substitute for the transcript
order that proves a packet preceded its work action.

## Pre-fork protocol

### Required public proof packet

Each field below must be observable in chat. Field labels are a suggested
stable shape; their exact typography is not part of the semantic contract.

| Field | Observable content | Why it exists |
| --- | --- | --- |
| `event` | `PRE-FORK`, plus a locally unique ordinal or address | Makes the packet and its ordering referable. |
| `fork` | The concrete unresolved choice and the work action not yet taken | Establishes that the report precedes commitment. |
| `thinking_problem` | The uncertainty, bias, weak inference, or omitted test at this fork | Connects learning to a real cognitive need. |
| `method` | Exact method name | Prevents a vague principle from standing in for a method. |
| `abbreviation` | Common abbreviation when one is verified to exist; otherwise an explicit `not established` | Makes omission visible without inventing an abbreviation. |
| `book` | Exact book identity | Supplies book provenance. |
| `author` | Author identity | Completes attributable provenance. |
| `literal_quote` | A checked literal quotation, visibly distinguished from commentary | Gives the owner the source's wording rather than remembered paraphrase. |
| `address` | A source location precise enough to re-find the quotation | Makes the quotation auditable. |
| `verification` | What was checked and whether verification succeeded | Prevents confidence language from concealing an unavailable source. |
| `baseline` | The live alternatives or expected choice before the operation | Creates a comparison point for causal influence. |
| `operation` | The concrete transformation, test, comparison, decomposition, or other action demanded by the method at this fork | Prevents decorative citation. |
| `operation_output` | The actual task-specific result of performing that operation | Shows that the method did work on the decision. |
| `causal_delta` | What the operation changed, eliminated, added, or conditionally confirmed in the choice | Separates causality from resemblance. |
| `decision` | The resulting choice and the condition that would have produced a different choice | Makes the method's decision role falsifiable. |
| `continuation` | The next authorized work action and its original-work check | Returns immediately to the work being done. |
| `proof_status` | `PROVED` or `PROOF GAP`, with missing conditions named | Prevents a partial packet from silently passing. |

### Ordering rule

The packet must appear before the committing work action in the visible
conversation. Within the packet the semantic order is:

`unresolved fork -> baseline -> verified method -> operation -> operation
output -> causal delta -> decision -> next work action`.

The method's operation may resolve the fork inside the packet. The resulting
file edit, external action, recommendation, approval request, or other
commitment follows the packet. This gives the owner an observable pre-action
boundary even though no transcript can prove the private order of internal
thought.

### Proof decision

Method application is **proved** only when all of the following are true:

1. The packet is public before the committing work action.
2. Method name, applicable common abbreviation, book, author, literal quote,
   address, and successful verification are present.
3. The method is relevant to the stated thinking problem.
4. A concrete operation is performed on the actual fork and its output is
   exposed.
5. `baseline`, `operation_output`, and `causal_delta` show how the decision was
   changed or tested.
6. If the decision is confirmed rather than changed, the packet states the
   discriminating test, what failure would have changed, and why the observed
   result passed it.
7. The next work action corresponds to the packet's decision and remains
   within the original authority and scope.

Application is **not proved** if any required provenance field is missing, the
quotation is paraphrased or unverified, the source cannot be re-found from the
address, the packet follows the committing action, the operation has no
visible task-specific output, the causal claim rests only on resemblance, or
the subsequent work ignores the stated result.

A `PROOF GAP` packet must name the failed conditions. It must not be relabelled
as `PROVED` by confidence, a later method list, or an invented quotation. The
agent continues the original work whenever that work is independently
authorized and safe; the gap remains in the coverage record. If normal task
authority or risk controls require a pause, that pause comes from the original
work contract, not from learning mode.

### Two escape routes explicitly closed

**Decorative citation** is blocked by requiring `thinking_problem`,
`baseline`, `operation`, `operation_output`, and `causal_delta`. A quotation
beside a decision fails unless its method performs a visible operation that
changes or discriminatingly tests the choice.

**Post-hoc method claiming** is blocked by packet order. Once a committing work
action is visible, a later packet can only be marked `MISS` and enter repair;
it cannot be counted as the missing pre-fork packet even if the later analysis
is excellent.

## Missed-method repair

Repair exists to improve the work and teach from failure without rewriting the
evidence trail.

### Trigger

Enter repair as soon as either the agent or owner identifies a substantial
post-activation fork whose committing work action lacked a proved pre-fork
packet. An earlier, pre-activation move may be analyzed by the same procedure
as a learning opportunity, but it is not labelled a mode breach.

### Repair packet and action

1. Publish `event: MISS` and address the action that occurred too early.
2. State which pre-fork proof conditions were absent. Preserve the miss in the
   record; do not excuse it as implicit method use.
3. Show the thinking weakness and the observed or plausible consequence for
   the original work.
4. Select a relevant method and complete its verified provenance fields. If
   verification is unavailable, declare `PROOF GAP`; never reconstruct a
   quotation from memory.
5. Apply the method's concrete operation now to the already-made choice or its
   produced artifact.
6. Compare the current result with the operation output and state whether to
   retain, revise, undo, or re-test the work.
7. Perform the authorized recovery action and verify it against the original
   DoD.
8. Mark the miss as `repaired`, `partially repaired`, or `unrepaired`, while
   keeping the original pre-fork failure visible.
9. Continue the next authorized step without waiting for a new command.

Repair proves only the repair-time use of the method. It never proves that the
method caused the earlier choice.

## Continuation of the original work

Learning output is interleaved at decision boundaries; it is not a detour into
a standalone lesson. The original work remains the semantic owner of:

- what outcome is being pursued;
- what files, systems, people, and actions are in scope;
- what authority has been granted;
- what tests or evidence define success;
- when user input is independently required;
- when the task itself is done.

After every proof or repair packet, `continuation` names and then performs the
next original-work action. The agent does not stop merely because it has taught
the method, ask the user to reissue the task, or treat the packet as the work
product.

If the method exposes a better move inside existing authority, the work adapts
and continues. If it suggests a scope, authority, or outcome change, the agent
surfaces that consequence and follows the original contract for obtaining the
needed decision. Learning mode cannot smuggle in expanded authority.

## Done and closure

There are two independent completion questions:

### Original-work done

The original work is done only when its own DoD passes. A complete proof packet
does not count as task completion, and learning mode must not weaken the
original checks.

### Session-mode coverage

At a session checkpoint, coverage is satisfactory only when:

1. explicit activation and the active latch are visible;
2. every observed substantial post-activation fork has either a proved
   pre-fork packet or a permanently visible miss record;
3. each discovered miss has a stated repair status;
4. all unverified quotations, unavailable sources, and incomplete causal
   demonstrations remain labelled as proof gaps;
5. the original work continued after packets and was checked by its own DoD;
6. no closing summary is used to upgrade a miss or gap into proof.

A compact closing coverage report may contain only counts and addresses of
`PROVED`, `MISS`, and `PROOF GAP` events plus the original-work result. It is an
index of evidence already present in the transcript, not new evidence.

The mode itself ends only with the current session boundary. The intent does
not define how that boundary is detected, so no reset phrase, timeout, or
cross-session persistence rule is invented here.

## Traceability to the intent

Classification:

- **Explicit**: directly required by the source wording.
- **Derived**: necessary operational consequence of an explicit goal or
  removal-test, but not prescribed in this exact mechanism.
- **Needs instruction**: the intent leaves a policy choice that cannot be
  recovered honestly from goals alone. A provisional fallback may be present,
  but it is not owner truth.

| Behavior | Classification | Intent basis | Consequence in this draft |
| --- | --- | --- | --- |
| Activate only on explicit invocation | Explicit | Function; Goal 1 | No inferred activation. |
| Remain active to the end of the current session | Explicit | Function; Goal 1; FAST | Persistent session latch. |
| Continue the work that was already underway | Explicit | Goal 3; literal owner source on non-interruption | Activation handoff and immediate continuation. |
| Preserve objective, scope, authority, DoD, pace, and continuity | Explicit | Goal 3 | Learning overlay cannot replace or broaden the work contract. |
| Report before every substantial fork | Explicit | Goals 1 and 2; forcing-function context | Pre-fork packet precedes the committing action. |
| Include exact method name, common abbreviation when available, book, author, literal quote with address, operation, relevance, and causal effect | Explicit | Function; Goal 1 | Required packet fields and proof conditions. |
| Treat paraphrase or unavailable source as a proof gap and never invent | Explicit | Unique context; Goal 3 | `PROOF GAP` status blocks the proof claim. |
| Teach through successful, missed, and forthcoming moves | Explicit | Goal 2; Function | Normal packet plus missed-method repair. |
| Show thinking weakness, consequence, and how the method improves or would improve the move | Explicit | Function; Goal 2 | Thinking problem and repair delta are mandatory. |
| Do not infer causality from resemblance | Explicit | Goal 2 | Baseline, operation output, and causal delta are required. |
| Keep a post-hoc packet classified as a miss | Derived | Forcing-function context; FAST; Removal-test | Transcript order is immutable; repair cannot backfill proof. |
| Separate the proof gate from authority to continue original work | Derived | Goal 3 combines explicit proof gaps with continuity | A gap blocks a proof claim, not independently authorized work. |
| Use a stable packet shape and event ordinal | Derived | Public, auditable proof must be addressable | Suggested fields; typography is non-normative. |
| Preserve a coverage record through the session | Derived | Session-wide cadence plus forcing function | Closing counts index earlier evidence only. |
| Exact threshold for “substantial fork” | Needs instruction | Term is used but not defined | Provisional material-effect heuristic; over-report when uncertain. |
| What qualifies as successful source verification | Needs instruction | Verification is required but mechanism is unspecified | Expose what was checked; no source whitelist invented. |
| Required format and granularity of a quotation address | Needs instruction | “Address” is required but not defined | Require re-findability, without mandating page, chapter, URL, or edition. |
| How to choose among several relevant “best” methods | Needs instruction | Relevance and “best methods” are required without ranking policy | Require a relevant method; do not invent a canon or scoring rule. |
| Whether one fork may require multiple methods | Needs instruction | The input does not specify cardinality | Minimal default is one sufficient method; additional methods need an actual distinct operation. |
| Exact session-boundary detector or manual deactivation rule | Needs instruction | Duration is explicit; boundary mechanics are absent | End only at detected session boundary; invent no phrase or timeout. |
| Required quotation length or copyright policy | Needs instruction | Literal quotation is required; length is absent | No length rule is introduced by this semantic draft. |
| Whether a provenance gap should block a particular high-risk work action | Needs instruction | Continuity and proof-gap handling are explicit, risk classes are not | Learning mode does not decide; original authority and safety rules govern. |

## Active-set assessment

“Active set” here means the number of semantic chunks that must be held at once
to perform a stage correctly. Packet fields already externalized in the
template count as one checklist chunk rather than one memory item each. These
are design estimates, not measured cognitive results.

| Stage | Estimated active set | Chunks held concurrently | Assessment |
| --- | ---: | --- | --- |
| Inactive trigger watch | 1 | explicit-invocation sentinel | Low. No learning semantics leak into ordinary work. |
| Activation handoff | 3 | session latch; original-work contract; current/next work position | Acceptable if the handoff stays brief. |
| Between forks | 2 | original work; substantial-fork detector | Sustainable session-wide cadence. |
| Open and prepare a fork | 4 | concrete fork and weakness; method relevance; verified provenance; planned operation and expected influence | Highest selection load; packet template should externalize details early. |
| Publish, decide, and act | 4 | packet completeness; before-action ordering; causal delta; original scope/authority | Manageable, but causality can be faked if the baseline is vague. |
| Missed-method repair | 4 | immutable miss; provenance and operation; before/after comparison; recovery and continuation | High but bounded; repair must not become a second project. |
| Original-work verification | 3 | resulting work action; original DoD; active session latch | Keeps learning subordinate to delivery. |
| Session checkpoint/closure | 3 | original-work result; event coverage; unresolved proof gaps and latch boundary | Compact if it indexes rather than repeats packets. |

The proposed cadence intentionally keeps ordinary execution at an active set of
two. The proof packet is verbose on the page because it externalizes evidence;
compressing those fields into memory would reduce visible proof while
increasing cognitive load.

## Residual risks

1. **Private post-hoc reasoning remains unobservable.** Transcript order proves
   that the packet preceded the work action, not that the agent had not already
   privately chosen. Baseline plus falsifiable operation raises the cost of
   retrospective storytelling but cannot eliminate it.
2. **“Substantial” is under-specified.** Over-classification harms pace and
   under-classification defeats the forcing function. Owner calibration is
   still needed.
3. **Verification has no source policy.** The intent requires a checked literal
   quotation but does not say which editions, repositories, or addresses are
   authoritative.
4. **Method quality is not proved by provenance.** A real quote can still come
   from a poorly selected method. The draft requires relevance and a concrete
   operation but lacks an owner-approved canon or ranking rule.
5. **Causal deltas can be narrated too easily.** Visible baseline, operation
   output, and a condition that would change the choice make the claim
   falsifiable, but judgment remains necessary.
6. **Proof density may slow the original work.** The routine/substantial split
   and compact stable packet mitigate this, but no acceptable cadence budget is
   specified.
7. **Session boundaries are undefined.** The required duration is clear; exact
   activation persistence across technical context resets or resumed chats is
   not.
8. **Repair can improve but not restore missing pre-fork evidence.** Any system
   that reports only final coverage counts could hide this distinction, so the
   immutable event addresses remain essential.

## Completion check for this semantic draft

- Activation and end-of-session persistence: specified in **Activation**.
- Session-wide cadence without interruption: specified in **Session-wide
  cadence** and **Continuation of the original work**.
- Observable proof fields and failure condition: specified in **Pre-fork
  protocol**.
- Decorative citation and post-hoc claiming: explicitly closed in **Two escape
  routes explicitly closed**.
- Missed-method repair: specified in **Missed-method repair**.
- Separation of original-work done and mode coverage: specified in **Done and
  closure**.
- Goal-derived versus instruction-dependent behavior: specified in
  **Traceability to the intent**.
- Stage-by-stage active set and unresolved uncertainty: specified in
  **Active-set assessment** and **Residual risks**.
