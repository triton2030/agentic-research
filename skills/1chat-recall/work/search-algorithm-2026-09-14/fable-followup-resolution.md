# Повторная проверка Fable и решения автора

Та же native session 98aa1245-8120-4560-925f-1a6fbb1dabeb,
resolved_model claude-fable-5-1. Итог Fable: блокирующего дефекта нет.

| Находка | Решение |
| --- | --- |
| Новый тест main использует настоящую hybrid.lock | Принято: cache dir каждого теста изолирован в temp; специализированные queue-тесты сохраняют своё окружение |
| Пустой eligible set назван no-lexical-match | Принято: no-eligible-records отдельно, в JSON и human; фильтры и отсутствие слов различимы |
| BM25 за depth теряет отметку буквального совпадения | Принято: bm25 channels учитывает все lexical matches; dense ограничен участвующими passage/file кандидатами |
| Domain score конфликтов может протечь в пустой ordinary search | Исправлено: сброс после conflict search; regression test |
| Позиционный смысл rankings | Явный комментарий BM25 first, optional dense second; нового механизма не добавлено |

Fable согласился сохранить прежний lexical admission для conflict retrieval.
Рекомендация Fable ограничить этот diff цитатами, не расширять автоматически
темы и не менять модель принята. Повторная проверка не оценивала реальный
корпус: локальные A/B выполнял рабочий агент.
