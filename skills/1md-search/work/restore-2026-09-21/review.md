# Независимая проверка

| Роль | Агент | Результат |
| --- | --- | --- |
| Смысл | skill_intent_review, Sol medium | Pass; текст сохраняет исходный заказ, не выбирает новый backend |
| Требования | skill_instructions_review, Sol medium | Найден потерянный fallback без разрешения; возвращён в Выбор корпуса |
| Применение | skill_trajectory_review, Sol medium | Реальный CLI recovery/replay/body read прошёл; уточнён первый запрос при неизвестном языке |

Это одна волна независимой проверки, затем две локальные коррекции по её
результатам. Для изменения текста языка и fallback есть readback, но нет
статистического сравнения поведения моделей. Выполненная проба описана в
[trajectory-evidence.md](trajectory-evidence.md).

Доставка: canonical portable, Codex metadata, tracked и installed projections
синхронизированы штатным `sync_simple_projections.py`; обе installed copies
прошли quick_validate, rumdl и byte parity.
