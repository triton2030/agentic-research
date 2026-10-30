# Calling the API directly

For what the script rejects on 2.5 models: other sizes, `xhigh`, `max`.
Recipes verified 2026-10-30. `DIR` and `NAME` as in [run.md](run.md):
`DIR` is the date folder under `_workspace/codex-image/`.

## What the API accepts

| Parameter | Values |
|---|---|
| `size` | `auto` or `WxH`: both edges multiples of 16, long edge ≤ 3840, ratio ≤ 3:1, 655,360 to 8,294,400 pixels; above 2560×1440 OpenAI calls it experimental |
| `quality` | `low`, `medium`, `high`, `auto`; 2.5 models also `xhigh`, `max` |
| `mask` | PNG with alpha, same size as the first image; a hint, not a stencil — the model edits beyond it. Not probed here |
| `markup` | 2.5 only: a transparent PNG of marks over the first image; not together with `mask`. Not probed here |

`1920x1080` is not a multiple of 16: ask for `1920x1088` and crop if exact
Full HD is needed.

## Generate

```bash
K=$(cat ~/.config/openai/api-key)
P="${DIR:?}/${NAME:?}"
[ -e "$P.png" ] && { echo "$P.png exists: new NAME per attempt"; exit 1; }
jq -n --rawfile p "$P.prompt.md" \
  '{model:"gpt-image-2.5-sunburst-2026-09-08", prompt:$p, size:"1920x1088", quality:"xhigh"}' |
  curl -s https://api.openai.com/v1/images/generations \
    -H "Authorization: Bearer $K" -H "Content-Type: application/json" -d @- > "$P.json"
if jq -e '.data[0].b64_json' "$P.json" >/dev/null; then
  jq -r '.data[0].b64_json' "$P.json" | base64 -d > "$P.png"
  jq -c 'del(.data)' "$P.json" && rm "$P.json"
else
  jq -c .error "$P.json"
fi
```

For transparency add `background:"transparent"` to the object.

## Edit and references

```bash
K=$(cat ~/.config/openai/api-key)
P="${DIR:?}/${NAME:?}"
[ -e "$P.png" ] && { echo "$P.png exists: new NAME per attempt"; exit 1; }
curl -s https://api.openai.com/v1/images/edits -H "Authorization: Bearer $K" \
  -F model=gpt-image-2.5-sunburst-2026-09-08 \
  -F "image[]=@base.png" -F "image[]=@reference.png" \
  -F size=2048x1152 -F quality=high \
  -F "prompt=<$P.prompt.md" > "$P.json"
```

`image[]` order is Image 1, Image 2 in the brief. For transparency add
`-F background=transparent -F output_format=png`. Parse the response as for
generation: on error no PNG appears and `.error` is printed.

The response carries `usage` — exact cost: `output_tokens` × $30 + input
`image_tokens` × $8 + `text_tokens` × $5 per million.
