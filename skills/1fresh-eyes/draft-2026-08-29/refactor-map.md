# Refactor map — 1fresh-eyes — 2026-08-29

Статус: черновик в истории. Не live owner и не installed package.

## Функция

На материальной развилке вынести judgment в новый изолированный поток, который
не наследует рамку main: панель четырёх направлений — продукт по умолчанию;
один явно названный доступный specialist profile — исключение с тем же
контрактом свежести и своим native output.

## Уникальный контекст

Main не может сам вычесть из накопленного контекста собственную рамку. Новый
поток становится свежим не от ярлыка роли, а от ненаводящего входа,
непересекающихся способов проверки и независимой опоры на источники.

## Цель пользователя

- На развилке длинной работы получить четыре действительно разные рамки; при явном named-запросе — один нативный продукт без ритуальной панели.
- Не передать свежему потоку гипотезу main, желаемый вывод или взаимозаменяемую зону.
- По проверяемым основаниям выбрать следующий ход, ближайшую альтернативу или продолжение без изменений; хорошую работу не ломать ради критики.

## Материальное решение

Panel-only вариант отклонён. Поздний состав панели — `ladder` / `solvent` /
`prospector` + cross-family Premortem — не отменил решение владельца
2026-08-10 о named exception. Проверенный Premortem показал, что isolation и
brief templates одиночных вызовов не имеют второго owner-а, а `auditor` и
соседний `1deep-agents` по-прежнему маршрутизируют их через `1fresh-eyes`.

Не переоткрыто без отдельного owner-решения: фиксированный состав четвёрки и
обязательность Premortem. A/B фиксированной панели против динамической не
проводился.

Новая owner-boundary 2026-08-29: верность идее выше буквального копирования;
агентские добавки не должны вредить скилу. Поэтому потолок 20 остаётся
диагностикой внимания, а не product goal; reference существует только для
самостоятельной когнитивной фазы, не для каждого тривиального handback.
Источник: `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:15`.

Owner-boundary той же даты: правильное поведение сначала выводится из
`Уникального контекста` и `Цели пользователя` как commander's intent;
процедурная строка остаётся только у невыводимой runtime-механики, safety
boundary, критичного порядка или falsifying acceptance. В bounded-pass туда
перенесены причина изоляции, разные пути проверки, native handback и запрет
голосования; дубли удалены без нового дробления. Источник: тот же holder, `:21`.

Уточнение `:22` переносит тот же принцип внутрь содержательных references.
Локальную `Цель` получили `packet`, `panel`, `premortem`, `steering` и
`synthesis`; малый `named` остался служебным. Точные runtime API, схемы,
authority/terminal boundaries, критичный порядок и falsifying acceptance не
поглощены целью.

## Плоский список старых указаний

