# Interview Protocol

`user-interview` is the durable user-truth loop. It captures preferences,
vision, constraints, red lines, and answers to consequential questions.

## What To Ask

Ask only when the answer changes a future decision:

- strategy direction or Stage ordering;
- task scope, Must-not, or verification depth;
- product/business/design intent;
- user preference, taste, or red line;
- conflict with stored user truth.

Every question must state:

1. why it matters;
2. what decision changes depending on the answer;
3. what future risk it removes.

## What Not To Ask

Do not ask implementation trivia when the agent should decide as an expert:

- framework/library/database choices without user-level consequence;
- style preferences already stored in `INTERVIEW.md`;
- questions where all answers lead to the same next move;
- broad interview blocks before the user needs them.

## EVPI Rule

Before asking, check:

> If answer A and answer B lead to the same next move, do not ask.

Take a position instead. The user can correct it.

## Conflict Handling

If a new durable signal conflicts with stored user truth, do not overwrite
silently. Ask what changed: situation, priority, evidence, or preference.

After the reason is clear, replace or merge the old line in `INTERVIEW.md`.

## Capture

When the user answers, write the durable result to the relevant section of
`INTERVIEW.md`. Prefer updating an existing line over appending duplicates.

Do not store one-off task facts here. Store only durable user truth that can
change future routing, scope, tone, Must-not, or verification depth.
