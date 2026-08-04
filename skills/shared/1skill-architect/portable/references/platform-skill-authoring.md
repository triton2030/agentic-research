# Platform Skill Authoring - Source Router

Этот файл существует только в portable source, чтобы относительный route из
`SKILL.md` оставался разрешимым до сборки. Runtime projection заменяет этот
address содержимым ровно одного platform owner-а:

- [Codex authoring contract](../../platforms/codex/references/platform-skill-authoring.md)
- [Claude authoring contract](../../platforms/claude/references/platform-skill-authoring.md)

Не добавляй сюда общую authoring truth: она принадлежит portable `SKILL.md` и
`local-skill-contract.md`; platform delta принадлежит указанным targets.
