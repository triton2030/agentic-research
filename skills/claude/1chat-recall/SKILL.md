---
name: 1chat-recall
description: >
  Use when a material decision may depend on what the owner said earlier,
  durable owner evidence appears in the current Claude session, the user asks
  what they said, or a recall record needs repair. Without source-bound
  applicability and chronology checks, an agent may re-ask the owner or apply
  a plausible but stale or out-of-scope quote.
allowed-tools: Bash(python3 *), Bash(uv *), Read, Grep, Glob
---

# Chat recall

## Product job

At a material fork, recover not a quote dump but **applicable working context**
sufficient to continue the current work without making the owner repeat
themselves. The consumer is a future agent; success is the correct next
decision, not a high rank or a large number of matches.

Working context is a transient synthesis over source evidence. It does not
create a persistent owner profile or become new owner truth.

## Invariants

Source-bound owner evidence is primary. A verbatim quote stays a quote, a Plan
choice stays a selection, and note/raw evidence remains visibly non-verbatim.
A wrong or missing date, type, topic, or format never cancels the record.

A useful isolated quote carries a `context-note` by default, but that note
contains only surprise delta: what cannot reasonably be inferred from the quote
plus its `type/topic`. Repeating, paraphrasing, or confirming what is already
clear is forbidden; when no non-inferable delta exists, omit the field.

Retrieval includes exact, legacy, partial, multiline, and raw records.

The log is dated evidence, not current canon. A later quote may supersede an
earlier one, and an approximate timeline must not be presented as current
truth.

## Why bare search fails

The natural default is to continue from visible chat or treat the first
semantically similar or newest hit as the current position. Exact wording, a
date, and rank look authoritative even when the quote belongs to another scope,
is an idea rather than an adopted decision, or has already been corrected. A
late check does not help after the assumption has begun steering
implementation.

The missing control act is an applicability gate before commitment:

```text
material fork
→ bounded claim cluster
→ full consequential records
→ applicability + commitment + time + coverage
→ decision-ready context | abstain
```

The bare command “find earlier words first” does not close this failure: it
still permits a top hit or a list of quotes without deciding applicability.

## Decision controller

Before retrieval, name the current fork and one or more independent claims that
earlier owner words could change. Do not begin with “what does the owner think
in general”: it merges scopes and rewards a coherent story instead of
applicable evidence.

Use only the current project's recall by default. Cross-project retrieval is
allowed only under explicit user scope; never silently merge its results with a
local position. Retrieval selects candidates for reading. Show every record
capable of changing the decision and compare applicability, evidence kind,
commitment, source time/precision, and cluster coverage.

Return to yourself or the user the smallest packet containing:

- applicable decisions, boundaries, criteria, and preferences;
- the displaced position and why it no longer governs, when relevant;
- scoped exceptions, conflicts, and gaps;
- the agent's own implementation inferences, explicitly not as owner words;
- dates and `record_id` values only for consequential claims.

If scope, commitment, chronology, or coverage remains unresolved, keep the
conflict visible and abstain or ask the owner. False application is worse than
missed recall. Keep tool rows, scores, and corpus counts internal unless they
change confidence or the user requested a search report.

### Contrastive scenes

> **Default → transition.** The newest top-1 looks like the current decision.
> `show` reveals that it is a narrower idea while the earlier record is an
> adopted general direction. The controller preserves the direction and adds a
> scoped exception instead of claiming false supersession.

> **Anti-example.** The agent found five exact quotes, showed dates, and called
> them context. No decision changed and applicability was not resolved:
> retrieval happened, the product did not.

> **Transfer.** For a broad question about the owner's position, first separate
> claims and scopes. Build several bounded packets or return a gap; do not infer
> one profile from thematically similar phrases.

## Operational branches

- A material current decision depends on established goals, boundaries,
  decisions, criteria, corrections, or preferences: build only the claim
  cluster that can change the decision and apply the controller above.
