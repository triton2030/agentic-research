# Design Review Questions

Answer in Russian. Keep the structure below. Use screenshot filenames or
manifest ids as evidence. If a question is not answerable from the screenshots,
write `не проверено по скриншотам`.

## Verdict

1. Is this screen ready to ship visually, or does it need another design pass?
2. What are the top 3 issues by user-visible severity?
3. What should be fixed first if only one hour is available?

## Space And Density

1. How much free space is visible on each major screen state: too little, enough,
   too much, or uneven?
2. Is the empty space doing useful grouping and hierarchy work, or does it look
   accidental?
3. Are there places where whitespace is large but the screen still feels busy?
4. Are vertical rhythm, section spacing, and edge padding consistent across the
   scroll?
5. Does any content feel cramped against viewport edges, cards, toolbars, or
   neighboring elements?

## Spacing And Padding Logic

1. For each spacing problem, is the right fix to add air, reduce dead air,
   redistribute gaps, align/symmetrize edges, or standardize the rhythm?
2. Do spacing and padding values look like a deliberate scale or token system,
   or do they look like unrelated one-off numbers?
3. Are related elements closer to each other than to unrelated elements, so
   proximity supports the meaning instead of flattening all content into equal
   distance?
4. Do repeated cards, rows, sections, and controls follow a stable spacing
   rhythm, or do similar blocks drift by a few pixels without intent?
5. Are left/right and top/bottom insets symmetrical where symmetry is expected,
   and intentionally asymmetrical where the composition needs it?
6. Do larger gaps clearly signal a section break, priority shift, or breathing
   room, or do they create accidental holes between content that should stay
   connected?
7. Does each container's internal padding match its scale, density, corner
   radius, and content weight?
8. Are cards, pills, badges, chips, and buttons given enough inner breathing
   room for their rounded corners, or do large radii make the content feel
   pinched against the curved edges?
9. Is the dashboard or dense surface using a chosen density mode, such as
   compact, comfortable, or spacious, or is density changing randomly between
   modules?
10. Are gaps inside a semantic group smaller than gaps between groups, and are
   section gaps larger than card/content gaps?

## Text Load

1. Is the screen overloaded with text for its job?
2. Can a user understand the screen in 3-5 seconds from headings, labels, and
   visible structure?
3. Do headings and subheadings form a correct meaning structure: page promise,
   section idea, supporting explanation, then details?
4. Does the subheading clarify the heading, or does it introduce a competing
   message?
5. Are paragraphs, helper text, badges, captions, or labels competing for
   attention?
6. Does the amount of text change logically between desktop and mobile?
7. Are there repeated phrases or explanatory text blocks that should become
   labels, shorter copy, or progressive disclosure?

## Hierarchy And Typography

1. Is the ratio between headline size, subhead size, body text, captions, and
   controls logical?
2. Are headings oversized inside compact panels, cards, sidebars, or dashboards?
3. Are there weak headings that should be stronger because they own a section?
4. Is line length comfortable on desktop and mobile?
5. Are font weights, sizes, and spacing used to create hierarchy, or are they
   used decoratively?
6. Are there too many nearby font sizes, weights, letter-spaced labels, numerals,
   and body styles, creating visual dirt instead of clear hierarchy?
7. Do font family, font face, weight, width, style, and optical size choices feel
   like one coherent type system, or do weight changes read like unrelated
   fonts?
8. Is there enough typographic variety to create hierarchy and character without
   making the interface feel like it uses many typefaces?

## Visual Weight And Attention

1. Does visual weight match semantic priority: size, contrast, position, color,
   depth, and motion should make the most important thing feel most important?
2. Is every large element large for a reason, or is it visually louder than its
   meaning deserves?
3. Does any secondary text, decoration, badge, card, illustration, metric, or
   control compete with the main message or primary action?
4. Does the design guide attention through the intended sequence of reading,
   understanding, and action?
5. Are hierarchy exceptions intentional and useful in context, or do they look
   like accidental emphasis?
6. Do equal-sized cards, panels, or modules imply equal importance, and is that
   implication true for the content?

## Information Model And Containers

1. Is the chosen container model right for the information: card grid, list,
   table, priority stack, timeline, split panel, or dashboard module?
2. If the design uses many similar cards, do those cards actually carry similar
   kinds of information, actions, density, and urgency?
3. Are semantically related items placed near each other, or are similar items
   separated by unrelated modules that interrupt comparison and scanning?
4. Do some containers feel empty while others are text-heavy, chart-heavy, or
   action-heavy without a clear reason?
5. Does the layout let the user compare and triage information quickly, or does
   every card require a separate decoding effort?
6. If the selected pattern is wrong for the content, say so directly and explain
   why the structure is a poor fit rather than only listing local polish fixes.

## Composition

1. Is there a clear primary focal point in each viewport?
2. Does the eye path move through the screen in the intended order?
3. Are groups aligned and sized consistently?
4. Do repeated components have stable dimensions, or do they visually jump?
5. Are section transitions understandable in the bridge screenshots between
   sections?

## Gestalt Grouping And Alignment

1. Are related elements grouped by proximity, similarity, common region,
   alignment, or continuity in a way that matches their meaning?
2. Are unrelated elements separated clearly enough, or do they appear to belong
   together by accident?
3. Do section starts, content columns, card edges, and text blocks share stable
   alignment axes across the scroll?
