# LLM Failure Modes

Catalog of ways language models produce formal-pass-bad-work. Use during the adversarial pass of `task-planner` (Step 3 of the task-file lifecycle). For each mode there is a probe question and a countermeasure criterion.

## 1. Claimed verification

**Pattern:** Model writes "I verified X" without running the command or reading the file.
**Probe:** Does the criterion allow a pass with the string "verified" alone?
**Countermeasure:** Require command and expected output, not a claim. `Evidence: output of <cmd>` not `Evidence: I ran it`.

## 2. Mock-shaped implementation

**Pattern:** Function returns the happy-path value hardcoded; passes one test but implements nothing.
**Probe:** Can the Must criterion be satisfied by returning a constant?
**Countermeasure:** Include at least two input variants with different expected outputs, or require a property-style check.

## 3. Silent edge case skipping

**Pattern:** Empty input, null, large input, unicode, concurrency — model handles the cases it thought of and omits the rest.
**Probe:** What inputs outside the happy path would break the naive solution?
**Countermeasure:** Enumerate at least the edge cases the context implies (from existing tests, similar code, or user examples).

## 4. Rename without refactor

**Pattern:** Model moves or renames a symbol instead of changing behavior.
**Probe:** Would the criterion pass if nothing behavioral changed, only the name?
**Countermeasure:** Tie the Must item to observable behavior change (output diff, metric, log line, regression test).

## 5. Summary-based review

**Pattern:** Agent says "I reviewed the file" but only saw the first chunk.
**Probe:** Does the criterion require a specific line or section of the file to be cited?
**Countermeasure:** Name a specific artifact to quote back — a line range, a function, a config key.

## 6. Comment as behavior

**Pattern:** Model adds a `// TODO: handle X` or a docstring instead of handling X.
**Probe:** Does the criterion differentiate behavioral change from textual change?
**Countermeasure:** Require test-level or runtime-level evidence, not just file diff.

## 7. Happy-path-only success claim

**Pattern:** "All tests pass" meaning only the one test that was written.
**Probe:** Does the criterion require the full suite, the specific new tests, and no-regressions?
**Countermeasure:** Break verification into: new tests pass, existing suite passes, no skipped tests added.

## 8. Stale-context hallucination

**Pattern:** Model cites a function, file, or flag that existed once but is gone.
**Probe:** Could the criterion be satisfied by referencing something that no longer exists?
**Countermeasure:** Require a read of the current file as part of verification, not memory of it.

## 9. Tool not actually invoked

**Pattern:** Model narrates a tool call in prose but never emits it.
**Probe:** Can the criterion be satisfied from chat text alone?
**Countermeasure:** Require a tool_use block as evidence, named by tool and arg shape.

## 10. Scope creep as diversion

**Pattern:** Model fixes the easy adjacent thing and reports success on both.
**Probe:** Is the criterion narrow enough that adjacent fixes do not satisfy it?
**Countermeasure:** State the target file and target symbol explicitly; forbid unrelated changes in Must not.

## 11. Test-passing-but-wrong

**Pattern:** Test is written loosely enough that a wrong implementation passes it.
**Probe:** Could the test pass with a pathological implementation?
**Countermeasure:** Require at least one negative assertion (something that must NOT happen) alongside positive ones.

## 12. Specification drift

**Pattern:** Model gradually reinterprets the task mid-work to match what it found easy.
**Probe:** Does the criterion lock the scope in a way the model cannot soften?
**Countermeasure:** Quote the user's exact phrasing in the Must items; forbid paraphrase-as-spec.

## 13. Confidence theatre

**Pattern:** Model writes "clearly", "obviously", "as expected" to paper over uncertainty.
**Probe:** Does any Must item depend on agent self-report of confidence?
**Countermeasure:** Replace any self-report with an external check (command, file, number, human review).

## Using this catalog

In Step 7, do not copy every item. Pick the 2-5 modes most relevant to the task type:

If several chosen modes collapse into one stronger observable criterion, prefer the merged criterion over one countermeasure per mode.

- Code changes: 1, 2, 3, 4, 6, 7, 10, 11.
- Refactors: 4, 5, 10, 12.
- Research / writing: 5, 8, 12, 13.
- Config / infra: 1, 4, 8, 10.
- Tool integration: 1, 9, 10.

For each chosen mode, run the Probe against your draft criteria and apply the Countermeasure.

## Pulse-check specific modes

These apply only to `pulse-check` mode. Unlike modes 1-13 above, they are about the integrity of the memory probe itself rather than a task contract.

### 14. Post-hoc recall

**Pattern:** Model reads `_ops/` first and then writes the recall block to match — passes the probe by rereading, not remembering.
**Probe:** Was the recall block finalized before the verify block in this invocation?
**Countermeasure:** Enforce strict order in the output — emit recall first, then read `_ops/`, then emit actual and trace. Do not edit recall after verify reveals the text.

### 15. Paraphrased recall

**Pattern:** Recall reproduces `_ops/` almost verbatim and the model marks `remembered`. Imitation of memory, not memory.
**Probe:** Could a reader tell recall from actual without the labels?
**Countermeasure:** Force recall to be the model's own paraphrase. Judge the verdict by semantic match, not textual overlap.

### 16. Soft verdict

**Pattern:** Model hedges into `partial`, `mostly`, or `aligned-with-caveats` when recall is uneven.
**Probe:** Is the verdict exactly one of `remembered`, `drift`, or `forgotten`?
**Countermeasure:** The pulse-check taxonomy has three values and no softer middle. Missing memory is `forgotten`. Mis-oriented dialog is `drift`. Everything else is `remembered`.
