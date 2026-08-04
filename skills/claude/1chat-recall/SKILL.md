---
name: 1chat-recall
description: >
  Use when durable owner evidence appears in the current Claude session,
  existing owner evidence may materially change a current decision, the user
  asks what they said, or a recall record needs repair. Capture and read
  source-bound evidence in `_ops/chat-recall`: keep the owner's wording, but
  shorten quotes by deletion only — never paraphrase, never hide malformed
  text.
allowed-tools: Bash(python3 *), Bash(uv *), Read, Grep, Glob
---

# Chat recall

## Invariant

Source-bound owner evidence is primary. A verbatim quote stays a quote, a Plan
choice stays a selection, and note/raw evidence remains visibly non-verbatim.
A wrong or missing date, type, topic, or format never cancels the record.
Retrieval includes exact, legacy, partial, multiline, and raw records.

The log is dated evidence, not current canon. A later quote may supersede an
earlier one, and an approximate timeline must not be presented as current
truth.

## Router

- Fresh durable owner evidence appeared: capture every independent useful
  thesis in the same turn, one record per meaning. Skip an approval,
  confirmation, or command when its own words do not form durable knowledge.
  Always skip credentials and pasted material that is not the owner's
  position.
- Earlier input or a Plan/AskUserQuestion choice from the current session can
  change a durable result: read current-session evidence.
- A material current decision depends on established goals, boundaries,
  decisions, criteria, corrections, or preferences: read only the recall cluster
  that can change that decision.
- The user explicitly asks what they said, asks to find quotes, or requests a
  recall harvest: use corpus retrieval.
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

When an already useful deletion-only quote still has an unresolved referent,
add `--context-note "<one short agent explanation>"`. It is stored inline in
the same record, remains visibly non-verbatim, and appears through `show`; it
does not participate in the record ID, BM25, or dense ranking. It may only name
the discussed object or situation: it must not add a new conclusion, rationale,
URL, path, or pointer to a transcript/another record. The limit is 300
characters; `--kind note` cannot carry `--context-note`. A context note never
makes a weak quote worth capturing: apply the usefulness gate first, then add
context.

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
quote search or harvest, establish the runtime-specific variables:

```bash
DIGEST="${CLAUDE_SKILL_DIR}/scripts/chat_digest.py"
RECALL_DIR="$PWD/_ops/chat-recall"
```

Then follow
[`references/reading-the-log.md`](references/reading-the-log.md), which owns
`check`, inventory, local hybrid/lexical retrieval, filters, timeline, `show`,
bounded output, and abstention.

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
- Stop after the fresh durable theses are captured or the bounded question is
  answered or explicitly abstained, with provenance and diagnostics visible.
