---
name: 1codex-image
description: >-
  Use when a raster image must be made or changed: generate, edit, recolor,
  restyle, combine references, cut out a background, mock up a UI screen, or
  draw an icon set. Recraft by name: 1recraft.
---

# 1codex-image — a brief the image model can draw from

## Context

Raster images here are made by OpenAI GPT Image with the owner's API key; it
is his main image route. Recraft only when he names it (`1recraft`), Codex
only when he names it (`1codex`).

A bad image almost always comes from the prompt. Agents write it out of habit
as a technical spec: where each thing sits and what is under what, pixel
sizes, a color for every element, "no other text". The image model is a
strong designer, and from a spec it draws exactly the dictated skeleton and
nothing more. The owner calls this the most frequent mistake agents make with
images. One probe on the same video editor screen: a brief saying "make it
beautiful" plus a list of what must be there gave a rich professional
workspace; a spec with positions, pixels, hex colors and "no other text" gave
an empty frame with five labels.

The model also does far more than draw from scratch. It edits an existing
image from words: recolors it, makes it darker or lighter, changes the time of
day or the art style, switches a UI to a dark theme while keeping its text and
layout, removes or replaces objects, moves an object from one image into
another, draws a new screen in the style of a screenshot, and returns an
object on a transparent background. It also draws a whole cohesive icon set in
one call: 16 icons in a 4×4 grid on a transparent background. Reach for this
before saying "that can't be done". Changing an existing flat graphic, or an
exact chart from data, stays local or in code: the model would redraw it.

## Task

Write a short brief that gives the model the purpose, the feeling and what
must be there, and leaves the rest to its imagination; run it per
[run.md](references/run.md) and check the result.

## Goal

An image that serves its purpose and shows the model's own design taste —
often better than anything the brief could spell out. The owner uses this
model for its imagination: complex designs, icons, whole icon sets. In his
experience, the longer and more detailed the brief, the worse the image. Pin
only what he pinned: exact text, a brand color, what an edit must preserve.

## When you write a brief for a new image

The order joins the owner's rule with the examples in OpenAI's GPT Image 2.5
prompting guide:

1. What it is and what for, in one sentence: `A desktop video editing app for
   a product called "Cutline" — the main editing workspace.` OpenAI's examples
   open with `Create a …`. The intended use sets the model's mode and level of
   polish.
2. The impression — quality, mood, style, palette in words:
   `Make it beautiful: a modern, premium professional tool with a
   design-award level of polish. Dark theme with one vivid accent color.`
   OpenAI's anchor phrase for UI is `It should look like a real,
   well-designed, beautiful app`; for photos, write `photorealistic`.
3. `It should include:` — a list of what must be in the image, as things, not
   places. For a complex UI: the windows and panels and what each shows. Name
   what matters most in words of hierarchy: `the headline as the largest
   element`.
4. Exact text only where the owner needs it, in quotes. Other labels the
   model invents plausibly — so for a UI, do not add `no other text`.
5. Short output conditions: `Flat screenshot of the app window only, no
   device frame`.

Test before sending: if a line of the brief says where something sits, what
it is under, or how many pixels it takes, and the owner never said so, delete
it. Every such line takes a decision away from the model, and what it was
told to leave out it will not draw. If the owner dictated a layout, keep his
layout as he gave it, in English.

Length: probed briefs that worked ran 65–150 words for a new image and 30–40
for an edit; a brief grows only with the number of items, never with a
description of layout.

Write the brief in English, as all of OpenAI's examples are; the guide sets no
language. Labels go in the language they need on the image — Russian text came
out letter-perfect in probes. A number the model has to compute itself may
come out wrong (a probe got a budget total wrong): give important numbers
ready-made.

## When you edit an existing image

The image goes in as Image 1. The brief states the target state in plain
words, then `Keep everything else unchanged:` and what the owner needs kept,
including what earlier edits changed — or the next edit rolls them back. Do
not describe the whole picture again. A simple change of condition takes one
sentence: `Make it look like a winter evening with snowfall.`

The model redraws the whole picture, not just the changed part: details drift,
and they drift more with every chained edit. Edit from the last approved
version, not from the latest output; when the keep-list grows longer than the
change, write one combined brief from the original. When pixels outside the
change must stay exact, paste the original back over them locally.

## When you pass reference images

Give each one a number and a role in one phrase — `Image 1 is a screen of the
"Ledgerly" app — use it only as the design reference`, `Image 2 is the
subject` — and say what goes where: `Place the dog from Image 2 into Image 1`.
A new screen of an existing product is drawn from a screenshot of its current
screen: words cannot carry a live product's style. No screenshot at hand —
capture the running screen or ask the owner for one.

## When you need a transparent background

Read [transparent.md](references/transparent.md) first: it decides whether
the model is needed at all, which models can do it, and the brief's wording.

## Reference files

- Every call: [run.md](references/run.md) — command, model, quality, size,
  cost, what to do when a call fails.
- Before the brief of your case: the example in
  [prompts.md](references/prompts.md) — complex UI, next screen, illustration
  and photo, poster and slide, edits, references, product, logo, character
  series, icon set, restoration.
- Size or quality the script rejects, `xhigh`, `max`: [api.md](references/api.md).

## When the image arrives

Open the image and check it against the request: every item of the list is
there, exact text matches letter by letter, an edit kept what it had to. Tell
the owner about a miss and fix it with one change to the brief: every attempt
is paid.
