# Claude Skill Authoring

Читай этот reference при создании или существенной правке Claude skill,
`description`, invocation policy, runtime transfer или source-backed claims.

## Желаемый Результат

Skill активируется в правильный момент и возвращает Claude недостающий
профессиональный контракт. Body улучшает observable outcome, не заставляя Opus
5 или Fable 5 изображать authoring procedure.

Portable core задаёт outcome, decision standard, boundaries, evidence,
conditional routes и stop. Порядок действий появляется только там, где его
нарушение воспроизводит correctness, safety или tool failure.

## Core Contract

- `description` — discovery contract для model-invoked skill. Main use case,
  trigger words и adjacent boundaries должны переживать сокращение metadata;
  body до активации недоступен.
- `SKILL.md` — compact contract, а не учебник. Держи core outcome, критерий
  решения, materially important boundaries, evidence, conditional routes и
  stop/handoff.
- В skill входит только **Delta**: неочевидная domain logic, failure mode,
  correction или профессиональный ход, который модель не выводит надёжно из
  задачи, текущего контекста и ближайшего owner.
- Authority, required output и side-effect boundary называй, только когда они
  меняют допустимое действие.
- Не проси читать все references. Каждый bundled file получает
  action-changing route из `SKILL.md`.
- Reference files держи one level deep; длинному reference дай короткую
  plain-text карту содержания. Body до 500 строк — ceiling, не цель.
- Scripts оправданы deterministic behavior, external tooling или повторяемой
  хрупкой операцией; examples — не компенсация слабого interface.

## Outcome Или Workflow

Outcome/decision contract — default для judgment, design и quality work:

- какое состояние должно стать истинным;
- какой decision standard разрешает tradeoff;
- какие boundaries действительно материальны;
- какое evidence может опровергнуть успех;
- когда нужен reference/tool/agent;
- где stop или handoff.

Workflow contract оправдан, когда порядок сам является частью корректности:
необратимая операция, safety boundary, transactional sequence, protocol или
хрупкий tool handoff. Оставляй только инвариантную последовательность, а не
универсальную процедуру «для надёжности».

## Discovery Contract

Model-invoked description должна сохранять одну routing function:
**Condition × Delta**.

- **Condition** — observable anchor, который Claude может распознать сейчас:
  user phrase, action, artifact, file или path. Абстрактная тема слабее
  наблюдаемого момента.
- **Delta** — неочевидная ставка, из-за которой body стоит открыть.
- Capability catalog не заменяет trigger.
- Near-miss boundary нужен только там, где сосед действительно претендует на
  тот же момент.
- Description остаётся pointer к body, не его digest.

Cut-test: если удаление фразы не меняет, какой skill должен активироваться
против живых соседей, это no-op или body material.

## Candidate Canvas И Invocation

Полный installed set model-invoked descriptions — authoring-time candidate
canvas. Runtime co-presence не гарантирована, поэтому broad/adjacent trigger
дополнительно проверяется на фактически видимом prompt surface.

- Shared trigger phrase — collision/ownership question, не literal-dedupe.
- Правду о skill держит его собственный description; сосед использует bare
  pointer вместо пересказа.
- `disable-model-invocation: true` подходит deliberate/manual skill, который
  не должен конкурировать в model discovery.
- Live Claude skill root и resolved model проверяются, а не выводятся по alias,
  старому пути или другой платформе.

## Evidence По Claim

Evidence должен различать именно заявленное свойство:

- admission claim — повторяемый момент, полезная Delta и наблюдаемый gap;
- routing claim — representative use/skip/near-miss cases и живые collisions;
- structure claim — platform validator и reachable bundled resources;
- behavior claim — observable assertion на реалистичной задаче;
- relative-improvement claim — baseline или previous version;
- distribution claim — source/installed projection sync.

Global, frequent, broad, risky, collision-prone или already-regressed surface
требует более сильного evidence по поднятому риску. Это не превращается в
фиксированное количество prompts, обязательный benchmark или универсальный
verification ritual.

Prompt visibility доказывает только возможность selection. Matcher или
structural validation не доказывают полезный output.

## Model Baseline

- Opus 5 и Fable 5 получают lightweight skill + progressive disclosure.
- Generic self-review, automatic verifier и fan-out не входят в portable
  baseline. Objective validation и independent verifier добавляются по
  task/risk contract.
- Model, effort, thinking, long-run и fallback rules принадлежат текущему model
  owner/runtime. Не копируй их в skill.
- Старые Claude 4.x skills и prompts — historical migration evidence, не
  active baseline или fallback.

## `skill-creator` Handoff

`1skill-architect` выбирает surface, contract shape, routing claim и evidence
bar. Официальный Claude `skill-creator` выполняет scaffolding, validation,
forward testing, measured benchmark и packaging.

Его step list — механика конкретного tool, а не обязательная форма skill body
или универсальный authoring ritual. Не воспроизводи matcher/eval pipeline в
этом reference.

## Source Discipline

- Anthropic-endorsed claim требует current official source:
  `platform.claude.com/docs`, `code.claude.com/docs`,
  `anthropic.com/engineering` или `github.com/anthropics/skills`.
- Local engineering называй local engineering, не рекомендацией Anthropic.
- Не изобретай metrics, limits или runtime availability. Drift-prone факт
  перепроверяй в live docs/runtime.

Current anchors:

- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
- <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>
- <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5>
- <https://code.claude.com/docs/en/slash-commands>
- <https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md>
