# LLM Failure Modes

Catalog of formal-pass-bad-work patterns. Use it during the adversarial pass of `criteria-generator`.

For each chosen mode, run the probe against your draft criteria and apply the countermeasure.

## 1. Claimed verification

Pattern: the agent writes "verified" without running the command or reading the artifact.

Probe: could the criterion pass with the word `verified` alone?

Countermeasure: require the command and the expected output, not a claim about running it.

## 2. Mock-shaped implementation

Pattern: the output looks right on one happy path but the real work is not implemented.

Probe: could the criterion be satisfied by returning a constant, stubbing the result, or hardcoding one example?

Countermeasure: require multiple inputs, a property check, or behavior that cannot be faked by a single canned path.

## 3. Silent edge-case skipping

Pattern: the agent handles the obvious case and omits null, empty, large, unicode, concurrency, or other implied cases.

Probe: what cases outside the happy path would break the naive solution?

Countermeasure: name the implied edge cases or require evidence from nearby tests and existing behavior.

## 4. Rename without refactor

Pattern: a symbol moves or changes name while behavior stays broken.

Probe: would the criterion still pass if nothing behavioral changed?

Countermeasure: tie the criterion to observable behavior change, not textual movement.

## 5. Summary-based review

Pattern: the agent says it reviewed a file after skimming one section.

Probe: does the criterion require a specific line, section, config key, or function to be cited?

Countermeasure: require a named artifact to quote back.

## 6. Comment as behavior

Pattern: the agent adds a comment, TODO, or docstring instead of making the behavior real.

Probe: does the criterion distinguish runtime change from textual change?

Countermeasure: require runtime, test, or output evidence rather than diff alone.

## 7. Happy-path-only success claim

Pattern: "all tests pass" means only the one newly written test passes.

Probe: does the criterion require both the targeted proof and a no-regression check?

Countermeasure: separate targeted verification from broader regression evidence.

## 8. Stale-context hallucination

Pattern: the agent cites a file, function, or setting remembered from old context rather than the current workspace.

Probe: could the criterion be satisfied by referencing something that no longer exists?

Countermeasure: require current-file evidence, not memory.

## 9. Tool not actually invoked

Pattern: the agent narrates a tool call in prose but never performs it.

Probe: could the criterion be satisfied from chat text alone?

Countermeasure: require tool output, command output, or another observable trace of the action.

## 10. Scope creep as diversion

Pattern: the agent fixes something adjacent and reports success on the original task too.

Probe: is the criterion narrow enough that adjacent changes do not count?

Countermeasure: state the target artifact, target behavior, or target decision explicitly; forbid unrelated changes when necessary.

## 11. Test-passing-but-wrong

Pattern: the test is weak enough that a pathological implementation still passes it.

Probe: could the evidence pass while the real requirement is still violated?

Countermeasure: require at least one negative assertion or counterexample, not only the positive case.

## 12. Specification drift

Pattern: the agent gradually softens the task to match what it found easy to do.

Probe: does the criterion preserve the user's actual ask or only a paraphrased interpretation?

Countermeasure: quote the user's scope explicitly and forbid paraphrase-as-spec when precision matters.

## 13. Confidence theatre

Pattern: the agent writes "clearly", "obviously", or "as expected" to cover uncertainty.

Probe: does any criterion rely on the agent sounding confident?

Countermeasure: replace self-report with an external check, named source, command, file, or number.

## Picking Modes

Pick only the modes relevant to the task:

- Code changes: 1, 2, 3, 4, 6, 7, 10, 11
- Refactors: 4, 5, 10, 12
- Research or writing: 5, 8, 12, 13
- Config or infrastructure: 1, 4, 8, 10
- Tool integration: 1, 9, 10
