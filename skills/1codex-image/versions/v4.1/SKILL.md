---
name: 1codex-image
description: >-
  Use when a raster image must be made or changed: generate, edit, recolor,
  restyle, combine references, cut out a background, mock up a UI screen, or
  draw an icon set. Recraft by name: 1recraft.
---

# 1codex-image — goals for a thinking designer

## How to work with the model

Images are made by OpenAI GPT Image with the owner's API key. Recraft only
when he names it (`1recraft`), a Codex thread only when he names it (`1t3`).

The model thinks: steer it like an agent, with goals, not drawing orders. Its
job is to work out how to meet the goal — order, size, accents, cards,
colors — and that is what the owner uses it for: it is his designer. A brief
is built from modules:

- task — what the image is, what it is for, what must be in it, as a list;
- style — the approved look in one paragraph; it carries over word for word
  to other tasks, and what it names becomes a motif there too;
- the owner's invariants — what he pinned or reacted to, in the cheapest
  words.

Every word pulls a meaning with it, and the strongest one spreads over the
whole picture. So an invariant rewrites the brief: find the words that pull
against it and rewrite them; never append a line on top.

Two kinds of result. Designs of pages, screens and concepts are an idea
generator: invented labels and a wrong text color are expected, and the test
is whether the goal is met. An image that ships — a banner, a post — gets its
text checked letter by letter and no invented claims about the product.

What each phrase did, next to what and in how many runs, is kept in
`~/Documents/GitHub/agentic-research/knowledge/модель/gpt image 2.5.md`. Its
strongest lessons (2026-11):

- Nouns decide, adjectives tune, bans weigh least: `a block of translucent
  ice` gave an ice object; `iceberg`, `glacier` gave rocky landscape.
- A genre phrase is a strong lever — `a premium product photograph` brought
  an empty background, studio light and one centred object — unless another
  line already fixes the framing.
- It reads literally: `like an ember` drew an ember; `the ice holds the fire`,
  `no drama` changed nothing visible.
- The mood follows the main accent's color: red-orange lava read as menace,
  golden-amber as warmth.
- Strength is a ladder of words: `barely visible` → `quiet glow` → `narrow
  crack` → `seam` → `molten` (lava).
- An open slot gets a default: no light word — daylight; no typeface —
  decorative letters; no background — scenery; a list of points — icons.
- Quoted text comes out exact, Russian too; a number it must compute may not.

A spec — positions, pixels, a color per element — gets exactly its skeleton
back: the same app screen came out rich from a short brief and empty from a
spec. In the owner's experience, the longer the brief, the worse the image.

## Task

Give the model a goal it can design toward — task, style and the owner's
invariants in the fewest words it reads as them — run the call, and judge the
image by its goal.

## Goal

An image that serves its purpose in the model's own design and holds the
owner's invariants: exact text where it ships, a brand color, what an edit
keeps, what he reacted to. Everything else stays the model's choice.

## When you write a brief

English, 60–150 words, growing only with the number of items:

1. Task: what it is and where it will be used — this sets genre and polish;
   name the genre when it matters (`a premium product photograph`, `It should look
   like a real, well-designed, beautiful app`).
2. Style: mood, palette and, when the look depends on it, light — dark or
   bright, and its source. An approved style paragraph is reused word for
   word.
3. `It should include:` — things as nouns, not places; the main one gets a
   hierarchy word.
4. Exact text in quotes, in its own language, with its typeface in words:
   `each line exactly as quoted and only once`.
5. Output: `Flat finished artwork, full bleed` or `Flat screenshot of the app
   window only, no device frame`.

Where something sits or how many pixels it takes, write only if the owner
dictated it, in his words.

The approved banner of the series (style paragraph second):

```text
Create a social post image for X that sums up the first week of PERMAFROST, a Bitcoin DeFi launch by Subfrost: seven days, four upgrades.

Make it beautiful: a calm, premium corporate look. Minimal and quiet, very few details. Softly lit, calm and atmospheric, in cool steel blue and soft turquoise, wrapped in thick soft fog. Clean, translucent ice with almost no texture. A clean minimalist 3D render.

It should include:
- a giant block of clear translucent ice seen up close, filling most of the frame
- a deep crack inside the ice glowing hot red-orange, lighting the ice from within
- the headline "PERMAFROST" as the largest element, in elegant wide-spaced white sans-serif capitals
- "7 DAYS / 4 UPGRADES"
- four short labels: "More ways to deposit", "Precise boost", "Safe bonding", "Flexible farms"
- a calm empty corner for a logo

All text in English, each line exactly as quoted and only once, no other text. Flat finished artwork, full bleed.
```

## When the image misses or the owner reacts

Read the lessons file first: it may already hold the words for this
invariant. Translate his words, do not paste them. A reaction names an
invariant — a state that must hold ("looks like cold mountains" → ice, not
landscape). Reach it with the cheapest words — a new genre or noun first, one
step on the strength ladder next, a concrete ban last, with what fills the
space — and rewrite the lines that pull against it. The rest stays free.

To explore, keep one base brief and run three variants in parallel, each
changing one line. Run a winner twice more before trusting it, then drop
pinned lines one at a time while the invariant holds.

After a series, add to the lessons file what each phrase gave, under what it
controls: the phrase, the effect with what it dragged along, the brief it
stood in and the number of runs; a row a new run confirms or contradicts is
updated, not doubled. Commit it in `agentic-research`.

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

Judge it by its kind. An image that ships: every item there, text letter by
letter (a stylized A without its bar reads as Λ), no invented claims. A design
for ideas: is the goal met. An edit: it kept what it had to. Show each image
with its number and the lines that differ; give the file link, model,
quality, size and cost; copy a used image to the project's assets.
