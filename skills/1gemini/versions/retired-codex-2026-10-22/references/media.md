# One-file audio and video analysis

Open this file only when Gemini must inspect local audio or video.

## What the route actually supports

Antigravity CLI 1.1.18 added native recognition for common audio attachments.
In the 2026-08-27 account tests on runtime 1.1.22, repeated standalone WAV
calls ended with the generic agent-termination error while an MP4 carrier made
from the same synthetic audio completed. The wrapper therefore uses one
deterministic carrier call rather than retrying an uncertain native call. A
matching completed tool event proves delivery; it does not prove transcription
accuracy.

The wrapper accepts one direct video with suffix `.mp4`, `.mov`, `.webm`,
`.avi`, or `.ogv`, and one audio source with suffix `.mp3`, `.wav`, `.aif`,
`.aiff`, `.m4a`, `.aac`, `.flac`, `.ogg`, or `.opus`. It stages video as an
unchanged copy. It uses FFmpeg to put audio into a black H.264 MP4 with a
192-kbit/s AAC track; this is lossy delivery transcoding.

## Operation

Tell the user the exact source file whose content will be sent to Google, that
audio will be transcoded into an MP4 carrier, and that the Antigravity
conversation may remain in local state and under Google's data retention after
the staged carrier is deleted. Then run:

```bash
python3 /Users/triton/.codex/skills/1gemini/scripts/gemini_advisor.py \
  --cwd /absolute/project/path --media '/absolute/path/to/file.mp3' <<'EOF'
<what to identify, transcribe, compare, or explain>
EOF
```

The wrapper handles one file per run so a directory is never uploaded by
accident. It copies video unchanged or transcodes audio into a temporary
isolated project, never overwrites the source, verifies its SHA-256 after the
call, and deletes the temporary project. Antigravity still persists
conversation metadata and content outside that temporary project; do not
describe the whole interaction as ephemeral.

Treat the call as successful only when `media.viewed` is true. A `SUCCESS`
result without the matching completed `view_file` event does not prove that
Gemini saw the file.

`media.viewed` proves delivery, not transcription accuracy. For archival
speech, request timestamps and mark uncertain passages; treat names, dates,
and verbatim quotations as claims to verify against the recording.

The wrapper rejects other formats. Report that exact boundary; do not rename an
unsupported file or expose its whole parent directory to `agy`.

Official [Antigravity changelog](https://antigravity.google/changelog/) and
[headless reference](https://antigravity.google/docs/cli/headless/), checked
2026-08-27. The carrier is a live-characterized reliability workaround, not an
official requirement.
