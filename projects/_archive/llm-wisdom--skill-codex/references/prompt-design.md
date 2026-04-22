# Prompt Design

Prompts should carry stable behavior, not compensate for every missing control surface.

## Durable core

- role or stance
- audience model
- success bar
- priorities and tradeoffs
- red lines
- default behavior under uncertainty

## Helpful moves

- Surface the hidden assumption about user intent before acting.
- Write anti-sycophancy rules around observable patterns, not vague wishes to "be honest".
- Keep the stable system layer separate from the current task spec.
- Add only the lines that actually change behavior.

## Mistakes to avoid

- Mixing stable identity with temporary task details.
- Turning the prompt into a manifesto instead of a working contract.
- Using long reasoning instructions as if they guarantee correct reasoning.
- Trying to solve runtime, permission, or evaluation problems with wording alone.

## Good sign

Two careful readers would infer similar priorities, tradeoffs, and default behavior from the prompt.
