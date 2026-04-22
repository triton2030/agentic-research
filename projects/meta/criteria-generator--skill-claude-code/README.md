# Criteria Generator — Claude Code

Клодовская версия скилла `criteria-generator`. Рядом лежит кодексовская версия: `projects/meta/criteria-generator--skill-codex/`.

## Что Это

Тот же скилл: берёт пользовательскую задачу, читает контекст проекта, быстро фиксирует LLM-устойчивый task contract и по умолчанию не тормозит ход работы: коротко напоминает, что важно из `_ops/`, и сразу возвращает агента к задаче. Если есть `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md`, считает их upstream картой от `main-strategy` и использует для более сильного task contract.

**Основная роль — переводить `Goal` и активный `Stage` из `_ops/PROJECT-PLAN.md` (плюс релевантные предпочтения из `_ops/INTERVIEW.md`) в локальные task-level критерии, чтобы исполнитель маленькой задачи не терял фокус на общей цели.** Каждый `Must` несёт `Anchored in:` со ссылкой на секцию плана / интервью или явную метку `local-only — <reason>`. Это не общее "усиление критериев", это goal-alignment механизм.

## Отличия От Кодекс-Версии

- В Claude Code можно использовать `AskUserQuestion` для 1-3 load-bearing EVPI-вопросов, когда инструмент доступен.
- Нет `agents/openai.yaml`; routing держится на frontmatter Claude Code.
- `criteria-generator` сам не создаёт и не обновляет `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md`; эти артефакты принадлежат `main-strategy`.

Остальное (discovery, EVPI, adversarial pass, quality gate, формат output, Red Flags) — без изменений по сути, включая новый handoff: task contract должен рождаться из стратегической карты плюс active instruction layer, который уже оформил `system-architect`.

## Файлы

- `SKILL.md` — ядро, адаптированное под Claude Code.
- `references/discovery-map.md` — карта источников контекста.
- `references/failure-modes.md` — каталог типовых LLM-халтур с пробами и контрмерами.
- `references/format-examples.md` — три рабочих примера output на разных типах задач.

Во время исполнения скилл ничего не пишет в `_ops/`. В `contract` режиме его default-выход — компактный receipt, короткое напоминание что держать в голове из `_ops/`, затем немедленный возврат к работе.

## Куда Деплоить

В `~/.claude/skills/criteria-generator/` для персонального Claude Code skill, либо в `.claude/skills/criteria-generator/` внутри проекта.
