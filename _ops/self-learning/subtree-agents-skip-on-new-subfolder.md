# Subtree AGENTS.md skip on new subfolder

## Observation

При создании новой sub-папки внутри существующего subtree (например, `experiments/<X>/<new>/`) модель читает root `CLAUDE.md` (получает его через session-start hook) и считает orient достаточным. Subtree `AGENTS.md` родительского каталога не открывается — он не виден через session-start, требует явного Read, а forward momentum «надо начать D1» подавляет ритуал.

Корень: orient-before-act контракт в global `CLAUDE.md` требует читать subtree `AGENTS.md` «каждой задетой папки», но новая subfolder воспринимается как greenfield, не как edit задетой папки. Inference miss: создание `mcp/` внутри `experiments/md-embedding-server/` = edit того subtree, не isolated greenfield.

## Counter

- 2026-05-21 [Claude Opus 4.7]: создал `experiments/md-embedding-server/mcp/` (10+ файлов) без открытия `experiments/AGENTS.md` или `experiments/md-embedding-server/AGENTS.md` (если есть). Closeout review поймал как `missing` anchor. Smoke прошёл, реальной поломки не обнаружено, residual risk остался.
- 2026-05-21 [Claude Opus 4.7]: closeout task-002. CLAUDE.md был автоматически loaded в context через system-reminder + injected `1start-here/SKILL.md` slice. Модель приняла это за достаточный orient и не сделала explicit Read на root `AGENTS.md` несмотря на CLAUDE.md MUST «Сначала прочитай AGENTS.md». Variant: «implicit-load illusion» — anchor виден в context через reminder ≠ anchor прочитан как companion file. Subtree `_ops/AGENTS.md` тоже не открыт. Smoke clean, project-graph покрыл папочный граф, residual risk low.

## Possible upgrade

Read-list для нового subfolder под существующим subtree должен включать parent `AGENTS.md` явно. Возможный путь — `1start-here` orient контракт можно сделать более explicit про «новая sub-папка = edit parent subtree», или добавить prompt в session-start про «перед созданием subfolder X прочитай X/../AGENTS.md».
- 2026-05-21 [Claude Opus 4.7]: cross-check round 1 (Batch 1 — Tools & navigation) проверял 1start-here по criteria «stale skill-folder script paths» — отчитался clean. Не искал adjacent staleness категории (CLI subcommand vocabulary в routing prose типа «map / headings / narrow read» — старые 0.1.x MCP tool names). Stale vocabulary дошла до Phase C closeout. Variant: «narrow subagent criteria → adjacent staleness missed». Сходно с «implicit-load illusion» pattern (subtree-agents skip). Mitigation: при design cross-check критериев включать adjacent categories (vocab drift, framing drift), не только exact path/symbol matches.
