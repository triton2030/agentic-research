# Проверяемый вопрос v1

Какие изменения управляющего текста 1md-search нужны, чтобы агент при
автоматическом вызове надёжно находил неизвестный Markdown по смыслу,
получал достаточное прочитанное evidence для исходной задачи и соблюдал
границы корпуса без ненужных действий? Ответ изменит редакцию скилла.
Сохранить текущий путь без изменения тоже допустимо при наличии оснований.

Объект: замороженный пакет `/Users/triton/Documents/GitHub/agentic-research/skills/1md-search/work/steering-2026-09-22/before/`.
Хеши: `/Users/triton/Documents/GitHub/agentic-research/skills/1md-search/work/steering-2026-09-22/before-sha256.json`.
Источник доставки: `/Users/triton/Documents/GitHub/agentic-research/skills/shared/1md-search/portable/` и `platforms/codex/agents/openai.yaml`.

## Основания

- Прямой текущий заказ: «Проверь скил по лучим практикам управлеиня агентами [$1fresh-eyes] и улучши его».
- Ранее владелец выбрал «Автоматическое подключение скилла при поиске по смыслу» и полную переработку 1md-search; из сохранённых слов: `/Users/triton/Documents/My_projects/md-tools/_ops/chat-recall/2026-09-21-223200-codex-01a0c503.md`.
- Последнее уточнение владельца: «У нас осталась логика что можно прогревать только одну папку, то есть сами эмбединги только в корне но в настройках можно указать что используем только выбранные папки?».
- Runtime цель: `/Users/triton/Documents/My_projects/md-tools/_ops/GOAL.md`; product frame `/Users/triton/Documents/My_projects/md-tools/_ops/product-frames/md-tools-agent-runtime.md`.
- Авторский контракт: `/Users/triton/.codex/skills/1agent-steering/references/steering-science.md` и `/Users/triton/.codex/skills/1skill-creation/SKILL.md`.
- Точные runtime owners: `/Users/triton/Documents/My_projects/md-tools/docs/architecture-lock.md`, `docs/cli-conventions.md`, `src/md_cli/catalog.py`, `src/navigator/config.py`, `api_search.py`, `api_index_context.py`.
- Наблюдение: установленный md доступен; общий suite предыдущей работы 696 passed. Изолированный loopback workflow cold-index → dry-run/confirm → FRESH → dense result → body read исполнен. Это не измерение частоты автоактивации, качества на разных corpus или adherence ко всем веткам.
- Уже доступно: глобальная установка в Codex/Claude; единый CLI; filters и corpus config; semantic/exact/file-read routes; свежие агенты для проб; disposable corpora без внешних платных вызовов.

## Границы

Разрешены исследование и отчёт. Не меняй исходники, installed packages,
индексы пользователя или внешние данные; не вызывай других агентов и не
вызывай модель родителя обратно. Если нужно сохранить отчёт, только
`/Users/triton/Documents/GitHub/agentic-research/skills/1md-search/work/steering-2026-09-22/reports/prospector.md`.
Текущий заказ улучшает skill; смена backend на локальный E5, полномочий,
глобальная переиндексация и переписывание runtime не приняты.
Unknowns: универсальная точность retrieval, автоматический выбор на будущих
задачах, перенос E5 на длинные документы. Не дополняй их догадкой.

## Независимость

Main уже читал все 4 файла текущего пакета, названные runtime docs и skill
creation/steering материалы, прошлую пробу и отчёт предыдущего аудита.
Предыдущих fresh-eyes панелей этой редакции: 0. Был один прошлый этап
skill-authoring с 3 ролями; их выводы здесь не передаются.
Общие цель и объект доступны всем. Другие агенты независимо исследуют цель,
допущения, внешние способы решения, доступные возможности и вред от успеха.
Не читай отчёты других линз. Если локальные документы уже прочитаны main,
проверь их самостоятельно; неизвестных источников ради новизны не выдумывай.

## Собственная зона

Главная зона: текущие первичные внешние примеры того, как агент получает недостающие основания из локальных источников при ограниченной области. Прочитай профиль /Users/triton/.codex/agents/prospector.toml и исполни его developer_instructions; веб обязателен, не выдавай аналогию по памяти за evidence. Разные миры поиска принадлежат методу профиля.
