# Account-backed Antigravity runtime

Open this file when authentication, model routing, resume, permissions, or CLI
output fails.

The owner route is the official Antigravity CLI authenticated through the OS
keyring. `modelProvider: null` in
`~/.gemini/antigravity-cli/settings.json` is compatible with that account
route. `modelProvider: gemini` selects the separate Gemini API-key route and is
rejected by the wrapper. Gemini and Google API environment variables are
removed from the child process so they cannot silently change billing or data
handling.

The wrapper launches the signed `agy` binary directly, without a shell. It
does not read or reuse Google OAuth tokens and does not call an Antigravity
private backend. This narrow boundary matters because Antigravity's terms
restrict third-party access while the official headless documentation also
supports scripts and CI; the combination is not expressly clarified for every
third-party orchestrator.

Plan mode is not a hard filesystem sandbox: Antigravity headless permissions
may auto-allow workspace reads and writes. The wrapper therefore runs every
call in a disposable directory and never makes the source project its
workspace. It forwards only a minimal environment, rejects every tool event in
text mode, and permits only the exact staged-file `view_file` in media mode.
This is fail-closed result acceptance, not an OS-level guarantee that the
same-user `agy` process cannot open a known absolute source-project path.

Headless calls disable slash-command and skill expansion. The 2026-08-27 live A/B
reduced a one-line text probe from 15,574 to 6,632 upstream input tokens. Do
not combine that flag with `--mode plan`: Antigravity 1.1.22 reports that plan
mode has no effect when expansion is disabled. Safety is owned by the
disposable workspace, sandbox and zero-tool text result contract instead.

`--log-file` is redirected into the temporary execution project, but Antigravity
still stores conversation databases and metadata under its account state and
may retain interactions remotely. Staged-file deletion is not conversation
deletion. Do not delete undocumented Antigravity databases manually; use a
future official conversation-deletion surface if Google provides one.

The result keeps Antigravity's `duration_seconds` and token `usage` as reported
evidence, not wrapper measurements. The wrapper adds monotonic
`wrapper_elapsed_seconds` and labels the upstream duration source. Official
docs do not define whether resumed `usage` is turn-only or conversation-wide,
so `usage_scope` preserves that uncertainty instead of guessing.

## Updating the runtime

Run `agy update`, then verify `agy --version` and `agy models`. The executable
version is authoritative: self-update can leave it inside a Homebrew cask path
whose directory still names an older release. Keep the default Pro model while
it remains available; a higher Flash version number alone is not grounds to
change the advisor model. Run a fresh wrapper call and a resume after updating.
Audio also needs FFmpeg with `libx264` and AAC support.

Checked 2026-09-22: `agy update` reports 1.2.8 as latest; `agy models` still
includes `gemini-3.1-pro-high`. Installation/auth and headless docs rechecked.
Other source observations below remain dated 2026-08-27:


- [install and keyring authentication](https://antigravity.google/docs/cli/install/)
- [headless events and resume](https://antigravity.google/docs/cli/headless/)
- [modes](https://antigravity.google/docs/cli/modes/)
- [permissions](https://antigravity.google/docs/cli/permissions/)
- [conversations](https://antigravity.google/docs/cli/conversations/)
- [models](https://antigravity.google/docs/models/)
- [terms](https://antigravity.google/terms)
