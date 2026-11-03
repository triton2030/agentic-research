# Transparent background

Only the 2.5 models return real transparency; `gpt-image-2` rejects it. The
model never cuts an object out — it redraws it: shape and colors match, fine
texture does not. Choose the route by what you are given:

| Case | Route |
|---|---|
| flat graphic on a plain background: logo, icon, asset with exact colors | no model: `uv run -q --with pillow python -I ~/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py --input IN.png --out OUT.png --auto-key border` — free, pixels unchanged; the background color must not occur inside the object, or it turns into holes |
| a photo, even on a studio background (shadows and gradients) | edit with a 2.5 model and a transparent background; tell the owner before the call that the object will be redrawn |
| a new object, hair, fur, fluff | generate with a 2.5 model and a transparent background |
| glass, a clear bottle | no route cuts it cleanly: generate it on its final background |

## Brief

The parameter alone does not work: the brief outweighs it, and a described
scene eats the transparency. Without a word about shadows the model leaves a
semi-transparent shadow under the object. Tail for a new image:

```text
Isolated subject on a fully transparent background, full object visible with generous padding. No backdrop, no scenery, no rectangle, no plinth, no checkerboard, no cast shadow, no reflection.
```

Removing the background from a given photo (probed: clean, no shadow; the
apple was redrawn):

```text
Remove the background completely. Keep the apple exactly as is: same shape, colors, stem, highlights. No shadow, no ground, no reflection. Output the apple alone on a fully transparent background.
```

In later edits of a transparent asset repeat `preserve the transparent
background`.

## Checking the file

Check pixels, not the preview: mode RGBA and a clear share of pixels with
alpha 0. A painted checkerboard looks the same but is paint. Composite the
image over a dark and a light background: a semi-transparent shadow or halo
is a defect. The object body comes back at alpha 250–253, not 255 — that is
normal.
