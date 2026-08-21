---
type: method
title: Improving chat-recall retrieval experimentally
description: This method captures the pilot process for evaluating retrieval changes against real evidence, explicit acceptance criteria, and correction loops.
tags: [method, retrieval, evaluation]
---

# Improving chat-recall retrieval experimentally

This method describes how the pilot corpus approaches chat-recall retrieval improvements. It is appropriate when a retrieval script or ranking change is being proposed and the goal is to show a meaningful improvement over the current toolchain without drifting into abstract redesign.

## When to use it

Use this method when a proposed retrieval improvement needs to beat both the current script and ordinary shell-based search in a way that justifies extra tooling. The user states on 2026-08-11 that the goal is to create a script that is better than the current one and better than standard methods, "significantly better" so the added tool burden is worthwhile, and also that the script should remain light and fast ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)).

## Prerequisites

- A real or realistically backfilled recall corpus rather than only synthetic fixtures ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)).
- A clear separation between testing the script and testing the skill itself, because the user explicitly corrected that distinction ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)).
- Search topics or evidence targets that come from the project's own materials rather than invented prompts ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)).

## Steps

1. **Define the actual object under test.** Confirm whether the experiment is about the inner retrieval script, the higher-level skill, or another layer. On 2026-08-11 the user corrects the framing: this is not testing the skill itself, but the script inside the skill and the choice of quote-search method ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)).
2. **Set acceptance criteria before expanding architecture.** The script must be meaningfully better than current and standard approaches, and it must stay lightweight and fast ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)).
3. **Choose evidence-bearing queries from inside the project.** One correction says the index file is not itself the search target; instead, it tells you what exists in the project, and the evidence should be sought in the local chat-recall folder that actually contains the gold material ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)).
4. **Backfill missing retrieval metadata if the corpus shape is inadequate.** On 2026-08-14 the user says the current quote files are not yet prepared well enough for realistic testing and should be manually updated with session-context metadata ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)).
5. **Read whole relevant sessions when deriving file-level retrieval aids.** Another correction says quote snippets alone are insufficient for session-context backfill; the relevant sessions must be found and really read ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)).
6. **Keep retrieval aids separate from quote evidence.** The selected design keeps `session_candidates` separate from record ranking so the helper card can route file discovery without pretending to prove owner intent ([2026-08-14 codex holder part 2](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_2.md)).
7. **Use correction loops to simplify rather than layer.** If a proposed fix adds too much machinery or noisy metadata, the 2026-08-11 corrections favor removing the problematic layer instead of extending it ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)).

## Verification

A candidate improvement passes only if it demonstrably retrieves the needed evidence better than the previous approach, remains fast and simple enough to justify use, and does not contaminate evidentiary ranking with file-level hints.

## Failure modes

- Testing the wrong layer.
- Optimizing for experimental elegance instead of concrete script improvement.
- Using topic hints as if they were evidence.
- Building extra architectural layers when the correction pattern favors simplification.

## Sources

- [2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)
- [2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)
- [2026-08-14 codex holder part 2](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_2.md)
