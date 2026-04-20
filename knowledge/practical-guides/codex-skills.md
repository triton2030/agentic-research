# Codex Skills

Короткий practical guide только по Codex-специфике.
Общие правила authoring — `knowledge/guides/perfect-skills.md`.
Постоянная короткая памятка — `knowledge/practical-guides/skill-authoring-checklist.md`.
Официальный OpenAI corpus — `knowledge/guides/official-codex-skills-patterns.md`.

## Что Важно Именно Для Codex

- Installed skill держать lean в `~/.codex/skills/<name>/`: только то, что реально нужно Codex.
- `description` писать как routing contract: `Use when ...`, boundaries, skip-cases. Для Codex длинный boundary-rich `description` — нормальный официальный паттерн.
- `agents/openai.yaml` добавлять почти всегда: для Codex metadata — реальная UI/routing surface, не косметика.
- `SKILL.md` оставлять тонким; в официальном repo-local corpus типичная форма часто ближе к short operational playbook, чем к длинному guide.
- Ядро строить вокруг `Overview` / `Quick start` / `Workflow`; детали выносить в `references/`, `scripts/`, `assets/`.
- `references/` держать в один переход от `SKILL.md`; для reference-файлов длиннее 100 строк — давать table of contents в начале.
- После правок прогонять `quick_validate.py`, а не полагаться на визуальную проверку.
- Для длинного `description` с `:` использовать folded scalar (`>`) или безопасное quoting, иначе YAML может сломаться.

## Чего Не Делать

- Не класть в installed skill лишние `README.md`, `CHANGELOG.md`, `QUICK_REFERENCE.md`.
- Не дублировать один и тот же материал в `SKILL.md` и `references/`.
- Не писать `description` как label уровня “this skill helps with X”; без boundary wording Codex хуже роутит skill.
- Не подменять Codex-native workflow терминальными обходами без реальной причины.

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
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py /path/to/skill
```
