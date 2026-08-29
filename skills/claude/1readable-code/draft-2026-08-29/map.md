# Карта рефактора 1readable-code — 2026-08-29

## Функция

В момент нетривиальной правки или review удержать код дешёвым для следующего
coding-агента: один понятный владелец поведения, концентрированное правило и
фальсификатор на owning boundary. Скил не принимает contract decisions.

## Уникальный контекст

Сильный coding-agent часто делает рабочую локальную правку, но может оставить
следующую правку дорогой. Исследования в текущем полугодовом окне показывают:
чистота кода снижает навигационный и token cost без измеримого роста pass rate,
а cross-file refactoring остаётся слабым местом. Brooks/conceptual integrity и
Ousterhout/deep modules поэтому задают owner-высоту и эвристику, а не обещание
роста correctness.

## Цели пользователя

1. Изменённое или проверяемое поведение имеет одного очевидного смыслового
   владельца.
2. Owning unit концентрирует правило, не разбрасывая его по callers.
3. У implementation- или review-claim есть фальсификатор на owning boundary.

## Старые указания и новый владелец смысла

| Старое указание | Что с ним стало | Почему |
| --- | --- | --- |
| Cleanliness lowers revisits/tokens, not correctness | `Unique Context` | Сохранён подтверждённый мотив без обещания pass-rate |
| Correctness/data/security are preconditions | `Unique Context` | Один носитель вместо отдельного Goal и Stop |
| Truth lives where it executes and one unit owns it | цель 1 + owner gate | Цель задаёт результат, gate делает его наблюдаемым |
| Scatter costs more than a wrapper | цель 2 + cost rule | Сохранена асимметрия, каталог smells не возвращён |
| Dated model Delta | снято из управляющего текста | GPT-5.6/Fable 5 не проверены; дата и модели остаются evidence |
| Failure map: no obvious home → helper/flag/folder | owner gate + cost rule | Сбой поглощён решением, отдельная карта не нужна |
| Name owner before first edit | owner gate | Сохранён адресуемый след |
| Inventory what disappears | readability-only surface rule | Условно для surface, добавленной ради формы, не ритуал для required behavior |
| Units that fail together/independently | co-failure rule | Сохранён как граница единицы |
| Read the data edge first | conditional data-edge rule | Сохранён только при реальном data trigger |
| Prove requested thing | falsifying check | Сохранён на owning boundary и, когда это другая поверхность, на requested artifact |
| Re-enter at each structural choice | снято | Старый прогон не проверил эффект; observed degradation на старых моделях не доказывает повторный skill gate |
| Six traces or explain each absence | один evidence packet | Снята отчётная нагрузка, оставлены owner и claim-specific falsifier |

## Новые или усиленные ограничения

| Добавка | Дефолт → механизм → решение → вред без строки → цена строгости |
| --- | --- |
| existing или proposed owner | запрет нового owner блокирует устранение scatter → различить private concentration и contract choice → разрешить proposed owner до contract boundary → нечестный caller-owner либо лишний handoff → proposed owner надо доказать surface-rule |
| surface added only for readability | новая обёртка выглядит аккуратно → interface cost невидим → требовать меньше копий правила или знающих его callers → новая концепция без снижения knowledge cost → не запрещает required surface |
| stop на contract choice | улучшение формы соблазняет расширить scope → readability присваивает design authority → остановить выбор нового контракта → незапрошенное изменение interface/seam/test surface → иногда нужен отдельный design pass |

## Evidence и gaps

- Owner words: `_ops/chat-recall/2026-08-11-050000-claude-ad4c0fa8.md:18-22`.
- Текущий заказ и строгий protocol gate:
  `_ops/chat-recall/2026-08-29-153512-codex-01a04d13.md:18-20`.
- Primary sources retained: arXiv `2604.02547`, `2605.20049`, `2605.07001`,
  `2605.10039`, `2606.05574`, `2607.27250`.
- Прямой эксперимент Brooks/deep modules → agent correctness не найден.
- Черновик ещё не проверен на GPT-5.6, Claude Opus 5 и Claude Fable 5.
- Owner topology не решён: package history считает Claude tracked owner общим
  источником обеих installed projections, а `skills/claude/README.md` требует
  отдельный Codex owner для non-shared package.
