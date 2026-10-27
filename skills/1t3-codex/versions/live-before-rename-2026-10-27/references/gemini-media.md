# Audio, video and PDF through Gemini

A Gemini thread in T3 Code can't hear or see: it gets audio and video as raw
bytes and hunts for a workaround. The Antigravity CLI (`agy`) hears and sees,
so the package carries `scripts/gemini.py` for media. It also reads PDF and
files outside the thread's project. It doesn't need T3 Code.

## When running it

```bash
python3 "<skill-dir>/scripts/gemini.py" --dir /absolute/folder/path <<'BRIEF'
<what to hear or see, and the answer's form>
BRIEF
```

- The file lies in `--dir` or in a folder from `--add-dir`. Audio opens as
  MP3, WAV, OGG and Opus; convert M4A, AAC, AIFF and FLAC first:
  `ffmpeg -i recording.m4a recording.mp3`. Video: MP4, MOV and WebM.
- Put "If something fails, record the exact error and stop; don't look for
  workarounds" into the brief: without it Flash hunts for a workaround on a
  file that didn't open.
- Title the run `Gemini 3.8 Flash/high · <gist>`, with Argon
  `Gemini 4 Argon/high · <gist>`. In Claude Code use `timeout: 300000` for a
  short recording and `run_in_background: true` for a long one. In Codex take
  the `session_id` from `exec_command` and wait with `write_stdin`. For a
  long recording pass `--timeout 30m`: the default wait is ten minutes. Long
  recordings were not measured.

## When the answer arrives

- stderr carries a receipt. If the file is missing from its `viewed:` line,
  Gemini never opened it and wrote from memory. A `WARNING` line under the
  receipt names a failed tool call, such as an unsupported format.
- You can't hear the recording yourself. When a decision depends on a name,
  number or date from the transcript, get a second one independently — a
  separate call with `--neutral --add-dir /folder` or local `whisper-cli` —
  and compare.

## When the script returns an error

- `SUCCESS with an empty answer` without a permission refusal or timeout —
  retry once: in a probe the same brief passed on retry.
- `invalid model selection` — the chosen model left the subscription. The
  owner picks a replacement.
- The script names a permission refusal or timeout itself, with the next
  step. `agy -p /usage` shows the remaining quota.

## How the script works

Measured on 2026-10-13 on `agy` 1.2.14 with `gemini-3.8-flash-high`. On `agy`
1.3.4 on 2026-10-14, MP3 audio and MP4 video opened the same way; one call of
three returned an empty answer with no reason (`run ended with no output and
no recorded error`), and a retry with the same brief passed. On `agy` 1.4.3
on 2026-10-20, an MP3 was transcribed verbatim in 20 seconds. The event
stream now calls file reads `read_file` with a `Path` parameter instead of
`view_file` and `AbsolutePath`; the wrapper understands both. Without
`--full`, Gemini got no folder listing or file search: it reads only paths
named in the brief. "Per the docs" means no live check.

### Wrapper modes

| Need | Flag |
| --- | --- |
| let it read another folder | `--add-dir /path`, repeatable |
| a view without project instructions | `--neutral` plus `--add-dir` for the needed folders |
| web search, commands, writing files | `--full` |
| continue the same conversation | `--resume <id from the receipt>`; set folders and permissions again |
| a strictly shaped answer | `--schema '<JSON Schema>'` |
| Gemini 4 Argon instead of Flash: audit, advice | `--model gemini-4-argon-high` |
| Claude on the Google subscription instead of Gemini | `--model claude-opus-5-5-high` or another `claude-*` from `agy models` |
| work longer than 10 minutes | `--timeout 30m` |

Without `--full` Gemini only reads. `--full` lifts all approvals at once:
`agy` has no separate web-only permission. With it the wrapper itself adds
the shared rules to the run: don't commit unasked, don't touch others' edits,
don't call other agents, don't record the brief as the owner's words.

stdout carries the answer. stderr carries a line per tool call while it
works and a receipt at the end: model, time, tokens, conversation id, tools,
files read (`viewed:`) and, after `--full`, files touched (`changed:`). The
wrapper returns a permission refusal or timeout as an error with the cause
and next step; bare `agy` would report them as exit 0 with an empty answer.

### Permissions in non-interactive mode

| Action | No flags | Opened by |
| --- | --- | --- |
| read a working-folder file by path | yes | — |
| read another folder | no | `--add-dir` |
| write a file, even in the working folder | no | `--full` |
| run a shell command | no | `--full` |
| search the web and read URLs | no | `--full` |

