# DEC — Decision Record

**Purpose:** preserve one material fork, why the option won, its consequences
and the revisit boundary. **Default authority:** `decision`. Aliases: ADR, BDR.
Near-miss: evidence → RPT; product scope → PRD; change design → EDD.

**Ban:** DEC owns the choice and its rationale, not facts and not
implementation. One decision question per record.

**Non-obvious contracts:** Context = REFERENCE — pointers and owner identities,
not a retelling of the situation. Required Follow-through = LOCAL: affected
owner pointer → the exact decision-induced delta, never a copy of the spec.
Revisit Conditions must be observable triggers, not a calendar reminder.

## Business Decision Record Profile

BDR is a self-sufficient append-only historical record of a material business
choice, not a current-truth owner. After acceptance it is not edited; a new
decision creates a new BDR, and the same move updates the live owners with the
normative consequences.

A BDR contains no Markdown links, wikilinks, URLs, filesystem paths, anchors or
graph relations (`depends-on`, `derived-from`) — neither in body nor in
frontmatter. Predecessor, successor, affected owner and provenance are named as
plain stable IDs without link syntax. A local contract may choose the fields for
those IDs, but must not turn the historical record into a dependency hub.

**Conditional modules:** architecture/business/legal/vendor impact;
approval/dissent log; rollout gate; options matrix.

**Completion check:** downstream owner updates are addressed to their owners,
not hidden inside the DEC.
