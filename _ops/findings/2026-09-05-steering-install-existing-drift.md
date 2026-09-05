# Существовавший drift перед установкой 1agent-steering

2026-09-05, baseline `sync_simple_projections.py --check`: Claude installations
1plan-map/SKILL.md и references/epic-schema.md, 1goal/SKILL.md и
references/craft.md отличаются от shared owners. Codex и tracked projections
соответствовали owners. В Claude уже изменены маршруты product-frames/principles
на GOAL/_docs и docs-write, а epic-schema использует 🟠 и связь health с
последней записью апдейтов. Эти изменения существовали до данной работы.

Полный sync откатил бы их. Выполнена только проекция нового owner-authored
вызова 1agent-steering; проверка удаления этой вставки восстанавливает исходный
SHA каждого файла. Все четыре исходных drift-сообщения сохранились без новых.
Provenance и согласование этих старых изменений не исследовались; новый скилл
и его вызовы установлены. След:
`skills/1agent-steering/installation-delta.json`.
