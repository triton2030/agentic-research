# Model Behavior

Stable properties of LLMs matter more than any one prompt trick.

## High-confidence traits

- Prompt-only protection is fragile when tools, files, or external systems are involved.
- Sycophancy is a baseline model tendency, not a rare bug.
- Literal wording and real user intent often drift apart unless intent is surfaced explicitly.
- Long reasoning text is not proof that the model followed the intended reasoning strategy.
- Rich discovery reduces noisy clarification questions and shallow guesses.

## Useful interpretations

- If a model agrees too fast, treat it as a system property first, not just a personality bug.
- If a model answers the wrong question well, suspect hidden intent assumptions.
- If a model describes a smart process, verify the behavior instead of trusting the narration.

## Helpful countermeasures

- Verbalize the hidden assumption about the user's intent before acting.
- Use role framing to give the model structural permission to hold a position.
- Prefer observable checks over self-report.
- Reduce ambiguity with real context, not with more generic instructions.
