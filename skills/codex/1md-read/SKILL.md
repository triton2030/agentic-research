---
name: 1md-read
description: >
  Use before any Markdown read or first project-context orientation when `.md`
  files are present. Without it agents often full-read, use arbitrary line
  windows, or mistake routing metadata for evidence; frame the decision, read
  the smallest addressable body that could change it, and stop at sufficient
  coverage.
---

# 1md-read

## Product Job

Markdown triggers this skill; the **next decision or action** hires it. Deliver
the least addressable evidence that lets downstream work continue correctly, or
an honest gap that prevents false commitment, while leaving context for the
actual task. A reading report is not the product.

When the requested product is itself a filesystem inventory or coverage answer,
exact map fields are sufficient evidence for that narrow claim. Do not read
prose merely to perform the genre of this skill.

## Causal Contract

A known file, grep hit or plausible heading makes immediate reading feel cheap;
more text then appears safer. The smooth failure is a correct-looking answer
resting on a map, arbitrary line window or diluted body after avoidable context
has already shaped the next continuation.

Break that trajectory before the read. Keep one compact working contract:

```text
decision or claim ← smallest sufficient evidence unit ← result that could change it
```

If the possible change cannot be named, another body has not earned context.
The local measure is decision-changing evidence per context spent, not files
covered or commands completed.

“Smallest” means the smallest **semantically sufficient boundary**, not the
fewest lines. `Artifact-wide` is also an evidence obligation, not a synonym for
“the user named this document”, “this is an owner” or “the question is broad”.
Before a non-short full-file read, name which separated sections must interact
and how that interaction could reverse the decision. Otherwise map and select.

## Controller

1. Name the claim and the evidence result that could change the next action.
   Keep this working state internal; do not make it user-facing ceremony.
2. Reuse a known handle. Direct full reading is justified when the file is
   measured short (`1–2k` tokens is an orientation, not a hard limit) or the
   named nonlocal dependency above requires continuity. Otherwise map only
   enough to obtain a handle.
3. For a prose claim, decide from the selected body with its semantic boundary,
   never from its filename, heading, description or rank. For an explicit
   inventory/coverage claim, exact returned map fields can finish the job.
4. Continue only when a named gap points to another evidence unit with a
   concrete chance to change the decision.

Selection and evidence are separate phases: choosing tools before the claim
turns the menu into the task; concluding before body extraction turns routing
compliance into evidence theatre.

## Cheapest Sufficient Handle

| Known state | Read route |
| --- | --- |
| Measured short file or named nonlocal dependency | Direct Read |
| Root-scoped stable section ID | `md extract --section-root ROOT --section-id ID --extract --json` |
| Known folder, file not chosen | `md orient FOLDER --json` → select |
| Known large file, section not addressed | `md toc FILE --with-tokens --json` → `md extract` |
| Exact row, frontmatter field or raw block | Exact extraction; do not load its whole heading by habit |
| Several immediate anchored wikilink premises | Bounded linked reading from the source section |

The table is enough for ordinary routes. Open
[`references/progressive-reading.md`](references/progressive-reading.md) only
for partial/continued folder maps, customized numeric maps, budget recovery or
stable-ID diagnostics. Open
[`references/linked-reading.md`](references/linked-reading.md) only when the
source claim actually depends on anchored wikilinks.

If the target is unknown by meaning, the missing act is semantic discovery. Use
`1md-search`; do not imitate it with a broad `orient`, `ls` or `toc` dump.

## Thought Demonstrations

> **Default → transition.** To decide whether a plan permits an API change, a
> grep hit near “approval” invites a fixed line window and an “Authority”
> heading invites a verdict from the outline. The claim is normative: map only
> to address the complete authority/stop-rule subtree, then decide from it.

> **Anti-example.** “What does this document say about X?” names a source, not a
> whole-file dependency. Full-reading a long owner and later calling the claim
> artifact-wide is elastic justification. Conversely, mapping a measured short
> README whose whole argument matters is ceremony, not boundedness.

> **Transfer.** One registry version can be supported by its exact row even
> inside a huge section. A contradiction between separated definitions can
> require the whole file. The claim, not file size alone, sets the boundary.

## Evidence And Delivery

- Maps, headings, snippets, ranks and link reasons route to prose; they do not
  prove prose meaning or owner truth. Returned paths/coverage can prove a claim
  specifically about inventory.
- An exact heading section includes its nested subtree until the next heading of
  the same or higher level. Fixed `-A/-B` windows do not prove that boundary.
- Budget drops, unresolved anchors and continuation coverage are real gaps.
- A stable section marker is a root-scoped reading locator, not a link,
  authority claim or `depends-on` edge. Missing or duplicate IDs fail closed.
- Filesystem routes do not promise semantic-index exclusions; actual returned
  paths define factual scope.

Keep the bounded state `claim ← addresses read ← conclusion/material gaps`.
Do not repeat raw maps, JSON or a full reading packet in the final answer unless
the user asks for a reading/audit report or provenance is the deliverable.

This skill reads addressable Markdown evidence. It does not assign authority,
perform semantic discovery or make the project’s product/business verdict.

Stop when the next action is supported by evidence, material gaps are known,
and no unread unit has a named concrete chance to change it. Reopen for a new
claim, unresolved link, dropped section or conflicting body.
