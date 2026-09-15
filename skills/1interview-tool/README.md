---
description: "Origin, rejected rules and verification evidence for 1interview-tool."
---

# 1interview-tool — происхождение, потери и проверка

Живой owner: `skills/shared/1interview-tool/`. Tracked проекции —
`skills/claude/1interview-tool/` и `skills/codex/1interview-tool/`; installed —
`~/.claude/skills/1interview-tool/` и `~/.codex/skills/1interview-tool/`.
Проекции напрямую не редактируются.

- `origin.md` — слова владельца, одобренный синтез и допуск к пересборке;
- `cut.md` — снятые правила и таблица потерь;
- `evidence.md` — support envelope и результаты проверок.

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1interview-tool --write --install
python3 skills/shared/sync_simple_projections.py 1interview-tool --check
```

## Редакция 2026-09-15

[Установленная версия](versions/installed-2026-09-15/SKILL.md) исследует ошибки будущего исполнения документов. Варианты полноценно обоснованы; найденные ценные ответы сохраняются в конце. Формы и их архив лежат в `_ops/interviews/` и `_ops/interviews/_archive/`; архив не является каноном.

[Источники и карта изменений](work/foresight-2026-09-15/cut.md), [проверки](work/foresight-2026-09-15/evidence.md), [состояние работы](work/foresight-2026-09-15/state.md).
