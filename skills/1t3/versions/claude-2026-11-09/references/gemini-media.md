# Audio, video and PDF through Gemini

A Gemini thread can't hear or see; the Antigravity CLI can, and
`scripts/gemini.py` wraps it. It needs no T3 Code and also reads files
outside a project.

```bash
python3 "<skill-dir>/scripts/gemini.py" --dir /absolute/folder <<'BRIEF'
<what to hear or see, and the answer's form>
If something fails, record the exact error and stop; don't look for workarounds.
BRIEF
```

- The file lies in `--dir` or an `--add-dir` folder, and the brief names its
  path. Opens MP3, WAV, OGG, Opus, MP4, MOV, WebM, PNG, JPG, PDF; convert
  M4A, AAC, AIFF and FLAC first: `ffmpeg -i x.m4a x.mp3`. Long recordings
  were not measured.
- In Claude Code: `timeout: 300000` for a short recording,
  `run_in_background: true` for a long one; a run longer than the default ten
  minutes needs `--timeout 30m`. Title the run `Gemini 3.8 Flash/high ·
  <gist>`, with Argon `Gemini 4 Argon/high · <gist>`.
- Read the stderr receipt: a file missing from `viewed:` was never opened,
  and the answer is from memory; a `WARNING` line names a failed tool call,
  such as an unsupported format.
- You can't hear the recording yourself. When a decision rests on a name,
  number or date, get a second transcript — `--neutral --add-dir /folder` or
  local `whisper-cli` — and compare.

| Need | Flag |
| --- | --- |
| Argon for audit or advice (not tried on media); Claude on the Google subscription | `--model gemini-4-argon-high`, `--model claude-opus-5-5-high` |
| another folder | `--add-dir /path`, repeatable |
| no project `AGENTS.md` and `GEMINI.md`, which Gemini otherwise follows | `--neutral` |
| writing, shell, web — all approvals at once; the wrapper adds the shared rules | `--full` |
| continue a conversation | `--resume <id from the receipt>`, with folders and flags again |
| a strictly shaped answer | `--schema '<JSON Schema>'` |

Without `--full` Gemini only reads named paths; writing is denied even in
the working folder. A web search reads pages whole: one question took 70
seconds and 170 thousand tokens.

When it fails: `SUCCESS with an empty answer` without a named refusal or
timeout — retry once; `invalid model selection` — the model left the
subscription; a refusal or timeout the script names with its next step.
A long `--full` run ended with `There was a network issue` after the work was
done: the files stay, and the wrapper prints the last text and a `--resume`
hint. `agy -p /usage` shows the quota. Conversations live in
`~/.gemini/antigravity-cli/` and their contents go to Google; there is no
official delete, so don't delete the databases by hand.
