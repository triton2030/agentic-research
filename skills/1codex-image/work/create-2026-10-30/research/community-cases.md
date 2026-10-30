# GPT Image: community cases beyond the labeled-spec template

Collected 2026-10-30. Every source below was opened on 2026-10-30; the date
in each case is the source's own publication date. Only content read on the
opened page is reported. Pages were read through a summarizing fetcher, so
quotes are short and some prompts are fragments. Where a prompt is long, the
case gives its shape and the parts that carry the technique.

## Evidence Labels

| Label | Meaning |
| --- | --- |
| **measured** | numbers from a described test: pixel or alpha statistics, counts, drift scores |
| **hands-on** | the author ran the prompts and shows or describes outputs; no metric |
| **official** | OpenAI docs, cookbook or forum staff |
| **vendor doc** | a reseller's or host's guide (Runware, Venice, APIYI); often careful, but tied to their own API wrapper |
| **anecdotal** | one person, one run, or a claim with no output shown |

## Model Landscape As Of 2026-10-30

- `gpt-image-2` (snapshot `gpt-image-2-2026-04-21`) shipped 2026-04-21. On
  this model, `input_fidelity` errors; the cookbook says its input fidelity
  is already high. Yet the cookbook's own edit examples still pass
  `input_fidelity="high"`, so the cookbook contradicts itself.[^cookbook][^mask-thread]
- `gpt-image-2.5-flare` (fast default) and `gpt-image-2.5-sunburst` (edit
  precision) shipped 2026-09-08. They add `quality` values `xhigh` and `max`.
  The 2.5 models support transparency.[^oai-guide][^transp-broken]
- Transparency on `gpt-image-2` came and went. It entered API preview on
  2026-08-20, then was discontinued around 2026-09-30/10-01. Forum users
  were told to move to the 2.5 family.[^transp-preview][^transp-broken]
- The official guide says: "Masking with GPT Image is entirely prompt-based".
  With several inputs, the mask applies to the first image.[^oai-guide]
- Known limits from the official guide: text can be imprecise, character
  consistency may drift, and precise layouts are hard. Complex prompts can
  take up to 2 minutes.[^oai-guide]

---

## 1. UI, App and Website Mockups

### 1.1 Exhaustive enumeration of chrome and exact labels

- **Model**: "GPT-Image" next to Nano Banana 2, from a WeChat author. The
  collection is gpt-image-2 era (April 2026). **hands-on**: outputs are shown
  side by side.[^zerolu]
- **Goal**: a mobile e-commerce home screen that reads as a real screenshot.
- **Prompt shape**, verbatim excerpts:
  > Generate a high-fidelity mobile e-commerce app homepage screenshot … The interface should look fully realistic …
  > Layout requirements:
  > - status bar with time 9:41, 5G signal, and battery icon
  > - … 10-icon function grid
  > - flash-sale module with countdown and three product cards
  > - "guess you like" two-column product waterfall with at least 6 product cards
  > - bottom tab bar with five tabs
  > Use these exact Chinese labels where appropriate: … bottom tabs: "首页、分类、购物车、消息、我的"
  > … should closely resemble a real app screenshot rather than concept art.
- **Technique**: list every module and its count, then give a label inventory
  per module in quotes. Close with "real screenshot, not concept art". The
  sibling music-player prompt adds exact numbers: time 18:26, progress
  01:42 / 04:18, and "5 to 7 scrolling lines" of lyrics. It ends with "feel
  like a real production interface rather than a Dribbble concept".[^zerolu]
- **Result**: the gallery shows readable CJK labels. No failures reported.

### 1.2 Structure before style; lock platform and chrome

- **Source**: the freestylefly/awesome-gpt-image-2 analysis pages
  (instagit). **anecdotal**: rules distilled from cases, no shown A/B.[^ff-ui-pitfalls][^ff-antipatterns]
