# Wave-2 repair runtime receipt

Дата: `2026-08-21`.

Статус: `diagnostic-only`; stock acceptance по-прежнему заблокирован тем же
несовместимым `include_integrity` между bundled VikingBot и опубликованным
`openviking-sdk==0.1.8`. V2 запускался тем же ignored disposable shim, что и
v1. Shim не tracked и не является доказательством stock route.

## Frozen inputs and separation from V1

- Source URI: `viking://resources/chat-recall-pilot`.
- Frozen inventory: `182` holders, pilot selection `6`, inventory SHA
  `490171eae7376460a45f18fb947e4d4f6784b35db10aa8146695fc6f0448ec2e`.
- Official Skill URI: `viking://agent/skills/llm-wiki`.
- V1 target remained
  `viking://resources/chat-recall-wiki`; V2 target is new:
  `viking://resources/chat-recall-wiki-v2-repair`.
- V1 local tree SHA before and after V2 export:
  `483b204ef333326094d2fa04371582e633229f866a0b35e1d1a678f6cde29ff5`.
- V2 export is separate under `artifacts/wiki-v2/`.

## Exact compile request

The same server command and ignored compatibility shim from v1 were used. The
request body was sent to `POST /bot/v1/compile`:

```json
{
  "from": ["viking://resources/chat-recall-pilot"],
  "to": "viking://resources/chat-recall-wiki-v2-repair",
  "skill": "viking://agent/skills/llm-wiki",
  "reason": "Wave-2 repair only. Merge semantically equivalent owner statements into one canonical retrieval page instead of per-source retellings. For every recurring position, state the exact count of distinct source records, earliest and latest dated occurrence with source links, current formulation, and any change or contradiction. Create a dedicated page for the OpenViking chat-recall knowledge-library outcome and its boundaries because the source holder contains it. Preserve provenance; if evidence is insufficient, say so rather than infer. Use stock English Wiki behavior; no prompt/Skill fork, no ontology fork, no full backfill.",
  "runtime_timeout_seconds": 900
}
```

Reason SHA-256 (without trailing newline):
`637741113a6464239f3e61d5db6a9fbfe7d3a4c687a5ce5d2571864dda0925ab`.

Accepted response:

```json
{"status":"ok","result":{"task_id":"cmp_cc9abd10702e4104becab28e7b0a25b4","status":"accepted","to":"viking://resources/chat-recall-wiki-v2-repair"}}
```

Terminal receipt:

```json
{
  "task_id": "cmp_cc9abd10702e4104becab28e7b0a25b4",
  "status": "completed",
  "stage": "completed",
  "created_at": "2026-08-21T10:47:46.424341Z",
  "updated_at": "2026-08-21T10:50:08.980397Z",
  "from": ["viking://resources/chat-recall-pilot"],
  "to": "viking://resources/chat-recall-wiki-v2-repair",
  "skill": "viking://agent/skills/llm-wiki",
  "okf_version": "0.1",
  "created": [
    "viking://resources/chat-recall-wiki-v2-repair/concept/Chat recall owner statement canon.md",
    "viking://resources/chat-recall-wiki-v2-repair/concept/OpenViking chat-recall knowledge-library outcome.md",
    "viking://resources/chat-recall-wiki-v2-repair/index.md"
  ],
  "updated": [],
  "unchanged": [],
  "page_count": 3,
  "link_count": 0,
  "warnings": []
}
```

## V2 tree and export

```text
viking://resources/chat-recall-wiki-v2-repair/
├── index.md
└── concept/
    ├── Chat recall owner statement canon.md
    └── OpenViking chat-recall knowledge-library outcome.md
```

The verbatim URI tree is in `artifacts/wiki-v2-tree.txt` with SHA-256
`8e2c6005409b00b0e3c25a48bc2002cb10959ab981b7814291495eba6a591ae5`.
The three exported pages total `14643` bytes:

- `concept/Chat recall owner statement canon.md` —
  `978bbf63d3e8a2c991652a7a5dfe19805edcbc6668865b0d55c87450fbd8eb2d`.
- `concept/OpenViking chat-recall knowledge-library outcome.md` —
  `73d5adaa5945eae06df17e62b8b0fe8706daeee91858cd6e6c555d5407c95fc3`.
- `index.md` —
  `d1f563a819d3e5b1f737bd66837af145c854defd94437c7f7320abc8ad34ade8`.

## Direct output checks

The checker read the exported pages directly. Results:

- `6` recurring sections found in the canonical page.
- Every section has `Distinct source records`, `Earliest dated occurrence`,
  `Latest dated occurrence`, `Current formulation`, and `Change or
  contradiction` fields.
- Every recurring section has at least one source URI link; total provenance
  links across V2 pages: `34`.
- Reported distinct-record counts by section: `3`, `2`, `2`, `3`, `2`, `4`.
- Dedicated outcome page exists, is linked from `index.md`, contains
  `Boundaries`, explicitly marks insufficient evidence, and contains source
  links.
- V2 pages contain no V1 target URI.

`md check` passes for `README.md` and this receipt. It reports 2 broken links
for the generated V2 `index.md` because the runtime writes `%20` for spaces in
relative links while the local checker matches physical names without URL
decoding. The runtime-generated pages were not rewritten; link usability stays
an audit gap.

These are direct field/provenance checks, not a semantic audit of whether each
model-generated count is correct against all holder records. The v2 canonical
page itself says where evidence is thin; no full-corpus or matched retrieval
claim is made.

## Remaining gaps

- Stock Compile still needs an upstream-compatible SDK/bot package; the shim
  must not be promoted to acceptance.
- The six counts and first/latest chronology still need the locked manual audit
  and matched retrieval comparison from the reviewer contract.
- Compile metadata reports `link_count=0`; the exported index contains encoded
  relative links, but link usability remains an audit item.
- This remains a six-holder diagnostic pilot; no full backfill, Graphiti change,
  prompt/Skill fork, ontology fork or source-holder edit was performed.
