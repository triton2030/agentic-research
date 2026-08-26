# BRC — Business Rules Catalog

**Purpose:** own exact changeable rules and decision tables instead of free
policy prose. **Default authority:** `canon`. Alias: BR. Near-miss: decision
rationale → DEC; lifecycle → SEM; execution steps → PROC; agent rule →
`1instruction-placement`.

**Ban:** BRC owns the normative rule text, not why it was chosen and not how it
is executed. Each Rule ID has exactly one normative logic representation — the
atomic statement in the Rule Catalog or a named Decision Table, never both.

**Non-obvious contracts:** Normative Vocabulary = REFERENCE (DOM/glossary; local
clarification only). Decision and Evidence Basis = REFERENCE, no copied
rationale. Examples and Counterexamples are nonnormative, tied to Rule/Table
IDs, and never restate a rule. Consumer Mapping = LOCAL: owner links →
rule-specific applicability. Rule Record Contract owns required fields and
allowed workflow states.

**Conditional modules:** permissions; pricing/calculation; jurisdiction
variants; manual override; moderation; audit requirements.

**Completion check:** overlapping active rules carry explicit precedence.
