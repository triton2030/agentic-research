# Structural Change Without Owner Skill

## Observation

При работе, которая меняет structural surface (новая папка в иерархии,
central index `_ops/project-graph.md`, paired AGENTS↔CLAUDE shim, hooks
folder shape), модель делает правки сама вместо routing через owner skill
`1folder-contract`. Pattern: модель видит, что задача «понятная» (создать
папку, обновить routing), и не зовёт structural owner, потому что нет
explicit prompt-level trigger. В результате — ownership leak в central
index: новая поверхность существует, но не описана в `depends-on`,
`related-when` или `veto-class`.

`1folder-contract` SKILL.md прямо говорит: «Structural controls — folder
shape, hooks, validators, config, permissions, MCP/apps, scripts и
runtime boundaries — являются режимом `1folder-contract`.» Но модель не
сверила свою активность с этим определением до действия.

## Counter

- 2026-05-20 [Claude Opus 4.7]: function-first refactor wisdom-agents.md
  → 5 файлов в `knowledge/agents/`. Создал новую папку, обновил
  `related-when` в `_ops/project-graph.md`, но `depends-on` block не
  тронул — `knowledge/agents/*.md` пропал из central index до closeout
  review. Closeout (`1work-review` + read of folder-contract criteria)
  поймал gap, дописал строку depends-on. Один лишний repair cycle.

## Possible upgrade

Перед substantive write на любую structural surface (folder create /
delete / rename, `_ops/project-graph.md`, AGENTS.md routing block,
hooks, settings.json) — проверить, не режим ли это `1folder-contract`.
Триггер по объекту правки, не по explicit user prompt: «trade folder
shape» / «change central index» / «add new owner surface» = автоматом
позвать или сверить с `1folder-contract` criteria до write.

Сейчас trigger surface `1folder-contract` фокусируется на user-facing
phrases («связка слоёв», «комфортно ли агенту», «Owner Map»). Можно
добавить implicit triggers по типу действия: создание новой папки в
`knowledge/`, правка `_ops/project-graph.md`, новый owner surface без
declaration. Это сместит skill ближе к moment-of-action.
