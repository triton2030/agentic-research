# Карта рефактора 1readable-code — 2026-08-29

## Функция

При каждом переходе к написанию или изменению кода остановить реактивное
исполнение задачи и вернуть coding-agent стратегический взгляд CTO/архитектора:
как сегодняшняя форма повлияет на читаемость, стабильность и цену будущей
разработки.

## Уникальный контекст

Coding-agent уже знает классические engineering practices, но task focus часто
скрывает верхнюю картину и будущие последствия. Поэтому скил называет
Ousterhout's strategic programming/deep modules и Brooks's conceptual integrity
как сжатые handles, а не пересказывает каталог правил.

## Цели пользователя

1. До программирования подход оценён из будущего системы, а не только из
   текущей задачи.
2. Код сохраняет conceptual integrity и концентрирует сложность в deep modules,
   чтобы будущая правка оставалась локальной и читаемой.
3. Материальный риск будущей стабильности получает свежий внешний challenge до
   реализации.

## Старые указания и новый владелец смысла

| Старое указание | Что с ним стало | Почему |
| --- | --- | --- |
| Cleanliness lowers revisits/tokens | снято из active body | Новый owner-смысл шире навигационной цены: strategic programming и будущее системы |
| Correctness/data/security are preconditions | requested-behavior falsifier | Не превращать readability в замену корректности |
| One semantic owner | Brooks conceptual integrity + deep modules | Известная практика названа, а не пересказана |
| Scatter costs more than wrapper | deep modules | Каталог конкретных smells больше не нужен |
| Co-failure/co-change rules | снято как известное | Выводится сильным coding-agent из named practices |
| Data edge first | снято как известное | Это локальная best practice, не уникальный strategic context |
| Name owner before first edit | strategic choice before first edit | Gate поднят с локального owner-а к форме будущей системы |
| Readability-only surface cost | deep modules | Оставлен смысл меньшего interface burden без отдельной формулы |
| Contract choice route | `codebase-design` / `1codebase-design` | Скил напоминает линзу, но не присваивает contract design |
| Claim-specific falsifier | requested-behavior falsifier | Сохраняет correctness без прежнего отчётного packet |
| Re-enter at each structural choice | automatic trigger on coding transition | Момент задаётся discovery surface, а не повторным ритуалом внутри тела |

## Новые или усиленные ограничения

| Добавка | Дефолт → механизм → решение → вред без строки → цена строгости |
| --- | --- |
| pause before first edit | task focus запускает правку раньше system view → observable pre-edit gate → назвать strategic choice → tactical shape закрепляется первым diff → короткая задержка на каждом coding transition |
| named practices, no tutorial | автор может пересказать handbook → знания уже в модели → использовать practice handles → длинный skill конкурирует с самой задачей → результат зависит от знания модели |
| fresh subagent beyond one local edit | исполнитель наследует собственную рамку → independent view → атаковать future stability до edit → скрытая связность становится дорогой позже → latency и отдельный agent turn |
| future-locality trace | общий совет не меняет решение → назвать вероятную следующую правку → проверить форму через её будущую цену → strategic rhetoric без design consequence → прогноз остаётся гипотезой, не гарантией |

## Evidence и gaps

- Новая owner-коррекция:
  `_ops/chat-recall/2026-08-29-153512-codex-01a04d13.md:21-27`.
- Прежние owner-слова про coding-agent, Brooks/Ousterhout и parity:
  `_ops/chat-recall/2026-08-11-050000-claude-ad4c0fa8.md:18-22`.
- Primary research остаётся в `../evidence.md`; оно поддерживает цену
  навигации и слабость cross-file refactoring, но не доказывает этот exact
  prompt или subagent mechanism.
- Формулировка владельца про subagent — `идея`, не безусловное решение;
  черновик делает его обязательным только beyond one obvious local edit и
  предъявляет эту цену на approval.
- Старые audit/probe rounds проверяли прежнюю owner-функцию и не утверждают
  эту версию.
- Product Frame у пакета отсутствует.
- Owner topology между shared parity и отдельным Codex owner не решён.
