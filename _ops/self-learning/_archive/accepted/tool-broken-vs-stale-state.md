# Tool Broken Vs Stale State

## Observation

Модель списывает ошибку на инструмент, не проверив что **input state**
устарел. Tool crash → conclusion «tool broken / `pick --files` не
работает», тогда как реальная причина — устаревшая JSON map от прошлой
сессии (ссылалась на удалённые в этой же сессии файлы).

Pattern: **error attribution skip**. Когда tool exits with stack trace,
модель прыгает к выводу «bug в инструменте» без шага «а актуальные ли
inputs?». В сессии, где сам же удалял/перемещал файлы, любая
saved-state JSON (headings map, search output, pick map) становится
stale без явного refresh.

Связано с canonical failure mode `stale-anchor` из 1start-here
(якоря не проверены свежим Read), но другая мишень: тут stale не GOAL
или criteria, а **scratch state модели от прошлого turn'а**.

## Counter

- 2026-05-20 [Claude Opus 4.7]: re-test 1md-navigator после improvement.
  `pick /tmp/knowledge-headings.json --files 30,27,25 --extract` упало
  со stack trace `path.read_text` на несуществующем файле. Я написал в
  critique «`pick --files` не работает», в первом round'е feedback
  пользователю. Реально — JSON map был сгенерирован в начале сессии,
  до того как я удалил `wisdom-agents.md`; pick пытался читать
  удалённый файл. Регенерация map'а через `headings --output
  /tmp/<fresh>.json` → `pick --files 5,7 --extract` сработал. Критика
  была неверной атрибуцией.

## Possible upgrade

Перед атрибуцией tool error — короткий ground-check:
- input state mtime vs session-write times: если saved-map старше
  последнего file delete/move в сессии — regenerate первым делом.
- error message mentions a path? → `ls <path>` до conclusion «tool
  bug». Если path gone — это stale state, не tool.

Применимо: любая работа с saved JSON maps (headings, search, pick),
embedding indexes, cache files, test fixtures, snapshot files.

Стоимость регенерации почти всегда меньше стоимости false-positive
bug report.