- Earlier input or a Plan/AskUserQuestion choice from the current session can
  change a durable result: read current-session evidence.
- Fresh durable owner evidence appeared: capture every independent useful
  thesis in the same turn, one record per meaning. Skip an approval,
  confirmation, or command when its own words do not form durable knowledge.
  Always skip credentials and pasted material that is not the owner's
  position.
- The user explicitly asks what they said, asks to find quotes, or requests a
  recall harvest: use corpus retrieval; quote search remains a servicing output
  when there is no current decision.
- An existing record has diagnostics or malformed metadata: use repair. This is
  the only branch allowed to search another session.

## Current-session evidence

Use the native current-session reader when earlier user input or a Plan answer
can change a durable result:

```bash
RECALL="${CLAUDE_SKILL_DIR}/scripts/chat_recall.py"
SESSION="${CLAUDE_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-}}"
python3 "$RECALL" --session-id "$SESSION"
```

The default is bounded and excludes the current turn. Add
`--include-current-turn` only when locating the exact record for a fresh
capture; add `--all` only when the bounded result is insufficient. A Plan
option is agent-authored: represent it as a selection (“user selected X”), not
a verbatim quote.

## Capture

Do not capture every durable utterance. Capture each independent useful owner
thesis as a separate record: decision, correction, preference, idea, criterion,
candidate rule, personal workflow fact, or factual assertion. A record passes
the usefulness gate only when its own words, outside neighboring messages, can
change a future decision, boundary, criterion, preference, or understanding of
the owner. `“Yes, let's fix it that way”` fails: its meaning lives in someone
else's context rather than in the quote. Preserve the owner's wording by
deletion-only shortening; do not turn agent summaries, inserted text,
credentials, or non-durable commands into quotes.

For an exact transcript record:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/chat_capture.py" \
  --quote "<owner words>" \
  --source-timestamp "<timezone-aware transcript timestamp>" \
  --type решение --topic документация-и-знания --agent claude \
  --project "$PWD" \
  --session "${CLAUDE_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-}}"
