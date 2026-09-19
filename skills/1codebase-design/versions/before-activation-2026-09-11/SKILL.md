---
name: 1codebase-design
description: >-
  Use when code work reaches a contract decision: choosing, reviewing, or
  changing an interface, seam, adapter, port, component boundary, dependency
  boundary, or test surface. Combine with 1domain-modeling when the contract
  carries a business rule; use 1readable-code when the contract stays stable.
---

# Codebase Design

## Outcome

Choose the smallest honest contract that reduces caller knowledge and
concentrates change while keeping ownership, recovery, and caller-visible
obligations legible.

A **deep module**—substantial useful behavior behind a small interface—is a
valuable heuristic, not a mandate. “Keep the current shape” is a valid result
when a new abstraction would add more knowledge than it hides.

## Design Language

- **Module:** anything with an interface and an implementation, at any scale.
- **Interface:** everything a caller must know for correct use: operations,
  invariants, ordering, errors, configuration, and material performance facts.
- **Seam:** a place where behavior can vary without editing the caller.
- **Adapter:** a concrete implementation occupying a seam.
- **Depth:** useful behavior or policy obtained per unit of interface knowledge.
- **Locality:** change, diagnosis, and verification remain near their owner.

Prefer the project's established vocabulary when these terms would conflict
with its domain language.

## Design Decision

Before recommending a new contract, name the simplest credible alternative
that adds no interface or seam, or show why none can serve the committed
requirement. If the alternative serves the same concrete pressure or
requirement without greater caller knowledge or change radius, keep it. Start
from that pressure or requirement, not an architecture pattern.

A new or changed seam is earned only when evidence shows that it:

- removes knowledge, policy, or coordination from current or intended callers;
- gives the chosen contract concern one clear owner;
- isolates a real effect, external dependency, variation, or deployment seam;
- reduces the likely radius of a current class of change;
- makes an invariant or failure contract easier to state and verify.

Do not add a seam for hypothetical variation alone.

## Interface Contract

Make the normal case direct and invalid use difficult or immediately legible.
An interface is small by **required knowledge**, not method count. State only
caller-relevant:

- operations, inputs, and results;
- invariants and invalid states;
- ordering or lifecycle constraints;
- errors and the owner of recovery;
- side effects and material timing;
- configuration and performance facts that change correct use.

Hide assembly and implementation choices, not these obligations. Reject
pass-through layers that merely rename another interface. Side effects are not
a design failure; hidden ownership, surprising timing, and unclear recovery
are.

## Verification Boundary

Test each distinct risk at the smallest boundary that owns it. Prefer behavior
tests through the contract that should survive an internal refactor. Keep
adapter integration or contract tests for dependency-specific obligations, and
retain internal tests for dense invariants, fault localization, or algorithms
whose failures would otherwise be expensive to diagnose. Test location follows
owned behavior, not a universal public-versus-private rule.

For a recommendation, name the claim-specific falsifier and what result would
change the verdict. For an implemented change, run that check and report its
result; if it cannot run, mark the claim unverified.

## Conditional References

- If dependency behavior determines seam placement or test strategy, read
  [dependencies](references/dependencies.md) before choosing the boundary.
- If two or more materially different interface bets remain viable, read
  [design alternatives](references/design-alternatives.md) before recommending.

## Working Output

Make the decision reviewable with the smallest packet that names:

- the concrete pressure or committed requirement, and current or intended callers;
- the current shape and simplest no-new-abstraction alternative;
- why the chosen seam and interface reduce required knowledge or change radius;
- caller-visible invariants, failures, effects, and material performance facts;
- the verification boundary, falsifier, and result or unverified status;
- unresolved assumptions and the cost of being wrong.

## Stop

Stop without adding an abstraction when evidence does not distinguish it from
the simpler shape. Do not redesign unrelated code.
