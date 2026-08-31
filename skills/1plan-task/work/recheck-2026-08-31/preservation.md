# Сохранность 1plan-task

| Смысл | Носитель | Вердикт |
| --- | --- | --- |
| Task как автономный prompt одного агента | Контекст | сохранён |
| Один current writer | Контекст + маршрут передачи | сохранён |
| Goal/result/proof/boundary | Цель + обязательное содержание | сделано явным |
| Relevant sources + load-bearing lines | Обязательное содержание | сохранён |
| Next и stop без planning-чата | Обязательное содержание | восстановлен из product intent и эталона |
| Budget около 20 без artificial split | Контекст | сохранён |
| Current map/epic/sibling gate | Маршрут создания; frontier только по принятому контракту карты | сохранён без глобального запрета параллельности |
| Stale resume stop | Маршрут продолжения | сохранён |
| Sequential authority transfer | Маршрут передачи | сохранён |
| Defer reason/re-entry | Маршрут отложения | сохранён |
| Whole-result closure + map refresh | Маршрут закрытия | сохранён |
| Continuation state/evidence | Обязательное содержание | восстановлен по clean trajectory finding |
| `_ops/plans` | Контекст + route addresses | добавлено по новому owner-evidence |

Reference-файлов нет: условные операции коротки и находятся в гарантированно
прочитанном основном теле; в конкретном запуске активен только один маршрут.
