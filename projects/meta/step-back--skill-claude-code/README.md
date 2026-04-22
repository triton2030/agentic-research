# step-back (Шаг Назад)

Cognitive meta-regulator for the dialog. Antidote to reasoning failures common to humans and LLMs.

## What it is

The one moment in the conversation where the model is allowed and required to doubt its **own line of reasoning** — not the answer, not the plan, but the framing itself. Every other skill optimizes *inside* the accepted frame. This one asks: is the frame right?

## Scope

- Works on any topic, any project, with or without code.
- No file writes. No persistence. No other-skill routing as part of the skill itself.
- Single-block output, strict 4-field form, then the reframed next move executes immediately.

## Taxonomy of reasoning failures it catches

Universal (humans + LLMs): anchoring, Einstellung, premature convergence, goal drift, sunk cost, streetlight effect.

LLM-specific: sycophancy, confabulation, chain-of-thought unfaithfulness, goal misgeneralization, frame lock from instruction layer.

See [references/cognitive-failures.md](references/cognitive-failures.md) for how each shows up in dialog and the form of reframe that breaks it.

## File layout

- `SKILL.md` — thin skill body.
- `references/cognitive-failures.md` — taxonomy of the 11 failure classes.
