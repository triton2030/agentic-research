---
description: "Turn an observed target-model instruction failure into the smallest testable wording delta."
read-when: "A trace or correction shows a model-specific instruction failure; never run as a generic checklist."
---

# Model Failure → Wording Delta

## Contract

Use this reference only after a trace, correction or representative eval shows
a concrete failure. The skill body owns instruction placement; the current
project's model wisdom or primary model guide owns model-specific behavior.

1. Record the observed tell, exact instruction, runtime/model actually resolved
   and why the failure matters.
2. Separate observation from mechanism. If the mechanism is not supported by a
   current owner/source, label it a hypothesis and repair only the observed gap.
3. Choose the smallest matching wording delta:
   - local rule applied too narrowly → name the full class/surface and exceptions;
   - assessment turned into mutation → state authority, deliverable and stop;
   - required tool was skipped → say when, why and which surface is required;
   - work expanded around the outcome → name in/out scope and simplest
     sufficient result;
   - progress/completion outran evidence → bind claims to a tool result or
     artifact from the current run;
   - delegation was too broad, too narrow or wrongly sequenced → give a decision
     rule, independence test and whether the root must wait;
   - output density/style drifted → name audience, required content and what may
     be omitted;
   - strict completeness/order matters → number only the invariant sequence.
4. Re-run the same representative case. If the delta does not change the
   observed behavior, remove it rather than stacking another instruction.
5. Promote a repeated model-specific finding only to the current model owner,
   not into this global skill reference.

## Do Not

- Do not copy a model wisdom file or migration guide into the skill.
- Do not infer a family-wide trait from one trace.
- Do not compensate with generic “be proactive”, “be careful”, MUST or a
  longer self-check stack.
- Do not change effort, tools and prompt wording together when attribution
  matters.

## Stop

Return the observed tell, smallest wording delta, representative re-check and
remaining uncertainty. No observed failure means no model-specific rule.