The docs promise writing to the working folder is allowed by default; on
this machine it is denied. The `agy` flags `--mode accept-edits`,
`--mode plan` and `--sandbox` alone open nothing in the table, so the wrapper
doesn't pass them.

`--full` is `--dangerously-skip-permissions`. Together with it, `--sandbox`
limits only shell commands: writing outside the working and temporary
folders gets `Operation not permitted`. It doesn't limit the file-writing
tool, and commands keep network access.

A persistent alternative to `--full` is `permissions.allow` rules in
`~/.gemini/antigravity-cli/settings.json`, e.g. `read_url(*)` for the web
without other permissions. It is a global Antigravity setting that also
applies in its interactive mode. The owner changes it; not tested here.

### What the wrapper reads from `agy`

It runs `agy --output-format stream-json` and takes the model from the `init`
event, tools from `step_update` events and the answer from the `result`
event.

It recognizes an empty answer with status `SUCCESS` by stderr text:
`required the "<permission>" permission` is a refusal, `print timeout` a
timeout. If `agy` changes these wordings, the wrapper returns the generic
"SUCCESS with an empty answer" error with the raw stderr.

Token counts and duration in a resumed conversation are cumulative: they
cover the whole conversation, not the last turn.

### Long work with full permissions

Measured on 2026-10-13: Gemini with `--full` built a 70 KB HTML page, ran a
browser check itself and fixed what it found. Both turns, the first of 10
minutes and a 3-minute continuation, ended with `There was a network issue
connecting to the server` after the work was done; the files stayed on disk.
The wrapper then prints Gemini's last text and a `--resume` hint. The cause
of the drops is unknown.

Flash fills in the unknown with assertions: in a comparison table it wrote
"no" where the sources were silent.

### Conversations

`--resume` continues a conversation by id from any folder. Conversations live
in `~/.gemini/antigravity-cli/`; request contents go to Google. There is no
official delete command; don't delete the databases by hand.

### Media

Gemini opens a file with its read tool, so the file must be in the working
folder or a folder from `--add-dir`, and the brief must name its path.

| Kind | Opens | Doesn't open |
| --- | --- | --- |
| audio | MP3, WAV, OGG, Opus | M4A, AAC, AIFF, FLAC |
| video with sound | MP4, MOV, WebM | — |
| images | PNG, JPG | — |
| documents | PDF | — |

Measured on synthetic 3–10 second files; long recordings were not measured.
The read tool rejects an unsupported file with `unsupported mime type`. The
answer still comes back non-empty, so the wrapper prints `WARNING` instead of
failing.

### Instructions and cost

Antigravity injects the working folder's `AGENTS.md` and `GEMINI.md` itself,
and Gemini follows them. `--neutral` runs it in an empty temporary folder
without them.

An empty question costs about 12 thousand input tokens, a call with one file
read about 24 thousand. A web search for one question took 70 seconds and
170 thousand tokens: pages are read whole.

### Model and quotas

The script defaults to `gemini-3.8-flash-high` — the `MODEL` constant in
`scripts/gemini.py`. `--model` also accepts `gemini-4-argon-*` and `claude-*`;
the script rejects other Gemini models: the owner chose these. `agy models`
lists what is available; Gemini 3.1 Pro is in the docs but not in this
account's list.

`agy -p /usage` shows the weekly and five-hour remainders: for Gemini, for
Claude with GPT, and a separate weekly one for Gemini 4 Argon. Probe
2026-10-20: `gemini-4-argon-high` read a file and answered in 33 seconds;
media on Argon were not tried.

### What the wrapper doesn't use

`agy` has image generation (`generate_image`), browser control, its own
agents (`~/.gemini/config/agents/*.md` and `--agent`), MCP and several turns
in one process (`--input-format stream-json`). The wrapper uses none of them.
Generation was checked on 2026-10-16 through a T3 thread with `instanceId`
`antigravity` (`gemini-3.8-flash-high`): the agent calls the built-in
`generate_image` (`prompt`, `image_name`, `aspect_ratio`) itself and saves a
1024×1024 JPEG without alpha to
`~/.t3/userdata/providers/antigravity/<hash>/antigravity-acp/brain/<session>/`,
so the task says where to copy the result; the tool doesn't name the image
model. The other capabilities are untested as a subagent route.

Docs, read 2026-10-13:
[headless mode](https://antigravity.google/docs/cli/headless/),
[permissions](https://antigravity.google/docs/cli/permissions/),
[sandbox](https://antigravity.google/docs/cli/sandbox/),
[modes](https://antigravity.google/docs/cli/modes/),
[models](https://antigravity.google/docs/models/).
