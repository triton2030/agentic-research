# Codex Skills

Короткий practical guide только по Codex-специфике.
Общие правила authoring — `knowledge/guides/perfect-skills.md`.
Постоянная короткая памятка — `knowledge/practical-guides/skill-authoring-checklist.md`.
Официальный OpenAI corpus — `knowledge/guides/official-codex-skills-patterns.md`.

## Что Важно Именно Для Codex

- Installed skill держать lean в `~/.codex/skills/<name>/`: только то, что реально нужно Codex.
- Каждый skill держать вокруг одной работы. Instruction-only — default; `scripts/` добавлять только для детерминированности, повторяемой хрупкой логики или внешнего tooling.
- `description` писать как routing contract, а не summary: `Use when ...`, `Trigger when ...`, реальные user phrases, boundaries, skip-cases, tool/workflow preference. Первый sentence должен переживать shortening initial skills list: главный use case и trigger words ставить в начало. Для Codex длинный boundary-rich `description` — нормальный официальный паттерн, но boundary-rich не значит process-heavy.
- Всё "когда использовать" класть во frontmatter `description`: body грузится уже после trigger, поэтому body-only `When to use` не помогает первичному выбору skill.
- Модельный baseline держит `knowledge/wisdom-gpt-5.5.md`; здесь оставлять
  только Codex packaging и installed-skill правила.
- Workflow писать imperative и проверяемо: явные inputs, expected outputs,
  stop condition и когда читать `references/` / запускать `scripts/`.
- Если skill управляет tools/subagents, явно разделять policy: когда делать
  локально, когда искать, когда делегировать, когда остановиться.
- В Responses-based workflows учитывать `phase`, assistant-item replay и
  compaction; это runtime/state contract, не украшение prompt.
- `agents/openai.yaml` добавлять только когда skill действительно должен иметь
  Codex UI/routing metadata. Это реальная surface, но не ритуал для каждого
  изменения.
- `SKILL.md` оставлять тонким; в официальном repo-local corpus типичная форма часто ближе к short operational playbook, чем к длинному guide.
- Ядро строить вокруг `Overview` / `Quick start` / `Workflow`; детали выносить в `references/`, `scripts/`, `assets/`.
- `references/` держать в один переход от `SKILL.md`; для reference-файлов длиннее 100 строк — давать table of contents в начале.
- После правок прогонять `quick_validate.py` через `uv`, а не полагаться на визуальную проверку.
- После правок проверять routing prompts: несколько `should-trigger` и
  `should-not-trigger` фраз против `description` до раздувания body.
- Для длинного `description` с `:` использовать folded scalar (`>`) или безопасное quoting, иначе YAML может сломаться.

## Чего Не Делать

- Не класть в installed skill лишние `README.md`, `CHANGELOG.md`, `QUICK_REFERENCE.md`.
- Не дублировать один и тот же материал в `SKILL.md` и `references/`.
- Не писать `description` как label уровня “this skill helps with X”; без boundary wording Codex хуже роутит skill.
- Не прятать trigger phrases, negative triggers и adjacent-case boundaries только в body.
- Не подменять Codex-native workflow терминальными обходами без реальной причины.
- Не добавлять длинный пошаговый ritual, если модель может выбрать путь сама и
  критерий результата наблюдаем.

## Минимальная Структура

```text
skill-name/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
└── assets/
```

Создавать только те подпапки, которые реально нужны.

## Команды

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/init_skill.py my-skill --path /target/path
python3 ~/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py /path/to/skill --interface display_name="My Skill" --interface short_description="Short UI text" --interface default_prompt="Use $my-skill to ..."
uv run --python 3.12 --with PyYAML python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py /path/to/skill
```
