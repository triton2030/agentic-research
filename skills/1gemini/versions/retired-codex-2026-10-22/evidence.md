# Evidence

Status: accepted 2026-08-19 by root under the owner's explicit end-to-end
implementation authority. Corrected-snapshot audits: excess/structure
`architecture_ok`; provenance/acceptance `pass` with no blocking findings.

Support envelope: Codex GPT-5.6, macOS arm64, Python 3.14, official Google
Antigravity CLI 1.1.22, authenticated owner account, `gemini-3.1-pro-high`,
reasoning high, calls up to 30 minutes.

## Claims and falsifiers

- Account text execution: a fresh wrapper call must return a requested exact
  token, `SUCCESS`, matching model, disposable resolved cwd, conversation ID,
  usage, no attached source workspace, and no forwarded source-path environment.
- Resume: a follow-up using that conversation ID must return a second exact
  token and the same conversation ID.
- Media observation: synthetic video and synthetic audio must each show a
  completed matching `view_file` event on the staged file. Video is staged
  unchanged; audio is staged as a disclosed MP4 carrier. Source SHA-256 must
  match before and after.
- Failure closure: fake-runtime tests must reject mismatch, missing/duplicate
  result, non-success status, permission failure, any unexpected tool, API
  provider, unsupported media, resume identity mismatch, and timeout.
- Packaging: `quick_validate.py` and Python compilation must pass.

No personal archive file is part of the acceptance probe.

## Live observations, 2026-08-19

- Current isolated text: `ISOLATED_TEXT_OK`, conversation
  `22d23ff4-2955-4c47-8068-67234d8d4aa3`, `SUCCESS`, exact model,
  no attached source workspace; resolved temp cwd was deleted.
- Current resume: `ISOLATED_RESUME_OK`, same conversation ID, turn count 2,
  new disposable cwd deleted.
- Current synthetic yellow MP4: completed `view_file`, response `yellow`,
  identical source SHA-256 before/after, disposable cwd deleted.
- Current synthetic repeated spoken word: MP3 was carried as MP4, completed
  `view_file`, response `orchard orchard orchard`, unchanged source SHA-256,
  disposable cwd deleted. An earlier shorter single utterance was misheard as
  `cell`; delivery is proven, perfect ASR is not.
- Unit contract: 13 tests passed. `quick_validate.py`, `py_compile`, and
  `ruff check` passed.
- Fresh Codex discovery: `codex debug prompt-input` listed `1gemini` and the
  narrowed Claude/Hermes sibling boundaries.
- Fresh routing: applicable probe «Попроси Gemini дать второе мнение» returned
  `1gemini`; near-miss «что такое Google Gemini» returned `NONE`.
- Retention boundary: the staged project is deleted and media logs are routed
  into it, but Antigravity conversation DB/WAL and remote interaction retention
  survive that cleanup. The skill discloses this and does not claim ephemeral
  processing or manually delete undocumented state.

## Addressed source observations, checked 2026-08-19