```

Pass the delta through `--context-note "<one short agent explanation>"`. It
stays inline, visibly non-verbatim, and available through `show`, but does not
participate in the record ID, BM25, or dense ranking. Do not add a new
conclusion, rationale, URL, path, or pointer to a transcript/another record.
The limit is 300 characters; `--kind note` cannot carry `--context-note`. A
context note never makes a weak quote worth capturing: apply the usefulness
gate first.

`--source-timestamp` always has a value. It accepts timezone-aware ISO, an
approximate ISO/date, or `unknown`. Approximate/unknown records must also pass
`--timestamp-source`, normally `--timestamp-precision`, and optionally
`--source-ref`. Use `--kind selection` for a chosen agent-authored option and
`--kind note` for a later explanation.

Default `source=transcript` is allowed only after reading that exact native
record. A remembered, inferred, filename-derived, or semantically matched time
is repaired/approximate even when written as a timezone-aware ISO; pass its
honest source and non-exact precision.

If the fresh message has no transcript record, preserve it with an observation
timestamp and explicitly pass both `--timestamp-source turn-context` and
`--timestamp-precision minute` (or `date`). Never present observation time as
source-exact; capture rejects that combination.

### Metadata

Choose metadata by the durable meaning of the thesis, not by incidental nouns
or the current task name. Code validates vocabulary membership, not semantic
correctness; the agent must make and check the semantic choice before writing.
Run `python3 "${CLAUDE_SKILL_DIR}/scripts/chat_capture.py" --list-metadata` when
the vocabulary is unclear.

Classify the speech act, not its sentence form:

- An explicit repair of prior understanding, decision, or action is
  `коррекция`, even when it also establishes a new state.
- A condition for judging good, ready, successful, or feasible is `критерий`.
- An adopted durable course or state is `решение`; an unadopted possibility is
  `идея`.
- A stable taste or cross-task expectation is `предпочтение`; stable personal
  or workflow context is `обо-мне`.
- A reusable instruction awaiting promotion to its owner is
  `правило-кандидат`.
- A factual assertion with no stronger speech act is `факт`; this records what
  the owner asserted and does not independently verify truth.

Topic is one broad retrieval owner:

- `цели-и-приоритеты` — purpose, outcomes, priorities.
- `границы-и-объём` — scope, red lines, intentional exclusions.
- `продукт-и-ценность` — product behavior, offer, value.
- `пользователи-и-потребности` — audiences, needs, pains, scenarios.
- `бизнес-и-монетизация` — business model, prices, sales, economics.
- `бренд-и-коммуникация` — positioning, voice, external communication.
- `контент-и-редактура` — copy, media, publishing, editorial decisions.
- `дизайн-и-опыт` — visual language, interface, experience.
- `исследования-и-источники` — research, provenance, evidence, citations.
- `данные-и-аналитика` — data, metrics, calculations, interpretation.
- `архитектура-и-модель` — system structure, domain model, relationships.
- `код-и-реализация` — code behavior, API, technical implementation.
- `инструменты-и-автоматизация` — CLI, applications, automated flows.
- `агенты-и-ии` — models, agents, prompts, agentic behavior.
- `работа-и-процессы` — workflow, coordination, order, work habits.
- `документация-и-знания` — documents, memory, navigation, owner truth.
- `качество-и-проверка` — acceptance, review, tests, done criteria.
- `безопасность-и-доступ` — secrets, permissions, privacy, acceptable risk.
- `операции-и-инфраструктура` — environments, services, deployment, operation.
- `обо-мне-и-предпочтения` — personal context, taste, stable expectations.

When several topics fit, choose the owner most likely to retrieve the thesis
later; do not mint a narrower label. Use `работа-и-процессы` for how work is
organized, `инструменты-и-автоматизация` for the tool or automated flow itself,
`документация-и-знания` for document authority/navigation, and
`архитектура-и-модель` for system entities and relationships. `неопределено`
and `без-темы` are independent repair-only sentinels; either requires
`--kind note` when adding a repair note and neither is a fallback for fresh
quotes.

## Corpus retrieval

When recorded owner evidence can change the current work, or for an explicit
quote search or harvest, use the project-local corpus by default and establish
the runtime-specific variables:

```bash
DIGEST="${CLAUDE_SKILL_DIR}/scripts/chat_digest.py"
RECALL_DIR="$PWD/_ops/chat-recall"
```

Then follow
[`references/reading-the-log.md`](references/reading-the-log.md), which owns
`check`, inventory, local hybrid/lexical retrieval, filters, timeline, `show`,
bounded output, evidence weighting, and abstention. Its rows and scores are
intermediate state; finish with the controller packet above.

## Repair

Historical search outside the live session is allowed only to repair an
already-existing recall record. Follow
[`references/repairing-the-log.md`](references/repairing-the-log.md).

In a read-only task, show the repair backlog. In a mutation-authorized task,
repair it session-by-session, use exact only after native text/choice
verification, and explicitly mark unresolved metadata.

## Boundaries and stop

- `chat_digest.py` owns `_ops/chat-recall` retrieval; generic Markdown search
  does not replace it. Screen history is not native transcript evidence.
- Do not send quotes or transcript evidence to network tools, import quotes from
  unrelated chats, or promote the dated log to current canon.
- If the answer stops at a quote dump, declares a top hit current without the
  gate, or repeats the quote in `context-note`, shaping failed: return to the
  last unchecked condition instead of widening output.
- Stop after fresh durable theses are captured or a material bounded fork has
  decision-ready context or an explicit abstention, with provenance,
  diagnostics, and material gaps visible.

The design hypothesis is dated 2026-08-04 for Claude Opus 5 and Claude Fable 5.
A change to the working model set, or matched cases where the bare command
“find and read quotes” yields the same decision and evidence, reopens the
mechanism for simplification.
