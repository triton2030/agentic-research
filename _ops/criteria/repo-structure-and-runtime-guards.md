# Repo Structure And Runtime Guards Criteria

## Зона ответственности

Когда работа меняет базовую форму проекта, папки, ownership, validators,
hooks, plugins, MCP/apps, runtime boundaries, deletion/move cleanup или
control-surface topology.

## Цель

Форма репо помогает агенту и человеку понять, где живёт правда, не превращая
`_ops` в backlog и не создавая лишних control surfaces или runtime guards.

## Критерии

Rule: Новая папка или файл создаётся только после выбора функции, которую не держит существующая поверхность.
Why: Иначе новый surface станет будущей точкой drift.

Rule: `_ops/` содержит горячую рабочую форму, а не backlog, inbox или архив.
Why: `_ops` должен читаться в работе и не превращаться в склад заметок.

Rule: `_ops/AGENTS.md` объясняет, как пользоваться папками `_ops` и какие скилы вызываются для recursive planning, criteria, interviews, findings и plans.
Why: Агенты не должны писать случайные вещи в `_ops` без скилла или необходимости.

Rule: Missing base shape создаётся через `bash ~/.claude/skills/1start-here/scripts/init-three-level.sh [/path]` (Claude) или `python3 ~/.codex/skills/1start-here/scripts/init_project_shape.py <repo-root>` (Codex); оба add недостающее без перезаписи существующих owner-файлов.
Why: Скрипт создаёт базовую форму одинаково на обеих агентных платформах, а устаревший маршрут после bootstrap передаётся в `1folder-contract`.

Rule: Base shape включает `_ops/plans/_archive/`, а каждая созданная папка внутри `_ops/plans/**` получает свой `_archive/`.
Why: User signal: при смене верхнего planning layer старые нижние задачи должны уходить в архив, а не оставаться активным контекстом.

Rule: `1start-here` отвечает за onboarding/bootstrap, а `1folder-contract` отвечает за уже выбранные structural controls.
Why: Пользователь решил отделить structural controls и system coherence от language-quality scope `1instruction-layer`.

Rule: Удаление старого surface требует назвать, чем теперь покрыта его функция.
Why: Chesterton's fence защищает load-bearing state от удаления под видом cleanup.

Rule: Если правило можно проверить структурно, сначала рассмотреть самый простой наблюдаемый validator, hook или permission.
Why: Runtime guardrail надёжнее текстового напоминания, но сложный guardrail сам становится системой поддержки.

Rule: `UserPromptSubmit` инжектит intent-grounding только на 1-м ходу сессии (threshold через `session-state.turn_id`); substantive-write gate реализован отдельным `PreToolUse` hook `criteria-gate.py`, который требует prior Read из applicable `_ops/criteria/*.md` перед `Edit`/`Write`/`MultiEdit` или mutating `Bash`; `SessionStart` инжектит только ориентационную часть `1start-here/SKILL.md` (между `<!-- session-start-inject:* -->` маркерами), а не весь файл.
Why: User decision (план «Hooks ↔ Skills enforcement architecture»): прежняя UserPromptSubmit-фраза «перед каждым write прочитай applicable файл» была non-blocking reminder, повторявшимся каждый ход даже после первого ориентационного; реальный write-gate в PreToolUse даёт structural enforcement без context noise.

Rule: Session state живёт в `~/.claude/state/session-{session_id}.json` через CLI `~/.claude/skills/1start-here/scripts/session-state.py`; это canonical shared structure между hooks и skills (anchor_reads, file_changes, skill_invocations, markers_seen, applied_criteria), разрывает re-read loops через mtime-tracking, привязывает Stop-маркеры к substance, GC удаляет файлы старше 14 дней.
Why: Stateless hooks стреляли одинаково каждый ход независимо от прошлой работы (re-read `documentation.md` 5 раз, verbatim citation декоративен, маркеры ради маркеров); session-state делает enforcement aware о прочитанном/применённом/закрытом.

Rule: `Stop` hook не заставляет проговаривать полный `1work-review`: он срабатывает только на sensitive surfaces (`_ops/criteria/`, `_ops/GOAL.md`, `_ops/PROJECT-ROADMAP.md`, `AGENTS.md`, `CLAUDE.md`, `.codex`, `.claude`) или 3+ изменённых файла; после этого просит компактную сверку просьбы, evidence и остаточного риска.
Why: User signal 2026-05-18 + Claude-side reference: финальные hook-сообщения стали слишком тяжёлыми после малейшей правки; hook должен держать safety net на широких/рискованных изменениях, а обычный maintenance закрываться без ритуала.
