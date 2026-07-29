# Reading the recall log

`chat_digest.py` is the only retrieval owner. It treats every Markdown
star-block as a record. Metadata diagnostics never remove a record from
inventory, search, timeline, or `show`.

## Bounded route

Before opening this route, the runtime-specific root `SKILL.md` sets `DIGEST` to
its installed `scripts/chat_digest.py`. This shared reference never assumes a
Claude- or Codex-specific environment variable.

```bash
RECALL_DIR="<project>/_ops/chat-recall"

python3 "$DIGEST" "$RECALL_DIR" --check
python3 "$DIGEST" "$RECALL_DIR"
python3 "$DIGEST" "$RECALL_DIR" --query "субагент* параллел*" \
  --limit 12 --max-chars 8000
python3 "$DIGEST" "$RECALL_DIR" --show <record-id>
```

The default command is a cheap topics/types/period inventory. `--query` builds
an in-memory SQLite FTS5 index with one record per document and BM25 ranking.
The record text has normal weight; `topic` has a small boost. Add original
terms, synonyms, and explicit Russian prefix forms such as `субагент*`.
Automatic lemmatization is intentionally absent.

Filters remain metadata, not query text:

```bash
python3 "$DIGEST" "$RECALL_DIR" --query "память контекст" \
  --type коррекция,правило-кандидат --agent <agent> --since 2026-07-01
python3 "$DIGEST" "$RECALL_DIR" --timeline --session <uuid>
```

Supported filters are `--type`, `--topic`, `--grep`, `--since`, `--until`,
`--agent`, and `--session`. `--limit 12` and `--max-chars 8000` are bounded
defaults. `--json` returns `total`, `matched`, `returned`, `truncated`,
`selection`, quality counts, warnings, and records.

`selection=none` is a valid abstention, not a failure. A timeline orders known
timestamps, then isolates unknown records; chronology alone never means
“current truth”. Use `--show` for the complete text, provenance, address, and
diagnostics of one stable `record_id`.

## Diagnostics

`--check` reports repair backlog but exits successfully so records remain
readable. `--check --strict` is the validation gate and exits non-zero while
diagnostics remain. Repair procedure and evidence rules live only in
[`repairing-the-log.md`](repairing-the-log.md).
