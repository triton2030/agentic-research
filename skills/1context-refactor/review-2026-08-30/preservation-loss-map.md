# Preservation / loss map — `1context-refactor`

## Цель

Показать смысловую дельту clean-room candidate 2026-08-30 против прежнего
пакета, не требуя совпадения структуры.

| Прежний смысл | Решение в exact candidate |
| --- | --- |
| Любой загруженный слой может влиять | Сохранён в `SKILL.md#Уникальный-контекст`. |
| Post-factum, не прогноз будущих ошибок | Сохранён; профилактика остаётся соседнему skill. |
| Мета-анализ всей доступной сессии | Сохранён в `SKILL.md#Работа`. |
| Типовые ошибки агента | Каталог снят; higher-order модель «любой pre-error контекст» покрывает их без пяти resident units, а примеры остаются в owner evidence/history. |
| Pre-error context и причинный порог | Сохранены одной высокоуровневой проверкой. |
| Дорогой маршрут → `1index` | Сохранён независимо от причинного статуса. |
| Системная проблема → `1findings` | Сохранена только вне текущего результата. |
| Повлиявшие слова пользователя → совет | Сохранены только после causal proof. |
| Source repair → authority + replay | Сохранён в последней строке runtime prompt. |
| Общий causal gate всех outputs | Снят после trajectory finding; у каждого результата свой gate. |
| Refactor/coherence/simplify/audit как локальные режимы | Поглощены semantic owners; этот skill доказывает причину и адресует repair. |
| Семь прежних references | Полностью поглощены self-contained prompt-ом; проверочная история не вошла в runtime. |

Остаточный риск: clean probe должен показать, что causal unknown не блокирует
independently proven route/finding и одновременно блокирует advice/repair.
