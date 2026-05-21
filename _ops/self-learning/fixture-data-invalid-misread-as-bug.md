# Fixture data invalid misread as bug

## Observation

При первом fail в smoke / integration test модель сразу прыгает в "что-то не так с моим кодом" режим — гипотезы про race condition, subprocess concurrency, uv lock, schema drift. Реальная причина часто проще: fixture path не существует, fixture data в формате который backend не ожидает, входной объект empty. Это canonical debug anti-pattern: skip "verify input" step, нырять в backend troubleshooting.

Корень: forward momentum фокусирует внимание на code I just wrote (новый wrapper, новый tool, новая абстракция), а fixture воспринимается как stable / trustworthy. Reality: fixture обычно собирается quickly и менее проверен чем production code.

## Counter

- 2026-05-21 [Claude Opus 4.7]: в smoke test md-mcp один из tools (md_pick) вернул Python traceback в stderr с exit 1. Гипотезы пошли в сторону race condition между uv-запусками concurrent subprocesses. Реальная причина — test path `_ops/criteria/` не существовал (удалён ранее, видел в git status), md_map вернул `{ empty: true }`, и я передал этот empty object как `map_data` в md_pick — backend не получил `files` field и упал. Direct CLI repro on real fixture passed instantly. Lost ~5 минут на false debug path.

## Possible upgrade

Перед фантазированием про backend race / concurrency / locking — `ls <fixture_path>` и `head <fixture_output>`. Дешёвая проверка: «может ли input быть невалиден?» решает 80% smoke fails. Это можно вынести в SKILL.md `1cli-tools` или explicit стенограмму в обработчиках test failure.
