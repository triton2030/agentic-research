# Subtree AGENTS.md skip on new subfolder

## Observation

При создании новой sub-папки внутри существующего subtree (например, `experiments/<X>/<new>/`) модель читает root `CLAUDE.md` (получает его через session-start hook) и считает orient достаточным. Subtree `AGENTS.md` родительского каталога не открывается — он не виден через session-start, требует явного Read, а forward momentum «надо начать D1» подавляет ритуал.

Корень: orient-before-act контракт в global `CLAUDE.md` требует читать subtree `AGENTS.md` «каждой задетой папки», но новая subfolder воспринимается как greenfield, не как edit задетой папки. Inference miss: создание `mcp/` внутри `experiments/md-embedding-server/` = edit того subtree, не isolated greenfield.

## Counter

- 2026-05-21 [Claude Opus 4.7]: создал `experiments/md-embedding-server/mcp/` (10+ файлов) без открытия `experiments/AGENTS.md` или `experiments/md-embedding-server/AGENTS.md` (если есть). Closeout review поймал как `missing` anchor. Smoke прошёл, реальной поломки не обнаружено, residual risk остался.

## Possible upgrade

Read-list для нового subfolder под существующим subtree должен включать parent `AGENTS.md` явно. Возможный путь — `1start-here` orient контракт можно сделать более explicit про «новая sub-папка = edit parent subtree», или добавить prompt в session-start про «перед созданием subfolder X прочитай X/../AGENTS.md».
