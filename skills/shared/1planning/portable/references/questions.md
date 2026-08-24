# Questions to the owner

Moment: work hit an owner decision — before plan creation (the questions
gate) or mid-flight (a new fork). A question lives as its own note in the
project's questions folder, not as a plan section and not as a chat line: a
chat line dies with the window, and the owner does not open plan sections.

## Every question reaches the owner

- **Blocking** — the answer changes the goal, an epic, a success criterion,
  the first route, or falls in the project's Founder-only zone (money,
  obligations): stop only the affected branch; unaffected work continues.
  This list is the owner of the blocking vocabulary; the body gate points
  here.
- **Minor** — the answer does not change the next branch: a question note
  without a stop; it accumulates and waits for the owner in a batch; work
  proceeds on a labeled assumption with a review trigger. Silently turning
  a question into an assumption with no note is forbidden: the owner said
  "all questions must be asked to me".
- Derivable from the Goal, the principles, or owner records →
  `1use-principles`, not a question.

## The question note

```markdown
---
тип: вопрос
статус: открыт | отвечен | архив
касается: "[[<epic or work>]]"
ответ: ""
срок: <default date>
обновлено: <date>
---

# <the question in one line, in the owner's domain words>

**Что меняет ответ.** <which branch is waiting>

**Варианты.** <options with the cost of each; the recommendation marked>
```

A question is answerable by one owner action — the mechanics (buttons, the
`ответ` property) are set by the project instruction. IDs and internal
jargon in the question text are the mark of an untranslated question.

## Deadline and default

Every question has a deadline; when it passes, a minor question closes by
its default — a labeled assumption with a review trigger — and a blocking
one escalates through a live channel. The owner's silence is planned for,
not ignored.

## After the answer

An answer is accepted when the owner's word arrives through any channel —
a note property, a button, or a chat line. In the same move:

1. record the owner's word in chat-recall (a button answer is their word
   too);
2. move the decision to its owner — plan, epic, canon, instruction; the
   note does not own decisions;
3. `статус: архив` with the recall record's address; the unblocked branch
   continues.

The note is a temporary envelope: the live question list stays short.
