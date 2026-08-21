# OpenViking Wiki pilot for `chat-recall`

This directory contains the first, representative runtime pilot setup and its
receipts. It is a derived experiment: `_ops/chat-recall/` remains the immutable
source evidence; the ignored `.runtime/` tree is disposable staging and runtime
state.

The pilot is intentionally smaller than the full holder corpus. Its stock
acceptance gate is explicit: pinned OpenViking plus the pinned upstream LLM Wiki
Skill must import a frozen representative set and compile a navigable Wiki
without a local compatibility patch. The current receipt records that stock
compile is blocked by a packaged SDK mismatch; `artifacts/wiki/` is retained as
non-stock diagnostic output only.

## Scope

- OpenViking `0.4.16`, pinned to upstream tag commit
  `499995f3ed2e7f551a715179c4053772c51ff819`, AGPL-3.0.
- Official `examples/compile/ov-compile-skills/llm-wiki/SKILL.md` from that tag.
- Local-only resource and output roots; no watcher, WebDAV, realtime capture,
  Graphiti ingest, prompt fork, or external publication.
- Russian source questions/answers are allowed; the stock Wiki output follows
  the upstream skill's language behavior.

## Re-run

The exact commands and their terminal receipts live in
`artifacts/receipt.md`; the machine-readable version/source inventory is in
`artifacts/runtime-inventory.json`.
The deterministic inventory and pilot selection are produced by:

```bash
uv run --locked --project . python scripts/build_inventory.py \
  --source-dir ../../_ops/chat-recall \
  --inventory artifacts/source-inventory.json \
  --selection artifacts/pilot-selection.json \
  --stage-dir .runtime/pilot-source
```

The stock compile command and its failed response are recorded in the receipt.
A clean checkout must provide the required local LLM configuration; secrets
never belong in this directory or its receipt.

## V1 and V2 diagnostic outputs

- V1: `artifacts/wiki/`, target URI
  `viking://resources/chat-recall-wiki`, receipt `artifacts/receipt.md`.
- V2 repair: `artifacts/wiki-v2/`, target URI
  `viking://resources/chat-recall-wiki-v2-repair`, receipt
  `artifacts/v2-receipt.md`, delta `artifacts/v2-delta.json`.
- Both exports are diagnostic only: the stock gate remains blocked by the
  pinned package's SDK mismatch, and V2 is a separate target rather than a
  rewrite of V1.

## Evidence boundary

`artifacts/` is the committed, human-readable pilot evidence and the explicitly
labelled diagnostic Wiki tree. `.runtime/` and `.venv/` are ignored. A
successful command or a smooth generated page is not a pilot verdict:
recurrence, chronology, provenance and matched retrieval are later audit work,
and stock acceptance remains blocked until the SDK mismatch is resolved without
a local shim.