4. Is there subtle alignment drift between sections, such as one section being
   slightly offset from the previous one without a clear reason?
5. Are there floating or orphaned elements that do not visually belong to a
   group?
6. Are asymmetries, broken grids, or unusual spacing choices justified by the
   content, or do they weaken the structure?

## Visual Noise

1. Are there too many colors, gradients, shadows, borders, outlines, badges,
   icons, dividers, or decorative elements?
2. Is there card-inside-card nesting or stacked framed surfaces that make the UI
   feel heavy?
3. Do backgrounds, images, or effects help the task, or are they ornamental
   noise?
4. Is the palette balanced, or does the page collapse into one dominant hue
   family?
5. Are icons meaningful and recognizable, or are they used as decoration?

## Surface Details And Badges

1. Do badges, pills, chips, buttons, and small status elements communicate
   status, action, selection, or metadata clearly?
2. Are local details crisp and proportionate to the component's role, or are
   they visually louder than the information they support?
3. Are borders, shadows, fills, and outlines consistent with the element's
   meaning and interaction state?
4. Do hover, selected, disabled, loading, and inactive affordances look plausible
   where they are visible?
5. Do small decorative surfaces add useful status, grouping, or affordance, or
   do they create local noise that distracts from the content?

## Consistency And System Logic

1. Are repeated colors, components, borders, shadows, icons, and
   typographic treatments used consistently for the same meaning?
2. Do similar things look similar and different things look different enough?
3. Are there one-off visual decisions that do not connect to the rest of the
   system?
4. Does repetition create a predictable design language, or does it make the
   page feel monotonous and undifferentiated?
5. Where consistency is broken, is the break justified by a real change in
   meaning, state, importance, or task?

## Spatial Balance

1. Is the screen balanced vertically and horizontally, or does one side/top/bottom
   feel accidentally heavy or empty?
2. Are top and bottom spacing, left and right padding, and section insets
   symmetrical where symmetry is expected?
3. When spacing is intentionally asymmetrical, does it improve hierarchy,
   grouping, or flow?
4. Do sticky headers, sidebars, cards, and floating controls create balanced
   negative space, or do they leave awkward gaps?
5. Does the visual center of the composition match the user's intended focus, or
   is attention pulled to an unimportant area?

## Interaction States

1. For each clicked/expanded screenshot, is the changed state obvious?
2. Do menus, dialogs, drawers, tabs, and selected states feel spatially connected
   to the trigger?
3. Does the interaction introduce layout shift, crowding, or accidental overlap?
4. Are pressed, selected, disabled, loading, empty, and error states visually
   plausible where captured?
5. Does the UI still make sense after animation settles?

## Mobile Scroll

1. Does each mobile viewport work as a real human scroll moment, not just as a
   cropped desktop layout?
2. Are tap targets, sticky bars, nav, drawers, and primary actions comfortable?
3. Does any text wrap badly, overflow, or create awkward isolated words?
4. Are section starts and ends clear while scrolling?
5. Are important actions visible at the right time, or do they disappear below
   the fold too early?

## Responsiveness

1. What changes between desktop and mobile are improvements, and what changes
   are regressions?
2. Does the design preserve the same information hierarchy across viewports?
3. Are images, tables, charts, cards, and grids resized deliberately?
4. Does any layout rely on desktop-only horizontal space?
5. Are there desktop screenshots that look good only because the viewport is
   wide?

## Brand And Taste

1. Does the interface feel specific to its product/domain, or generic?
2. Does it look like a usable product surface rather than a marketing collage?
3. Is the style restrained where the workflow needs scanning and repetition?
4. Is there any obvious AI-generated sameness: decorative gradients, generic
   cards, vague icons, empty polish, or visual filler?
5. What one design decision gives the screen the most character?

## Beauty And Creative Vitality

1. Is the interface visually alive, memorable, and desirable enough for its
   product context, or is it merely clean and correct?
2. Does restraint improve trust and scanning, or has it become blandness,
   sameness, or low-energy design?
3. Is there a purposeful creative idea in composition, typography, color,
   interaction, imagery, data display, or rhythm?
4. Do recommendations preserve or strengthen character, or would they flatten the
   screen into a generic dashboard?
5. Is boredom itself a user-visible design problem here? If yes, explain what
   kind of creative move would add energy without harming usability.

## Accessibility From Visual Evidence

1. Are contrast risks visible?
2. Are focus order, keyboard support, and screen-reader behavior not checkable
   from screenshots? Name those gaps instead of guessing.
3. Are text sizes, target sizes, and hit areas visually safe?
4. Are important states communicated by more than color alone where visible?
5. Is motion likely to distract or obscure the settled state?

## Fix Recommendations

1. List concrete fixes in priority order.
2. For each fix, say whether it is a spacing, typography, layout, content,
   color, component, hierarchy, alignment, grouping, consistency, interaction,
   or responsive fix.
3. For spacing fixes, say whether the move is to add air, reduce dead air,
   redistribute gaps, align/symmetrize edges, or standardize the rhythm.
4. Name the screenshots where the issue is visible.
5. Say what should stay unchanged because it is already working.
6. Say what would require another screenshot pass after implementation.
7. If the biggest fix is structural, name the unsuitable design decision and the
   better direction at the level of information architecture, not just CSS.
8. If the screen is competent but boring, recommend one concrete creative
   direction, not only cleanup.
