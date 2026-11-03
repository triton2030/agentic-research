---
name: 1codex-image
description: >-
  Use when a raster image must be made or changed: generate, edit, recolor,
  restyle, combine references, cut out a background, mock up a UI screen, or
  draw an icon set. Recraft by name: 1recraft.
---

# 1codex-image — goals for a thinking designer

## How to work with the model

Images are made by one model only — `gpt-image-2.5-sunburst-2026-09-08`, the
owner's choice — with his API key. Recraft only when he names it (`1recraft`),
a Codex thread only when he names it (`1t3`).

The model thinks: steer it like an agent, with goals, not drawing orders —
working out order, size, accents and colors is the design work the owner
uses it for. The owner's idea — the concept, the feeling, the story — stays
in the chat as context for you; the brief is prompt engineering. A stated
concept is drawn literally (`something hot lies deep in the ice` → a bright
orange object), so pick each word by the image it gave in the lessons, even
a word that sounds off-goal (`3D render` did not make a game).

A brief is built from modules, each a section that can change alone: style
(genre phrase included — it sets the look), subject, content (what this image
is about, exact text, empty space) and the owner's invariants in the
cheapest words. Change only the subject and the camera moves while the look
stays; change only content and size and every material keeps one look, each
aspect ratio recomposed. Prose or sections give the same image, but a
section named `Text:` or `Content:` invites icons next to labels.

The modules leak: the opening phrase and any place or genre word set style
too. Every word pulls a meaning with it, and the strongest one spreads over
the whole picture. So an invariant rewrites the brief: find the words that
pull against it and rewrite them; never append a line on top.

Two kinds of result. Designs of pages, screens and concepts are an idea
generator: invented labels and a wrong text color are expected, and the test
is whether the goal is met. An image that ships — a banner, a post — gets its
text checked letter by letter and no invented claims about the product.

What each phrase did, next to what and in how many runs, is kept in
`~/Documents/GitHub/agentic-research/knowledge/модель/gpt-image-2.5-sunburst-2026-09-08.md`.
Its strongest lessons (2026-11, about 170 banners):

- Nouns decide form and material, bans weigh least: `a block of translucent
  ice` gave an ice object, `glacier` gave rock, `levitating` the whole object
  floating. Style sentences about light, palette and material weigh as much
  as nouns, each owning one dimension — remove them one at a time to see
  which.
- Genre and place words bring their typical picture: `poster` — a big
  headline; `Swiss` — the Alps, every time. A genre needs room: `the cover of
  an annual report` gave a light editorial page only when the subject did not
  fill the frame. Genres with a known calm look work (`a high-end
  architectural visualization`, `an Apple product page`); a brand or print
  genre (`a luxury car advertisement`, `a printed brochure`) brought neither
  its object nor a change.
- It reads literally: a simile draws its image (`like an ember`). Visible
  words work, evaluations do not: `beautiful`, `calm`, `barely visible`, `low
  detail` change little, and `low contrast` and `low detail` are drawn as pale
  haze that lightens the image. For soft and dark together, name the tones and
  the fog: `deep, muted midtones`, `the fog is a deep, dense blue-grey`.
- The accent's color sets the mood — red lava read as menace, golden-amber as
  warmth; its strength is a ladder (`barely visible` → `quiet glow` → `narrow
  crack` → `seam` → `molten`); `the only warm color and the only strong
  accent` makes the rest recede.
- One sentence can move the whole picture: `The whole picture is low in
  contrast: muted tones, no deep blacks, no bright highlights, no visible
  sun.` Words of purity (`pristine`, `pure`) brighten it and bring a sun.
- Every line takes room: a background line shrinks the subject; an unnamed
  slot gets a default — daylight, decorative letters, scenery. Silence gives
  the genre's stock picture, not variety: a brief of feelings alone drew one
  scene four times out of five; variety comes from different named nouns.
  Words of distance move the camera (`far below` turned a close wall into a
  view down a chasm).
- Quoted text comes out exact, Russian too; a computed number may not. Across
  repeats, what is named holds; layout, sun and background details vary.

A spec — positions in pixels, a color per element — gets its bare skeleton
back; in the owner's experience, the longer the brief, the worse the image.
One sentence of layout is different: `Composition: all text on the left
third, stacked` or `a large, calm, empty area on the right third` was obeyed
every time and kept the picture rich.

