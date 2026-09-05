# Итог — 1chat-recall, 2026-09-05

Переписан и установлен в Codex и Claude. Проверяемый пакет:
`../../versions/installed-2026-09-05-goals/{codex,claude}`.

## Что изменено

Тело и три режима построены заново от цели. Capture оставляет восстановимую
речь, Retrieval возвращает применимое evidence либо различимый пробел,
Integrity ограничивает изменения доказанным поручением. Сохранены авторство,
deletion-only, selection, metadata, локальный корпус, хронология, живой owner,
фоновый дешёвый поиск и границы repair. Специфичные runtime швы сохранены.

Helper-ы создают первую карту с записью атомарно, показывают релевантные
конфликты отдельно и поддерживают `--supersedes-unresolved SEARCH_NOTE`.
Четыре ответа отмены взаимоисключающие; старая запись не отменяется по догадке.
Фильтрация ранжированных позиций сохраняется; conflict route использует тот же
выбранный lexical/hybrid runtime. При обрезке warning не пропадает.

## Evidence

- Два независимых reviewer-а; выводы и решения — `reviews.md`.
- Финальный Codex owner: `python3 -m unittest discover -s skills/codex/1chat-recall/tests -p 'test_chat_*.py' -q` — 125 tests OK, 16.074s.
- Финальный Claude owner: аналогичная команда для Claude — 122 tests OK, 15.978s.
- `test_evaluate_retrieval.py` Codex — 6 tests OK. Всего выполнено 253 теста в финальной проверке.
- `cli-probe.json`: настоящий subprocess Capture → query → strict в отдельном
  временном корпусе; реальный lexical и hybrid. Первая карта создана;
  conflict-only query имеет selection=conflicts и warning при returned=0;
  unresolved запись сохранена и видна; strict exit=0.
- `installed-manifest.json`: SHA-256 всех 20 файлов Codex и 21 файла Claude;
  состав/содержимое owner, installed и версии совпадают. Claude live — ссылка
  на tracked owner; Codex live — отдельная проекция.
- Все относительные Markdown-ссылки installed пакетов разрешаются;
  description обеих сред — 182 символа. Тесты больше не замораживают прежнюю
  прозу: семантика проверена отдельно, механически проверяются routes/tools.
- Trigger cases: «запомни мой критерий» → Capture; «что я раньше решил» →
  Retrieval; «проверь корпус» → Integrity; «составь handoff» → не этот skill;
  до существенной реплики нет capture, после неё есть. Это авторская проверка
  маршрутизации, не измеренный model benchmark.

## Нагрузка и пределы

Reviewer оценил совместный active set в примерно 22 Capture / 25 Retrieval /
20 Integrity обязательств до локального закрытия интерфейсных пробелов.
Финальные правки добавили сведения о path/tool, а не новый режим; снижение
активной нагрузки не заявлено. Цели заменили порядок рассуждения, но не
сняли дорогие ограничения. Два text review не являются поведенческим A/B;
универсальное превосходство или меньшая latency не доказаны. Поисковый runtime
ранжирует ограниченный набор, не доказывает отсутствие всех старых отмен.

## Установленные тексты

- [Codex SKILL](/Users/triton/.codex/skills/1chat-recall/SKILL.md)
- [Codex Capture](/Users/triton/.codex/skills/1chat-recall/references/capture.md)
- [Codex Retrieval](/Users/triton/.codex/skills/1chat-recall/references/retrieval.md)
- [Codex Integrity](/Users/triton/.codex/skills/1chat-recall/references/integrity.md)
- [Claude SKILL](/Users/triton/.claude/skills/1chat-recall/SKILL.md)
- [Claude Capture](/Users/triton/.claude/skills/1chat-recall/references/capture.md)
- [Claude Retrieval](/Users/triton/.claude/skills/1chat-recall/references/retrieval.md)
- [Claude Integrity](/Users/triton/.claude/skills/1chat-recall/references/integrity.md)
