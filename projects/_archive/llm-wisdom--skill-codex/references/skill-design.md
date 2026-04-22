# Skill Design

A skill is a repeatable workflow with a trigger, not just a folder of advice.

## What belongs in a skill

- one recurring job
- a clear trigger
- a visible working order
- known failure modes worth blocking
- observable signs of done

## What belongs in references

- longer examples
- anti-pattern catalogs
- step-specific heuristics
- background knowledge that is useful but not mandatory every time

## Portable packaging

- Keep `SKILL.md` thin.
- Use `agents/openai.yaml` for metadata.
- Add only the references the workflow actually needs.
- Avoid hidden repo-local assumptions in a supposedly global skill.

## Mistakes to avoid

- turning `SKILL.md` into one giant lecture
- making the trigger so broad that the skill becomes vague
- duplicating the same rule in the core and in references
- hiding the real workflow under generic advice

## Special case

A knowledge-heavy skill can still be valid if the repeated job is "load and apply the right stable knowledge modules." The knowledge should live in focused references, not in one monolithic main file.
