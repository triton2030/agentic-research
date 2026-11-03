---
name: 1codex-image
description: >-
  Use when a raster image must be made or changed: generate, edit, recolor,
  restyle, combine references, cut out a background, mock up a UI screen, or
  draw an icon set. Recraft by name: 1recraft.
---

# 1codex-image — the fewest words the model reads as the owner's intent

## How the model draws

Images are made by OpenAI GPT Image with the owner's API key; he uses it for
its imagination. Recraft only when he names it (`1recraft`), a Codex thread
only when he names it (`1t3`).

The model is a designer who thinks in genres: from the strongest words of a
brief it picks the most typical picture of that genre and fills every slot
the brief leaves open with the genre's defaults. Measured on 20 banners
(2026-11) and confirmed by OpenAI's guide and practitioners:

- Nouns decide, adjectives tune, bans weigh least: `a block of translucent
  ice` gave an ice object up close; `iceberg`, `glacier` gave rocky landscape.
- A genre phrase is the strongest lever: `a premium product photograph`
  brought an empty background, studio light and one centred object at once.
- It reads literally: `like an ember` drew an ember; `the ice holds the fire`,
  `no drama`, `restraint` changed nothing visible.
- The strongest word spreads: `crack` cracked all the ice, `dark` added rocks,
  waves and a sunset.
- Strength is a ladder of words: `barely visible` → `quiet glow` → `narrow
  crack` → `seam` → `molten` (lava).
- An open slot gets a default: no light word — daylight; no typeface —
  decorative letters; no background — scenery; unasked icons and dividers.
- Quoted text comes out exact, Russian too; a number it must compute may not.
- One brief varies run to run; a strong line repeats across briefs.

So a spec — positions, pixels, a color per element — gets exactly its skeleton
back: the same app screen came out rich from a short brief and empty from a
spec. In the owner's experience, the longer the brief, the worse the image.

## Task

Turn the owner's intent into the fewest words the model reads as it, run the
call, and check the image.

## Goal

An image that serves its purpose in the model's own taste and holds the
owner's invariants: exact text, a brand color, what an edit keeps, what he
reacted to. Everything else stays the model's choice.

## When you write a brief

English, 60–150 words, growing only with the number of items:

1. What it is and where it will be used — this sets genre and polish; name
   the genre when it matters (`a premium product photograph`, `It should look
   like a real, well-designed, beautiful app`).
2. `Make it beautiful:` with mood, palette and, when the look depends on it,
   light: dark or bright, and its source.
3. `It should include:` — things as nouns, not places; the main one gets a
   hierarchy word.
4. Exact text in quotes, in its own language, with its typeface in words:
   `each line exactly as quoted and only once`.
5. Output: `Flat finished artwork, full bleed` or `Flat screenshot of the app
   window only, no device frame`.

Where something sits or how many pixels it takes, write only if the owner
dictated it, in his words.

```text
Create a social post image for X that sums up the first week of PERMAFROST, a Bitcoin DeFi launch by Subfrost: seven days, four upgrades.

Make it beautiful: a calm, premium corporate look. Minimal and quiet, very few details. Dark and atmospheric, in deep slate grey and muted turquoise, with soft fog. Shot like a premium product photograph: one object, soft studio light, a seamless dark background.

It should include:
- an enormous block of pure turquoise ice, its sharp edges catching the light
- warm amber and red light pouring from a narrow crack in its heart
- the headline "PERMAFROST" as the largest element, in elegant wide-spaced white sans-serif capitals
- "7 DAYS / 4 UPGRADES"
- a calm empty corner for a logo

All text in English, each line exactly as quoted and only once, no other text. Flat finished artwork, full bleed.
```

## When the image misses or the owner reacts

Translate his words, do not paste them. A reaction names an invariant — a
state that must hold ("looks like cold mountains" → ice, not landscape). Reach
it with the cheapest words: a new genre or noun first, one step on the
strength ladder next, a concrete ban last, with what fills the space (`only
the ice in an empty dark misty space`). The rest stays free.

To explore, keep one base brief and run three variants in parallel, each
changing one line; log what each word gave and what it dragged along. Run a
winner twice more before trusting it, then drop pinned lines one at a time
while the invariant holds. Show each image with its number and the lines
that differ.

## When you start from an existing image

Number the inputs with a role each (`Image 1 is the approved poster — edit
it`, `Image 2 is a style reference only`; a style reference brings its
composition too, and a person keeps the reference's pose unless you name a
new one). Write the target state, then `Keep everything else
unchanged:` and what must stay, earlier edits included.

The model redraws the whole picture and drifts with each chained edit: edit
from the last approved version, rewrite from the original when the keep-list
outgrows the change, paste exact pixels back locally. What must stay
identical — a face, a product label, a character, UI text — name in every
brief, or the model "improves" it; for people add `Do not change faces,
facial features, expressions or identity in any way`. A new screen of a live
product starts from a screenshot of it.

| Case | Add |
|---|---|
| Working UI | `no promotional banners` |
| Photo | `photorealistic`, visible texture |
| Icon set | one call, a 4×4 grid in reading order; cut with `slice_grid.py` |
| Logo | a sketch to find the form, then redraw as SVG |
| Transparent background | read [transparent.md](references/transparent.md) first |
| Flat graphic to change, exact chart | locally or in code, not the model |
| "Enhance" | it redraws; suggest an upscaler |

## When you run the call

Key: `~/.config/openai/api-key` — never print it or put it in a file, URL or
log; every image is paid from the owner's balance. Save the brief as
`_workspace/codex-image/<YYYY-MM-DD>/<name>.prompt.md` in the project root:

```bash
S=~/.claude/skills/1codex-image/scripts
$S/gen.sh <name> [<name> …]                    # parallel; IMAGES="a.png b.png" for an edit
uv run -q --with pillow --with numpy --with scipy python -I $S/slice_grid.py SHEET.png 4 4 OUT
```

`gen.sh` saves the image beside its brief, never overwrites and prints the
cost. Defaults: `gpt-image-2.5-sunburst-2026-09-08`, `QUALITY=high`,
`SIZE=2048x1152` (`1152x2048`, `2048x2048`; an edit keeps the source's ratio,
edges multiples of 16); `FORMAT=webp` is lighter.

- `high` ≈ $0.04, `max` ≈ $0.17, 4K `max` ≈ $0.40. Raise quality only for an
  unmet need; ask the owner, naming the sum, before `max`, 4K or a batch over
  $1. No seed or reasoning setting exists.
- Drafts: `MODEL=gpt-image-2.5-flare` (garbled a UI label once) or
  `QUALITY=low`.
- API fails: tell the owner and offer a Codex thread; never switch yourself —
  Codex spends his subscription.

## When the image arrives

Check it against the request: every item there, text letter by letter (a
stylized A without its bar reads as Λ), an edit kept what it had to. Give the
owner the file link, model, quality, size and cost; copy a used image to the
project's assets. A miss is fixed by one change: every attempt is paid.
