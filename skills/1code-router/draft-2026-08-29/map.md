# Карта рефактора 1readable-code — 2026-08-29

## Функция

При каждом переходе к написанию или изменению кода переключить реактивное
исполнение задачи на стратегический взгляд CTO/архитектора:
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
2. Получившийся код остаётся связным и удерживает вероятную будущую правку
   локальной и читаемой.

## Старые указания и новый владелец смысла

| Старое указание | Что с ним стало | Почему |
| --- | --- | --- |
| Cleanliness lowers revisits/tokens | снято из active body | Новый owner-смысл шире навигационной цены: strategic programming и будущее системы |
| Correctness/data/security are preconditions | снято как agent default | Не превращать readability-skill в общий validation controller |
| One semantic owner | Brooks conceptual integrity + deep modules | Известная практика названа, а не пересказана |
| Scatter costs more than wrapper | deep modules | Каталог конкретных smells больше не нужен |
| Co-failure/co-change rules | снято как известное | Выводится сильным coding-agent из named practices |
| Data edge first | снято как известное | Это локальная best practice, не уникальный strategic context |
| Name owner before first edit | strategic choice before first edit | Gate поднят с локального owner-а к форме будущей системы |
| Readability-only surface cost | deep modules | Оставлен смысл меньшего interface burden без отдельной формулы |
| Contract choice route | `codebase-design` / `1codebase-design` | Скил называет оба runtime-соседа и не присваивает contract design |
| Claim-specific falsifier | снято как agent default | Общая проверка поведения не является уникальной функцией readability-skill |
| Re-enter at each structural choice | automatic trigger on coding transition | Момент задаётся discovery surface, а не повторным ритуалом внутри тела |

## Новые или усиленные ограничения

| Добавка | Дефолт → механизм → решение → вред без строки → цена строгости |
| --- | --- |
| strategic lens before first edit | task focus запускает правку раньше system view → named-practice gate → дать будущей цене изменить подход → tactical shape закрепляется первым diff → короткая задержка на каждом coding transition |
| named practices, no tutorial | автор может пересказать handbook → знания уже в модели → использовать practice handles → длинный skill конкурирует с самой задачей → результат зависит от знания модели |
| fresh subagent only on material uncertainty or direct request | исполнитель может наследовать собственную рамку именно на открытой развилке → independent view → атаковать unresolved future stability до edit → скрытая связность становится дорогой позже → latency только там, где есть стратегическая неопределённость |
| proceed without ceremony | named lens может породить отчёт без решения → explicit escape path → продолжить при отсутствии material consequence → ritual заменяет coding → не остаётся обязательного trace, что линза была применена |
| conditional strategic closure | обычный test не проверяет будущую цену формы → вернуться к той же цене только если она меняла подход → убедиться, что итог её снял → стратегическое решение остаётся декларацией → проверка условна и не требует отчёта |
| русский body + английский trigger-only `description` | смешение discovery и instruction body раздувает кнопку запуска → разделить язык и поверхности по прямому решению владельца → routing остаётся коротким, active body понятен владельцу → длинное описание рекламирует процесс вместо момента → runtime-сосед назван только как near-miss |
| commander intent прежде procedure | автор лечит каждый риск отдельным шагом → цели и Unique Context формируют ментальную модель → агент сам выводит известные practices и anti-ritual stop → checklist конкурирует с задачей → точные runtime seams остаются hard lines |

## Evidence и gaps

- Новая owner-коррекция:
  `_ops/chat-recall/2026-08-29-153512-codex-01a04d13.md:21-28`.
- Решение установить обе runtime-проекции и языковой контракт:
  `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:19-20`.
- Общий принцип commander intent прежде procedure:
  `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:21`.
- Прежние owner-слова про coding-agent, Brooks/Ousterhout и parity:
  `_ops/chat-recall/2026-08-11-050000-claude-ad4c0fa8.md:18-22`.
- Primary research остаётся в `../evidence.md`; оно поддерживает цену
  навигации и слабость cross-file refactoring, но не доказывает этот exact
  prompt или subagent mechanism.
- Формулировка владельца про subagent — `идея`, не безусловное решение;
  черновик включает его только при материальной стратегической неопределённости
  либо прямом запросе владельца.
- Старые audit/probe rounds проверяли прежнюю owner-функцию и не утверждают
  эту версию.
- Product Frame у пакета отсутствует.
- Shared portable owner выбран как минимальная topology: generic sync его
  поддерживает, runtime-specific различий в body нет, Codex отличается только
  `agents/openai.yaml`.
