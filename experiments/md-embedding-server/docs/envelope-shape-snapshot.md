# Envelope Shape Snapshot

Generated from live `md_ping` MCP response on 2026-05-22.

## Top-level `_envelope` fields

| Field | Observed type | Notes |
|---|---|---|
| version | number | present |
| tool | string | present |
| corpus_root | null | present |
| corpus_state | null | present |
| lock | null | present |
| cost | object | present |
| size_estimate | object | present |
| next_step | array | present |

## Observed Sample

```json
{
  "_envelope": {
    "version": 1,
    "tool": "md_ping",
    "corpus_root": null,
    "corpus_state": null,
    "lock": null,
    "cost": {
      "turn_usd": "__VOLATILE__",
      "session_usd": "__VOLATILE__"
    },
    "size_estimate": {
      "bytes": 319,
      "items_returned": 0
    },
    "next_step": []
  }
}
```

## Immutable Contract

- CLI refactor must preserve these field names and nullable structure.
- Volatile values are allowed to differ; field presence and type are not.
- Stricter CLI transaction safety may change `next_step` directive contents, but not the envelope field shape.