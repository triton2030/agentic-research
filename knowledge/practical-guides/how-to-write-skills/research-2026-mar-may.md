---
description: "Source-backed выводы из официальных docs и исследований марта-мая 2026 о skill authoring."
read-before-edit: []
edit-after-edit: []
---
# Research 2026 Mar-May

Срез источников на 19 мая 2026. Здесь только выводы, которые меняют authoring
практику.

## Official Baseline

- OpenAI Codex docs: skills — reusable workflows; plugins — distribution.
  Codex выбирает skill по `name`/`description`/path, а full `SKILL.md` читает
  только после выбора. Из-за context budget description нужно front-load.
  Source: [OpenAI Codex skills](https://developers.openai.com/codex/skills)
- OpenAI Codex best practices: начинать с 2-3 конкретных use cases, clear
  inputs/outputs, user trigger phrases; не покрывать все edge cases заранее.
  Source: [OpenAI Codex best practices](https://developers.openai.com/codex/learn/best-practices)
- OpenAI GPT-5.5 guidance: outcome-first prompts, success criteria, stop rules,
  осторожность с `reasoning.effort`; старые process-heavy stacks не переносить
  автоматически. Source: [OpenAI GPT-5.5 guidance](https://developers.openai.com/api/docs/guides/latest-model)
- Anthropic / Agent Skills: progressive disclosure — frontmatter, body, bundled
  files; scripts полезны там, где нужна repeatable deterministic execution.
  Source: [Anthropic Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- Agent Skills standard: `name` до 64, `description` до 1024, `SKILL.md` body,
  optional `scripts/`, `references/`, `assets`, recommended body under 500
  lines. Source: [Agent Skills specification](https://agentskills.io/specification)

## Что Подтвердили Исследования

- SkillsBench (Feb 2026): skills дают сильный, но variable effect; “есть skill”
  намного слабее, чем “правильный skill, правильный момент, правильное
  содержание”. Практика: каждый skill требует proof loop, а не веры в формат.
  Source: [SkillsBench](https://www.skillsbench.ai/blogs/introducing-skillsbench)
- SkillReducer (31 Mar 2026): на 55k+ public skills найдено много token waste;
  compression descriptions/body улучшала качество при меньшем контексте.
  Практика: сначала резать non-actionable content, потом добавлять.
  Source: [SkillReducer](https://arxiv.org/abs/2603.29919)
- SkillMOO (10 Apr 2026): optimization чаще выигрывает через pruning и
  substitution, а не накопление инструкций. Практика: treat skill bundle as
  something to evolve and prune.
  Source: [SkillMOO](https://arxiv.org/abs/2604.09297)
- Wild benchmark (6 Apr 2026): benefits падают в реалистичных условиях, когда
  агент сам ищет skill в большой библиотеке. Query-specific refinement
  восстанавливает часть эффекта. Практика: description/retrieval quality —
  first-class authoring surface.
  Source: [Wild benchmark](https://arxiv.org/abs/2604.04323)
- SkillRet (7 May 2026): large-scale skill retrieval далека от solved; модели
  плохо выделяют skill-relevant signals в длинных шумных queries. Практика:
  имена, descriptions, taxonomy и near-miss evals важны не меньше body.
  Source: [SkillRet](https://arxiv.org/abs/2605.05726)
- SkillGen (9 May 2026): хорошие skills можно синтезировать из successful и
  failed trajectories, но проверять надо как intervention: with/without,
  repairs vs regressions. Практика: skill authoring начинается с traces.
  Source: [SkillGen](https://arxiv.org/abs/2605.10999)
- SkillSmith (12 May 2026): raw skill injection создаёт лишний context и
  повторное reasoning; boundary-first compiled interfaces снижают tokens/time.
  Практика: skill должен явно задавать operational boundaries.
  Source: [SkillSmith](https://arxiv.org/abs/2605.15215)
- BIV (12 May 2026) и Semantic Supply-chain Attacks (12 May 2026): metadata и
  body — operational text, а не документация; description-implementation gap и
  semantic attacks реальны. Практика: third-party skills читать, сравнивать
  заявленное с фактическим, особенно scripts/network/credentials.
  Sources: [BIV](https://arxiv.org/abs/2605.11770),
  [Semantic Supply-chain Attacks](https://arxiv.org/abs/2605.11418)
- Malicious Or Not (17 Mar 2026): description-only scanners дают шум; repo
  context снижает false positives и показывает abandoned repo hijacking risk.
  Практика: security review смотрит весь repo/package, не только `SKILL.md`.
  Source: [Malicious Or Not](https://arxiv.org/abs/2603.16572)

## Итог Для Нашего Канона

1. **Less is more, но не “short is always better”.** Короткий core + нужные
   bundled files сильнее длинного ядра.
2. **Description — главный рычаг.** Без trigger evals skill может быть идеален
   внутри и бесполезен снаружи.
3. **Author from traces.** Лучший материал — реальные успехи, провалы,
   corrections, issue/review history.
4. **Evaluate as intervention.** Считать repairs и regressions, а не только
   красивый output.
5. **Security is semantic.** Проверять не только код, но и то, как
   `description` и инструкции меняют selection, trust и runtime actions.
