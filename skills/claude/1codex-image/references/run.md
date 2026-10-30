# Running a call

## Key and files

The key is in `~/.config/openai/api-key`; never print it or put it in a file,
URL or log. Every image is paid from the owner's API balance.

Every image and its brief go to `_workspace/codex-image/<YYYY-MM-DD>/` in the
root of the current project — the owner's choice. Save the brief there as a
file first: it is sent from the file and stays as the record of what the
model received. An image the project will use is then copied to where the
project keeps its assets.

## Defaults

The owner's defaults: model `gpt-image-2.5-sunburst-2026-09-08` (a dated
snapshot does not change when OpenAI moves the undated name) at 2K, quality
`high`. Measured: 2048×1152 `high` — 30 s, about $0.04.

| Shape | `size` |
|---|---|
| landscape: web screen, banner, illustration | `2048x1152` |
| portrait: mobile screen, poster | `1152x2048` |
| square: icon, icon set, object | `2048x2048` |
| edit | the source's aspect ratio, long edge 2048, both edges multiples of 16 |

A style or character reference does not set the edit's ratio — only the edit
target does: a wide photo sent into a square gets reframed.

Other choices:

- Draft, exploring a form, many variants: `gpt-image-2.5-flare`, `low`. In a
  probe Flare garbled one UI label that Sunburst got right.
- Dense small text: `xhigh`.
- `max` or 4K (`3840x2160`): ask the owner first, naming the sum — about
  $0.40 an image, up to two minutes, and OpenAI calls sizes above 2560×1440
  experimental. Ask also before a batch above $1.
- One call, one image unless the owner asked for variants: each `n` is paid.
- `gpt-image-2` has no transparency and no `xhigh`/`max`; there is no reason
  to pick it.

## Generate

```bash
DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/_workspace/codex-image/$(date +%F)"
mkdir -p "$DIR"
NAME=hero-v1   # one name per attempt; the brief is "$DIR/$NAME.prompt.md"
K=$(cat ~/.config/openai/api-key)
P="${DIR:?}/${NAME:?}"
[ -e "$P.png" ] && { echo "$P.png exists: new NAME per attempt"; exit 1; }
jq -n --rawfile p "$P.prompt.md" \
  '{model:"gpt-image-2.5-sunburst-2026-09-08", prompt:$p, size:"2048x1152", quality:"high"}' |
  curl -s https://api.openai.com/v1/images/generations \
    -H "Authorization: Bearer $K" -H "Content-Type: application/json" -d @- > "$P.json"
if jq -e '.data[0].b64_json' "$P.json" >/dev/null; then
  jq -r '.data[0].b64_json' "$P.json" | base64 -d > "$P.png"
  jq -c '.usage' "$P.json" && rm "$P.json"
else
  jq -c .error "$P.json"
fi
```

Transparent background: add `background:"transparent", output_format:"png"`
to the object.

## Edit and references

Same `DIR`, `NAME`, `P` and overwrite check; then:

```bash
curl -s https://api.openai.com/v1/images/edits -H "Authorization: Bearer $K" \
  -F model=gpt-image-2.5-sunburst-2026-09-08 \
  -F "image[]=@target.png" -F "image[]=@reference.png" \
  -F size=2048x1152 -F quality=high \
  -F "prompt=<$P.prompt.md" > "$P.json"
```

`image[]` order is Image 1, Image 2 in the brief. Transparent background: add
`-F background=transparent -F output_format=png`. Parse the response as above.

## What the API accepts

| Parameter | Values |
|---|---|
| `size` | `auto` or `WxH`: both edges multiples of 16, long edge ≤ 3840, ratio ≤ 3:1, 655,360 to 8,294,400 pixels. `1920x1080` fails — use `1920x1088` |
| `quality` | `low`, `medium`, `high`, `xhigh`, `max`, `auto` |
| `mask` | PNG with alpha, same size as the first image; a hint, not a stencil — the model edits beyond it. Not probed here |
| `markup` | 2.5 only: a transparent PNG of marks over the first image; not with `mask`. Not probed here |

## Cost

The response's `usage` gives the exact cost: `output_tokens` × $30 + input
`image_tokens` × $8 + `text_tokens` × $5 per million. Each input image adds
about $0.01. Report it with the result.

## Icon sheet

Cut a sheet drawn as a grid into files:
`uv run -q --with pillow --with numpy --with scipy python -I ~/.claude/skills/1codex-image/scripts/slice_grid.py SHEET.png 4 4 OUT_PREFIX`.
Icons on the sheet cross the even grid lines, so a plain grid crop clips
them; the script assigns each piece to the cell holding its center.

## When a call fails

- No key, no balance, API down: tell the owner the cause and offer a Codex
  thread via `1codex`, but do not switch on your own — Codex spends his
  subscription limit, and the choice is his.
- `Transparent background is not supported for this model`: that is
  `gpt-image-2`; use a 2.5 model.
- `Invalid size`: recheck the size rules above.

In the reply give the file link, model, quality, size and the cost from
`usage`.
