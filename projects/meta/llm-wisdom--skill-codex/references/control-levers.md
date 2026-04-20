# Control Levers

Prompt wording is only one lever. It is often not the strongest one.

## Stronger-than-prompt levers

- permissions and sandbox boundaries
- approval checkpoints before risky actions
- validation and schema-constrained outputs
- explicit verification protocols
- evals and regression checks
- role split or narrower ownership

## Quality architecture

- Acceptance criteria work best when they are observable, unambiguous, and non-bypassable.
- Self-report is not evidence.
- Small tool sets reduce drift and accidental misuse.
- High-risk roles should default to narrower autonomy.
- Judge the trajectory and artifacts, not only the final prose.

## Good patterns

- Separate stable system rules from task-specific criteria.
- Use generator -> critic -> refiner when the cost of wrong output is high.
- Let uncertainty trigger escalation instead of forced confidence.
- If the model keeps failing the same way, change the workflow or guardrail, not just the wording.

## Smell

If the advice you are giving is only "make the prompt clearer", you may be ignoring the stronger lever.
