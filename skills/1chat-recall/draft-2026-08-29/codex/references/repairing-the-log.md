# Repairing and backfilling recall

## Protocol

1. Admit only an existing record with diagnostics/doubtful provenance, an
   explicit structural-validation request, or an explicit owner request to
   restore useful pre-capture statements. A current-session duplicate is not
   Repair: return to the body router and run Capture for metadata correction.
2. Name one project and one specific session or bounded session set before
   reading; never guess a neighboring chat or import unrelated conversations.
3. Reapply the usefulness gate to every source message: preserve only a thesis
   that can change a future decision, boundary, criterion, preference, or
   understanding outside neighboring messages, never the whole transcript.
4. Resolve evidence in this order: named native transcript → exact unique local
   fragment → bounded local semantic/manual search for the exact native record
   → explicit gap. Semantic similarity, filename, frontmatter, raw time, or
   `unknown` alone never authorize capture.
5. Read Codex transcript evidence with separate commands; put
   `--repair-session` before the subcommand for a non-current session:

   ```bash
   ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"
   SESSION="<canonical session UUID>"

   python3 "$ROOT/scripts/chat_recall.py" --repair-session "$SESSION" \
     read --scope user --limit all
   python3 "$ROOT/scripts/chat_recall.py" --repair-session "$SESSION" \
     search "<exact fragment>" --scope user --limit 20
   python3 "$ROOT/scripts/chat_recall.py" --repair-session "$SESSION" \
     show "<record id>"
   ```

6. Preserve literal owner speech as `quote`, an owner-selected option as
   `selection`, agent explanation as `note`, and malformed structure as `raw`.
   Use one semantic type; only unrecoverable Repair metadata may use
   `неопределено` or `без-темы`, and existing owner evidence never becomes a
   note to obtain a sentinel.
7. Preserve the source timestamp, not repair time. Use `exact` only after native
   text/selection verification, otherwise `minute` or `date`; `unknown` is only
   valid for `note`. Holder filename/frontmatter/heading follow the earliest
   `exact|minute` source date, while `date` precision never moves the holder.
8. Supply the same searchable metadata as fresh Capture: a non-paraphrasing
   `context-note` for each quote, the complete non-truth `session-context`, one
   type/topic, project, agent, source timestamp, and source session. Write via
   `chat_capture.py`; add only applicable `--kind`, `--supersedes`, or
   `--contested`:

   ```bash
   python3 "$ROOT/scripts/chat_capture.py" \
     --quote "<source text>" --context-note "<missing source context>" \
     --session-context "<tasks; artifacts; operations; names and synonyms>" \
     --source-timestamp "<native timestamp>" --type <type> --topic <topic> \
     --agent codex --project "<project root>" --session "$SESSION" --json
   ```

9. In read-only work, report the backlog without mutation. When mutation is
   authorized, first preserve checksums and untracked backups outside the
   scanned corpus; merge duplicate holders only within one project and session.
10. Run structural validation and prove that prior text/raw-block multisets did
    not shrink, new quotes exist in native sources, timestamps/sessions remain
    honest, every record opens by exact address, diagnostics remain visible or
    are fixed, and each project has at most one holder per session:

    ```bash
    python3 "$ROOT/scripts/chat_digest.py" \
      "<project root>/_ops/chat-recall" --check --strict
    ```

11. Report restored signal and exact record addresses plus provenance,
    chronology, structure proof, unresolved diagnostics, or the precise blocker.