## Task

Give the model a goal it can design toward — task, style and the owner's
invariants in the fewest words it reads as them — run the call, and judge the
image by its goal.

## Goal

An image that serves its purpose in the model's own design and holds the
owner's invariants: exact text where it ships, a brand color, what an edit
keeps, what he reacted to. Everything else stays the model's choice.

## When you write a brief

English, 60–200 words, growing only with the number of items. Sections in
this order make the brief easy to change one part at a time:

1. Style: genre and use (`the cover of an annual report`, `It should look
   like a real, well-designed, beautiful app`), mood in visible words,
   palette, and light — dark or bright, and its source. An approved style
   block is reused word for word.
2. Subject: the object or scene as nouns, with distance words (`seen up
   close`); the main one gets a hierarchy word.
3. Content: what this image is about; exact text in quotes, in its own
   language, with its typeface in words for every line — an unnamed line
   changes font between runs; empty space for text or a logo, if needed.
4. Constraints, last: `All text in English, each line exactly as quoted and
   only once, no other text.` — or, for a background to lay text on later,
   `No text, letters, numbers, logos or watermarks anywhere.` — then `Flat
   finished artwork, full bleed` or `Flat screenshot of the app window only,
   no device frame`.

Where something sits or how many pixels it takes, write only if the owner
dictated it, in his words.

```text
Style:
- The cover of an annual report by a serious financial company.
- <mood and restraint in visible words>
- <light, palette, and the colour of fog or background>
- <material of the subject>
- A clean minimalist 3D render.

Background:
- <the subject, seen up close, filling most of the frame>
- <the one accent: its form, colour and strength>

Content:
- the subject: <what this image is about>
- the headline "<TEXT>" as the largest element, in <typeface in words>
- "<second line>" in <typeface in words>
- a calm empty corner for a logo

Constraints:
- All text in English, each line exactly as quoted and only once, no other text.
- Flat finished artwork, full bleed.
```

## When the image misses or the owner reacts

Read the lessons file first: it may already hold the words for this
invariant. Translate his words, do not paste them. A reaction names an
invariant — a state that must hold ("looks like cold mountains" → ice, not
landscape). Reach it with the cheapest words — a new genre or noun first, one
step on the strength ladder next, a concrete ban last, with what fills the
space — and rewrite the lines that pull against it. The rest stays free.

Run several variants per round in parallel, each one change away from a
base, so every effect can be named: a line per variant, a grid for two
questions, a removal test for a suspected word. Change a brief the owner
liked one line at a time: its "contradictions" may be working — `pure`, fog
and `atmospheric` made a luminous haze that an eight-line cleanup lost.
Repeat a winner two or three times; what he liked that does not repeat — the
layout, the sun — name in the brief or edit from that image. "Darker" or
"softer" is judged by numbers, not by eye: the mean and the spread of the
grey channel (Pillow `ImageStat`); one brief drifts about ±5 of 255.

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
from the last approved version, paste exact pixels back locally. Name what
must stay identical — a face, a product label, UI text — in every brief, or
the model "improves" it; for people add `Do not change faces, facial
features, expressions or identity in any way`. A new screen of a live
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

`gen.sh` saves the image beside its brief, never overwrites, prints the
cost and fixes the model. Defaults: `QUALITY=high`,
`SIZE=2048x1152` (`1152x2048`, `2048x2048`; an edit keeps the source's ratio,
edges multiples of 16); `FORMAT=webp` is lighter.

- `high` ≈ $0.04, `max` ≈ $0.17, 4K `max` ≈ $0.40. Raise quality only for an
  unmet need; ask the owner, naming the sum, before `max`, 4K or a batch over
  $1. No seed or reasoning setting exists.
- Drafts: `QUALITY=low`.
- API fails: tell the owner and offer a Codex thread; never switch yourself —
  Codex spends his subscription.

## When the image arrives

Judge it by its kind. An image that ships: every item there, text letter by
letter (a stylized A without its bar reads as Λ), no invented claims. A design
for ideas: is the goal met. An edit: it kept what it had to.

Then show it: each image on its own, never a collage, captioned with its
number and change. Text between tool calls stays folded away, so the closing
message carries each full brief with its changes against the base as a
`diff` block (one brief with the line marked when variants differ in one
line), with model, quality, size and cost. Copy a used image to the
project's assets.
