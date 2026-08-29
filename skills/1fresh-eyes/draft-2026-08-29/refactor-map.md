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
3. Не применять его к локальному review, cross-model совету, одному методу или framework-gap.
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
22. Не передавать гипотезу main, его маршрут, подозреваемое место или желаемый вердикт.
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
50. Два follow-up без сужения evidence/альтернативы/границы — stop.
51. Panel brief несёт decision anchor, end result, zone, source-bound facts/gaps и boundaries.
52. Critic brief несёт decision, professional question, raw evidence zone, facts/gaps и boundaries.
53. Auditor brief несёт claimed done, atomic acceptance conditions, raw checks, evidence/gaps и read-only boundary.
54. Md-scout brief несёт corpus, retrieval question, scope, dependent decision, facts/gaps и exclusions.
55. Steering trace сохраняет initial verdict, intervention и revised/unchanged verdict.
56. Synthesis группирует material findings по source, verdict и severity.
57. Raw agent output не переносится молча в canon.

## Группировка и поглощение

| Обслуживаемая цель | Старые указания | Новый владелец | Решение |
|---|---:|---|---|
| Routing и admission | 1–8 | `description` + шаг 1 body | Сжаты до наблюдаемой развилки, decision anchor и двух режимов. |
| Телос и anti-harm | 9–15 | три цели + Stop | Сохранены; критика не самоцель и surviving route остались явными. |
| Состав и независимый запуск | 16–30 | шаги 2–3 + `launch.md` | Состав сохранён; panel и named exception разделены; runtime-механика разнесена по формам. |
| Приёмка и синтез | 31–44, 51–57 | шаг 5 + `synthesis.md` | Перезапуск теперь вызывается одинаковым method/evidence path, не честным совпадением выводов. |
| Retained dialogue | 45–50 | шаг 4 + `steering.md` | Сохранён отдельной условной стадией; не активен в первом проходе. |
| Датированная runtime-гипотеза | 27 | validation notes | Не является постоянным behavioral rule; проверяется перед install. |

## Карта стадий и активный набор

Счёт ручной: одна единица — независимо исполнимое действие, ограничение или
критерий. Пояснение той же единицы повторно не считается.

| Стадия | Вход | Один reference | Выход | Активных единиц |
|---|---|---|---|---:|
| Admission | наблюдаемая развилка или named request | — | decision anchor + mode | 8 |
| Claude panel launch | anchor + panel mode | `claude/references/launch.md` | 4 terminal reports | 16 |
| Codex panel launch | anchor + panel mode | `codex/references/launch.md` | 3 native + 1 Claude report | 19 |
| Named launch | anchor + explicit role | runtime `launch.md` | 1 native report | 14 |
| Correction, only if needed | wrong premise or residual question | runtime `steering.md` | repaired/retained report | 13 |
| Panel synthesis | terminal reports | runtime `synthesis.md` | next/alternative/continue | 17 |
| Named handback | terminal native output | runtime `synthesis.md` | preserved native product | 14 |

Текущий live surface до refactor: body ≈15 единиц по последнему историческому
счёту; panel brief ≈10; named templates 6–9; steering ≈8; synthesis ≈18;
Codex Premortem ≈11. Некоторые поздние стадии пересекают потолок 20.

## Новые ограничения и вытесненная свобода

- Два entry modes вместо общего router-а закрывают смешение панели с native products; цена — агент не может самовольно добавлять named critic в панель.
- Один reference на стадию закрывает накопление нескольких procedural packs; цена — launch templates и Codex Premortem живут в одном более длинном файле.
- Совпавшие выводы допускаются при разных evidence paths: закрывается ложный rerun полезного консенсуса; вытесняется простой proxy «разные ответы = независимость».
- Fixed four-lens panel сохранена только как owner-bound constraint; она вытесняет динамический выбор минимального roster до отдельного A/B и нового решения владельца.

## Остаточные gaps до install

- Проверить trigger use/skip/near-miss на фактически resolved Claude Opus 5 и GPT-5.6.
- Проверить один real panel holdout и один named exception holdout; structural validation не докажет поведение.
- Reconcile tracked Claude owner с более новой installed Claude delta 2026-08-12; не перетирать её молча.
- Исправить stale/broken evidence anchors Product Principles после approval текста.
- Решить tracked Codex owner отдельно: сейчас live Codex package — единственный runtime owner, второй source tree не изобретён.
