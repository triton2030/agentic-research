---
name: 1domain-modeling
description: >-
  Use when code adds or changes a business concept, rule, or invariant, or one
  rule spans layers and related concepts may change independently. Not for
  simple wiring or prose-only work.
---

# Domain Modeling in Code

## Outcome

Place each consequential piece of domain meaning where a future change to that
meaning has one obvious owner, one coherent edit path, and focused proof.
Component boundaries follow independent business reasons to change instead of
the current call sequence, storage shape, framework layers, or a noun-to-class
mapping.

A domain model here is the code's working account of identities, decisions,
invariants, policies, state transitions, and relationships. It can be expressed
with existing functions, types, modules, or services. A new abstraction is not
an automatic result.

## Why the Natural Default Misses

The current request foregrounds the nearest endpoint, conditional, table, or
file. Putting the rule there is locally cheap, and splitting code into familiar
technical layers looks organized. The semantic cost appears later: one policy
change touches validation, orchestration, persistence, and presentation, while
no symbol owns the decision itself.

“Separate concerns” does not repair this default. Almost any layer split can be
described as a concern after the fact. Use an observable change trace instead:

```text
business scenario
-> decision or invariant
-> facts it needs
-> independent reason to change
-> semantic owner in code
-> focused proof
```

If the trace cannot reach one owner without following unrelated technical
layers, the model is still distributed accidentally.

## Controller: Model Change Pressure Before Components

Start with one concrete scenario that forces a business decision. Inspect the
current code and terminology, then keep a compact working model of the
following:

- the domain concepts the scenario distinguishes;
- the decision, calculation, transition, or invariant that makes the scenario
  valid or invalid;
- the facts the decision owns versus facts it merely consumes;
- the actor, policy, lifecycle, regulation, or product choice that can change
  it independently;
- the current symbols that already encode all or part of that meaning.

Use that model to choose the code shape:

1. **Name the decision, not the plumbing.** Prefer terms a domain change will
   use. Reconcile overloaded or competing names in code before adding another
   synonym.
2. **Keep one reason to change together.** Rules and state that enforce the same
   domain decision should have one semantic owner even when callers arrive
   through different transports or workflows.
3. **Separate independent change.** Split policy from mechanism, or one domain
   responsibility from another, only when they have different decision owners,
   lifecycles, failure modes, or credible change pressures.
4. **Expose intent at the boundary.** Callers ask the owner to make the domain
   decision; they do not reassemble it from flags, raw fields, or ordered helper
   calls. Invalid states should be rejected at the boundary that knows why they
   are invalid.
5. **Make duplication delegate.** Several entry points may repeat cheap input
   checks, but consequential domain meaning has one owner. Boundary checks must
   not grow into competing implementations of the policy.

The simplest credible shape is always the comparator. Expected volatility is
evidence only when grounded in a roadmap, repeated changes, different business
actors, configurability, regulation, separate lifecycle, or costly failure. A
hypothetical future variant does not earn an interface or component by itself.

## Component Boundary Test

A proposed component or split is earned when it changes the future edit path:

- its name points to a coherent domain responsibility rather than a generic
  technical role;
- it owns a decision or invariant that callers would otherwise need to know;
- its internals can change for that business reason without coordinated edits
  in unrelated components;
- its interface uses domain intent and keeps storage, transport, and assembly
  detail behind the boundary;
- focused tests can fail for its owned behavior without exercising the whole
  application.

Remove the proposed boundary mentally. If the next domain change and its proof
remain equally local and understandable, keep the simpler shape.

## Thought Demonstrations

> **Default -> transition.** Refund eligibility is checked partly in an API
> validator, partly in an order service, and partly in a persistence query.
> Those locations follow execution stages, but “eligibility” is one business
> decision. Give that decision one domain-named owner; let entry points gather
> facts and delegate. A policy change now alters one implementation and its
> focused scenarios rather than three layers.

> **Anti-example.** Turning every noun into an entity class and every verb into
> a service produces a recognizable domain-modeling shape, but it does not
> reduce change spread. If `Refund`, `RefundPolicy`, `RefundManager`, and
> `RefundValidator` all interpret eligibility, the model is still fragmented.

> **Transfer.** Entitlement rules are used by an HTTP endpoint, a scheduled
> worker, and an import job. The transports may remain separate, while the
> entitlement decision and its invariants share one semantic owner. The same
> controller applies without requiring a framework, aggregate pattern, or new
> package hierarchy.

## Working Output

For a design, implementation, or review, make the decision legible with the
smallest useful packet:

- scenario and credible change pressure;
- domain decision or invariant and the code term that names it;
- current and proposed semantic owner;
- boundary kept, removed, or introduced, with the simpler comparator;
- focused proof and unresolved assumptions.

This packet is transient reasoning or part of the task response. Do not create,
update, or name project documentation. The durable result is the code's names,
types, interfaces, behavior, and tests.

## Evidence and Stop

The change is supported only when code search reaches the intended owner, a
representative policy change stays within that owner and explicit callers, and
focused tests exercise the owned scenarios and invariants. Passing broad tests
or producing a tidy folder tree is only a proxy.

Stop without a new abstraction when current evidence does not distinguish it
from the simpler shape. Stop after the touched domain meaning has one legible
owner and proof; do not remodel unrelated code or impose a universal domain
architecture.
