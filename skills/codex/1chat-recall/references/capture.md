# Capture

## Goal

The corpus gets owner positions with their subject, conditions and strength;
working remarks about the thing at hand and bare agreements stay out. A record
is made in the same turn it was said, and a helper receipt proves it.

## Why

The scene is available now; a future reader has only the record. A missed
position cannot be found later, an unneeded record distorts the picture of how
he thinks, and a wrong subject makes an exact quote useless. A user message may contain pasted
documents or other people's and agents' conversations: the message role does
not prove who wrote each fragment. The helper takes text you already confirmed;
it does not establish authorship.

## Criteria

- A `quote` is shortened only by deletion, keeping words, order and essential
  conditions. Unclear authorship stays a gap; a pasted fragment is never
  recorded as the owner's.
- Kind and type never strengthen what was said: a `note` is your explanation,
  not owner speech; an idea or rule-candidate does not become a decision; a
  reaction to one case does not become `предпочтение` or `обо-мне` just because
  of «мне не нравится».
- `context-note` is a short set of search keys: missing names and synonyms. A
  paraphrase of the position or of your proposal there creates false evidence.
  `session-context` holds the subjects of the whole conversation.
- The result is a helper receipt with the record address, or an explicit
  failure. A manual write bypasses the helper's checks and atomicity.

## When you decide whether to record

One test: would an agent a month from now, facing a similar choice, decide
differently knowing these words?

Passes: longer reasoning about a concrete thing — what he likes, dislikes and
why; a choice of path with a reason; a boundary he drew; a correction of your
understanding that will recur in similar work.

Does not pass: an instruction about the current thing («сделай этот текст
разговорнее», «возьми для этой задачи модель X»), agreement to a step of current
work («да удаляй»), anything that says nothing outside this task. Its work ends
in this turn.

## When the owner agrees with your proposal

«Окей», «да», «давай» mark a choice: judge by what he agreed to, not by the
word. A package of several items is several choices — test each. Agreement to a
whole draft or artifact needs no record: the decision lives in the artifact, and
only individual choices in it can pass the test. Record a passing choice as
`selection`: its text is the words of the accepted proposal, shortened only by
deletion, like a `quote`. His own words added to the agreement — a condition, a
caveat, a reason — go next to it as a separate `quote`.

## When you set subject, scope and type

Keep in the excerpt the words that limit subject, situation, time and firmness.
Add missing names of the subject and project as keys in `context-note` if the
conversation shows them. Unknown scope stays unknown, not "all projects
forever", and no field widens it: «в этой папке стало слишком много файлов» is
about that folder; "the owner dislikes big folders" attributes a generalization
he never made, even with a verbatim quote.

The type is the strength of the remark at that moment. A remark with no sign of
acceptance that reads as either a question or a wish is `идея`; if work depends
on its meaning, ask. A judgment about a concrete thing — what is good and bad in
it and why — is usually that thing's `критерий`; `предпочтение` needs words
about a recurring expectation. A change of his own position is `решение` or
`предпочтение`; `коррекция` fixes your understanding or action.

## When you prepare the record

A subject this conversation already recorded is updated with `--replace`
(below), not recorded again.

[chat_capture.py](../scripts/chat_capture.py) runs with `python3`. Read the
whole topic map from `--list-metadata` before choosing a topic: matching words
do not define a subject's boundary. No fitting topic — `--new-topic` adds it in
the same call; in an empty project it creates the first map and record. A topic
holding a third of the corpus or more no longer separates subjects: for a new
independent subject inside it, create a narrow topic. A record linked to an
earlier one (below) stays in the earlier one's topic: the helper accepts links
only within one topic.

`--add-subjects "subject; synonym"` appends search keys to the existing session
card and keeps the old ones. The first record of a file needs a full
`--session-context`; replacing the whole card requires reading the conversation
first. Do not mix the two in one call.

For a same-turn record `--source-timestamp` and `--source-ref` may be omitted.
For a historical `capture-needed`, pass the original remark's time.

## When a new remark changes an earlier one

Searching for the earlier record is not required: the corpus is context, and
the current rule lives in live files and the conversation. If you already have
the address of another conversation's record — from what you just read —
link it with `--supersedes` (a record of this conversation is replaced
instead, below): ordinary search then returns the new words, and
the old ones stay visible in `--topic … --timeline`. Avoid `--contested`: it
removes both records from ordinary search and leaves them only under
`conflicts`. Link by a verbatim record that cannot hold together with the new
remark under the same conditions, never by guess.

A record is not the rule. If the remark changes a rule the project keeps in a
live file, change that file by its own route as well.

## When a later remark of this conversation touches a recorded subject

One conversation keeps one record per subject, and the record evolves: the
owner decided so on 26 Oct 2026, because corrections appended beside earlier
records made conversation files long, and a reader had to read a whole file to
find the final position. A later remark on the same subject — taking it back,
a new condition, a reason, a change of mind — goes into the existing record
with `--replace`, not into a new record beside it. Build the version from all
his remarks on the subject, shortened only by deletion and kept in order. A
reason he named for a change (a result, a new fact, someone else's opinion)
stays inside the version: the next agent needs it. The type describes the
outcome; the time is that of the remark that settled it — the write time in
the same turn, otherwise its `--source-timestamp`.

`--replace <file>.md#recall-<id>` removes the old block and appends the new
version under the same address; the address is in the receipt or in this
conversation's file. The helper does not carry
over the old version's links: pass again those that still hold; the receipt
lists dropped ones. It refuses a record linked from another record and a
record of another conversation. A document may cite the record too: search its anchor in the project with
`rg`; a document rests on the old words. In any of these cases save the new
remark as its own record linked with `--supersedes`, as above.

## When you store an answer and its address

Two answers in one message are told apart by `--source-ref` of the specific
fragment, e.g. `<message-id>#goal` and `<message-id>#scenes`; reuse it on retry.
Without it, the exact original time plus metadata tell scenes apart. A retry
after an error does not need a changed quote.

To link an old record without a stable heading, use
`file.md:line sha:<record_sha256>`; take the hash from output after reading and
confirming the quote — the current line alone is not enough, and no repair of
the old file is needed. Several addresses: repeat values or the flag. Pass
text, metadata and any known link in one Capture call.

For a footnote use `anchor` from the receipt, `<file>.md#recall-<id>`;
`line_anchor` is only the current reading position.

## When the conversation branched or words came in a command

Owner words in slash-command arguments are his speech and pass the same test. After a branch the conversation has a new session id; recording under the old id mixes branches in one file. In Codex the helper takes the current window id from `CODEX_THREAD_ID` or `CODEX_SESSION_ID` when `--session` is not passed; after a branch, check that it is the branch id. Pass the session card on the first record of a file; later the old subjects stay and new ones are added with `--add-subjects`.
