---
description: "Различия Agent Skills standard, Codex, Claude Code, MCP и API/runtime при упаковке skills."
read-before-edit: []
edit-after-edit: []
---
# Platform Deltas

Коротко: общий authoring canon один, но discovery, packaging и runtime разные.

## Agent Skills Standard

- Минимум: папка с `SKILL.md`.
- Frontmatter: `name` обязателен, до 64 символов, lowercase/hyphen; должен
  совпадать с именем папки.
- `description` обязателен, до 1024 символов, описывает что делает скилл и
  когда применять.
- Optional: `license`, `compatibility`, `metadata`, experimental
  `allowed-tools`.
- Рекомендуемый body — до 500 строк; длинные детали выносить.
- `scripts/`, `references/`, `assets/` загружаются или используются по мере
  необходимости.

## Codex

- Skills — authoring format; plugins — distribution unit.
- Codex сначала видит `name`, `description`, path. Initial skill list ограничен
  примерно 2% окна или 8000 символов; descriptions сначала сокращаются, а при
  большом наборе skills могут быть пропущены. Поэтому первая фраза должна нести
  главный use case и trigger words; `120-200` символов — локальная эвристика.
- Локации docs: `$HOME/.agents/skills`, `.agents/skills`; на этой машине также
  проверять live-root `~/.codex/skills/<name>`.
- `agents/openai.yaml` optional: UI metadata, `policy.allow_implicit_invocation`,
  MCP/tool dependencies. Не писать из памяти: генерировать helper-скриптом и
  валидировать.
- Instruction-only — default. `scripts/` добавлять только для
  детерминированности, внешнего tooling или повторяемой хрупкой операции.
- После правки запускать `quick_validate.py`.

Команды:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  my-skill --path /target/path

python3 ~/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py \
  /path/to/skill \
  --interface display_name="My Skill" \
  --interface short_description="Short UI text" \
  --interface default_prompt="Use $my-skill to ..."

qv-skill /path/to/skill

# Fallback без project discovery и без implicit Python download:
uv tool run --python 3.13 --no-python-downloads --from 'PyYAML==6.0.3' python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /path/to/skill
```

## Claude Code

- Skills грузятся через progressive disclosure: metadata всегда доступна,
  `SKILL.md` читается при активации, bundled files — по ссылке.
- В Claude Code combined `description + when_to_use` сейчас сокращается после
  1536 символов. Это runtime delta, не новый portable standard: cross-surface
  skill следует лимиту Agent Skills выше. Front-load use case и проверяй live
  docs после обновлений runtime.
- Claude чаще undertrigger, чем overtrigger, поэтому description может быть
  немного “pushy”: реальные фразы пользователя, неявные случаи, boundaries.
- Free skills живут в `~/.claude/skills/<name>/SKILL.md`.
- Plugin skills живут в marketplace/plugin package, имеют namespace, version,
  source и toggle; подходят для sharable bundles: skills, agents, hooks, MCP,
  commands.
- В installed skill не класть `README.md`, `CHANGELOG.md`, `QUICK_REFERENCE.md`
  и историю создания. Human-doc живёт в `knowledge/`.
- `agents/openai.yaml` не использовать для Claude Code skills.

## Skills + MCP

MCP даёт доступ к инструментам и данным. Skill учит агента workflow: какие
tools вызвать, в каком порядке, как передавать данные, что проверять и где
остановиться.

Две рабочие рамки:

- problem-first: пользователь описывает outcome, skill оркестрирует tools;
- tool-first: tool уже подключён, skill учит best workflow и ограничения.

## API / Long-Running Agents

Для OpenAI Responses skill bundle может быть загружен в контейнер и найден
агентом в runtime. Для таких workflows сохранять state: assistant items,
tool outcomes, phase, compaction milestones, blockers и next concrete goal.

Для Claude API skills идут через skill management / container capabilities;
для production-пайплайнов важнее versioning, distribution, security review и
with/without regression checks.
