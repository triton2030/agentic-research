# Meta — Links Knowledge

Снимок на 28 апреля 2026.

Здесь источники по памяти, аудиту, eval и model-delta, которые меняют
управление агентной системой. Устойчивые выводы поднимаются в `wisdom-*` и
`guides/`.

## Memory

- https://arxiv.org/abs/2603.07670
  Memory как отдельный цикл `write -> manage -> read`, а не просто “длинный контекст”.

- https://arxiv.org/html/2506.06326v1
  Memory OS of AI Agent — иерархия STM/MTM/LPM с segmented paging и heat-based eviction.

- https://arxiv.org/pdf/2603.24639
  Experiential Reflective Learning — пул reusable heuristics из reflection на прошлых trajectories, retrieval под новую задачу.

- https://fazm.ai/blog/ai-agent-memory-triage-retention-decay
  Memory triage: почему 100% retention — баг. Spectrum стратегий вытеснения и importance scoring.

- https://arxiv.org/html/2512.12856v1
  FiFA benchmark и Forgetful-but-Faithful architecture: структурированное забывание бьёт наивную retention.

- https://www.letta.com/blog/agent-memory
  Практическая рамка памяти для агентов: remembrance vs personalization слои.

## Audit And Eval

- https://arxiv.org/abs/2602.21230
  Trajectory-aware evaluation и пределы оценки только по финальному ответу.

- https://keg.cs.tsinghua.edu.cn/persons/xubin/papers/AgentIF.pdf
  Constraint taxonomy для agent instruction following: formatting, semantic и tool.

- https://dl.acm.org/doi/10.1145/3711896.3736570
  Survey по evaluation и benchmarking LLM-агентов.

## Model Delta

- https://developers.openai.com/api/docs/guides/latest-model
  GPT-5.5: outcome-first prompts, fresh baseline, `medium` default effort,
  Responses API, tool descriptions, `phase` и compaction.

- https://developers.openai.com/api/docs/guides/reasoning
  Reasoning effort, state handling, reasoning items и `phase` для GPT-5.5
  tool-heavy workflows.

- https://platform.claude.com/docs/en/about-claude/models/migration-guide
  Claude Opus 4.7 migration: literal scope, strict effort, progress updates,
  fewer tools/subagents, tokenization and task budgets.

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  Claude Opus 4.7 prompt tuning: verbosity, effort, tool triggering,
  subagents, tone and long-horizon agentic work.
