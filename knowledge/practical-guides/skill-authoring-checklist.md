# Чеклист Перед Написанием Скилла

Пройди сверху вниз.
Если на один из первых вопросов ответ “нет”, скилл пока не писать.

## Go / No-Go

- Это повторяемый workflow, а не разовый кейс, сырая идея или просто тема?
- У этого workflow есть свой trigger и свой порядок работы, а не только общая область знаний?
- Это точно скилл, а не правило для системного prompt, `AGENTS.md`, `script` или `reference`?
- Без скилла агент уже реально ошибается, плавает или тратит лишние ходы?

## Routing

- `description` написан как routing contract: когда вызывать, а не что скилл “умеет”?
- Первый sentence `description` уже содержит главный use case и trigger words,
  если список skills будет сокращён?
- В `description` есть boundaries: когда использовать, когда не использовать, какие соседние кейсы не сюда?
- Для `description` есть 8-10 `should-trigger` и 8-10 `should-not-trigger` примеров?
- Платформенная metadata surface учтена: что реально увидит модель до загрузки тела скилла?

## Shape

- У скилла один coherent unit of work и один default path?
- Скилл задаёт outcome, boundaries, evidence и stop condition раньше, чем
  длинный процесс?
- В `SKILL.md` осталось только ядро: workflow, gotchas, `done when`, pointers?
- Длинные детали вынесены в `references/`, хрупкая повторяемая логика — в `scripts/`, выходные ресурсы — в `assets/`?
- `scripts/` добавлены только там, где нужна детерминированность, внешний
  tooling или повторяемая хрупкая операция?
- Есть template, checklist или validator там, где качество без этого будет плыть?
- Старый progress/self-check/thoroughness scaffolding оставлен только если
  baseline на новой модели без него реально проседает?
- Tool/subagent policy оправдана задачей, а не привычкой фан-аутить работу?

## Proof

- Понятно, по чему считать работу завершённой?
- Есть хотя бы один реальный `with_skill` vs `without_skill` прогон?
- После model upgrade сравнен короткий baseline против старого prompt stack?
- Для GPT-5.5 проверены `low`/`medium` перед эскалацией в `high`/`xhigh`, если
  runtime позволяет?
- После первого прогона ты готов вырезать всё, что не улучшает routing, качество или надёжность?
