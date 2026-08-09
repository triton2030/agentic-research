---
name: 1document-system
description: >
  Use when multi-file docs work must change an owner, type or topology, or
  assemble one typed artifact/projection. Route system versus direct mode;
  leave ordinary prose to the local contract.
---

# Document System

Familiar commercial document types are compression: the model already knows how
a PRD, ADR or API spec is written, so a type name activates a professional
prior — dense style, known sections, a genre ban — without spelling any of it
out. This skill spends that prior to make agents write less, find truth by
name, and keep every document inside its genre.

## Goal

A typed corpus where any mutable answer has exactly one owner, every artifact
obeys its genre, and the next clean session routes intent → zone → file by
name and description alone. Writing less is the point: structure comes from
the type, not from emitted text.

## Success criteria

- Every mutable answer has one semantic owner; a view, index or map never owns
  truth.
- Each artifact passes its genre ban: a spec carries no opinions, a decision
  record no chronicle, a catalog no rationale essays.
- No empty structure exists: nothing was materialized without content.
- A clean session finds the owner of a question without opening wrong files:
  filename code + description are sufficient routing.
- The corpus and its control layer (contracts, maps, indexes) both shrink or
  hold; growth without displaced text is a defect.

## Invariants

- A live local contract wins entirely; this skill is the fallback, never the
  enforcement. Local registry codes, sections and metadata replace defaults
  wholesale — do not normalize them back.
- Design order: claims → owner → typed carrier → derived views → control.
  Starting from a catalog of documents distributes one idea across every genre
  that can mention it.
- Type name = activated prior + genre ban. Standard sections live in the
  model; write only deviations, ownership modes and bans.
- Template inversion: an empty slot is not materialized — no heading, no
  placeholder row, no «not applicable». A status marker exists only for a real
  question that has no answer yet. Coverage is checked in the head, not
  emitted.
- Current truth, decision history, derived view, ops state and evidence stay
  distinguishable; promotion of any view into a second truth is the central
  failure this system exists to prevent.
- New type admission is atomic: registry entry + first substantive artifact in
  the same change; a type needs an independent seam (owner, lifecycle, reader
  or validation) — scope alone is not a seam.
- A structural rule without an executable gate drifts: prose bans hold style,
  scripts hold structure. Anything that must not drift names its project-local
  script owner.
- The control layer pays the same rule budget as the corpus: contracts, maps
  and indexes about documents also grow silently; each addition names what it
  displaces.

## Delta

The model writes documents well. It does not:

- keep one mutable answer in one home — it re-explains truth everywhere a
  genre allows a mention;
- resist filling every slot a template shows — coverage feels like quality;
- notice mid-file genre drift — a spec becomes a chronicle one paragraph at a
  time;
- see corpus-level cost — each document looks justified alone.

## Known failures

`when → failure → cost → where`

- owners, types or topology change → catalog-first design → empty taxonomy and
  parallel truth → [system-mode](references/system-mode.md)
- one typed artifact or projection to write → slot-filling ceremony → prose
  nobody asked for → [direct-mode](references/direct-mode.md)
- type choice without a local registry → wrong prior activated → wrong genre
  ban applied → [catalog](references/catalog.md), then exactly one template
- frontmatter → questionnaire metadata → retrieval noise instead of routing →
  [metadata-contract](references/metadata-contract.md)
- reader view needed → view silently becomes second truth →
  [projections](references/projections.md)
- files need homes → mixed folder axes, premature folders →
  [topology-contract](references/topology-contract.md)
- live corpus is compressed or deduplicated → silent loss behind resolving
  links → [compaction-safety](references/compaction-safety.md)
- corpus too large for one context → inventory worker becomes reviewer →
  [delegation](references/delegation.md)

## Mechanics

1. **Mode gate.** Owner/type/topology change → system mode. One typed artifact
   or projection with a known zone → direct mode. Known owner + known local
   contract + ordinary prose → this skill stays silent.
2. **Local first.** Read the local registry/contract before any default; its
   vocabulary is the working vocabulary.
3. **Hard transition: mapping before cutover.** A refactor of a live corpus
   stops at a target owner map; rewrite, move and delete belong to a
   separately accepted task under compaction-safety.
4. **Hard transition: admission before materialization.** No folder, template
   or registry entry exists before its first substantive artifact.

## Completion

Artifact or map delivered + genre ban checked + inverted slots listed (what
was consciously not written) + affected owners updated or named. A result that
grew the corpus names what it displaced.
