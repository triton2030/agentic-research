# Cross-Runtime Skill Sync Skip

## Observation

Когда модель правит skill в одном runtime (`~/.claude/skills/`), она **не
активирует** проверку «есть ли mirror в другом runtime (`~/.codex/skills/`)
и нужно ли синхронизировать». Edits идут на active side, sister copy
остаётся отставшей. User обычно ловит это и явно просит «обнови в кодекс
тоже».

Pattern combo: **streetlight effect** (working context — active runtime, mirror
copy less visible) + **single-runtime tunnel vision** (skill в чате
ассоциируется с runtime, в котором ты сейчас работаешь) + **invisible
infrastructure** (Codex skills существуют, но не в frontload session
context — нет skill list, нет hooks, нет SkillStart load).

Особенно опасно когда mirror — не просто copy, а **divergent fork**
(`md_graph.py` пример): blind overwrite ломает features sister runtime,
manual port требует diff analysis. Тихий accumulation drift между
runtimes.

## Counter

- 2026-05-20 [Claude Opus 4.7]: после правок к Claude versions `1md-graph`,
  `1md-navigator`, `1instruction-layer`, `1folder-contract` SKILL.md +
  `_ops/criteria/folder-contract.md` + global `~/.claude/CLAUDE.md` — не
  активировал «mirror in `~/.codex/skills/` нуждается в sync». User явно
  попросил «обновлять в кодекс версии тоже но в стиле для гпт5.5».
  Обнаружил при discovery что `md_graph.py` дополнительно **diverged
  fork** (47128 vs 45396 bytes), не просто старая копия — отдельный
  finding для решения.
- 2026-05-20 [Claude Opus 4.7] второй случай в той же сессии: правки
  `1md-navigator` SKILL.md (matcher inventory триггеры, Modes table,
  Workflow §2, Anti-patterns) применил **идентично по содержанию** в Claude
  и Codex копиях. User напомнил «помни что у гпт 5.5 свой стиль» — после
  чего пересмотрел Codex Workflow §2 и сжал до outcome-only формы (убрал
  bullet expansion). Pattern recurrence в одной сессии после уже сделанной
  записи — sync-attention не стал durable, classify reminder не появился
  автоматически. Возможно нужна **именно структурная защита** (hook на
  PostToolUse сравнивает Claude vs Codex SKILL.md и flags «style-identical
  diff в Workflow / process-heavy секциях»), потому что memory-side
  reminder уже фактически проигнорирован дважды за сессию.

## Possible upgrade

При substantive edit к skill X в одном runtime — обязательная проверка
`ls ~/.codex/skills/X/` (или симметрично `~/.claude/skills/X/`) до
объявления work done. Если mirror существует — либо sync в том же ходу
(если style mapping тривиален), либо явный handoff finding «mirror N
runtime отстаёт». Не закрывать work как done только для одного runtime
без acknowledgment второго.

Возможная структурная защита: hook на PostToolUse для Edit/Write в
`~/.claude/skills/<name>/`, который сравнивает hash с
`~/.codex/skills/<name>/` и kicks finding если diverge. Это **defense-
in-depth** через runtime instead of memory.

Связано с feedback `marketplace-version-bump` (cache invalidation после
edit) — близкий класс «forgot to propagate after edit».
