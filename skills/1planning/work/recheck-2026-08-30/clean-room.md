# Clean-room reimplementation — planning-family

## Изоляция

После отклонённого первого запуска исполнитель `/root/clean_core_retry`
получил только три новых commander's intents. Он не читал репозиторий,
old/live packages, history, evidence, прежние candidates или общие
owner-ограничения и не менял файлы.

## Результат

Clean-room reimplementation и Zero-based design независимо вывели три
body-only скила без references:

- `1planning`: chat-decision до записи, один approved result, handoff вниз;
- `1plan-map`: человеческая карта пути и evidence-state без task-authority;
- `1plan-task`: автономный prompt одного агента с semantic-break stop.

После проверки старого пакета вернулись только observed-harm seams:
последовательный frontier, duplicate retrieval и pre-write executability gate.
Условный `1index` seam сохранён по отдельному принятому решению о трудно
найденном маршруте и запрете копировать найденную правду.

## Нулевая альтернатива

Exact schemas, Obsidian assets, routers, stage references, snapshots, status
vocabulary, project validators, mode labels и writer-recovery ceremonies не
выводятся из новой функции и не возвращены без самостоятельного доказанного
вреда.
