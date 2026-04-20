---
name: llm-wisdom
description: "Use when you need portable knowledge about how language models behave, fail, shortcut, or can be constrained into better work. Load the right reference modules for model behavior, failure patterns, escape patterns, control levers, and prompt or agent design instead of inventing rules from the current task alone."
---

# LLM Wisdom (Codex)

Portable knowledge library for how language models behave, fail, drift, shortcut, and can be pushed into higher-quality work.

This is a flexible knowledge skill. It does not impose one fixed task workflow. Its job is to load the right stable knowledge modules before you answer, design an artifact, or diagnose a model problem.

## When to use

- The user wants to understand recurring LLM behavior, not just solve one local task.
- The user wants to create or rewrite an agent, prompt, or skill using portable principles.
- The user wants to diagnose hallucination, sycophancy, shortcutting, fake completion, or scope drift.
- The user wants to know which control lever is stronger: prompt wording, role split, permissions, validation, verification, or eval.
- The result should travel across projects, folders, or machines with minimal hidden context.

## When not to use

- The user needs only a one-off task prompt for a single current job.
- The task is a trivial wording tweak with no reusable LLM lesson.
- The need is purely repo-local process documentation rather than portable model or agent knowledge.
- The answer depends mainly on live product facts, current docs, or external research not contained in this skill.

## Hard gates

- Do not reduce every problem to prompt wording if runtime controls or verification are the real lever.
- Do not present local observations as universal truths about models.
- Do not answer with generic advice like "be specific" or "add more detail" if the real issue is bypass, scope drift, or weak evidence.
- Do not confuse confidence, verbosity, or reasoning style with real quality.
- Do not paste the whole library into the final artifact. Synthesize only the relevant subset.

## Input context

Bring in only the context that changes the diagnosis or synthesis:

- what question, failure, or design decision is in front of you;
- what layer is being changed: agent, prompt, skill, runtime, eval, or workflow;
- what failure is observed or feared;
- what evidence exists versus what is still a hypothesis;
- what must remain portable across repos or machines.

If a fact does not change the knowledge surface, the cause, or the countermeasure, leave it out.

## Process

1. Name the current knowledge surface with [references/knowledge-map.md](references/knowledge-map.md).
2. Read only the thematic modules that match the real issue:
   - core model traits -> [references/model-behavior.md](references/model-behavior.md)
   - recurring degradation modes -> [references/failure-patterns.md](references/failure-patterns.md)
   - shortcutting and fake completion -> [references/escape-patterns.md](references/escape-patterns.md)
   - stronger control surfaces -> [references/control-levers.md](references/control-levers.md)
   - prompt writing -> [references/prompt-design.md](references/prompt-design.md)
   - agent construction -> [references/agent-design.md](references/agent-design.md)
   - skill construction -> [references/skill-design.md](references/skill-design.md)
3. Separate stable knowledge from local inference. Say plainly what is portable and what is only a hypothesis about this situation.
4. Apply the principles to the current problem. Prefer naming failure classes, causes, and countermeasures over dumping every note you read.
5. If the real fix belongs outside prompting, say so plainly and point to the stronger lever.
6. If you are building an artifact, synthesize only the subset that belongs in that artifact. Do not turn the artifact into a copy of the library.
7. Run the closing pass in [references/final-check.md](references/final-check.md).

## Done when

- The relevant knowledge surface is explicit.
- Stable knowledge is separated from local inference.
- The answer names concrete failure modes or control levers instead of vague prompt advice.
- Any built artifact receives only the relevant subset of guidance.
- Portability limits or uncertainty are stated plainly.

## References

- [references/knowledge-map.md](references/knowledge-map.md)
- [references/model-behavior.md](references/model-behavior.md)
- [references/failure-patterns.md](references/failure-patterns.md)
- [references/escape-patterns.md](references/escape-patterns.md)
- [references/control-levers.md](references/control-levers.md)
- [references/prompt-design.md](references/prompt-design.md)
- [references/agent-design.md](references/agent-design.md)
- [references/skill-design.md](references/skill-design.md)
- [references/final-check.md](references/final-check.md)
