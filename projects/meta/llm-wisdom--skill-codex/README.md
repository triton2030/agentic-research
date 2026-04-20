# LLM Wisdom — Codex

Переносимый Codex-skill `llm-wisdom` как библиотека устойчивых знаний о том, как языковые модели ведут себя, ошибаются, уходят в shortcutting, имитируют завершение работы и что реально повышает качество.

Это не task-router и не попытка запихнуть в один prompt “всю мудрость”. Его форма другая:

- `SKILL.md` держит только карту применения;
- `references/` хранит тематические модули по устойчивым поверхностям знания;
- при вызове skill сначала выбирается нужная knowledge-surface, потом подтягиваются только релевантные модули.

Главные поверхности:

- `model-behavior` — системные свойства LLM, которые повторяются между задачами;
- `failure-patterns` — типовые режимы деградации и самообмана;
- `escape-patterns` — как модель “сбегает”, не сделав работу по-настоящему;
- `control-levers` — что сильнее prompt wording: валидация, evidence, permissions, evals;
- `prompt-design`, `agent-design`, `skill-design` — как собирать более качественные агентные артефакты.

Опоры:

- [knowledge/wisdom-LLM.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-LLM.md)
- [knowledge/wisdom-agents.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-agents.md)
- [knowledge/wisdom-skills-plugins.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-skills-plugins.md)
- [knowledge/guides/perfect-system-prompts.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/guides/perfect-system-prompts.md)
- [knowledge/guides/perfect-skills.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/guides/perfect-skills.md)
- [knowledge/practical-guides/codex-skills.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/practical-guides/codex-skills.md)

Файлы:

- `SKILL.md` — тонкая карта того, как выбирать модули
- `agents/openai.yaml` — UI metadata
- `references/knowledge-map.md` — навигация по поверхностям знания
- `references/*.md` — тематические модули по поведению, сбоям, обходам и качеству