1. Вызывать skill, когда длинная работа дошла до проверки траектории или неразрешённого остатка.
2. Вызывать skill по явному запросу fresh eyes, панели, critic, auditor или md-scout.
3. Не применять его к unnamed локальному review, cross-model совету, одному методу или framework-gap; явный named-запрос пользователя остаётся входом.
4. До запуска назвать вопрос на столе.
5. До запуска назвать, какое решение изменит ответ.
6. Взвешивать ход против конечного результата из GOAL/Product Frames.
7. Если эти owners неполны, вывести результат из имеющегося и профессиональных практик.
8. Не запускать панель без вопроса и decision consequence.
9. Искать лучший следующий ход у тех, кто смотрел не туда, куда main.
10. Требовать разных рамок, иначе панель возвращает prior main в копиях.
11. Считать расхождение продуктом, а не помехой.
12. Назвать следующий ход, ближайшую альтернативу и продолжение без изменений.
13. Не превращать критику в самоцель.
14. Считать выживший маршрут с опорой полноценным результатом.
15. Не править артефакты панелью и не подменять ею final acceptance.
16. Панель состоит из `ladder`, `solvent`, `prospector` и cross-family Premortem.
17. Domain critics не являются линзами панели.
18. Каждая линза получает собственную зону.
19. Swap-тест: взаимозаменяемые briefs означают, что зоны не выведены.
20. Первые проходы запускаются в новых non-fork потоках.
21. Brief должен быть самодостаточным и ненаводящим.
22. Передавать текущий маршрут/решение как source-bound объект judgment, но не rationale main, diagnosis, подозреваемую причину или желаемый вердикт.
23. Не пересказывать метод роли: им владеет role definition.
24. Получить terminal report каждой обязательной линзы.
25. `story_unfalsifiable` — terminal Premortem verdict, а не находка.
26. Недоступная роль или runtime — честный stop, не имитация.
27. Смена runtime, roster или cross-family route переоткрывает механическую часть.
28. Явно названный доступный specialist profile запускается один, без панели.
29. Named exception проходит тот же decision gate и isolation contract.
30. Native output named profile не превращается в critic verdict.
31. Каждый panel report предъявляет native verdict.
32. Каждый panel report предъявляет собственный falsifier.
33. Каждый panel report предъявляет source anchor.
34. Каждый panel report предъявляет отдельное следствие для решения.
35. Уникальной фразы недостаточно для доказательства различия.
36. Одинаковый вывод допустим только при разных evidence paths и основаниях.
37. Взаимозаменяемый метод/evidence — invalid test, а не подтверждение.
38. Decision-changing утверждения проверяются по источнику.
39. Путь или citation сами по себе не являются support.
40. Findings различаются как accepted, rejected, deferred, needs verification или incomplete.
41. Native disagreement сохраняется, а не усредняется.
42. Голосование не выбирает следующий ход.
43. `satisfied`/`architecture_ok` — полноценный результат без повторного запуска.
44. Владелец решения синтезирует, роли не получают authority над решением.
45. Фактическую ошибку исправлять в том же retained stream.
46. Исправление передаёт только fact/source/scope delta, не желаемый вывод.
47. Follow-up того же stream не становится новым независимым голосом.
48. Новый stream нужен при смене вопроса, линзы, scope или утечке inherited context.
49. Follow-up не расширяет исходные permissions и write scope.
50. Follow-up прекращается, когда он не может назвать новый material evidence step, falsifier или сужение decision boundary.
51. Panel brief несёт decision anchor, end result, zone, source-bound facts/gaps и boundaries.
52. Critic brief несёт decision, professional question, raw evidence zone, facts/gaps и boundaries.
53. Auditor brief несёт claimed done, atomic acceptance conditions, raw checks, evidence/gaps и read-only boundary.
54. Md-scout brief несёт corpus, retrieval question, scope, dependent decision, facts/gaps и exclusions.
55. Steering trace сохраняет initial verdict, intervention и revised/unchanged verdict.
56. Synthesis группирует material findings по source, verdict и severity.
57. Raw agent output не переносится молча в canon.
58. Panel brief перечисляет, что main уже читал, и даёт каждой линзе другую главную source zone.
59. `Кругов пройдено` передаётся только числом, без маршрута и результатов main.
60. Если Codex сам запущен из Claude, он не вызывает Claude обратно для Premortem, а возвращает явный skip с gap.
61. Codex package содержит runtime metadata `agents/openai.yaml`.

## Группировка и поглощение

| Обслуживаемая цель | Старые указания | Новый владелец | Решение |
|---|---:|---|---|
| Routing и admission | 1–8, 28–30 | `description` + три anchor-шагa body | Named mode включается только буквальным выбором profile пользователем. |
| Телос и anti-harm | 9–15 | три цели + `synthesis.md` | Решение принадлежит main; surviving route остаётся полноценным. |
| Состав и независимый запуск | 16–27, 51–54, 58–61 | `packet.md` + `panel.md` / `named.md` + Codex `premortem.md` | Пять крупных фаз вместо 19–23 файлов; packet остаётся frozen boundary, runtime launch — отдельный deep module. |
| Приёмка и синтез | 31–44, 55–57 | `synthesis.md` | Verify, preserve disagreement и decision handback собраны в одной когнитивной фазе; named product её не читает. |
| Retained dialogue | 45–50 | `steering.md` | Сохранён отдельной условной стадией; не активен в первом проходе. |
| Датированная runtime-гипотеза | 27, 60–61 | runtime refs + validation notes | Постоянны только проверяемая loop-boundary и metadata; остальная механика проверяется перед install. |

## Карта стадий и активный набор

Счёт ручной: одна единица — независимо исполнимое действие, ограничение или
критерий; schema считается одной только когда поля не задают самостоятельных
выборов. Выполненные anchor-решения становятся artifact и не остаются активной
процедурой следующей фазы. Число показывает риск потери внимания, но не
оправдывает церемониальное дробление.

