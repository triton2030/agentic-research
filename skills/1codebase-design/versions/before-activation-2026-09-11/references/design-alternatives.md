# Design Alternatives

Use this reference when one interface choice is materially uncertain and
plausible alternatives differ in knowledge burden, ownership, or change
radius.

## Useful Alternatives

Alternatives must express genuinely different design bets, such as:

- one policy-rich operation versus several composable primitives;
- a caller-oriented facade versus an effect-oriented port;
- an explicit lifecycle object versus stateless operations;
- keeping the current shape versus introducing a new seam.

Cosmetic renaming or arbitrary method-count variants do not count.

Each viable alternative should make comparable evidence visible:

- caller usage and knowledge required;
- invariants, failure modes, ordering, and effects;
- what complexity moves behind the interface;
- dependency and adapter consequences;
- likely change radius for the pressure that triggered the design work;
- costs, including migration and new concepts.

Recommend the smallest design that best serves the concrete pressure or
committed requirement. A hybrid is justified only when every added contract
element pays for its caller knowledge and migration cost, and ownership
responsibilities remain coherent.
