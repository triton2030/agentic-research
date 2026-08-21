---
kind: module-card
волна: 1
роль: writer
модель: gpt-5.6-luna
thinking: max
---

# Модуль — stock runtime и representative Wiki

## Outcome

В отдельном Codex worktree создать минимальный воспроизводимый
`experiments/openviking-chat-recall/`, поднять stock OpenViking, импортировать
representative frozen corpus и получить первую Wiki официальным LLM Wiki Skill.

## Ownership

- Пишет только `experiments/openviking-chat-recall/**`.
- `_ops/chat-recall/**`, существующий Graphiti и global skills — read-only.
- Не один в кодовой базе: не откатывать чужие изменения; адаптироваться к ним.

## Inputs

- `_ops/plans/openviking-chat-recall/{task,status,context}.md`
- `_ops/chat-recall/**`
- официальный OpenViking repository/docs/runtime
- карточка reviewer-а не является входом до фиксации собственного inventory.

## Делает

1. Проверяет current package/version/license и фиксирует pin.
2. Создаёт локальную конфигурацию без секретов и внешней публикации.
3. Строит deterministic inventory и representative subset, включающий повторы,
   изменение позиции, противоречие, method и устойчивое предпочтение.
4. Импортирует subset штатным resource route.
5. Устанавливает официальный LLM Wiki Skill из pinned upstream.
6. Компилирует Wiki с reason из task-критериев и сохраняет команды, inventory,
   compile receipt и дерево результата.
7. Запускает доступные lint/tests/doctor и делает task-owned commit.

## Не делает

- Не запускает full 181-holder backfill.
- Не форкает prompts/Skill и не добавляет свою ontology.
- Не объявляет Wiki качественной по собственному впечатлению.
- Не редактирует план: возвращает evidence в thread final.

## Done evidence

- Commit hash и точный список task-owned файлов.
- Runtime/version/license receipt.
- Source inventory и правило выбора subset.
- Выполненная compile command, terminal result и URI/tree Wiki.
- Все ошибки и отклонения от stock route названы явно.