- **Rules**:
  - Name the exact OS and device.
  - Lock the panel order ("header → sidebar → main content → footer").
  - "Explicitly list every visible text element verbatim."
  - Enumerate the chrome ("dark status bar with battery 85%", "bottom
    navigation with three icons (Home, Search, Profile)").
  - "Define functional constraints (platform, layout, text, chrome) before
    adding stylistic cues."
- **Failure named**: mixing platform traits, such as Twitter verification
  ticks in a TikTok mock, "creates unrealistic hybrid UIs". Style references
  can also make the model return a moodboard or process sheet; fix it by
  asking for one output explicitly.

### 1.3 Anchor screen as design-system reference for later screens

- **Source**: Higgsfield blog (Mariam Barova, 2026-04-30). Model: GPT Image
  2.0. **hands-on**, vendor platform.[^higgsfield]
- **Sequence**:
  1. Desktop landing page from text. The prompt opens "Modern dark minimal
     landing page for "CUE" — AI-powered recipe generator." It gives the
     exact headline "Cook with what you have", a subheadline, the input
     placeholder text, logo, palette, a mood line, and one hero metaphor.
  2. Mobile version: the same image as reference, ratio 9:16, **no new
     prompt**.
  3. Next screen: "@image_1 — visual style and design system reference for
     CUE app." / "Same design system as @image_1. Recipe result screen —
     title, cook time, …"
- **Result**: the author says text was rendered accurately. No failures
  reported, so treat this as a working recipe, not a stress test.

### 1.4 Multi-screen flow on one canvas

- **Source**: woshipm hands-on (2026-04-24, Chinese, gpt-image-2).
  **hands-on**.[^woshipm]
- **Prompt (fitness app)**: "生成一组 AI 健身运动 App 的界面设计，共4个屏幕横向排列"
  ("a set of four screens laid out horizontally"). It then describes each
  screen and ends with "所有文字使用中文" ("all text in Chinese").
- **Result**: consistent palette and type across the four screens, and
  Chinese "almost zero errors".
- **Follow-up trick (component extraction)**: "请提取这个 App 的所有 UI
  组件图，平铺在图片上，方便我切图使用" ("extract all UI components of this
  app, laid out flat, so I can slice them"). The output had buttons, cards,
  icons, nav bar and tags, but "needed adjusting" before it could serve as a
  spec.
- A Reddit post in r/PromptEngineering makes the same point: naming the
  screen count, the flow arrows and each screen's content "makes the output
  much more usable". **anecdotal**; the post's date is unclear in the
  snapshot.[^reddit-patterns]
- A community UI skill caps one canvas at four screens. Its reason is that
  consistency drops beyond that. **anecdotal**; I could not open the skill's
  reference file.

### 1.5 Device frames and aspect ratio

- The OpenAI cookbook's UI example asks to "Place the UI mockup in an iPhone
  frame". So the frame is opt-in by wording. To avoid it, just leave it out
  and describe a flat screenshot.[^cookbook]
- Astorie (app-store screenshots, vendor, no date) says "GPT Image 2 composes
  per aspect — re-cropping later breaks the device-frame composition." Its
  fix is to generate at the store size directly (1290x2796 etc.). It also
  generates with "no in-image headline text" and sets the headline
  downstream with another model. **vendor doc, anecdotal**.[^astorie]
- Dev.to guide (Jerry Zhang, May 2026): very tall full-page layouts "may get
  cropped at the bottom", and long strings still misrender. It gives the
  design system as concrete tokens ("Material Design 3 principles, Roboto
  font, 8px grid system"; hex colors). **anecdotal**.[^devto-web]

### 1.6 Very short prompts work when world knowledge carries the layout

- **Prompt**: "玄武门之变的朋友圈" ("a WeChat Moments feed for the Xuanwu
  Gate Incident"). Another: "Generate a UI design system for me in xx style,
  including web pages, mobile, cards, controls, buttons, and others". Both
  come from X posts collected in ZeroLu/awesome-gpt-image. **hands-on**:
  outputs are shown in the repo.[^zerolu]
- **Reading**: a familiar platform or genre can stand in for a long spec.
  Write long specs when the content is novel or must be exact.

---

## 2. Editing an Existing Image

### 2.1 Masks guide; they do not seal

- **Official**: "Masking with GPT Image is entirely prompt-based"; the mask
  must have an alpha channel and the same size as the image.[^oai-guide]
- **Forum test** (user _j, 2026-04-22, gpt-image-2, API). **hands-on**.[^mask-thread]
  - Prompt "Remove and infill the kitties that are marked."
  - Result: details outside the mask were kept "with high accuracy". But a
    yarn thread outside the mask was also edited: "The models don't have to
    obey, and don't."
  - Baseline: `gpt-image-1-mini` disobeyed the mask and reframed the image.
- **Forum analysis** (_j, 2026-05-25). **hands-on, partly speculative**.[^mask-analysis]
  - gpt-image-2 "receives no input transparency": transparent input areas
    were read as white.
  - The mask seems to be applied as transparency that "damages" the input,
    so the model may not see what is under the mask.
  - With a prompt asking for a car name, "The masked area - and logic - was
    exceeded".
- **Runware guide** (2.5 Flare; vendor doc).[^runware-mask]
  - "The mask makes the edit local, not sealed."
  - "Leave a margin between the white region and anything that must not
    move", because a mask drawn hard against a neighbour "invites the model
    to negotiate the shared edge".
  - Pad the mask for hair and soft edges.
  - "The mask chooses the region, the instruction chooses what happens
    inside it". So the prompt need not say "left".
  - "edit, then composite the protected element back over the result
    yourself."
- **Practical rule**: if pixels outside the edit must stay byte-exact, paste
  the original back outside the mask locally, after every edit.

### 2.2 Invariant lists: name the change, then name what survives

- **Cookbook** prompts, verbatim:[^cookbook]
  - "Remove the flower from man's hand. Do not change anything else."
  - Interior swap: "Preserve camera angle, room lighting, floor shadows, and
    surrounding objects."
  - Try-on: "Do not change her face, facial features, skin tone, body shape,
    pose, or identity in any way."
- **Runware iterative-editing guide** (vendor doc). Each pass names its own
  preserve list.[^runware-iter] Example:
  > Keep the lamp, its matte black shade, the green wall, the table, the floor, the framing and the lighting unchanged.

  Note that this list includes the *earlier* changes (the matte black shade,
  the green wall). The guide's rule is "Name the earlier changes in later
  instructions."
- **"3W1K" formula** (BestHub, 2026-06-06, Chinese). **anecdotal**: the
  latency figures it reports, 3.5–4 s, are implausible for gpt-image-2.[^besthub-iter]
  The formula: what to change + which attribute + what to keep + a strictness
  qualifier. Example:
  > 只将模特左手拿的手机从黑色改成银色，衣服纹理、背景大楼、姿势、表情、光影方向全部严格保持不变。

  ("Only change the phone in the model's left hand from black to silver; keep
  the clothing texture, background buildings, pose, expression and light
  direction strictly unchanged.")
- **Bulleted multi-edit** (Banani, Vlad Solomakha, Aug–Oct 2026). **hands-on**.[^banani]
  - The prompt opens "Edit this image with these changes:", followed by five
    bullets, one being "Remove the pink and yellow color streak/light trail
    effects entirely."
  - Result: all five changes landed, and layout and character were kept.
    Character consistency scored 3.5/5 because the face drifted over turns.

### 2.3 Drift over iterations: measured

| Test | Model | What was measured | Result |
| --- | --- | --- | --- |
| Morphed drift test, 2026-10-07[^morphed] | GPT Image 2.5 Sunburst Edit, medium, 1024² | 40 chained edits × 3 photos. Every prompt ended "Keep everything else in the image exactly the same." Mean RGB difference on untouched background patches | Mean 48.4 after 40 edits; crossed "visible" (10) at **edit 11**. Ideogram 4.5: 0.95; FLUX 3: 5.6 |
| Artificial Analysis via AlphaSignal, 2026-10-09[^aa] | GPT Image 2.5 Sunburst | 30 chained edits on one real-estate photo | Re-renders most of the frame each turn; about one fifth left unchanged; colour and texture drift compound |
| BestHub, Chinese, **anecdotal**[^besthub-iter] | gpt-image-2 | qualitative | Blur or colour shift after ~5 rounds; restart after 3–4 rounds and merge edits into one prompt |

- **Point**: the invariant sentence appeared in *every* Morphed edit, and
  drift still crossed the visible threshold. Restated invariants do not
  stop accumulation.
- **Counter-measures that the sources state**:
  - **Branch, don't chain.** Edit from the original or the last approved
    version, not from the latest output.[^morphed][^runware-iter]
  - **Restate once settled.** "chain while a human is still judging each
    round, and restate once the full list of changes is settled". Then
    regenerate from the original with one combined prompt.[^runware-iter]
  - **When to start over**: "An instruction stops landing", or "The list of
    things to preserve has grown longer than the change".[^runware-iter]
  - Keep `width`/`height` fixed for the whole chain, and keep every
    intermediate.[^runware-iter]
  - Watch for noise amplification. "repeated edits in the same chat can
    sometimes amplify artifacts"; regenerate from a fresh prompt rather than
    repairing.[^devto-infographic] The forum issue thread says the noise "is
    technical and cannot be fixed with prompting". Its tips are "Restart the
    session" and adding "LESS DETAILS".[^forum-issues]

### 2.4 ChatGPT edit path ≠ API edit path

- Forum, 2026-08-07 to 09-07. In ChatGPT, small edits redraw the whole image
  ("It always completely changes the art style"). OpenAI_Support confirmed
  that edits "can spread beyond" a selected area, with no timeline for a
  fix.[^forum-style]
- Forum, 2026-08-26/28. Users reported camera moves and new architecture,
  summed up as "Get 95% correct → attempt the final 5% → lose 30% of the
  previous work". Some also date a regression to about June 2026.[^forum-preserve]
- Reddit (r/aiwars, u/lucidity3K, May 2026). **anecdotal, contested**.[^reddit-edit]
  - Prompt "Change only the hat color. Do not change anything else."
    succeeded 0 of 5 times, with 99.7–99.97 % of pixels changed.
  - The author says the upload was resampled to 1536×1536.
- **Implication for an API skill**: these complaints are mostly about the
  ChatGPT hand-off. API results with masks are better (§2.1), but not
  pixel-safe.

---

## 3. Reference Images

### 3.1 Index and role labels

- **Cookbook**: "Place the dog from the second image into the setting of
  image 1, right next to the woman."[^cookbook]
- **Runware gpt-image-2 guide**: "Label references by index when there's
  more than one", e.g. "Image 1 is the scene to preserve. Image 2 is the
  style reference."[^runware-prompt]
- **Contradiction**: Runware's 2.5 Flare subject-consistency guide says
  "Reference order carries no meaning you can rely on". It advises: "Refer
  to each one by what it contains, not by its position in the array."[^runware-subject]
  - The two need not conflict. Safest is to say both, e.g. "Image 1 (the
    living room photo) is the scene; Image 2 (the brown dog) …".
  - The mask always goes to the *first* image.[^oai-guide]

### 3.2 Subject consistency across a series

- **Runware 2.5 Flare guide** (vendor doc).[^runware-subject]
  - "One reference is enough to establish a subject." "Three to five is the
    working range for one subject" when more angles are needed.
  - Keep one **preserve clause** as a single string in code, and append it
    word for word to every scene prompt. Example:
    > Keep the boot's two-tone olive and tan leather panels, its black lacing hardware, … its lace pattern and its lug sole exactly as they are in the references.
  - Failure modes:
    - A feature the references never showed gets invented: "The fix is
      another reference, not a longer prompt."
    - "A missing angle comes back as the wrong angle."
    - "The subject gets absorbed by the scene."
    - For exact content, "composite it afterwards".
- **Tech Stackups test** (2026-05-18/19, gpt-image-2 via `images.edit`).
  **measured** (pass/fail, time, cost).[^techstackups]
  - Placing a person with a cheek tattoo and green hair into a barista
    scene: identity kept, but the model copied the reference **head angle
    and blank expression**, so the result looked stiff.
  - Try-on with 4 references: jacket and bag matched; the glasses lost
    their distinctive details.
  - A 6-frame walk cycle generated as independent calls: **failed**, with
    style drift.
  - Ranking: third of four, behind FLUX.2 and Gemini 3.1 Flash.
  - About 200 s and $0.22 per edit.
  - **Lesson**: state the new pose and expression explicitly, or the
    reference pose leaks through.
- **Banani**: re-upload the reference images in later turns rather than
  relying on chat memory, because face drift grows with distance from the
  original.[^banani]
- **Cookbook (character)**: build an anchor image, pass it into every next
  page, and say "Do not redesign the character". Restate the character's
  details on each page.[^cookbook]

### 3.3 Style reference vs subject reference

- **Style reference**: "Use the same style from the input image and generate
  a man riding a motorcycle on a white background."[^cookbook]
  - In reference mode, composition is not guaranteed. Style may be adopted
    only partly; add "严格参考上传图片的风格" ("strictly follow the uploaded
    image's style"). **anecdotal**.[^besthub-iter]
- **Pencil playbook** (Emma Wilson, 2026-05-08, 12 brand scenarios).
  **hands-on**, no metrics.[^pencil]
  - Attaching the product image "worked better than describing it in text".
  - One photo was restyled into five styles (comic, risograph, linocut,
    neon line, indie animation), and the product stayed recognizable.
  - A 16:9 master was recomposed into 1:1, 4:5 and 9:16 with one resize
    prompt.
  - **Failure**: fonts are inferred, not reproduced. "Typography is the one
    area that will need a human eye."

---

## 4. Background Removal and Transparent Cutouts

### 4.1 Which path, by model (as of 2026-10-30)

| Path | Works on | Evidence |
| --- | --- | --- |
| Native `background="transparent"` + PNG/WebP | `gpt-image-2.5-flare`, `-sunburst`, `gpt-image-1.5`; **not** `gpt-image-2` since about 2026-10-01 (400 "Transparent background is not supported for this model.") | official guide; forum[^oai-guide][^transp-broken][^venice] |
| Key colour (green #00FF00 or magenta #FF00FF) + local removal | any model | community skill, APIYI, JXP[^imagegen2][^apiyi-green][^jxp] |
| Neutral grey backdrop + matting model (BRIA RMBG-2.0, BiRefNet) | any model | measured, LaoZhang[^laozhang] |

### 4.2 Native alpha: wording and measured quality

- **Prompt beats parameter.** The cookbook: "Prompt instructions take
  priority over `background="transparent"`."[^cookbook-transp]
- **Measured** (ofox/dev.to, 2026-08-24, `gpt-image-1.5`).[^owen]
  - The isolated-subject prompt "… isolated product cutout, no backdrop … no
    scene, no shadow" gave 67.3 % transparent pixels.
  - The same request "on a marble kitchen counter at sunrise" gave 43.5 %,
    with the scene partly knocked out.
- **Cookbook prompt fragments** (2.5 Flare default):[^cookbook-transp]
  - "Full object completely visible and generously padded."
  - "Preserve every natural transparency, refraction, translucent layer and
    fine material edge."
  - "Output an isolated object on actual fully transparent alpha; no
    backdrop, no rectangle, no plinth, no cast shadow".
  - Charts: "Keep the plot area, grid, and space between bars transparent."
- **Verify alpha in code.** Check that the mode is RGBA and read the alpha
  histogram (cookbook snippet). GPT Image returns opaque pixels at alpha
  **252–254, not 255**, so threshold at `>= 250` or `> 0`.[^cookbook-transp][^venice][^transp-preview]
- **Halo**: during the gpt-image-2 preview, users saw a thin grey border
  around stickers. A "white border" prompt made it worse. The proposed fix
  was client-side halo removal.[^transp-preview]
- **Fine-edge test** (LaoZhang, 2026-10-19, 2.5 Sunburst via proxy, one run
  per subject). **measured**.[^laozhang]
  - Native prompt suffix: "Transparent background. Isolated subject. No
    backdrop, no scenery, no checkerboard, no cast shadow."
  - **Curly hair**: native alpha was the best; flyaways kept, no halo on
    black, white or red. BRIA RMBG-2.0 left a faint grey fringe; u2net
    blurred the edges.
  - **Wine glass**: native alpha was flawed (mottled whitish film, mean
    alpha 97.5). Every cut-out kept grey inside the bowl, i.e. solid glass.
  - **Dandelion**: native alpha kept the filaments. BRIA and BiRefNet
    punched holes in the centre.
  - Clean-up: set alpha < 4 to 0 and > 250 to 255.
  - Licence: BRIA RMBG-2.0 is non-commercial; BiRefNet is MIT.
- **Runware (2.5 Flare)**: "A see-through subject comes back as a picture of
  transparency rather than as transparency". The glass bottle came back at
  opacity 0.83–0.99. Leave the shadow out "unless you own the layout it is
  going onto". Check every asset on a dark background.[^runware-transp]
- **Prompt-only "transparency"** without the parameter fails. The output is
  a painted checkerboard or near-white (JXP: alpha 255 everywhere). Forum
  users got checkerboards from the same prompt that "worked" for someone
  else.[^jxp][^transp-chatgpt]

### 4.3 Key colour

- **Community imagegen2 skill** (based on gpt-image-2):[^imagegen2]
  - Prompt "solid flat #ff00ff chroma-key background, no shadows, no
    gradients, no background objects".
  - Remove matching pixels locally, then **alpha-bleed** the hidden RGB of
    transparent pixels from nearby visible pixels.
  - Suppress key-coloured edge pixels (despill).
  - Fall back to `gpt-image-1.5` only when native alpha is required, and
    disclose which path was used.
- **JXP test** (2026-09-17, 2.5): flat #00FF00 came back at about (2,249,3),
  with a faint green tint at subject edges, a normal chroma-key limit.
  Choose green or magenta, not white. Hair was not tested.[^jxp]
- **APIYI** (2026-05-08): key colour is cheap (< 0.1 s) but "not ideal if
  your subject contains green tones". It recommends BiRefNet for hair and
  complex edges. **vendor doc**.[^apiyi-green]
- **Choice rule from the evidence**:
  - Hair, fur and fluff: native alpha, on a 2.5 model.
  - Glass: generate on the final background.
  - Flat icons and stickers: key colour or native alpha both work.
  - Pick the key colour absent from the subject, and always despill.

### 4.4 Sprite sheets

- One reported pattern is the source image plus a 1024² grid as a second
  reference. Expect an opaque background and "nonsensical" frame order.
  Crop each frame, remove its background separately, normalize to a fixed
  cell and anchor point, and reorder by hand. **anecdotal**.[^besthub-sprites]

---

## 5. Text, Infographics, Posters, Slides

### 5.1 Exact-text locking

- Quote verbatim strings, and add a no-extra-text clause:
  > Render every line of text verbatim, exactly as written, no extra characters, no other text anywhere in the frame.

  Spell unusual words letter by letter; text left unquoted may be
  rewritten.[^runware-prompt]
- Cookbook (ads): "Render the tagline exactly once, clearly and legibly,
  integrated into the ad layout." and "No extra text, no watermarks, no
  unrelated logos."[^cookbook]
- Use `quality` high for small or dense text; medium is enough for large
  headlines.[^runware-prompt][^cookbook] Simon Willison's dense "Where's
  Waldo" scene only became solvable at `--quality high --size 3840x2160`
  (13,342 output tokens, about $0.40).[^willison]
- State the script language: "所有文字使用中文" ("all text in Chinese").[^woshipm]

### 5.2 Failure envelope

- Kittl (gpt-image-2, about 200 prompts, vendor scale): "Extremely dense
  text blocks (100+ words) can introduce occasional letter swaps in the
  final lines". "Decorative scripts with heavy ligatures sometimes merge
  incorrectly." The review says Cyrillic renders accurately, but publishes
  no Cyrillic sample. **vendor, partly measured**.[^kittl]
- Crepal (Dora, 2026-05-05, product labels): multi-line fine print drifts.
  Two of five candle variants needed a second pass for label position. The
  in-session fix was "The label reads [exact text] — keep everything else
  the same." **hands-on**.[^crepal]
- Over-detail: GPT Image 2 tends to fill labels, connectors and panels with
  grain. Ask for "clean flat regions, restrained background detail,
  consistent lighting, minimal texture". **anecdotal**.[^devto-infographic]
- Cap the number of modules, and keep long prose out of infographic modules.
  **anecdotal**.[^ff-antipatterns]

### 5.3 Data and fact accuracy (charts, maps)

- Peter Surguy (ChatGPT Images 2, April–May 2026). **hands-on**, checked
  against the source data.[^surguy]
  - Text and layout were good.
  - The charts had errors: an invented 17th point, swapped series labels,
    a region in the wrong place, and bars at about 2× their true length.
  - Instant mode silently skipped web search and invented facts.
  - Staging (summarize → gather → draw) plus the correction "redraw the
    image, based around the information that you got from the web" fixed
    the content.
- The cookbook agrees: verify labels and values, and render charts
  deterministically when precision matters.[^cookbook-transp]
- **Rule**: put the real numbers in the prompt (cookbook §4.10), and draw
  precise charts in code. Use the model for illustrative graphics.

### 5.4 Translation inside an existing image

- "Translate the text in the infographic to Spanish. Do not change any
  other aspect of the image."[^cookbook]
- Comic variant: "placing the translated text in the original speech bubble
  positions".[^anil]

---

## 6. Product, Logos and Icons, Sketch-to-Render, Style Transfer, Restoration, Enhance

### 6.1 Product photography

- Preserve clause: "Preserve the bottle's shape, cap, label, and exact
  proportions; do not alter the bottle in any way." Without one, products
  get "improved": a simplified cap, a rewritten label.[^runware-prompt]
- Isolated product: "Do not restyle the product; remove the background and
  preserve clean alpha transparency."[^cookbook]
- Scale in a scene: "the product takes up roughly 40% of the frame,
  positioned slightly left of center". Complex mascot logos are only
  approximated.[^crepal]
- Fixing a label: the correction prompt plus the product reference image
  fixed a label that another model had broken. It then held across three
  scenes.[^pencil]
- Rewarx (45 images): fine textures were smoothed; glossy and transparent
  surfaces showed inconsistent reflections. It publishes no numbers.
  **weak**.[^rewarx]

### 6.2 Logos and icons

- Describe the brand personality and ask for a simple mark. Use "Fully
  transparent background", `n=4` for variations, and PNG output.[^cookbook]
  On 2.5 or 1.5, use native alpha (§4).
- Output is raster, so trace to SVG yourself. Treat it as ideation, not a
  final identity system. **anecdotal**.[^crepal]

### 6.3 Sketch or wireframe to render

- "Turn this drawing into a photorealistic image." plus "Do not add new
  elements or text."[^cookbook]
- A rough wireframe sketch used as a layout brief produced a finished
  poster ad.[^pencil]
- "Convert this wireframe into a high-fidelity e-commerce product page
  UI."[^devto-web]

### 6.4 Restoration and colorization

- Anand (2026-09-09): "Convert this image to color." on his parents'
  wedding photo. GPT Image 2 "messed up the faces". GPT Image 2.5 did better
  than Gemini 2.5 Flash. **hands-on**, judged by someone who knows the faces
  well.[^anand]
- **Implication**: on face-critical restoration, use a 2.5 model. Add an
  identity lock (the cookbook's try-on wording) and compare side by side.

### 6.5 "Enhance" and upscale-like edits

- Dev.to (Cuiyun Luo, April 2026): outputs "look great… until you zoom in".
  The model favours semantic correctness over pixel detail, and upscaling
  the raw output gave artifacts. The author used a dedicated upscaler.
  **anecdotal, promotional**.[^cuiwomie]
- No source opened shows gpt-image-2 doing faithful super-resolution. Expect
  re-rendering, not enhancement.

---

## 7. Prompt Length, Format and Language

| Question | What the opened sources show | Strength |
| --- | --- | --- |
| Short or long | The cookbook says start from a clean base prompt and add one change at a time.[^cookbook] One-line prompts succeed when a familiar genre or platform defines the layout (§1.6).[^zerolu][^woshipm] Long spec prompts win for novel or exact content (§1.1). The DetailMaster paper (gpt-image-1, not 2) found adherence degrades as prompts grow | hands-on; no gpt-image-2 A/B found |
| Labeled spec or prose | No controlled comparison found. Vendor guides prefer named sections; the freestylefly repo uses JSON for automation, not for quality | anecdotal |
| JSON | Runware: "JSON prompts are most useful when you're generating images programmatically". Swap single keys (`scene`, `lighting`) while keeping the rest fixed[^runware-prompt] | vendor doc |
| Negatives | There is no negative-prompt parameter. "negative prompt: bananas" appended to the prose works as text[^runware-prompt]. Positive phrasing is suggested over negations in ChatGPT edits[^forum-preserve] | vendor doc / anecdotal |
| Repetition | Repeating key prompt parts "can strengthen part of or the entire prompt" (forum, citing a paper)[^forum-issues] | anecdotal |
| Language | Write on-image text in the target script and name the language. CJK is reported reliable; Cyrillic is claimed accurate (Kittl) but unshown. No evidence that a non-English *instruction* language helps or hurts | anecdotal |
| Prompt rewriting | Mainline models revise the prompt and return `revised_prompt`[^oai-guide]. In ChatGPT, suppress enhancement with "(don't change the prompt, send it as it is.)"[^forum-issues] | official / anecdotal |
| Budget | The prompt limit is 32,000 characters[^runware-prompt] | vendor doc |

---

## Gaps

> [!question] No controlled A/B on prompt format or length for gpt-image-2 or 2.5
> I found no study comparing labeled spec, prose and JSON, or short and
> long prompts, on these models. Claims in §7 are practice, not measurement.

> [!question] Hair and fur with key colour, and despill quality
> No opened source measured green or magenta keying on hair against native
> alpha. LaoZhang measured only a grey backdrop with matting models.

> [!question] Cyrillic text accuracy
> Kittl's claim has no published sample, so a Cyrillic probe set would be
> needed before relying on it.

> [!question] Drift on plain gpt-image-2 and 2.5 Flare
> The chained-edit measurements cover only 2.5 Sunburst. CometAPI cites a
> "Tosea" three-round drift figure for Flare, Sunburst and gpt-image-2, but
> its two pages disagree, and I did not open the original test.

---

[^cookbook]: OpenAI Cookbook, "GPT Image Generation Models Prompting Guide", https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide — undated, gpt-image-2 examples; opened 2026-10-30.
[^cookbook-transp]: OpenAI Cookbook, "Generate Transparent Image Assets for Campaigns and Presentations", https://developers.openai.com/cookbook/examples/multimodal/transparent-image-assets-for-campaigns-and-presentations — originally 2026-08-20 for gpt-image-2; now defaults to gpt-image-2.5-flare; opened 2026-10-30.
[^oai-guide]: OpenAI API docs, Image generation guide, https://developers.openai.com/api/docs/guides/image-generation — current (2.5 Flare/Sunburst), opened 2026-10-30.
[^mask-thread]: OpenAI Community, "GPT Image 2 Masking Issue", https://community.openai.com/t/gpt-image-2-masking-issue/1379510 — 2026-04-22.
[^mask-analysis]: OpenAI Community, "Understanding how gpt-image models on edits see 'mask' and transparency", https://community.openai.com/t/understanding-how-gpt-image-models-on-edits-see-mask-and-transparency/1381752 — 2026-05-25.
[^transp-preview]: OpenAI Community, "Transparent backgrounds are now available in preview for GPT-Image-2 in the API", https://community.openai.com/t/transparent-backgrounds-are-now-available-in-preview-for-gpt-image-2-in-the-api/1391541 — 2026-08-20 to 09-16.
[^transp-broken]: OpenAI Community, "Is transparent background support broken in GPT-image-2?", https://community.openai.com/t/is-transparent-background-support-broken-in-gpt-image-2/1402707 — 2026-10-01.
[^transp-chatgpt]: OpenAI Community, "Having trouble getting transparent backgrounds in ChatGPT images", https://community.openai.com/t/having-trouble-getting-transparent-backgrounds-in-chatgpt-images/1380143?page=3 — 2026-05-10 to 05-16.
[^forum-issues]: OpenAI Community, "Collection of GPT-image-generator 2.0 issues, bugs, and work-around tips", https://community.openai.com/t/collection-of-gpt-image-generator-2-0-issues-bugs-and-work-around-tips-check-first-post/1379535 — first post 2026-04-22 (Daller).
[^forum-style]: OpenAI Community, "Image generator completely rewriting the style lately", https://community.openai.com/t/image-generator-completely-rewriting-the-style-lately/1389510 — 2026-08-07 to 09-07.
[^forum-preserve]: OpenAI Community, "How to preserve images during edits?", https://community.openai.com/t/how-to-preserve-images-during-edits/1392634 — 2026-08-26 to 08-28.
[^runware-prompt]: Runware, GPT Image 2 prompting guide, https://runware.ai/docs/models/openai-gpt-image-2/guides/prompting — undated; opened 2026-10-30.
[^runware-iter]: Runware, GPT-Image-2.5 Flare iterative editing, https://runware.ai/docs/models/openai-gpt-image-2-5-flare/guides/iterative-editing.md — undated.
[^runware-subject]: Runware, GPT-Image-2.5 Flare subject consistency, https://runware.ai/docs/models/openai-gpt-image-2-5-flare/guides/subject-consistency.md — undated.
[^runware-mask]: Runware, GPT-Image-2.5 Flare masked editing, https://runware.ai/docs/models/openai-gpt-image-2-5-flare/guides/masked-editing.md — undated.
[^runware-transp]: Runware, GPT-Image-2.5 Flare transparent backgrounds, https://runware.ai/docs/models/openai-gpt-image-2-5-flare/guides/transparent-backgrounds.md — undated.
[^venice]: Venice docs, transparent backgrounds, https://docs.venice.ai/guides/media/transparent-backgrounds — undated.
[^morphed]: Morphed, "AI image editor drift test" (Bilal Azhar), https://morphed.app/blog/ai-image-editor-drift-test — 2026-10-07.
[^aa]: AlphaSignal, "Artificial Analysis Runs 30 Edits to Expose How Image Models Drift", https://alphasignal.ai/news/artificial-analysis-runs-30-edits-to-expose-how-image-models-drift — 2026-10-09 (original on X, not opened).
[^techstackups]: Tech Stackups, character consistency comparison, https://techstackups.com/comparisons/gemini-vs-openai-vs-flux-vs-runway-character-consistency-may-2026/ — 2026-05-18/19.
[^banani]: Banani, "GPT Image 2 Tutorial, Prompts and Review for AI PMs" (Vlad Solomakha), https://www.banani.co/blog/gpt-image-2-generator-review — byline 2026-08-03, metadata 2026-10-22.
[^higgsfield]: Higgsfield, "Build a Full Marketing Stack for Your App — Full Prompts" (Mariam Barova), https://higgsfield.ai/blog/marketing-studio-video-2 — 2026-04-30.
[^woshipm]: 人人都是产品经理, "实测 GPT-Image-2:6 个能落地的提效场景", https://www.woshipm.com/?p=6383134 — 2026-04-24.
[^zerolu]: ZeroLu/awesome-gpt-image README, https://github.com/ZeroLu/awesome-gpt-image — read via raw README on 2026-10-30; entries cite X and WeChat posts from April 2026.
[^anil]: Anil-matcha/Awesome-GPT-Image-2-API-Prompts, https://github.com/Anil-matcha/Awesome-GPT-Image-2-API-Prompts — opened 2026-10-30.
[^ff-ui-pitfalls]: instagit analysis of freestylefly/awesome-gpt-image-2, "UI screenshot prompt pitfalls", https://instagit.com/freestylefly/awesome-gpt-image-2/ui-screenshot-prompt-pitfalls-and-avoidance/ — undated.
[^ff-antipatterns]: instagit, "Common Pitfalls and Antipatterns in GPT-Image2 Prompts", https://instagit.com/freestylefly/awesome-gpt-image-2/antipatterns-pitfalls-avoid-gpt-image-2-prompts/ — undated.
[^reddit-patterns]: r/PromptEngineering, "A few GPT Image 2 prompt patterns that worked better than I expected" (snapshot), https://reddit.sentinel-team.org/posts/1sv32te/snapshots/2026-05-01T21%3A40%3A57.156317Z — snapshot 2026-05-01.
[^reddit-edit]: r/aiwars, "ChatGPT Images 2.0 'Editing' Does Not Match the Observed Behavior" (snapshot), https://reddit.sentinel-team.org/posts/1t90jmb/snapshots/2026-05-15T22%3A48%3A21.97629Z — snapshot 2026-05-15.
[^astorie]: Astorie (ex-Martini), "How to Create AI App Store Screenshots with GPT Image 2", https://astorie.ai/how-to/create-app-store-screenshots/gpt-image-2 — undated (© 2026).
[^devto-web]: DEV, "How to Use GPT Image 2 to Generate Web Design" (Jerry Zhang), https://dev.to/jerry_zhang_3ce3c83791c57/how-to-use-gpt-image-2-to-generate-web-design-a-complete-guide-12o3 — May 6 (2026).
[^devto-infographic]: DEV, "Why GPT Image 2 Infographics Often Look AI Generated", https://dev.to/jacob_is_surfing/why-gpt-image-2-infographics-often-look-ai-generated-2eeh — Jun 3 (2026).
[^besthub-iter]: BestHub, "Master GPT-Image-2: Multi-Round Iteration, Local Editing, Batch Generation, Reference Images", https://www.besthub.dev/articles/master-gpt-image-2-multi-round-iteration-local-editing-batch-generation-reference-images-9ce1e928ce6c — 2026-06-06.
[^besthub-sprites]: BestHub, "Creating Perfect Game Sprites with GPT-Images 2.0", https://www.besthub.dev/articles/creating-perfect-game-sprites-with-gpt-images-2-0-a-step-by-step-guide-e3f99dbeb314 — 2026-04-23.
[^pencil]: Pencil Community, "Playbook: GPT Image 2.0 for Creative Work" (Emma Wilson), https://community.trypencil.com/public/blogs/gpt-image-20-for-creative-work-2026-05-08 — 2026-05-08.
[^laozhang]: LaoZhang AI Blog, "AI Transparent Background Test: Glass, Hair and Fine Edges", https://blog.laozhang.ai/en/posts/ai-transparent-background-glass-hair-test — 2026-10-19.
[^jxp]: JXP, "GPT Image 2.5 Transparent Background: Does It Really Work?", https://www.jxp.com/gpt-image/blog/gpt-image-2-5-transparent-background — 2026-09-17.
[^owen]: DEV (ofox), "'Transparent Background Is Not Supported for This Model': 3 Fixes", https://dev.to/owen_fox/transparent-background-is-not-supported-for-this-model-3-fixes-5b1l — tests 2026-08-24.
[^apiyi-green]: APIYI help, "gpt-image-2 transparent background not supported", https://help.apiyi.com/en/gpt-image-2-transparent-background-not-supported-en.html — 2026-05-08.
[^imagegen2]: Community skill "imagegen2" SKILL.md, https://claudskills.com/skills/imagegen2/SKILL.md — undated; its reference.md was not opened.
[^kittl]: Kittl, "Kittl Review: GPT Image 2", https://www.kittl.com/blogs/kittl-review-gpt-image-2-0/ — 2026-05-06 / 09-02.
[^crepal]: Crepal, "How to Use GPT Image 2 for Product Mockups" (Dora), https://crepal.ai/blog/aiimage/image-how-to-use-gpt-image-2-for-product-mockups/ — 2026-05-05.
[^rewarx]: Rewarx, "I Tested GPT-Image-2 Against Real Product Photos", https://www.rewarx.com/blogs/gpt-image-2-vs-real-product-photos — undated; vendor.
[^surguy]: Peter Surguy, "ChatGPT infographics", https://surguy.net/articles/chatgpt-infographics.html — after 2026-04-21.
[^willison]: Simon Willison, "gpt-image-2", https://simonwillison.net/2026/Apr/21/gpt-image-2/ — 2026-04-21.
[^anand]: S Anand, "Converting Black and White Photos to Color with GPT Image 2.5", https://www.s-anand.net/blog/2026/09/09/ — 2026-09-09.
[^cuiwomie]: DEV, "I built an AI image workflow with GPT Image 2.0, fixing its biggest flaw" (Cuiyun Luo), https://dev.to/cuiwomie/i-built-an-ai-image-workflow-with-gpt-image-20-fixing-its-biggest-flaw-4kf6 — Apr 24 (2026).
