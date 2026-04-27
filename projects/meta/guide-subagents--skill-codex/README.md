# Guide Subagents — Codex

Рабочая папка по Codex-скиллу `guide-subagents`.

## Что Это Закрывает

`guide-subagents` — короткий guide по типовым провалам native Codex
subagents. Он срабатывает только на явный запрос про subagents / delegation /
parallel workers / multiple agents.

Скилл держит пять вещей:

- понять, какой judgment должен купить запрос: скорость, evidence, critique,
  domain knowledge, disjoint implementation, validation или synthesis;
- решить, стоит ли вообще делегировать и какая форма дешевле: main agent, one
  sidecar, multiple workers, critique/evidence вместо implementation;
- оставить у main agent blocking step, integration surfaces и dirty/hotspot
  файлы;
- дать worker-ам owned-scope briefs с явно названными skills, нужным стилем и
  форматом;
- после возврата проверить on-disk diff и отделить scoped truth от repo-level
  или preexisting failures.

Форма результата при этом не фиксирована как "короткий ответ". Для
code-workers это часто короткий scoped delta. Для business / strategy /
marketing / analysis workers нормальным owned deliverable может быть
развёрнутый вывод в чат, если он не выходит за границы scope.

## Важные Границы

- Upstream owners остаются upstream: `project-roadmap`, `instruction-layer` /
  `repo-shape`, `task-contract`.
- `guide-subagents` не компенсирует отсутствующий план, не придумывает критерии
  и не превращается в mini-orchestrator.
- Если нужный judgment стратегический, а не исполнимый, ход уходит в
  `strategy-discussion`, а не в запуск workers.
- Не запускать subagents только потому, что задача кажется parallel-ready; без
  явного запроса пользователя main agent работает локально.
- Native Codex launch mechanics важны только там, где они предотвращают
  реальный сбой.

## Файл

- `SKILL.md` — компактный guide с trigger, split discipline, skill prompting и
  gotchas.
