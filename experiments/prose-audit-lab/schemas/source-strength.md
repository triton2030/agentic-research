---
description: "Evidence strength labels used across prose-audit runs."
depends-on: []
---

# Source Strength

Every evidence row must carry one source-strength label.

| Label | Strength | Meaning |
| --- | ---: | --- |
| `self_canon` | 1 | The artifact or owner docs state the claim. Good for traceability, weak for truth. |
| `derived_research` | 2 | Secondary synthesis, desk research, AI research, or analysis derived from other sources. |
| `external_secondary` | 3 | Independent published source, benchmark, review, article, market report, critique. |
| `external_primary` | 4 | Interview, survey, usability session, viewer panel, buyer call, primary dataset. |
| `observed_reality` | 5 | Actual behavior: payment, conversion, usage, retention, watched reaction, signed contract. |

## Decision Rule

`self_canon` can make a chain traceable. It cannot make a high-stakes decision
true.

`derived_research` can guide hypotheses. It cannot close reality.

Only `external_primary` or `observed_reality` can support a claim like:

- "buyers will buy";
- "studios will keep using it";
- "viewers will feel the intended emotion";
- "this deck will persuade investors";
- "this design communicates trust to the target audience".
