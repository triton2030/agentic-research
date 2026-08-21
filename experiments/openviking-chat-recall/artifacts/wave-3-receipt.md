# Wave-3 typed-evidence probe receipt

Дата: `2026-08-21`.

Статус: `candidate; overall probe not accepted`.

Writer сделал deterministic evidence seam и один offline diagnostic projection.
Semantic acceptance выполняет отдельный blind reader; stock runtime gate не
пройден и full corpus остаётся заблокирован.

## Frozen source provenance

Оба кластера читаются только из Git objects, не из текущего live holder:

| Cluster | Frozen ref | SHA-256 | Records | First | Latest |
| --- | --- | --- | ---: | --- | --- |
| A — retrieval aid is not proof | `6d392ae^:_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md` | `501cad60b995a15ce2382ea1c4f264f4c3f22a0e1450dda2fbe4d891c58016ff` | 4 | `2026-08-14T07:45:46.732000+00:00` | `2026-08-17T17:46:29+05:00` |
| B — current OpenViking outcome | `6d392ae^:_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md` | `c92addebb7e56454bb848a935f2bdfe6408f9b6949248c1ca56dd06ec0502443` | 5 | `2026-08-21T13:31:52+05:00` | `2026-08-21T14:44:26+05:00` |

The current live B holder is a different blob (`a9200dc7c80fc4be084cc85ab004c029e5ebdddb53a353c267b178f00ada2732`); it was not used. The manifest records the historical Git ref and the frozen SHA explicitly.

Verification command:

```bash
git show 6d392ae^:_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md | sha256sum
git show 6d392ae^:_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md | sha256sum
```

Terminal evidence:

```text
c92addebb7e56454bb848a935f2bdfe6408f9b6949248c1ca56dd06ec0502443  -
501cad60b995a15ce2382ea1c4f264f4c3f22a0e1450dda2fbe4d891c58016ff  -
```

## Deterministic evidence seam

Owner: `scripts/build_typed_probe.py`. The existing `scripts/build_inventory.py`
was not changed.

Command:

```bash
cd experiments/openviking-chat-recall
uv run --locked --project . python scripts/build_typed_probe.py \
  --manifest artifacts/typed-gold-manifest.json \
  --output-dir artifacts/typed-input
```

Terminal evidence:

```json
{
  "provenance_commit": "6d392ae^",
  "clusters": [
    {"id": "cluster-a-retrieval-aid-not-proof", "record_count": 4, "first": "2026-08-14T07:45:46.732000+00:00", "latest": "2026-08-17T17:46:29+05:00", "source_sha256": "501cad60b995a15ce2382ea1c4f264f4c3f22a0e1450dda2fbe4d891c58016ff"},
    {"id": "cluster-b-openviking-outcome", "record_count": 5, "first": "2026-08-21T13:31:52+05:00", "latest": "2026-08-21T14:44:26+05:00", "source_sha256": "c92addebb7e56454bb848a935f2bdfe6408f9b6949248c1ca56dd06ec0502443"}
  ],
  "schema": "openviking-chat-recall/typed-build-receipt.v1"
}
```

Focused tests:

```bash
cd experiments/openviking-chat-recall
uv run --locked --project . python -m unittest discover \
  -s tests -v
```

Result: `Ran 5 tests ... OK`.

The tests fail closed on source SHA drift and record quote drift, and cover exact
membership, count, first/latest chronology, frozen provenance refs and
byte-identical output.

Markdown structural checks:

```bash
cd experiments/openviking-chat-recall
md check --paths artifacts/typed-input --json
md check --paths artifacts/wiki-offline-diagnostic --json
```

Both returned `targets: 3` and `issues: []`.

## Stock runtime/package availability

The pinned runtime was started from the existing local config:

```bash
OPENVIKING_PILOT_ROOT="$PWD" OPENVIKING_CONFIG_FILE="$PWD/config/ov.conf" \
uv run --locked --project . openviking-server \
  --config "$PWD/config/ov.conf" --host 127.0.0.1 --port 19331 \
  --with-bot --bot-port 18791
```

Health evidence:

```json
{"status":"ok","healthy":true,"version":"0.4.16","auth_mode":"dev"}
```

