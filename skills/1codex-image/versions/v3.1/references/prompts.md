# Briefs by case

The order of a brief and what to keep out of it are in the skill body. Here:
what each case adds, and an example. "Probed" means the example ran on
2026-10-30 on `gpt-image-2.5-sunburst-2026-09-08` with the stated result; the
others follow OpenAI's prompting guide — a pattern, not a guarantee.

## Complex UI

List the windows and panels and what each shows; the model lays them out.
Exact text only for the product name and what the owner gave verbatim. The
model may add marketing extras on its own — a quote banner, an upgrade card;
for a working tool say `no promotional banners`.

Probed: a rich professional editor — media library, player, multi-track
timeline, inspector, plausible labels.

```text
A desktop video editing app for a product called "Cutline" — the main editing workspace. Make it beautiful: a modern, premium professional tool with a design-award level of polish. Dark theme with one vivid accent color.

The screen should include:
- a media library with a few video clips
- a large preview player showing a sunny beach shot
- a multi-track timeline with several video and audio tracks
- an inspector with color and audio settings
- a top bar with the project name "Summer Trip" and an Export button

Flat screenshot of the app window only, no device frame, no desk.
```

Not like this — the same screen as a spec gave an empty frame with five
labels:

```text
Layout: top bar 48px high across the full width with project name "Summer Trip" on the left and an "Export" button on the right; left panel 280px wide with a media library grid of 6 clip thumbnails in 2 columns; center top: preview player 860x480 … Text (verbatim): "Summer Trip", "Export", "Color", "Audio"; no other text
```

## Next screen of the same product

A screenshot of the current or approved screen goes in as Image 1, the design
reference; the brief lists the new screen's content the same way.

Probed: same design system, summary on top, budgets with percentages, the
overrun flagged; the model's own total was wrong ($351 instead of $271).

```text
Image 1 is a screen of the "Ledgerly" finance app — use it only as the design reference and design a new screen of the same app in exactly the same design system.

New screen: Budgets. Make it beautiful and easy to scan. It should include:
- budgets for Groceries ($412 of $600), Dining out ($198 of $250), Transport ($96 of $150) and Entertainment ($143 of $120 — over the limit, clearly flagged)
- how much is left this month in total
- a "New budget" button

Flat screenshot of the app window only.
```

## Illustration and photo

Style in words: medium, mood, palette. Room for page text is one more item on
the list; the model finds its place.

Probed: warm editorial illustration with an empty wall for the title.

```text
A wide hero illustration for a blog post about slow mornings. Make it beautiful: calm, warm, editorial, the kind of image that makes you want to read the post. Flat illustration with subtle paper grain, muted sage, cream and terracotta.

It should show:
- a person reading a paper book at a small kitchen table
- a steaming cup of tea
- a cat asleep on the windowsill
- soft early-morning light from the window
- a calm empty area where the post title will go

No text, no logos.
```

For a photo, add `photorealistic` and visible texture: skin, fabric, wear.

## Poster, slide, text in the image

Each line of text is a list item in quotes; the main one gets a hierarchy
word. Name the language of the text. Slides and charts get the real numbers;
dense small text needs `xhigh`. An exact chart from data belongs in code: the model
invents points.

Probed: every Russian label correct, including «ё» and «» quotes.

```text
A vertical poster for a jazz evening in a small bookshop. Make it beautiful: a risograph print look in two inks, deep blue and warm orange on cream paper, cozy and a little bohemian.

It should include:
- a double bass leaning on a bookshelf in warm lamp light
- the headline "Тихий джаз" as the largest element
- "Пятница, 14 ноября · 19:00"
- "Книжная лавка «Переплёт»"

All text in Russian, each line exactly as quoted and only once, no other text.
```

## Edit: light, color, style, theme

On a photo with people, add `Do not change faces, facial features,
expressions or identity in any way`: the model redraws the whole frame.

Probed — each changed only what it named:

```text
Make this scene a late evening: darker overall, warm light from a table lamp, deep blue night outside the window. Keep everything else unchanged: the person, the book, the cup, the cat, the furniture, the composition and the illustration style.
```

