# Authoring decisions — 1fresh-eyes — 2026-08-30

Статус: completed panel `19def…` дал наблюдаемый вход для последнего
семантического сокращения. Candidate `822c0…` получил две независимые чистые
проверки exact bytes; обе завершились без находок. По текущей owner-границе
следующий шаг — exact approval либо сохранение candidate, не новый review/run.

## Кнопка запуска

Имя `1fresh-eyes` называет операцию владельца. Description сохранён:

`Use when long work reaches a material trajectory fork, the user requests fresh eyes, or names one specialist profile such as auditor or Premortem.`

Он различает поздний наблюдаемый fork, явный запрос Fresh Eyes, named use и
near-miss cross-model/framework/local review. Нового routing failure после
последней trigger-пробы нет, поэтому новая формулировка не обоснована.

## Протокол поведения

Буквальные owner-решения сохраняют фиксированную панель трёх нативных линз и
cross-family Premortem, а также named exception. TWI-разрыв требует только
порядка `anchor → freeze → isolated runs → verified handback`; остальная
логика выражена как критерий результата.

## References

| Стадия | Наблюдаемый вход | Выход | Reference | Локальная цель | Active Claude/Codex |
|---|---|---|---|---|---:|
| Admission | trigger | якорь + mode | body | — | 19/19 |
| Neutralize, panel | якорь + panel | frozen packets / `panel_incomplete` | `packet.md` | да | 19/19 |
| Neutralize, named | якорь + named | frozen packet / blocker | `packet.md` | да | 16/16 |
| Named run | named packet | native result / blocker | inline runtime seam | — | 10/10 |
| Cross-family | Premortem packet | другой family report / blocker | `premortem.md` | да + контекст | 20/20 |
| Native panel | три packets + Premortem | четыре reports / incomplete | `panel.md` | да | 15/14 |
| Correction, native | wrong premise / missing check | corrected report / incomplete | `steering.md` | да | 15/17 |
| Correction, cross-family | wrong premise / missing check | corrected report / incomplete | `steering.md` | да | 15/15 |
| Handback | четыре terminal reports с завершённой correction | owner packet / incomplete | `synthesis.md` | да | 17/18 |

Conservative author recount exact `822c0…`:
Claude `SKILL 35 · packet 19 · panel 14 · premortem 18 · steering 16 · synthesis 19`;
Codex `SKILL 35 · openai.yaml 4 · packet 19 · panel 13 · premortem 18 · steering 18 · synthesis 19`.
Все активные стадии ≤20 без новых references или механического дробления.

`named.md` удалён: его малый exact launch проще держать прямо в named branch.
Остальные references не объединяются, потому что packet, cross-family,
native panel, correction и synthesis имеют разные входы, выходы и runtime
владельцев. Lane methods не дублируются: ими владеют definitions ролей.

## Agent-default chains

- **Freeze до первого report.** Без строки ранний вывод разумно используют
  для улучшения поздних packets → независимость теряется → цена строгости —
  обязательная подготовка всех packets заранее.
- **Разные primary zones.** Без строки одинаковый знакомый corpus выглядит
  надёжнее → роли повторяют один evidence path → цена — controller заранее
  разводит источники. Если четырёх релевантных зон нет, escape route — точный
  `panel_incomplete`, а не выдуманное различие.
- **Exact fresh runtime и cross-family bridge.** Без строки retained/forked или
  same-family поток выглядит дешевле → общий prior сохраняется → цена — точные
  runtime interfaces и дополнительная latency.
- **Recursive guard и terminal incomplete.** Без них обратный вызов или
  отсутствующая роль выглядят заменимыми → возможны зависание и имитация →
  цена — честный stop без результата.
- **Один Premortem без nested delegation.** Без строки cross-family agent
  разумно расширяет поиск собственными subagents → четвёртая линза превращается
  в скрытую панель → evidence paths смешиваются → цена — меньшая внутренняя
  полнота одного отчёта. Clean-run `e1057e0b-…` наблюдал два лишних запуска.
- **Bounded waves.** Без строки capacity error выглядит terminal → панель
  недобирает обязательный report → цена — потеря идеальной одновременности.
- **Same-stream correction.** Без строки новый clean run выглядит свежее →
  одна линза превращается в два голоса → цена — retained-session bookkeeping.
  Trigger включает ошибочную посылку и отсутствующий обязательный проверочный
  элемент, потому что clean trial уже терял `falsifier`.
- **Source verification и no vote.** Без строк уверенный report/большинство
  выглядит authority → решение меняется без доказательства → цена —
  дополнительная проверка и более сложный handback. Непроверенный решающий
  claim или неразличимые evidence paths дают terminal `panel_incomplete`.

## Решение

Все цепочки замкнуты буквальным owner-смыслом либо наблюдавшимся failure trace.
Первый candidate побайтно совпал с runtime. Reviewers нашли реальные terminal
seams; последующая правка сначала размножила их по каждой ветке. Новый
owner-критерий `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:33`
изменил выбор: повторный routing поглощён одним terminal rule, runtime-цитаты
сняты как дубли, `named.md` удалён, форматное дробление tool calls отменено.

Оставшиеся hard lines имеют concrete counterfactual harm в цепочках выше либо
точный runtime interface. Число 20 остаётся attention signal, а не причиной
создавать церемониальную архитектуру.

Completed panel `19def…` подтвердил cross-family bridge, fixed native roster,
source-bound correction и non-voting handback. На его следе `822c0…` убрал
только выводимые дубли. Counts выше подтвердил независимый instruction checker
на exact bytes; все active sets остались `≤20` без новых references или стадий.