The typed resource import used the official SDK `add_resource` call with
`artifacts/typed-input` and target
`viking://resources/chat-recall-typed-probe`. The direct post-import tree had
three Markdown leaves (`index.md`, one page per cluster) and OpenViking's parser
directories; no live holder or full corpus was imported.

The official upstream Skill was fetched from:

`https://raw.githubusercontent.com/volcengine/OpenViking/v0.4.16/examples/compile/ov-compile-skills/llm-wiki/SKILL.md`

Its verified SHA-256 was
`c5e379843a0af6c4574f29ae8fd6637b2b89a0481da63a76472188633f4792de`.

The first SDK `add_skill()` attempt failed locally because pinned
`openviking-sdk==0.1.8` treats the inline Skill string as a filesystem path and
raises `OSError: [Errno 63] File name too long`. A direct stock HTTP POST of the
same verified Skill body to `/api/v1/skills` was accepted at
`viking://agent/skills/llm-wiki`; this proves the endpoint can accept the body,
not that the SDK/server/Compile surface is coherent.

The one direct stock Compile request was:

```bash
curl --silent --show-error --include --request POST \
  http://127.0.0.1:19331/bot/v1/compile \
  --header 'content-type: application/json' \
  --data-binary @- <<'JSON'
{
  "from": ["viking://resources/chat-recall-typed-probe"],
  "to": "viking://resources/chat-recall-typed-wiki-stock",
  "skill": "viking://agent/skills/llm-wiki",
  "reason": "Wave-3 typed-evidence probe only. Compile the two deterministic typed evidence clusters into an evidence-grounded English LLM Wiki. Treat exact record count, membership, first/latest timestamps, source SHA and Git provenance as deterministic gold facts; preserve all exact owner quotes and do not recalculate or replace those facts. Preserve the five current OpenViking outcome obligations and the retrieval-aid-not-proof boundary, with provenance and uncertainty. Use only the supplied typed input; do not read live holders, backfill the corpus, or invent unsupported claims. Use the stock official LLM Wiki Skill and IA.",
  "runtime_timeout_seconds": 900
}
JSON
```

Exact response:

```text
HTTP/1.1 400 Bad Request
{"status":"error","result":null,"error":{"code":"INVALID_ARGUMENT","message":"AsyncHTTPClient.get_skill() got an unexpected keyword argument 'include_integrity'","details":{}},"telemetry":null,"profile":null}
```

This is a stock failure. No compatibility shim was retained or used for a
diagnostic runtime compile after the owner correction; no stock pass is claimed.

## One offline diagnostic transformation

Because the official Skill text was fetched and SHA-verified, one offline
diagnostic page set was produced using its index/page-type/provenance IA over the
typed input. It tests prompt/IA usefulness only; it is not an OpenViking runtime
export and has no semantic acceptance verdict.

Tree:

```text
offline-diagnostic://typed-evidence-wiki/
├── index.md
└── concept/
    ├── OpenViking chat-recall knowledge-library outcome.md
    └── Retrieval aid is not proof.md
```

The pages preserve exact count, first/latest, SHA, frozen Git refs and the exact
owner records for both clusters. The separate blind reader must still check
outcome recovery, recurrence, provenance and no-gold abstention.

Direct gold-field check (not a semantic acceptance):

```text
{"offline_gold_checks":[{"id":"cluster-a-retrieval-aid-not-proof","gold_fields":9,"missing":0},{"id":"cluster-b-openviking-outcome","gold_fields":10,"missing":0}]}
```

## Revised mental model and remaining gate

The observed runtime evidence falsifies the model that PyPI SDK, bundled server,
VikingBot and current Compile calls form one coherent stock product surface. The
three claims must remain separate:

1. **Deterministic evidence seam — measured pass.** Frozen Git blobs, exact record
   membership, count, chronology, provenance and typed Markdown output are
   reproducible and test-covered.
2. **Official prompt/IA diagnostic — produced, not accepted.** The offline Wiki
   applies the official LLM Wiki page model, but a blind reader must decide
   whether it preserves the current outcome without inversion.
3. **Stock runtime/package availability — blocked.** Health and resource import
   work, but stock Compile fails with the `include_integrity` SDK/VikingBot
   mismatch; this is not a stock acceptance.

No full corpus, general wrapper, source-holder edit, plan edit, global skill edit,
or upstream edit was made. Full backfill remains blocked until the blind-reader
Gate and a coherent stock Compile route are independently resolved.
