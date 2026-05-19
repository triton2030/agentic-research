# Meta — Links

Снимок после объединения 19 мая 2026.

Sources для памяти, eval, model-delta и meta tooling. Устойчивые выводы
поднимаются в `knowledge/wisdom-*` и `knowledge/guides/`; этот файл хранит
source/reference слой.

## Knowledge Sources

### Memory

- [Memory cycle](https://arxiv.org/abs/2603.07670)
  Memory как отдельный цикл `write -> manage -> read`, а не просто “длинный
  контекст”.

- [Memory OS](https://arxiv.org/html/2506.06326v1)
  Memory OS of AI Agent: STM/MTM/LPM, segmented paging и heat-based eviction.

- [Experiential Reflective Learning](https://arxiv.org/pdf/2603.24639)
  Experiential Reflective Learning: reusable heuristics из reflection на
  прошлых trajectories.

- [Memory triage](https://fazm.ai/blog/ai-agent-memory-triage-retention-decay)
  Memory triage, retention decay и importance scoring.

- [FiFA](https://arxiv.org/html/2512.12856v1)
  FiFA benchmark и Forgetful-but-Faithful architecture.

- [Letta agent memory](https://www.letta.com/blog/agent-memory)
  Практическая рамка agent memory: remembrance vs personalization.

### Audit And Eval

- [Trajectory-aware evaluation](https://arxiv.org/abs/2602.21230)
  Trajectory-aware evaluation и пределы оценки только по финальному ответу.

- [AgentIF](https://keg.cs.tsinghua.edu.cn/persons/xubin/papers/AgentIF.pdf)
  Agent instruction-following taxonomy: formatting, semantic, tool.

- [LLM agent evaluation survey](https://dl.acm.org/doi/10.1145/3711896.3736570)
  Survey по evaluation и benchmarking LLM-агентов.

### Model Delta

- [OpenAI latest model guide](https://developers.openai.com/api/docs/guides/latest-model)
  GPT-5.5: outcome-first prompts, fresh baseline, `medium` effort,
  Responses API, tool descriptions, `phase`, compaction.

- [OpenAI reasoning guide](https://developers.openai.com/api/docs/guides/reasoning)
  Reasoning effort, state handling, reasoning items и `phase`.

- [Claude migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide)
  Claude Opus 4.7 migration: literal scope, effort, progress, fewer
  tools/subagents, tokenization and task budgets.

- [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  Claude Opus 4.7 prompt tuning, tool triggering and long-horizon agentic work.

## Tools / Frameworks

### Memory Frameworks

- [Letta](https://www.letta.com/)
  Letta / MemGPT: production memory framework with tool-based write/read.

- [Awesome Agent Memory](https://github.com/TeleAI-UAGI/Awesome-Agent-Memory)
  Curated overview of LLM/MLLM memory systems, benchmarks and papers.

### Claude Code Learnings Patterns

- [claude-memory-skill](https://github.com/SomeStay07/claude-memory-skill)
  Project-memory skill with update, prune, reflect, status, contradiction
  detection and dedup.

- [planning-with-files](https://github.com/othmanadi/planning-with-files)
  Persistent markdown files for planning and knowledge.

- [Self-learning Claude Code skill](https://www.mindstudio.ai/blog/self-learning-claude-code-skill-learnings-md)
  Practical guide for `learnings.md`: structure, quality, growth management.

- [Learnings loop](https://www.mindstudio.ai/blog/how-to-build-learnings-loop-claude-code-skills)
  Learnings loop as read-execute-capture cycle for self-improving skills.
