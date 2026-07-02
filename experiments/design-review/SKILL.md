---
name: design-review
description: >
  Use after frontend implementation work is complete when Codex should capture
  desktop 16:9 and mobile scroll screenshots, then call a clean terminal design
  review agent. Creates project-local `_workspace/design-review/` evidence.
  Skip mid-implementation tweaks, static screenshot-only critique, Figma work,
  and technical browser QA that does not need visual design judgment.
---

# Design Review

## Outcome

Produce a visual design signoff packet after frontend work is finished:

- screenshot evidence in the target project's `_workspace/design-review/<run>/`;
- overlapping desktop 16:9 and mobile viewport screenshots;
- optional clicked/expanded state screenshots from an interaction plan;
- a clean `codex exec` design-agent answer based on `questions.md`.

The terminal design agent must not inherit the current chat, project `AGENTS.md`,
global skills, or source-code context by default. It reviews screenshots,
manifest data, and the editable question list only.

## Default Path

1. Confirm the frontend is in a reviewable state and a live URL exists.
2. Run the bundled command from the project being reviewed:

   ```bash
   /path/to/design-review/scripts/design-review \
     --url http://localhost:3000 \
     --project "$PWD"
   ```

3. If the UI has important menus, tabs, dialogs, hoverless mobile drawers, or
   post-click states, create an interaction plan and pass it:

   ```bash
   /path/to/design-review/scripts/design-review \
     --url http://localhost:3000 \
     --project "$PWD" \
     --interactions ./design-review-interactions.json
   ```

4. Report only the useful evidence: run directory, screenshot counts, review
   output path, failed captures, and residual risk.

## Workspace Rule

Always keep artifacts inside the project under review:

```text
<project>/_workspace/design-review/<timestamp>-<label>/
```

Do not scatter screenshots in the repository root, desktop, downloads, or the
skill folder. The skill folder is the reusable tool; `_workspace` is the per-run
evidence owner.

## Screenshot Contract

Desktop captures default to `1440x810` CSS pixels: 16:9, standard laptop-like
viewing, and easier visual comparison than full-page stitched screenshots.

Mobile captures default to common human-scroll profiles:

- `mobile-iphone`: `390x844`;
- `mobile-android`: `412x915`.

The capture script records:

- half-screen overlapping scroll positions, not isolated full viewport jumps;
- section-top screenshots for semantic anchors;
- bridge screenshots between adjacent sections so transitions can be judged;
- optional interaction screenshots after clicking configured selectors;
- a `manifest.json` and `screenshots.md` ledger.

The script waits for load, fonts, images, network idle when available, and a
settle delay after each scroll/click so animations have time to finish. Do not
disable animations unless the task is specifically about reduced-motion output.

## Question Contract

Edit `questions.md` when the design lens changes. The clean agent must answer
through that Markdown structure instead of inventing a new rubric.

Useful additions belong in `questions.md` when they change the review outcome.
Implementation details, CLI flags, and runtime caveats belong in this file or
the scripts, not in the questions.

## Clean Agent Boundary

`scripts/run-clean-design-agent.sh` creates a temporary `CODEX_HOME`, links only
`~/.codex/auth.json`, unsets API-key environment variables, runs from a neutral
temporary cwd, passes `--ignore-user-config`, `--ignore-rules`, `--ephemeral`,
and attaches screenshots with `codex exec -i`.

This is intentionally stricter than native same-thread subagents. If the review
needs source-code access, say that explicitly and run a separate technical
review. Do not quietly widen the design review agent into a code reviewer.

## Validation

Before trusting changes to this skill package:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /path/to/design-review

/path/to/design-review/scripts/design-review --help
/path/to/design-review/scripts/run-clean-design-agent.sh --help
node --check /path/to/design-review/scripts/capture-design-screenshots.mjs
```

For a real frontend, run `scripts/design-review` against a local URL and inspect
the generated `screenshots.md` before accepting the agent's verdict.

## Stop

Use this near the end of frontend programming work. Do not run it between every
small CSS edit unless the user explicitly asks for a visual checkpoint.
