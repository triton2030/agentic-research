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

- [Instruction Adherence in Coding Agent Configuration Files](https://arxiv.org/abs/2605.10039)
  Факторный эксперимент по структуре instruction-файлов: size, position,
  architecture и adjacent conflicts не дали надёжного эффекта; сильнее виден
  within-session drift.

- [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988)
  AGENTS/context files могут ухудшать success и увеличивать cost, если несут
  лишние требования; полезный вывод — минимальные requirements.

- [ContextCov](https://arxiv.org/abs/2603.00822)
  Natural-language instructions как passive text нарушаются; executable
  guardrails повышают constraint compliance.

- [RoadmapBench](https://arxiv.org/abs/2605.15846)
  Long-horizon coding остаётся нерешённым даже для Claude Opus 4.7; нужна
  декомпозиция, evidence и проверки, а не вера в длинный prompt.

- [SWE-Chain](https://arxiv.org/abs/2605.14415)
  Release-level upgrade chains показывают, что Claude Opus 4.7 лидирует, но
  агенты всё ещё ломают inherited functionality.

- [Trajectory-aware evaluation](https://arxiv.org/abs/2602.21230)
  Trajectory-aware evaluation и пределы оценки только по финальному ответу.

- [AgentIF](https://keg.cs.tsinghua.edu.cn/persons/xubin/papers/AgentIF.pdf)
  Agent instruction-following taxonomy: formatting, semantic, tool.

- [LLM agent evaluation survey](https://dl.acm.org/doi/10.1145/3711896.3736570)
  Survey по evaluation и benchmarking LLM-агентов.

### Model Delta

- [GPT-5.6 prompting guidance](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6)
  Текущий OpenAI baseline: prompt pruning, outcome/stop, concrete response
  controls, permission policy, tool routing, retrieval budgets, state и effort.

- Historical: [Introducing GPT-5.5](https://openai.com/index/introducing-gpt-5-5/)
  GPT-5.5 в Codex: сильнее в agentic coding, Terminal-Bench, tool use и
  token efficiency; всё равно требует точных validation loops. Сохранено как
  launch evidence, не как текущая guidance.

- [GPT-5 for Coding](https://cdn.openai.com/API/docs/gpt-5-for-coding-cheatsheet.pdf)
  GPT-5-family лучше следует инструкциям, но vague/conflicting `.cursor/rules`
  и `AGENTS.md` могут backfire.

- Historical: [Introducing Claude Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7)
  Opus 4.7 literal instruction following, `high`/`xhigh` effort для coding,
  новая tokenizer cost-shape и лучшая file-system memory.

- Historical GPT-5.5-era snapshot: [OpenAI model guide](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.5)
  Outcome-first prompts, `medium` effort, Responses API, tool descriptions,
  `phase`, compaction. Не использовать как активный baseline вместо GPT-5.6.

- [OpenAI reasoning guide](https://developers.openai.com/api/docs/guides/reasoning)
  Reasoning effort, state handling, reasoning items и `phase`.

- [Claude migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide)
  API-level migration details between current Claude model generations.

- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
  Current Opus guidance: effort, scope, verbosity, over-verification, tool use
  and subagent delegation.

- [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
  Fable-specific long-run guidance: effort, bounded autonomy, evidence-grounded
  progress, parallel subagents, memory and skill/prompt simplification.

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
