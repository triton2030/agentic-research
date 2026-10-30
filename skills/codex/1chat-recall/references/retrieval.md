# Retrieval

## Why

The corpus is context — what the owner thought then — not his current
decisions; those live in project docs, instructions and the current
conversation. Search returns candidates to read: a cut fragment, a session card
or a high rank does not replace his words. One exact phrase may find nothing
where he discussed the same subject in other words, and a later remark may
change his thinking without naming the subject.

## Task

Find and read the source conversations yourself to understand how the owner
thought about the current question. Do not delegate search or interpretation,
and do not replace what you found with another agent's report.

## Goal

You understand his thinking on the subject — with exact address, date and
conditions — and never present a quote as a current decision. A quote and your
own judgment stay distinguishable; a missing source or an unfinished search
stays visible.

## When you search

Read [search mechanics](search-mechanics.md) before the first search. Name the
subject of the current question and the project. Search not only its name but
the choice under discussion — e.g. development speed versus reliability when
the question is about checks in an app. That widens the query; it does not
attribute wishes to the owner.

```bash
ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"
TARGET_PROJECT_ROOT="${TARGET_PROJECT_ROOT:-$PWD}"
uv run --locked --script "$ROOT/scripts/chat_digest.py" \
  "$TARGET_PROJECT_ROOT/_ops/chat-recall" --query "<subject and choice>" --json
```

Without `--json` the digest prints readable quotes, and `--head` sets their
length; in JSON each candidate sits in `.holders[]` with its `.strongest_quote`.
With thin results, try other wordings, synonyms and stems with `*`. Check
`topic_candidates` and session cards, then the fitting topic via
`--topic <handle> --timeline --json`. Widen a blocking filter; raise the limit on
`truncated` and fix tool-output truncation too. The same query with a higher
limit does not replace new wording. If the helper is unavailable, use
`--lexical` or `rg` over the corpus and name the limitation; a tool error is
not an empty corpus.

`no-eligible-records`: the filtered set holds no eligible quotes — check filters
and excluded records. `no-lexical-match`: no word matches, though hybrid may
still return semantic candidates. Check `channels` per quote: a quote may come
from dense alone. Such a result points to a conversation to read;
`strongest_quote` or `query_domain=in-domain` does not mean the question is
answered.

## When you choose quotes

Start from the subject's records in date order: `--topic <handle> --timeline`
shows each conversation's record on it, the latest position included. Since
26 Oct 2026 a conversation keeps one evolving record per subject, so that
record carries the conversation's final position. Open a conversation file
only for the scene around a deciding quote: read a short file whole; in a long
one read all records of the subject, the replaced one sits at the end of the
file. Older files may still hold several records on one subject: read to the
last of them. A part you read must arrive whole: a truncated output is not a
read. A later conversation may change his position under other words: check
the cards of later conversations before you rely on a quote. Do not
cut lines with `cut -c`: an owner remark is one line. «начнём заново» may not
name the subject: recent cards are in `--digest --json`. Ordinary search
returns a superseded record's replacement, not the record, and contested
records appear only under `conflicts`. For exact Cyrillic words use `rg -n -w`.

For an old record without a stable anchor, cite the file with the quote's
opening and date; do not turn a found `#L` into a permanent link. Only an
explicitly ordered [Integrity](integrity.md) adds addressing to legacy records.

For each quote establish date, author, object, circumstances and strength at
the time, and find the live project document on the same subject. Judge what
may have changed since; a later date alone does not cancel a compatible
thought. A local «не нравится» does not become a general trait; words from a
neighboring topic may explain a choice, but carrying them to a new object is
your own judgment.

## When you use what you found

A quote is context, not a decision. Take the current rule from live project
files and the current conversation; a quote that diverges from them tells what
the owner thought earlier and changes nothing. A quote fresher than a live file
and diverging from it calls for a question to him:
the file changes on his current word, not on a quote. For agent instructions a
quote raises no question: they change on his current word. Without divergence,
history explains why things are as they are.

Present a material support as «<verbatim quote>» — date, the stable `address`
from output (`<file>.md#recall-<id>`), or the legacy reference above. Name
object and conditions if the remark is ambiguous without them. For
`kind: selection` the text is the words of a proposal he accepted, not his
speech — say so. Shorten only by deletion; a guess never goes inside quotation
marks. Never answer "as the owner would say".

The record type is the strength of his words then: an idea, a preference and a
decision all remain context. If live files and the conversation do not settle
the question, quotes help you propose an option or ask a precise question.
Make a reversible choice yourself; ask before an irreversible one and continue
independent work meanwhile.

No fitting words after a widened search — name the subject and the search
bounds, and separate your judgment from his words. Never fill the gap with an
invented preference. Once sources and conditions are clear, return to the task.
