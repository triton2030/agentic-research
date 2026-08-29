# Refactor map — 1fresh-eyes — 2026-08-29

Статус: черновик в истории. Не live owner и не installed package.

## Функция

На материальной развилке вынести judgment в новый изолированный поток, который
не наследует рамку main: панель четырёх направлений — продукт по умолчанию;
один явно названный critic, auditor или md-scout — исключение с тем же
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
28. Явно названный critic/auditor/md-scout запускается один, без панели.
29. Named exception проходит тот же decision gate и isolation contract.
30. Native output auditor/md-scout не превращается в critic verdict.
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
| Routing и admission | 1–8, 28–30 | `description` + шаги 1–5 body | Сжаты до наблюдаемой развилки; named mode включается только буквальным выбором пользователя. |
| Телос и anti-harm | 9–15 | три цели + Stop | Сохранены; критика не самоцель и surviving route остались явными. |
| Состав и независимый запуск | 16–27, 51–54, 58–61 | шаг 5 + `panel-launch.md` / `named-launch.md` / Codex `premortem.md` | Panel, named и cross-family bridge разделены на последовательные стадии; runtime-механика разнесена по формам. |
| Приёмка и синтез | 31–44, 55–57 | шаг 7 + `synthesis.md` | Перезапуск вызывается одинаковым method/evidence path, не честным совпадением выводов; named product synthesis не читает. |
| Retained dialogue | 45–50 | шаг 6 + `steering.md` | Сохранён отдельной условной стадией; не активен в первом проходе. |
| Датированная runtime-гипотеза | 27, 60–61 | runtime refs + validation notes | Постоянны только проверяемая loop-boundary и metadata; остальная механика проверяется перед install. |

## Карта стадий и активный набор

Счёт ручной: одна единица — независимо исполнимое действие, ограничение или
критерий. Пояснение той же единицы повторно не считается. Старые числа первого
draft отозваны literal checker: объединённые launch surfaces имели нижнюю
оценку ≥23 Claude и ≥37 Codex. Ниже — candidate после stage split; round-2
checker обязан пересчитать его с нуля.

| Стадия | Вход | Один reference | Выход | Активных единиц |
|---|---|---|---|---:|
| Admission | наблюдаемая развилка или explicit named request | — | decision anchor + mode | candidate 12 |
| Claude panel launch | anchor + panel mode | `claude/references/panel-launch.md` | 4 terminal reports | candidate 18 |
| Codex native launch | anchor + panel mode | `codex/references/panel-launch.md` | 3 native reports | candidate 18 |
| Codex cross-family pass | 3 native reports | `codex/references/premortem.md` | Claude verdict или explicit skip | candidate 15 |
| Named launch | anchor + explicit user-named role | runtime `named-launch.md` | 1 native report | candidate 16 |
| Correction, only if needed | wrong premise or residual question | runtime `steering.md` | repaired/retained report | candidate 14 |
| Panel synthesis | terminal reports | runtime `synthesis.md` | next/alternative/continue | candidate 19 |
| Named handback | terminal native output | — | unchanged native product | candidate 5 |

Текущий live surface до refactor: body ≈15 единиц по последнему историческому
счёту; panel brief ≈10; named templates 6–9; steering ≈8; synthesis ≈18;
Codex Premortem ≈11. Некоторые поздние стадии пересекают потолок 20.

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
| Один reference на стадию | Агент прочитает все procedural refs «для полноты» → progressive disclosure выглядит необязательной → какой instruction set активен сейчас → competing rules переполняют внимание → поздняя стадия требует нового чтения. |

Fixed four-lens panel — не новая добавка refactor-а, а буквальное owner-bound
ограничение; оно вытесняет dynamic roster до отдельного решения владельца/A-B.

## Остаточные gaps до install

- Проверить trigger use/skip/near-miss на фактически resolved Claude Opus 5 и GPT-5.6.
- Проверить один real panel holdout и один named exception holdout; structural validation не докажет поведение.
- Reconcile tracked Claude owner с более новой installed Claude delta 2026-08-12; не перетирать её молча.
- Повторно проверить candidate active-set count: текущие числа не acceptance evidence.
- Решить tracked Codex owner отдельно: сейчас live Codex package — единственный runtime owner, второй source tree не изобретён.
