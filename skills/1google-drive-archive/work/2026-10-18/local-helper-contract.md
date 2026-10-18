# Local archive verifier reference

Python 3 standard library only. No network, auth, cloud mutations, or source
deletion. Only a helper-created temporary output is removed after publication.

```sh
python3 archive_verify.py hash --path /absolute/source --out /new/local.json
python3 archive_verify.py compare --local /new/local.json --before /probe-before.json --after /probe-after.json --out /new/result.json
python3 archive_verify.py --help
python3 -m unittest -v test_archive_verify.py
```

Reports must have new paths: existing output names, symlinks, source aliases,
and input paths cannot be overwritten. Publication uses a private mode-0600
sibling temporary file and atomic no-clobber hardlink. Normal stdout is empty;
`--help` prints static usage. Stderr contains only fixed error codes. Exit 0
means `LOCAL_HASHED` for hash or `MATCH_SHA256` for compare; exit 2 means refusal,
`UNVERIFIED`, or `CANDIDATE_DIFFERS`. A failed hash produces no local record.

Remote input is exactly one JSON object with these keys, no extras or duplicates:

```json
{"schemaVersion":1,"checkedAt":"2026-10-18T12:00:00.000000Z","accountKey":"opaquePermissionId","fileId":"opaqueFileId","size":"123","sha256Checksum":null,"md5Checksum":null,"version":"1","trashed":false,"binaryFile":true,"canDownload":null,"ownedByMe":null}
```

`accountKey` is the authenticated Drive permissionId, never an email or token.
Both IDs must match `[A-Za-z0-9_-]{1,256}`. Size and version are canonical decimal
strings (at most 25 digits); version may be null. SHA256/MD5 are 64/32 hex digits
or null. `trashed`, `canDownload`, and `ownedByMe` are boolean or null;
`binaryFile` is boolean. UTC timestamps accept `Z` or `+00:00`, with optional
1–6 fractional second digits. Malformed, duplicate, extra, oversized (>1 MiB),
unreadable, or changing JSON inputs cannot prove equality.

Local record schemaVersion=1, kind=`local-hash`, status=`LOCAL_HASHED` contains
`startedAt`, `finishedAt`, absolute `sourcePath`, `bytesRead`, `sha256`, `md5`,
`deleteAllowed=false`, and `fstatBefore`, `fstatAfter`, `pathBefore`, `pathAfter`.
Each stat snapshot has integer `device`, `inode`, `size`, `mtime_ns`, `ctime_ns`;
path snapshots additionally contain `realPath`. Hash reads a nonempty regular
file once, with SHA256+MD5 updated from each same chunk. A final-component
symlink is refused and open uses O_NOFOLLOW. Parent-directory aliases such as
macOS `/tmp` are allowed; resolved paths are checked for stability. Snapshots
must agree before/after and the actual bytes read must equal the recorded size.

Comparison requires matching accountKey/fileId, binary and non-trashed metadata,
unchanged non-null version, unchanged size, and SHA256 before/after matching
the stable local record. Its interval must satisfy
`before.checkedAt < local.startedAt <= local.finishedAt < after.checkedAt`.
Missing SHA256 never falls back to MD5. A supplied MD5 contradicting matching
SHA256 causes refusal. Unknown/false access flags do not block equality but
yield `restoreAccessConfirmed=false`; true requires both flags true in both
probes. This flag only describes the supplied observations, not a tested restore.

Comparison output contains schemaVersion, kind, evaluatedAt, evidenceCheckedAt,
evidence, status, reason, deleteAllowed, and restoreAccessConfirmed. Evidence
contains each fully validated remote metadata record (or null if invalid), plus
the local hashes, bytesRead, startedAt, and finishedAt (or null if invalid).
This binds the report to safe accountKey/fileId, size/hash/version, and the
observed time interval. It never includes raw paths, arbitrary input text, or
an invalid record's values. `deleteAllowed` is always false, including
`MATCH_SHA256`.

`evidenceCheckedAt` is the supplied after.checkedAt, or null for an invalid after
record. It dates the historical cloud observation, not the local comparison.
`evaluatedAt` only dates the local evaluation. Re-evaluating old JSON does not
refresh the cloud check or prove the current cloud state.

Fixed comparison reasons:

- `MATCH_SHA256`: `SHA256_SIZE_VERSION_CONFIRMED`.
- `CANDIDATE_DIFFERS`: `SIZE_MISMATCH`, `SHA256_MISMATCH` (stable remote evidence).
- `UNVERIFIED`: `INVALID_LOCAL_RECORD`, `INVALID_REMOTE_BEFORE`,
  `INVALID_REMOTE_AFTER`, `REMOTE_ACCOUNT_CHANGED`, `REMOTE_ID_CHANGED`,
  `TIMESTAMP_ORDER_INVALID`, `LOCAL_READING_UNSTABLE`, `REMOTE_NOT_BINARY`,
  `REMOTE_TRASH_STATE_UNCONFIRMED`, `REMOTE_VERSION_UNAVAILABLE`,
  `REMOTE_SHA256_UNAVAILABLE`, `REMOTE_VERSION_CHANGED`, `REMOTE_SIZE_CHANGED`,
  `REMOTE_SHA256_CHANGED`, `MD5_METADATA_CONFLICT`.

CLI refusal codes: `ARGUMENT_ERROR`, `OUTPUT_IS_INPUT`, `OUTPUT_EXISTS`,
`OUTPUT_PARENT_CHANGED`, `SOURCE_SYMLINK`, `SOURCE_NOT_REGULAR`, `SOURCE_EMPTY`,
`LOCAL_CHANGED_DURING_READ`, `IO_ERROR`, `INTERNAL_ERROR`.

Limits: supplied records are not signed or authenticated by this helper. The
caller must use genuine authorized metadata probes, trusted local reports,
and a trustworthy clock. It checks a candidate's bytes, not which candidate the
owner intended. Snapshots cannot detect every adversarial transient mutation
that restores all observable state, and do not lock files after hashing. A later
local or cloud change invalidates the practical relevance of the result. It
does not implement a deletion plan, backup, media decoding, or a restore test.
Atomic publication requires a local filesystem supporting hardlinks; failure
is a fixed refusal, never an overwrite fallback. It fsyncs file data before
publication but does not claim power-loss durability of the directory entry.

## Verification

Date: 2026-10-18. Status: confirmed. Source:
`python3 -m unittest -v test_archive_verify.py` with local Python 3.14.7.
All 28 tests passed. They use only synthetic temporary content and cover stable
SHA256 matching, strict metadata/identity validation, mutation and replacement
during real reads, symlink refusal, interval ordering, historical time labels,
no MD5 fallback, access uncertainty, no-clobber races, and secret redaction.
No real media, cloud endpoint, restore, or deletion was tested.
