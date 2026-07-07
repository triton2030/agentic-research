---
description: "Research grounding for prose-audit: oracle problem, traceability, design rationale, argumentation, evidence quality, and human evaluation."
depends-on: []
---

# Research Grounding

This lab borrows from several fields because no single field owns "testing
prose with no single correct answer".

## Test Oracle Problem

Software testing has a known "oracle problem": sometimes the expected result is
unknown, unavailable, or too expensive to compute. That maps directly to prose
artifacts: we often cannot know whether a strategy, page, film premise, or
design will work before reality touches it.

Useful sources:

- [The Oracle Problem in Software Testing: A Survey](https://discovery.ucl.ac.uk/1471263/)
- [How Effectively does Metamorphic Testing Alleviate the Oracle Problem?](https://vuir.vu.edu.au/33046/1/TSEmt.pdf)
- [Metamorphic Testing: A Review of Challenges and Opportunities](https://dl.acm.org/doi/10.1145/3143561)

Design implication: do not demand a direct answer when none exists. Use partial
oracles: relations, invariants, counterfactuals, and refutation tests.

## Metamorphic Relations

Metamorphic testing checks relations between transformed inputs and outputs. For
prose, this becomes:

- If audience changes from expert to novice, does the core promise still survive?
- If the price doubles, which claim fails first?
- If the same landing page is judged by buyer vs competitor vs skeptical CFO,
  do the claimed strengths move predictably?

Design implication: tests should include "what changes if..." relations, not
only "is this coherent?".

## Requirements Traceability

Traceability research asks how requirements connect to design, code, tests, and
evidence. For prose-audit, traceability means every conclusion needs an address:
file, section, source, artifact element, interview, measurement, or observed
behavior.

Useful sources:

- [Requirements Traceability: A Systematic Literature Review](https://dl.acm.org/doi/epdf/10.1145/3672608.3707952)
- [Requirements traceability technologies and technology transfer decision support: A systematic review](https://www.sciencedirect.com/science/article/pii/S0164121218301754)

Design implication: traceability is necessary but insufficient. A chain can be
traceable to self-canon and still weak.

## Design Rationale

QOC design rationale represents decisions as Questions, Options, and Criteria.
That matters because many prose artifacts hide a decision as if it were a fact.

Useful sources:

- [Questions, Options, and Criteria: Elements of Design Space Analysis](https://www.tandfonline.com/doi/abs/10.1080/07370024.1991.9667168)
- [Design Space Analysis overview](https://europe.naverlabs.com/history/past-research/design-space-analysis/)

Design implication: important audits must recover alternatives. "Why this
audience, and not another?" is a first-class test.

## Argumentation And Defeaters

Toulmin argument structure separates claim, data, warrant, backing, qualifier,
and rebuttal. Argumentation schemes add critical questions that expose where a
reasoning pattern can fail.

Useful sources:

- [Toulmin Argument - Purdue OWL](https://owl.purdue.edu/owl/general_writing/academic_writing/historical_perspectives_on_argumentation/toulmin_argument.html)
- [Advances in the Theory of Argumentation Schemes and Critical Questions](https://informallogic.ca/index.php/informal_logic/article/view/485/453)

Design implication: rebuttal cannot be a decorative paragraph written by the
same defender. A separate challenger should own defeaters.

## Assurance Cases

Safety and assurance cases explicitly connect claims, assumptions, strategies,
and evidence. GSN is useful as a mental model even when we do not draw diagrams.

Useful sources:

- [GSN Community Standard v1](https://www.faa.gov/about/office_org/headquarters_offices/ang/redac/redac-sas-201503-gsn-community-standard-v1.pdf)
- [Visualizing Safety Cases](https://astah.net/support/modeling-basics-best-practices/visualizing-safety-cases/)

Design implication: a prose-audit report should make the argument structure
visible enough that another reviewer can attack it.

## Evidence Quality

Evidence-based fields separate certainty from conclusion. GRADE is healthcare-
specific, but the discipline transfers: evidence can be downgraded for bias,
indirectness, inconsistency, imprecision, or publication-like bias.

Useful sources:

- [Overview of the GRADE approach](https://book.gradepro.org/guideline/overview-of-the-grade-approach)
- [CDC ACIP GRADE Handbook, Chapter 7](https://www.cdc.gov/acip-grade-handbook/hcp/chapter-7-grade-criteria-determining-certainty-of-evidence/index.html)

Design implication: source strength is a separate field, not hidden inside a
verdict color.

## Qualitative Audit Trail

Qualitative research uses audit trails, triangulation, reflexivity, and
dependability/confirmability to make interpretive work inspectable.

Useful sources:

- [Practical guidance to qualitative research, Part 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC8816392/)
- [The pillars of trustworthiness in qualitative research](https://www.sciencedirect.com/science/article/pii/S2949916X24000045)

Design implication: every run keeps raw outputs, run decisions, and synthesis
separately. The synthesis must not erase minority findings.

## NLG / Human Evaluation

Natural-language generation evaluation has no universally accepted automatic
metric; human evaluation also varies and must be designed carefully.

Useful sources:

- [Human evaluation of automatically generated text: Current trends and best practice guidelines](https://www.sciencedirect.com/science/article/pii/S088523082030084X)
- [A Survey of Evaluation Metrics Used for NLG Systems](https://dl.acm.org/doi/10.1145/3485766)
- [Automatic Metrics in Natural Language Generation: A Survey of Current Evaluation Practices](https://arxiv.org/html/2408.09169v1)

Design implication: LLM judgment is another evaluator, not a gold standard.
