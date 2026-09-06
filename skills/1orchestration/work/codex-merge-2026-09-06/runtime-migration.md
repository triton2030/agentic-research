# Миграция владельцев

После приёмки кандидата:

1. `skills/codex/1orchestration/` становится runtime owner нового Codex-пакета.
2. `skills/claude/1orchestration/` становится runtime owner прежнего Claude-пакета; байты SKILL и references сохраняются.
3. `skills/shared/1orchestration/` снимается после сверки с закоммиченным снимком; старое дерево находится в папке оркестрации before/shared-orchestration и истории Git.
4. Существующий sync_simple_projections.py поддерживает два runtime owners без изменения кода.
5. Live `~/.codex/skills/1codex-bg-threads/` снимается только после установки, parity и сохранения полного снимка. Второй активный маршрут не оставляется.
6. Указатель `1deep-agents/references/runtime-orchestration.md` обновляется с 1codex-bg-threads на Codex-версию 1orchestration во всех существующих проекциях через shared owner.
7. Реестр и истории фиксируют runtime owners и адреса сохранённых версий.

Проверка before мутации: shared source, Claude tracked, Claude installed и retiring live package побайтно совпадают с сохранёнными состояниями — preinstall-safety.json.
