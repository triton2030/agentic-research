# Claude — проверка инструкций, волна 2

Проверяющий: claude_instruction_review, чистое окно. Неизменный claude-candidate по claude-candidate-hashes.json.

Находка: claude-intent заявляет actual Codex run и native Opus как falsifiers, но такого Claude-runtime прогона нет. Codex-авторинг Luna+Opus не доказывает новый Claude-маршрут. Ограничить заявленный результат проверкой текста и сохранности контрактов, явно назвать поведенческую проверку незакрытой.

Решение root: принято. claude-structural.json проверяет ссылки, отсутствие Desktop API, точное совпадение памяти и неизменность 1codex; live Claude end-to-end не выполнен и не заявляется.
