# Anti-patterns — Чему Я Не Верю

Это не абстрактные запреты. Это короткий список ошибок, которые ломают архитектурное мышление.

## Starting In The Wrong Place

- **Начинать с редактуры `AGENTS.md` до понимания проекта.** Инструкции — не стартовая точка, а вывод из project reality.
- **Начинать с control surface inventory до AI job map.** Если не понятно, какую работу должен делать ИИ, inventory превращается в фоновый шум.
- **Считать instruction layer целью, а не следствием.** Так рождаются красивые правила, которые не служат реальной траектории проекта.

## Failure Thinking

- **Россыпи симптомов без failure classes.** Это список неприятностей, а не архитектура.
- **Force fields в эпилоге.** Если силы появляются после решения, они оправдывают выбор задним числом.
- **`1 failure -> 1 prescription` как default.** Это санитария, но ещё не leverage.
- **Игнорировать `unbootstrapped` или `stale` upstream truth layer.** Тогда система начинает защищать призрак плана или случайный legacy layer.

## Control Surfaces

- **Переписывать `AGENTS.md`, не собрав карту существующих skills, ownership и guardrails.**
- **Принимать текстовое упоминание за runtime-факт.** `README сказал` не равно `реально установлено`.
- **Рекомендовать новый skill до отказа от более сильных слоёв.** Skill — дорогой слой, не default answer.

## Architecture Changes

- **Изменение без leverage verdict.**
- **Изменение без owner, backlink или sunset signal.**
- **Add-only answer без `Minimize pass`.** Если ничего не удалено и ничего не отклонено, система почти наверняка стала тяжелее.
- **Опираться на дисциплину человека там, где можно поставить более сильный guardrail.**

## Folder Discipline

- **Удалению папки без Chesterton's fence probe.**
- **Folder verdict без якоря в project reality, Stage или preference.**

## Questions

- **Вопросам без EVPI.**
- **Формату `согласен с моим анализом?`** Это sycophancy trap.
- **Вопросам, которые меняют только wording, а не layer / owner / add-vs-remove verdict.**
