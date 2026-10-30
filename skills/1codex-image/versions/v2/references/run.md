# Running a call

## Key and tool

The key is in `~/.config/openai/api-key`; never print it or put it in a file,
URL or log. Every image is paid from the owner's API balance.

The generator is OpenAI's own script bundled with Codex:
`~/.codex/skills/.system/imagegen/scripts/image_gen.py`. It updates with
Codex, so do not edit or copy it. The reference files next to it were written
for Codex's built-in generator and are outdated on models: their advice to
switch to `gpt-image-1.5` for transparency leads to a model OpenAI shuts down
on 2026-12-01.

## Command

Every image and its brief go to `_workspace/codex-image/<YYYY-MM-DD>/` in the
root of the current project — the owner's choice; create the date folder when
it is missing. Save the brief there as a file first: the script reads it, and
it stays as the record of what the model received. An image the project will
use is then copied to where the project keeps its assets.

```bash
DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/_workspace/codex-image/$(date +%F)"
mkdir -p "$DIR"
OPENAI_API_KEY=$(cat ~/.config/openai/api-key) uv run -q --with openai --with pillow \
  python -I ~/.codex/skills/.system/imagegen/scripts/image_gen.py generate \
  --model gpt-image-2.5-sunburst-2026-09-08 --quality medium --size 1536x1024 \
  --prompt-file "$DIR/$NAME.prompt.md" --no-augment --out "$DIR/$NAME.png"
```

- `--no-augment` is required: without it the script wraps the brief in its
  own labels, and the brief file stops being an exact record.
- The script checks that `--out` is free only after the paid call: a repeat
  with the same name is paid and lost. Give each attempt a new name with its
  own brief (`$NAME-v2`); never `--force` over an approved version.
- Size by where the image will live: web screen `1536x1024` (via API
  `1920x1088`), mobile screen and poster `1024x1536`, icon and object
  `1024x1024`.
- Edits and references: subcommand `edit` with one `--image` per picture; the
  flag order is Image 1, Image 2 in the brief.
- When Image 1 is the edit target, keep its aspect ratio in `--size`: a wide
  photo sent into a square gets reframed, and the object fills the whole
  frame. A style or character reference does not set the ratio. A ratio the
  script lacks (16:9, 4:3) — set the exact size via [api.md](api.md).
- Icon set drawn as a grid: cut it into files with
  `uv run -q --with pillow --with numpy --with scipy python -I ~/.claude/skills/1codex-image/scripts/slice_grid.py SHEET.png 4 4 OUT_PREFIX`.
  Icons on the sheet cross the even grid lines, so a plain grid crop clips
  them; the script assigns each piece to the cell holding its center.
- Transparent background: `--background transparent --output-format png`.

## Model and quality

The owner's main model is the snapshot `gpt-image-2.5-sunburst-2026-09-08`:
a dated snapshot does not change when OpenAI moves the undated name to a new
version.

| Need | Model | `--quality` |
|---|---|---|
| ordinary image, mockup, edit | `gpt-image-2.5-sunburst-2026-09-08` | `medium` |
| small or dense text, final asset | same | `high`; via API `xhigh` |
| draft, exploring a form, variants | `gpt-image-2.5-flare` | `low` |

Probes 2026-10-30: Flare garbled one label on a UI screen that Sunburst got
right. On `medium`, Sunburst twice left the bottom of a UI screen empty;
`xhigh` at 1920×1088 filled it.

The script knows only `gpt-image-2`: for 2.5 models it allows sizes
`1024x1024`, `1536x1024`, `1024x1536`, `auto` and quality up to `high`. The
API accepts more — see [api.md](api.md).

## Cost

Computed from the formula of OpenAI's calculator for 2.5 at 1024×1024: `low`
≈ $0.006, `medium` ≈ $0.013, `high` ≈ $0.05, `xhigh` ≈ $0.09, `max` ≈ $0.21;
2048×2048 roughly double. Measured: `xhigh` at 1920×1088 ≈ $0.07. Each input
image adds about $0.01.

One call, one image unless the owner asked for variants: every `--n` variant
is paid. Ask him, naming the sum, before `max` and before a batch above $1.

## When a call fails

- No key, no balance, API down: tell the owner the cause and offer a Codex
  thread via `1codex`, but do not switch on your own — Codex spends his
  subscription limit, and the choice is his.
- The script rejects a size or quality for a 2.5 model: call the API
  directly per [api.md](api.md).
- `Transparent background is not supported for this model`: that is
  `gpt-image-2`; use a 2.5 model.

In the reply give the file link, model, quality, size and estimated cost.
