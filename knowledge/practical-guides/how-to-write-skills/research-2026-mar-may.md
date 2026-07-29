---
description: "Source-backed выводы из официальных docs и исследований марта-мая 2026 о skill authoring."
read-before-edit: []
edit-after-edit: []
---

# Research 2026 Mar-May

Срез источников на 19 мая 2026. Это snapshot, а не живой источник истины.
Перед current/default/best-practice audit сверяй свежие официальные docs, затем
обновляй `authoring-canon.md` только теми выводами, которые меняют практику.

Recheck 2026-05-22: текущие OpenAI Codex docs и Agent Skills docs по-прежнему
поддерживают progressive disclosure, короткий `description` как trigger
surface, 2-3 concrete use cases как старт и более широкий trigger eval для
важных/спорных skill descriptions.

Recheck 2026-07-10: текущий Codex Build Skills contract явно добавил budget
initial skill list (до 2% context или 8000 символов при неизвестном окне),
shortening descriptions, возможный omission skills, skill-vs-plugin boundary,
instruction-only default и dependencies в `agents/openai.yaml`. OpenAI требует
front-load первой фразы, но не задаёт `120-200` как platform limit.

Recheck 2026-07-25: Anthropic сообщил, что для Opus 5 и Fable 5 удалил более
80% Claude Code system prompt без измеримой потери на coding evals. Новый
baseline: меньше универсальных rules и повторов, lightweight skills и
`CLAUDE.md`, progressive disclosure, interface-first tool design, auto-memory
вместо memory dump в instructions и rich references. Это направление для
pruning с with/without eval, а не разрешение на массовое удаление локальных
инвариантов.

## Official Baseline

- OpenAI Codex Build Skills: skills — authoring, plugins — distribution;
  initial skill list budgeted, descriptions могут сокращаться, skills —
  пропускаться. Front-load use case/trigger words; instruction-only — default;
  scripts нужны для deterministic behavior или external tooling.
  Source: [OpenAI Codex Build Skills](https://developers.openai.com/codex/build-skills)
- OpenAI Save workflows as skills: начинать с рабочего trace, runbook, command и
  accepted output; после следующего реального использования переносить correction
  обратно в skill.
  Source: [OpenAI Save workflows as skills](https://learn.chatgpt.com/use-cases/reusable-codex-skills)
- OpenAI GPT-5.6 guidance: outcome, constraints, evidence, completion bar,
  output shape и stop сохранять; повтор, obsolete process и нерелевантные tools
  сначала удалять; prompt менять по одному failure mode с тем же eval.
  Source: [OpenAI GPT-5.6 guidance](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6)
- Historical OpenAI GPT-5.5 guidance, superseded в активном каноне моделью
  GPT-5.6: outcome-first prompts, success criteria, stop rules, осторожность с
  `reasoning.effort`; старые process-heavy stacks не переносить автоматически.
  Source: [OpenAI GPT-5.5 guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.5)
- Anthropic / Agent Skills: progressive disclosure — frontmatter, body, bundled
  files; scripts полезны там, где нужна repeatable deterministic execution.
  Source: [Anthropic Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- Anthropic / Claude 5 context engineering: context — совокупность system
  prompt, skills, `CLAUDE.md`, memory и references; для новых моделей сначала
  сокращать obsolete constraints, переносить tool-use knowledge в interface и
  раскрывать длинные детали по необходимости.
  Source: [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- Agent Skills standard: `name` до 64, `description` до 1024, `SKILL.md` body,
  optional `scripts/`, `references/`, `assets`, recommended body under 500
  lines. Source: [Agent Skills specification](https://agentskills.io/specification)

## Что Подтвердили Исследования

- SkillsBench (Feb 2026): skills дают сильный, но variable effect; “есть skill”
  намного слабее, чем “правильный skill, правильный момент, правильное
  содержание”. Практика: каждый skill требует proof loop, но глубина проверки
  масштабируется по риску.
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
2. **Description — главный рычаг.** Без routing evidence skill может быть
   идеален внутри и бесполезен снаружи. Исторические `2-3` и `8-10/8-10` —
   примеры eval sizes, не текущие gates: выборка должна различать заявленный
   trigger и реальные near-misses.
3. **Author from traces.** Лучший материал — реальные успехи, провалы,
   corrections, issue/review history.
4. **Evaluate as intervention.** Считать repairs и regressions, а не только
   красивый output.
5. **Security is semantic.** Проверять не только код, но и то, как
   `description` и инструкции меняют selection, trust и runtime actions.
6. **Audit the assembled context.** Не повторять один tool/workflow contract в
   system prompt, `CLAUDE.md`, skill и tool description. Один слой владеет
   правилом; остальные маршрутизируют к нему, а удаление проверяется baseline.
