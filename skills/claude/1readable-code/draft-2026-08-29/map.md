# Карта рефактора 1readable-code — 2026-08-29

## Функция

В момент нетривиальной правки или review удержать код дешёвым для следующего
coding-агента: один понятный владелец поведения, концентрированная сложность и
проверка на настоящей границе поведения. Скил не принимает contract decisions.

## Уникальный контекст

Сильный coding-agent часто делает рабочую локальную правку, но может оставить
следующую правку дорогой. Исследования в текущем полугодовом окне показывают:
чистота кода снижает навигационный и token cost без измеримого роста pass rate,
а cross-file refactoring остаётся слабым местом. Brooks/conceptual integrity и
Ousterhout/deep modules поэтому задают owner-высоту и эвристику, а не обещание
роста correctness.

## Цели пользователя

1. Изменённое поведение имеет одного очевидного смыслового владельца и единый
   словарь проекта.
2. Код концентрирует сложность в устойчивых понятных единицах, не размножая
   концепции и не разбрасывая одно правило по callers.
3. Запрошенное поведение доказано на минимальной owning-boundary без обмена
   correctness, data integrity или security на внешнюю чистоту.

## Старые указания и новый владелец смысла

| Старое указание | Что с ним стало | Почему |
| --- | --- | --- |
| Cleanliness lowers revisits/tokens, not correctness | `Unique Context` + цель 3 | Сохранён подтверждённый мотив без обещания pass-rate |
| Correctness/data/security are preconditions | цель 3 | Один носитель вместо отдельного Goal и Stop |
| Truth lives where it executes and one unit owns it | цель 1 + owner gate | Цель задаёт результат, gate делает его наблюдаемым |
| Scatter costs more than a wrapper | цель 2 + cost rule | Сохранена асимметрия, каталог smells не возвращён |
| Dated model Delta | снято из управляющего текста | GPT-5.6/Fable 5 не проверены; дата и модели остаются evidence |
| Failure map: no obvious home → helper/flag/folder | owner gate + cost rule | Сбой поглощён решением, отдельная карта не нужна |
| Name owner before first edit | owner gate | Сохранён адресуемый след |
| Inventory what disappears | cost rule + final trace | Условно для новой surface, не ритуал для любого addition |
| Units that fail together/independently | co-failure rule | Сохранён как граница единицы |
| Read the data edge first | conditional data-edge rule | Сохранён только при реальном data trigger |
| Prove requested thing | falsifying check | Сохранён на owning boundary |
| Re-enter at each structural choice | снято | Старый прогон не проверил эффект; observed degradation на старых моделях не доказывает повторный skill gate |
| Six traces or explain each absence | один evidence packet | Снята отчётная нагрузка, оставлены owner, concentration, check, risk |

## Новые или усиленные ограничения

| Добавка | Дефолт → механизм → решение → вред без строки → цена строгости |
| --- | --- |
| `do not invent one as readability work` | локальный helper выглядит дешёво → ambiguity скрывает contract decision → не редактировать до честного owner → новая россыпь и ложный owner → иногда требуется отдельный design pass |
| `removes more … than it adds` | новая обёртка выглядит аккуратно → interface cost невидим → оставить simpler shape без net reduction → лишняя концепция для каждого будущего агента → отклоняет часть допустимых preparatory abstractions |
| stop на public contract | улучшение формы соблазняет расширить scope → readability присваивает design authority → остановить косметический redesign → незапрошенный breaking change → иногда рефактор разделяется на два хода |

## Evidence и gaps

- Owner words: `_ops/chat-recall/2026-08-11-050000-claude-ad4c0fa8.md:18-22`.
- Текущий заказ: `_ops/chat-recall/2026-08-29-153512-codex-01a04d13.md:16-17`.
- Primary sources retained: arXiv `2604.02547`, `2605.20049`, `2605.07001`,
  `2605.10039`, `2606.05574`, `2607.27250`.
- Прямой эксперимент Brooks/deep modules → agent correctness не найден.
- Черновик ещё не проверен на GPT-5.6, Claude Opus 5 и Claude Fable 5.
- Owner topology не решён: package history считает Claude tracked owner общим
  источником обеих installed projections, а `skills/claude/README.md` требует
  отдельный Codex owner для non-shared package.