```text
Redraw this illustration as a loose watercolor painting with soft bleeding edges and visible paper texture. Keep the composition, the person, the cat, the cup and every object where they are.
```

```text
Switch this app screen to a dark theme with an emerald green accent instead of indigo. Keep the layout, every text label, the numbers and the chart exactly as they are.
```

Drift adds up: in a published test of 40 chained Sunburst edits, each saying
"keep everything else the same", the background visibly shifted by edit 11.
When the keep-list grows longer than the change, write one combined brief
from the original.

## Edit: remove or replace an object

```text
In this room photo, replace ONLY the grey fabric sofa with a cognac leather sofa of the same size. Preserve the camera angle, room lighting, floor shadows and all surrounding objects. Keep all other aspects of the image unchanged.
```

## Reference images: style, subject, composition

- Name the new pose and expression, or a person brings the reference's head
  angle and blank look along.
- What the references never showed, the model invents: add a reference, not
  words.
- A style reference carries composition too: in a probe, the round tiles of
  the reference icons appeared on the new icon despite `no tile`.

Probed: style transfer onto an icon with a transparent background.

```text
Image 1 is a style reference (color palette and rounded flat icon style). Image 2 is the subject.
Redraw the apple from Image 2 as a flat app icon in the visual style of Image 1.
Isolated icon on a fully transparent background, no tile, no shadow, no checkerboard.
```

## Product

Unprompted, the model "improves" a product: simplifies the cap, rewrites the
label. Keep shape and label in words; describe scene and light as mood.

```text
Image 1 is the product: a glass bottle of cold-brew coffee with a kraft label. Create a photorealistic product photograph of it outdoors at dusk on wet slate, light rain, soft rim light — moody and premium. Preserve the bottle's shape, cap, label text and exact proportions; do not alter the bottle in any way.
```

## Icon set

A whole set in one call keeps one style across all icons — separate calls
drift apart. Name the grid and list the icons in reading order; the style is a
feeling, not a spec. Cut the sheet into files with `scripts/slice_grid.py`
(`run.md`): a plain grid crop clips icons that cross the cell lines, and
asking for "generous space" in the brief did not stop that.

Probed: 16 cohesive soft-3D icons in the listed order, transparent background.

```text
Create a set of 16 app icons for a personal finance app, arranged in a 4×4 grid. Make them beautiful and cohesive: one shared style, soft 3D with gentle gradients, friendly and premium.

Icons: wallet, credit card, piggy bank, chart going up, coins, receipt, calendar, shopping bag, house, car, airplane, gift, bell, lock, settings gear, user profile.

Fully transparent background, no text, no grid lines.
```

## Logo

Describe the brand and the feeling, not the geometry. A generated logo is a
sketch for finding a form; a logo for the site is then redrawn as SVG.

```text
Create an original, non-infringing logo for "Field & Flour", a local bakery. It should feel warm, simple and timeless: clean vector-like shapes, a strong silhouette, balanced negative space, readable at small sizes. Fully transparent background, a single centered logo with generous padding, no backdrop, no checkerboard, no watermark.
```

## Series with one character

First a character image the owner approved; it goes in as Image 1 for every
next frame. The same keep-sentence, word for word, in every brief of the
series. Describe the new scene and pose explicitly.

```text
Continue the children's book story with the character from Image 1. Do not redesign the character: same round face, short red curly hair, green raincoat with yellow buttons, brown boots, same watercolor style and palette.
New scene: she kneels in a snowy forest after a storm, gently lifting a frightened squirrel out of a fallen tree, smiling at it. Warm and comforting mood. No text, no watermark.
```

## Sketch to image

Here the sketch owns the layout: `Turn this drawing into a photorealistic
image. Preserve the exact layout, proportions and perspective. Do not add new
elements or text.`

## Restoration, colorizing, "enhance"

Colorize old photos and edit faces with a 2.5 model: `gpt-image-2` ruined
faces in a published test. Add `Do not change faces, facial features,
expressions or identity in any way` and show the owner the result next to
the original. "Enhance" is a redraw, not recovered detail: for fidelity,
suggest a dedicated upscaler.