| Стадия | Вход | Один reference | Выход | Активных единиц |
|---|---|---|---|---:|
| Admission | наблюдаемый trigger | body | якорь решения + `mode` | 30 / 30 |
| Packet, panel | якорь панели | runtime `packet.md` | замороженные пакеты ролей | 27 / 27 |
| Packet, named | якорь named | runtime `packet.md` | замороженный пакет роли | 23 / 23 |
| Premortem bridge, local | замороженный пакет | runtime `premortem.md` | отчёт другой семьи / blocker | 29 / 29 |
| Native panel | замороженные пакеты + Premortem | runtime `panel.md` | три отчёта / `panel_incomplete` | 25 Claude / 24 Codex |
| Synthesis | четыре устойчивых отчёта | runtime `synthesis.md` | decision handback | 24 Claude / 25 Codex |
| Named run + correction + handback | замороженный named packet | `named.md` / Premortem + условный `steering.md` | native product / blocker | 13 / 13 |
| Native correction | ошибочная посылка | runtime `steering.md` | заменённый отчёт | 22 Claude / 24 Codex |
| Cross-family correction, local | ошибочная посылка Premortem | runtime `steering.md` | заменённый отчёт | 24 / 24 |

Nested `$1codex` / `$1claude-mcp` bodies не входят в локальные закрытые суммы;
фактический active set на их вызове выше локальной фазы. Все excess остаются
диагностикой внимания: локальные цели увеличили conservative semantic count,
но clean probe не показал потери packet behavior; нового церемониального
дробления ради числа нет.

## Новые ограничения и вытесненная свобода

`дефолт → механизм → изменяемое решение → вред без строки → цена строгости`:

| Добавка | Пятизвенная цепочка |
|---|---|
| Decision anchor до панели | Агент может принять сам факт запроса fresh eyes за достаточный повод → ритуальный запуск кажется полезным → запускать ли панель без decision consequence → четыре отчёта не меняют решения → задержка до формулировки вопроса. |
| Current route как факт, но без rationale main | Агент либо скроет объект judgment, либо передаст своё объяснение → оба пути кажутся способом дать контекст → что именно получает fresh stream → без объекта ответ абстрактен, с rationale он копирует main → пакет требует source-bound state и запрещает часть полезного контекста. |
| `Main уже читал` + другая source zone | Агент отправит всем знакомый корпус → повторное чтение кажется надёжным → где линза ищет falsifier → разные роли принесут один evidence path → main обязан подобрать другой релевантный источник. |
| Named mode только по словам пользователя | Агент сам выберет знакомого critic вместо панели → специализация кажется дешевле → кто имеет право отменить fixed-four default → broad fork снова сузится до одной рамки → неявный специализированный trigger не получает isolation wrapper. |
| Bounded waves при capacity | Агент остановит обязательную панель после slot error → runtime limit выглядит terminal blocker → ждать/разбивать ли запуск → решение теряет обязательные голоса → теряется идеальная одновременность. |
| Одинаковый итог допустим при разных evidence paths | Агент перезапустит честный consensus → owner phrase «разные отчёты» легко спутать с разными выводами → считать ли равный verdict провалом → полезное подтверждение расходует новые потоки → стилистическое разнообразие больше не proxy независимости. |
| Source verification decision-changing claims | Агент примет уверенный native report → профиль выглядит authority → менять ли decision по citation → ложная опора попадёт в синтез → synthesis тратит внимание на проверку. |
| No final acceptance | Панель объявит проверяемый артефакт готовым → четыре experts выглядят как acceptance gate → кто закрывает done-state → critique подменит auditor evidence → нужен отдельный acceptance owner. |
| Только релевантный reference в текущем режиме | Агент прочитает все procedural refs «для полноты» → competing rules кажутся полезной полнотой → какой instruction set активен сейчас → внимание распадается → body-only handback остаётся допустимым escape; отдельный файл не обязателен для каждой стадии. |

Fixed four-lens panel — не новая добавка refactor-а, а буквальное owner-bound
ограничение; оно вытесняет dynamic roster до отдельного решения владельца/A-B.

## Install evidence и остаточные gaps

- Trigger use/skip/near-miss пройден на clean current GPT runtime и
  `claude-opus-5`; финальный English description отдельно вернул expected
  B/C/D/H use и A/E/F/G skip/near-miss.
- Named и panel trials выполнены; final hash-bound trace сохранён в
  `checks-install.md`.
- После reference-goal pass отдельный clean packet probe сохранил все девять
  falsifying fields panel/named packet без утечки main rationale.
- Claude и Codex tracked runtime owners синхронизированы с installed
  projections; byte parity и exact hash проверены.
- Финальный независимый recount после bounded-pass приведён выше; admission 30
  и nested runtime-owner остаются видимым excess. Functional probes не показали
  omission, поэтому ради цифры controller снова не дробится.
- Shared portable owner не создаётся: runtime-формы различаются cross-family
  механикой; installed copies — только projections своих tracked runtime
  owners.
