# Codex Helper-Path Overlay

This directory owns a narrow repair for helper commands in three externally
installed Codex packages:

- `1impeccable`;
- `1python-dev`;
- `1diagnosing-bugs`.

The live packages under the supplied Codex skills root remain external/upstream
owners. This overlay is not a package mirror or a second source tree. It records
only the exact path repair needed while no tracked package owner exists in this
repository.

From the repository root:

```bash
skills/codex-overlays/helper-paths/repair-helper-paths.sh \
  --root "${CODEX_HOME:-$HOME/.codex}/skills" \
  --check
```

`--check` is read-only and exits `1` when a known pre-fix form remains. Apply
only the known repair with:

```bash
skills/codex-overlays/helper-paths/repair-helper-paths.sh \
  --root "${CODEX_HOME:-$HOME/.codex}/skills" \
  --apply
```

The helper validates every expected block before writing. It accepts only the
known pre-fix or repaired form, preserves existing file modes, is idempotent,
and exits `3` without writes when target text has drifted. Rebase this overlay
deliberately if upstream changes any guarded block; do not import whole packages
here to make the check green.
