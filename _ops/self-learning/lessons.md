# Self-Learning Lessons

> [!summary] Живой контракт
> **Owner:** [[_ops/self-learning/README|Self-Learning]]
> **Skill:** `1self-learning`
> **Лимит:** до 4000 символов через `wc -m`
> **Граница:** проектные проблемы -> `1findings`; устойчивые цитаты -> `1user-said`; routing смотри в [[_ops/AGENTS|_ops routing]] и [[_ops/project-graph|Project Graph]].

## GPT-5.5

### Scope и user workflow

- Сначала фиксируй workflow, consumer map, batch bounds, freshness канона и живые лимиты skill-контракта.
- Не расширяй "исправь всё", не принимай рамку "сократить" до проверки потребителей и не решай по одному знакомому корпусу.
- Перед design/role-вариантами восстанови 1-2 реальных сценария: мягкая "полезная" роль может промахнуться, если пользователь ищет жёсткого оппонента.
- При batch-работе заранее называй включённые/исключённые папки, references и metadata; перед массовой заменой замораживай target set и проверяй dry-run.
- В Obsidian-форме уровни `##` / `###` и bullets — основа; callouts и закрытые toggles не должны оборачивать весь файл.

### Evidence before blame

- Перед обвинением tool/code проверяй вход: stale map, fixture path/output, temp side effect, cwd/git context, существование пути и валидность данных.
- Внешние skill-файлы проверяй прямым чтением, валидатором или diff против baseline; для metadata сначала смотри реальную YAML-shape, а не top-level ключи по памяти.
- Для read-only smoke держи temp roots в `/tmp`, иначе проверка портит доверие к слову "read-only".

### Tools и handoff

- Если skill/best-practice слой мог измениться, перечитай живой owner/source, а не локальный guide или старый снимок.
- При `argparse` помни, что тесты могут собирать `Namespace` вручную: используй `getattr(args, ..., default)` или обновляй fixtures.
- Если bridge relay truncated, восстанавливай полный вывод из durable logs до rerun.
- Когда пользователь спрашивает, почему не был вызван `1findings` или `1self-learning`, не объясняй задним числом вместо действия: классифицируй сигнал и запиши владельцу.
- Перед запуском named subagents сверяй доступные `agent_type`; если runtime не принимает роль, не имитируй критика, фиксируй mismatch.
- Для native subagents не смешивай `fork_context` с явным `agent_type`: либо наследуй full-history context, либо запускай named role без fork и дай self-contained brief.

## Claude Opus 4.7

### Review и background jobs

- После sensitive/global/structural write сразу запускай `1work-review`; маленький diff, стадия плана, closeout-summary или approval большого плана не закрывают review debt.
- На долгих background jobs не запускай poll-loop и не kill по low CPU: жди notification, продолжай другую работу, проверяй output/DB/network sockets и expected rate-limit duration.
- После compaction hook может видеть долг прошлых ходов, которого нет в видимом контексте: закрывай session-level review debt по доступным следам.

### Routing и соседние owner-скилы

- Не думай по аналогии между runtime roots: если файл/feature не найден в ожидаемом месте, расширь поиск по `~/.codex` / `~/.claude`.
- Новая subfolder внутри subtree = правка parent subtree: явно читай parent `AGENTS.md`, не считай injected/root context достаточным.
- При работе внутри одного скила спрашивай, какой соседний owner-skill уже владеет частью сигнала; frame активного скила не должен закрывать `1md-navigator`, `1md-graph`, `1ia-audit`.

### Debug и structural contracts

- Перед расширением downstream API трассируй pipeline до ближайшего места, где данные ещё correct; часто чинить надо mid-pipeline, не receiver.
- При tool error сначала refresh saved state и проверь path из traceback, потом называй tool broken.
- Structural surfaces (`project-graph`, папки, hooks, settings, paired shims) сначала route/check через `1folder-contract`.
- Для diagnostic thresholds проверяй минимум два стилистически разных корпуса; cutoff из одного familiar corpus не переносится.

## Other Agent

Пока пусто. Добавляй только переносимые уроки, которых нет в блоках выше.
