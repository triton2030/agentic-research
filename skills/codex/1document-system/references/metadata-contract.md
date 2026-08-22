# Metadata Contract

Metadata routes retrieval and authority; it is not a questionnaire. A live
local metadata contract wins wholesale — do not normalize a local schema back
to these defaults.

## Core (fallback)

Seven fields for `canon/` files and typed artifacts in `_ops/`:

```yaml
---
artifact-id: mavo-prd-personalization
description: Определяет продуктовые требования управляемой персонализации.
artifact-type: prd
authority: canon
artifact-scope-key: personalization
status: active
approved: false
---
```

- `artifact-id`: readable immutable kebab-case; move/rename never changes it;
  a historical collision gets a suffix, an old ID is never reused.
- `artifact-type`: lowercase code from catalog or local registry; the filename
  keeps the uppercase display code.
- `authority`: `evidence | decision | canon | projection | ops`.
- `artifact-scope-key`: stable logical scope, instance-specific for plural
  types (`checkout-tax`, not `project`).
- `status`: `draft | active | superseded | archived`.
- `approved`: the user's personal mark, not an authority gate.

One active canon artifact per `artifact-type + artifact-scope-key`.

## Description as retrieval surface

The phrase must let an agent pick this file among neighbors before reading the
body: information job + bounded scope + the near-miss difference when a
collision is possible. Understandable without filename and headings. No TODO,
no title repetition, no table of contents, no full summary. `1md-search`
indexes it separately — an empty or vague description is a retrieval defect,
not cosmetics. If a local contract forbids the field, use only its named
alternative label; without one, record `retrieval-label-unavailable` — do not
invent fields.

## Conditional fields

Only with a real function: `workflow-state` (type state, separate from file
lifecycle) · `depends-on` (hard invalidation edge holder → source; quoted
wikilink `"[[path#Heading]]"`) · `derived-from` (lineage, no update
obligation) · `supersedes` · `owner` (only when change rights actually
differ). Do not hand-maintain reverse dependents, paths, dates, validation
results or `last-reviewed` — unless a local contract gives them a live
function.

## Approval

A clear positive user reply is approval only when it unambiguously refers to
the current artifact — praise about the process does not transfer. Any
semantic edit resets `approved: false`; formatting and typo repair do not.

## Zones and adapters

In `canon/` metadata is required. Decision/change artifacts live in `_ops/`
and update the canon owner on acceptance. Projections need retrieval label +
lineage; full schema optional. A strict scanner (md-tools) validates its own
runtime profile, not this ontology: `UNKNOWN_FIELD` means a missing runtime
profile, not a semantic ban — record `runtime-schema-mismatch`, do not delete
needed fields or claim validation success.
