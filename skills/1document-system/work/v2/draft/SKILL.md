---
name: 1document-system
description: >-
  Use when about to write or substantially edit a project document: give it a
  standard type name and hold it to what must be acted on. Not for artifacts
  another skill owns, code comments, or chat.
---

# Document System

## Unique context

Agents think in stereotypes: from a document's name alone the model already
knows what lives where and how to write it, and the sections take it straight to
the right place. But the same corporate stereotype carries corporate volume, and
the documents have started to bloat. Without a type name the agent writes prose
and its own opinions, and turns a specification into a chronicle. The type name
is visible before the file is opened: the agent knows in advance which section
to look in.

## Your main goals

- A document ships in startup style: only what is needed to act or to find the
  answer is written, and a full set of sections filled for coverage is not
  success.
- Every mutable answer has one place, and from the type name and its sections
  the agent finds that place without opening extra files.
- A document never leaves its genre — no opinions and no chronicle in a
  specification; a corpus that grew without displacing text is not success.

## Protocol

1. Adopt the project's own vocabulary wholesale when it has one: a registry,
   naming convention or section contract is live when the project's current
   files actually follow it. Take its type names, sections and metadata
   entirely and blend nothing of your own into them, because two naming systems
   in one corpus destroy the address this skill exists to protect. No live
   vocabulary — continue with the steps below.
2. Find whether this answer already has a home before you create a file. Search
   by type term and by subject; an answer with an existing owner is written
   there. A second file for the same answer is sprawl that no later pass
   undoes, because both files then look legitimate.
3. Choose the type from the question that outlives this conversation, not from
   what the material is about. A startup carries few document types, and a type
   earns its place only when some question keeps coming back and someone has to
   act on the answer.
4. Take the lightest standard business-document term whose genre owns that
   question. The whole mechanism is the model's existing prior, so an invented
   label — "Payment Intelligence Brief" — fires no stereotype and delivers
   neither genre nor address; the closest standard term beats a more precise
   invented one.
5. Admit a new type into the project only together with the first real document
   written in it. A registered type with nothing in it is an empty promise that
   the next agent reads as a home and fills for coverage.
6. Name the file `<TYPE> — <subject>.md`. The type is read before the file is
   opened, so it lives in the filename; a type that appears only in a heading
   is invisible at the moment it is needed. Where a filename is fixed by
   convention — `README.md`, `AGENTS.md` — declare the type in the first line
   instead.
7. Make the subject a stable thing that will still exist next quarter, never
   the occasion of writing. `auth-refactor-notes-aug.md` types correctly and
   still hides its answer: the next agent cannot guess the occasion, so it
   writes a second file for the same answer.
8. Take from the stereotype only what belongs in this genre and in what order.
   Never take its length, its ceremonial sections or its register: the
   enterprise prior is trained on documents written for an absent reviewer, and
   every generator of corporate volume — coverage, justification, provenance,
   restatement — exists to serve that absent reader. Your reader is present and
   acts today.
9. Treat the genre's sections as an ordered slot list, never a template. Order
   is fixed so a reader can scan for a heading; presence is decided by content.
   A slot with no answer is not materialized — no heading, no placeholder, no
   "not applicable" — and a missing heading is itself the answer: this document
   holds no answer of that kind.
10. Admit each block by naming, in a few words, the action it enables or the
    question it answers. No such name, no block. This is the only stop for
    justification prose and recap, which are well-formed, on-topic and useless
    and therefore survive every instruction to write concisely.
11. Never write these families at all: revision history, status and version
    fields; executive summary, introduction, background, conclusion; scope
    preamble, in-document glossary, appendix. They read as structure rather
    than content, so a block-level test does not bite them, and they are the
    front doors — provenance is how chronicle enters a specification, summary
    is how restatement enters everything.
12. Move out what this genre does not own instead of deleting it. Every kind of
    content has one owning genre: rationale and opinion belong to a proposal or
    decision record, sequence of events to a log or changelog, definitions to a
    glossary, findings at a point in time to a report. Route the content to its
    owner — this single move is both the genre ban and the one-place rule.
13. Remove what your new content supersedes instead of writing beside it.
    Superseded means the new text replaces it, not that you would have phrased
    it differently; authorship makes no difference and git holds the history.
    Appending is the whole bloat engine on the edit path: the file grows
    monotonically, its strata start contradicting each other, and a chronicle
    forms by accretion.
14. Close on the finished file rather than on your account of it, by two
    signals. Every slot filled is the coverage signature — re-run step 10 on
    each block. Volume grew while no new scope entered means step 13 did not
    happen.

## Always

- Genre discipline never yields. A project's live vocabulary replaces the names
  and sections you would have chosen, and never licenses opinions, chronicle,
  ceremonial sections or growth without displacement.
- An artifact family another skill owns — task files, findings, product frames,
  agent instructions — stays with that skill. Route there instead of retyping,
  renaming or reshaping it, whatever its current form looks like.
