# Сохранность 1plan-task

| Смысл | Носитель | Вердикт |
| --- | --- | --- |
| Один approved result и один current writer | Context + Goal 1 | восстановлено по acceptance loss |
| Task как автономный prompt | Context + Goals 1–2 | сохранён |
| Relevant addresses + load-bearing lines | Goal 2 | буквальное owner-решение |
| Budget около 20 без artificial split | Context | буквальное owner-решение |
| Проверка одобренного результата до записи | Создание, п. 1 | восстановлено по финальному authority finding |
| Проверка живой задачи до возобновления | Продолжение, п. 1 | восстановлено по финальному mixed-probe finding |
| Duplicate retrieval | Create 1–2 | восстановлено по clean-run failure |
| Current map acceptance/frontier gate | Create 2,4 | восстановлено по acceptance probe: невалидная карта не открывает task |
| Semantic break | Goal 3 + Continue 1 | сохранено как authority boundary |
| Sequential authority handoff | Continue 3 | восстановлено по acceptance loss |
| Defer → reason → revalidate full handoff | Continue 4 + 1 | восстановлено по acceptance probe |
| Whole-result closure | Goal 1 + Continue 5 | сохранено по ложному local-Done harm |
| Exact schema, snapshot, modes, writer-recovery ceremony | — | снято: не доказано для глобальной функции |

## Agent-default chains

- `approval gate`: видимая карта выглядит разрешением → task пишет prompt без
  решения следующей работы → граница `1planning` обходится → цена: одна
  сверка утверждённого результата до записи.
- `resume gate`: старая живая задача выглядит по-прежнему исполнимой → frontier
  или одобренный результат уже изменились → task продолжает неверную работу →
  цена: одна сверка перед возобновлением исполнения.
- `sibling retrieval`: новое имя выглядит новым task → соседняя автономная цель
  уже совпадает → появляется двойной writer/результат → цена: один directory
  scan до записи.
- `current map gate`: старое approval выглядит достаточным → frontier уже
  изменился → task публикуется неисполняемым → цена: reread эпика и честный stop.
- `surprise sources`: полный список документов выглядит безопаснее → чистое окно
  теряет load-bearing строки → точные адреса и немногие критичные повторы →
  цена: автор отвечает за отбор.
- `budget`: полный контекст кажется полезным → attention распадается → сначала
  снимается пересказ, split только по самостоятельному результату → цена:
  неделимая задача может остаться близко к пределу.
- `semantic/closure gate`: локальные шаги выглядят достаточными → смысл или
  целый result не доказаны → task возвращается owner-у либо остаётся open →
  цена: нельзя закрыть удобным checklist completion.
- `writer handoff`: два окна считают себя writer-ом → контракт расходится →
  новый читатель доказывает cold start, а authority передаётся явно → цена:
  передача не мгновенна.
- `defer/resume`: старая остановка выглядит достаточной → причина или допуск
  устарели → execution возобновляется по памяти → цена: сохранить причину и
  повторить сверку.
