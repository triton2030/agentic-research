# Точечные исправления 2026-09-05

Основание: согласованный перечень пяти исправлений и двух малых правок;
утверждение владельца: `_ops/chat-recall/2026-09-05-013827-codex-01a06e21.md:17`.
Маршрут — точечное изменение согласованных правил, без полного пересоздания.

## Изменено

- Намерение и критерии больше не объявлены гарантией исполнения.
- 20 единиц — редакционный ориентир; активная нагрузка учитывает требования всех разделов и продолжающие действовать требования файлов.
- Дорогое снятие требует сравнительного наблюдения, включая снятие автором до проверки.
- Неспособность объяснить причину и несовпадение с прогнозом проверяющего больше не доказывают дефект требования.
- Однозначную потерю автор восстанавливает по принятым источникам; конфликт или новый выбор возвращает владельцу.
- Reference разрешён для самостоятельного режима без переполнения тела.
- Критерии покрывают существенные препятствия минимальным набором; пять — ориентир.

## Проверка

Два независимых read-only проверяющих проверили дельту по букве и траектории.
Оба нашли обход сравнительного прогона через снятие до проверки; принят,
условие перенесено из обработки находок в общее правило проверки.
Один также нашёл остаточную безусловную остановку после retry; принята,
остановка привязана к неразрешённому конфликту.

`sync_simple_projections.py 1skill-creation --check`: исходный пакет,
tracked-проекции и установленные пакеты Claude/Codex совпадают.
`git diff --check`: ошибок нет.

Это проверка текущего текста и маршрутов. Поведенческий сравнительный эксперимент
на существующем скиле не проведён; улучшение фактической надёжности не заявлено.

## Изменённые файлы пакета

- [SKILL.md](../../shared/1skill-creation/portable/SKILL.md)
- [references/goal-context.md](../../shared/1skill-creation/portable/references/goal-context.md)
- [references/behavior-protocol.md](../../shared/1skill-creation/portable/references/behavior-protocol.md)
- [references/reference-files.md](../../shared/1skill-creation/portable/references/reference-files.md)
- [references/refactor.md](../../shared/1skill-creation/portable/references/refactor.md)
- [references/agent-defaults.md](../../shared/1skill-creation/portable/references/agent-defaults.md)
- [references/check-approve.md](../../shared/1skill-creation/portable/references/check-approve.md)
- [agents/check-instructions.md](../../shared/1skill-creation/portable/agents/check-instructions.md)
- [agents/check-trajectory.md](../../shared/1skill-creation/portable/agents/check-trajectory.md)
