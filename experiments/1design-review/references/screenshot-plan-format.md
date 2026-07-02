# Screenshot Plan Format

Use this when writing `<project>/_workspace/design-review/<label>/screenshot-plan.json`.

## Contract

- `url` may be in the plan or passed by CLI.
- `groups` is required.
- Each group must contain 2-3 related screenshots.
- Group by visual question, not by scroll distance.
- For nontrivial pages, create several groups when there are several independent
  visual questions. Four to eight groups is normal when the page has enough
  meaningful sections, responsive states, or interactions. Do not split groups
  only to occupy reviewer slots.
- Every shot needs `profile` and either `scrollY`, `selector`, or both.
- Use `click` only for the state that must be reviewed after interaction.

## Template

```json
{
  "url": "http://localhost:3000/design-system",
  "notes": "Main agent inspected desktop and mobile before writing this plan.",
  "groups": [
    {
      "id": "first-fold-to-color",
      "purpose": "Judge first viewport hierarchy and transition into token overview.",
      "questions": ["hero hierarchy", "section bridge", "sticky header"],
      "shots": [
        {
          "name": "desktop-hero",
          "profile": "desktop-1440",
          "scrollY": 0,
          "notes": "First desktop viewport."
        },
        {
          "name": "desktop-color-bridge",
          "profile": "desktop-1440",
          "selector": "#design-system-color",
          "scrollBy": -120,
          "notes": "Bridge into color section with sticky header visible."
        },
        {
          "name": "mobile-hero",
          "profile": "mobile-iphone",
          "scrollY": 0,
          "notes": "First mobile viewport."
        }
      ]
    }
  ]
}
```

## Shot Fields

- `name`: short stable slug for the shot.
- `profile`: `desktop-1440`, `desktop-1080`, `mobile-iphone`, or `mobile-android`.
- `scrollY`: exact vertical scroll position.
- `selector`: CSS/text selector to scroll into view before capture.
- `scrollBy`: vertical adjustment after `selector` or `scrollY`; useful for sticky headers.
- `click`: selector to click before capture.
- `waitMs`: extra wait after scroll/click.
- `notes`: why this shot exists.

## Good Groups

- Desktop first fold + desktop bridge + mobile first fold.
- Desktop dense table + desktop next scroll state + mobile equivalent.
- Closed menu + open menu + settled post-click state.
- Section anchor hidden under sticky header + corrected offset + mobile anchor.

## Bad Groups

- Three unrelated page sections.
- Thirty scroll positions split mechanically.
- Desktop-only group when the risk is responsive.
- One screenshot with no comparison point.
