# EXP — Experiment Record

**Purpose:** precommit one risky hypothesis, record execution/results and state
an evidence-limited conclusion. Unified record: `authority: ops` while planned
or running, `evidence` after conclusion. Split profile: Brief=`ops`, Learning
Report=`evidence`. `workflow-state: planned|running|concluded|stopped`.
Near-miss: descriptive research → RSP/RPT; delivery → PRD; accepted choice → DEC.

## Core Sections — Precommit

| Heading | Mode | Contract |
| --- | --- | --- |
| Decision Context | REFERENCE | Risky assumption and downstream owner |
| Hypothesis | OWNER | Falsifiable relation, population, context, effect |
| Why This Assumption Matters | OWNER | Failure consequence and uncertainty |
| Prior Evidence | REFERENCE | Baseline/source links |
| Intervention and Comparison | OWNER | Manipulation/control or test condition |
| Population and Sample | OWNER | Unit, eligibility, target, assignment |
| Method and Window | OWNER | Steps, duration, exposure, contamination controls |
| Metrics | OWNER | Primary/guardrails, definitions, denominator |
| Success and Failure Thresholds | OWNER | Fixed numeric/observable thresholds |
| Insufficient-sample and Stop Rules | OWNER | Inconclusive, safety, quality boundaries |
| Instrumentation and Data Capture | LOCAL | Data/instrumentation owner links → experiment-specific capture |
| Confounders and Limitations | OWNER | Alternative explanations and controls |
| Ethics and Legal Safeguards | LOCAL | Ethics/privacy owner links → experiment-specific safeguards |
| Outcome Decision Table | OWNER | Result pattern → hypothesis disposition |

## Core Sections — Execution and Learning

| Heading | Mode | Contract |
| --- | --- | --- |
| Execution and Deviations | OWNER | Actual window/sample/treatment and deviations |
| Data Quality | OWNER | Missingness, integrity, contamination, exclusions |
| Results | OWNER | Metrics, uncertainty, raw evidence links |
| Interpretation and Conclusion | OWNER | Supported/rejected/inconclusive boundary |
| Canon and Decision Impact | LOCAL | Canon/DEC owner links → evidence-bounded proposed update, not accepted decision |
| Remaining Hypotheses and Next Test | OWNER | Residual uncertainty and next experiment |

## Conditional Modules

A/B allocation; qualitative prototype; sequential analysis; safety review;
cost/time budget; cohort follow-up.

## Completion Check

Precommit fields fixed before results or deviation explicit; actual denominator,
quality/confounders visible; conclusion bounded; canon changes handed to owners.