- `cli/install`: account auth is cached in the OS keyring; API-key provider is
  a [separate route](https://antigravity.google/docs/cli/install/).
- `cli/headless`: `-p`, model pin, stream JSON terminal result, conversation ID,
  usage, timeout, and resume are
  [official headless surfaces](https://antigravity.google/docs/cli/headless/).
- `cli/permissions`: active-workspace reads and writes can be auto-allowed;
  `--sandbox` does not establish project read-only. The wrapper therefore uses
  a [disposable workspace](https://antigravity.google/docs/cli/permissions/).
- `cli/prompting`: interactive video attachments list MP4, MOV, WebM, and AVI;
  audio/headless attachment is not documented. Headless media support in this
  package is explicitly live-characterized, not attributed to the
  [prompting page](https://antigravity.google/docs/cli/prompting).
- Terms restrict third-party Antigravity/OAuth access while official headless
  docs support scripts and CI. This package calls only the official binary and
  does not extract OAuth or call private endpoints; the orchestration wording
  remains [legally ambiguous](https://antigravity.google/terms).

## Independent acceptance

- Senior runtime/privacy lens found persistent conversation artifacts; the
  package now discloses them, redirects the ordinary log to temp, and makes no
  ephemeral-processing claim.
- Excess/architecture re-audit: `architecture_ok`, no structural findings.
- Provenance/acceptance re-audit: every P1-P5 and C1-C12 condition passed; no
  blocking findings.

## Current observations, 2026-08-27

- Upgraded the official Homebrew cask from 1.1.15 to 1.1.22; `agy --version`
  and the resolved live wrapper receipt both report 1.1.22.
- Fresh isolated text returned `GEMINI_POST_UPDATE_20260827`, `SUCCESS`, exact
  model, conversation `e94a11d3-73a1-4242-8455-9bf8787d5e52`, and no source
  project exposure.
- Direct synthetic WAV initially produced a matching completed `view_file`
  event and `DIRECT_AUDIO_OK`, but later independent native WAV probes repeatedly
  ended with `Agent execution terminated due to error`.
- Hardened unit contract: 18 tests passed; assertions prove the prompt is
  absent from argv, resume identity is exact, source-path environment is not
  forwarded, unknown tools fail closed, structured nonzero errors survive, and
  audio carrier/transcode failures are explicit.
- A live corpus-review resume reported upstream `duration_seconds: 170.10239`
  while the wrapper process completed in about 53 seconds. Official docs call
  the field run wall-clock time but do not define resume usage scope. The
  wrapper now preserves those upstream values with provenance and adds its own
  monotonic elapsed measurement; focused regression tests fail without both
  labels.
- A one-line live A/B measured 15,574 upstream input tokens on the former text
  route and 6,632 with `--disable-slash-commands` (about 57% less), with the
  same exact-response task. Antigravity warned that `--mode plan` has no effect
  under that flag; the wrapper removed the misleading mode and retains its
  sandbox, disposable cwd and fail-closed zero-tool text acceptance.
- Fresh refactored text returned `LIVE_STDIN_OK`; resume returned
  `LIVE_RESUME_OK` with the same conversation
  `dd5f7a48-5f67-4258-85da-c089309c8e1c` and turn count 2.
- Fresh wrapper-native WAV returned `LIVE_AUDIO_OK`, observed
  `view_file ACTIVE -> DONE`, preserved the source SHA-256, and deleted the
  staged temporary project.
- Hardened text returned `HARDENED_STDIN_OK`; exact resume returned
  `HARDENED_RESUME_OK` on conversation
  `7174d14f-d206-4ee5-b587-e686e6e916cf`. A separate final native WAV returned
  `FINAL_NATIVE_AUDIO_OK`, `SUCCESS`, exact model, and `view_file DONE` on
  conversation `cf89911a-9bdc-4a3a-8030-2bbfca5f60e5`.
- Current isolated A/B: a standalone native WAV failed, while an MP4 carrier
  made from the same 440-Hz source returned `CARRIER_1122_OK`. The final wrapper
  path returned `WRAPPER_CARRIER_1122_OK`, exact model, `view_file DONE`,
  unchanged source SHA-256, and `delivery: audio-mp4-carrier`. Private raw
  receipt: `/Users/triton/.codex/gemini-evidence/media-2026-08-27.json`.
- Private text/resume raw receipt:
  `/Users/triton/.codex/gemini-evidence/text-resume-2026-08-27.json`.
- `py_compile` and `ruff check` passed for the wrapper and contract tests.

## Update verified 2026-09-22

Installed owner: `~/.codex/skills/1gemini`; no tracked owner or Claude
projection was present. Official `agy update` reports 1.2.8 as latest.
FFmpeg upgraded from 9.0.1 to 9.0.2 with its seven Homebrew dependencies;
Homebrew also auto-updated itself from 6.0.19 to 7.0.6 during metadata refresh.
Final `brew outdated --json=v2 ffmpeg antigravity-cli` returned empty lists.

- Fresh text: `GEMINI_UPDATE_OK`; resume recalled `COBALT_739` from the first
  turn, same conversation `6ea2d926-2d7f-432b-a416-d9dec1ff157b`, exact
  `gemini-3.1-pro-high`, SUCCESS, no tool calls.
- Synthetic video: response `yellow`, matching completed staged-file read,
  source hash unchanged; receipt `~/.codex/gemini-evidence/2026-09-22/video.json`.
- Synthetic audio: continuous electronic tone identified, MP4 carrier read,
  source hash unchanged. Repeated after FFmpeg update and final parser fix:
  SUCCESS, conversation `f9fa602b-e5fb-433f-bf1f-828b9a1cc042`;
  receipt `~/.codex/gemini-evidence/2026-09-22/audio-final.json`.
- Parser regression: additional completed reads of another path or without a
  path are rejected, including after a valid read. The extra-path test failed
  before the fix. All 19 tests passed after the final change; Ruff and skill
  validation passed.
- Three independent reviews completed. Fixed historical A/B wording and the
  missing-path acceptance gap; runtime reviewer verified null/missing parameter
  cases and reran all 19 tests on final code. No remaining material findings.

Text/media instructions now match their actual output modes. Existing account
route, default Pro model, direct-process execution and carrier remain. These
synthetic probes demonstrate operation, not archival transcription accuracy or
an improvement in success probability. Standalone native audio was not retested.
