# BRC — Business Rules Catalog

**Purpose:** владеть точными изменяемыми rules и decision tables вместо
свободной policy prose. **Default authority:** `canon`. Alias: BR. Near-miss:
decision rationale → DEC; lifecycle → SEM; execution steps → PROC; agent rule →
`1instruction-shaping`. Для каждого Rule ID нормативная logic representation одна:
atomic statement в Rule Catalog либо named Decision Table, не обе.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Scope and Applicability | OWNER | Domain, actors, jurisdictions, exclusions |
| Normative Vocabulary | REFERENCE | DOM/glossary links, local clarification only |
| Rule Record Contract | OWNER | Required fields and allowed workflow states |
| Rule Catalog | OWNER | ID, scope/trigger, atomic statement or normative Table ID, exceptions, precedence, source, effective date, tests; table-backed logic not restated |
| Decision Tables | OWNER | Stable Table ID and complete condition → outcome combinations for table-backed Rule IDs; single normative logic home |
| Priority and Conflict Resolution | OWNER | Ordering, specificity, fallback, collisions |
| Effective Windows | OWNER | Activation, expiry, grandfathering, overlap |
| Decision and Evidence Basis | REFERENCE | DEC/RPT links without copied rationale |
| Examples and Counterexamples | OWNER | Nonnormative validation cases tied to Rule/Table IDs; no rule restatement |
| Deprecation and Supersession | OWNER | Replacement, transition, retained history |
| Consumer Mapping | LOCAL | PRD/SEM/API/PROC/test owner links → rule-specific applicability |

## Conditional Modules

Permissions; pricing/calculation; jurisdiction variants; manual override;
moderation; audit requirements.

## Completion Check

Active rules uniquely identified и testable; каждый Rule ID выбирает одну
normative logic representation — atomic catalog statement или referenced table;
overlaps имеют precedence; examples не становятся второй truth; consumers link
Rule IDs.

