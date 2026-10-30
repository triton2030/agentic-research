---
description: "Origin, rejected rules and verification evidence for 1interview-tool."
---

# 1interview-tool — происхождение, потери и проверка

**Снят 2026-10-30** при переходе владельца на систему скилов Matt Pocock.[^removal]
Интервью теперь ведут `/grill-with-docs` и `/grill-me`, вопросы другому
человеку — `/to-questionnaire` плагина `mattpocock-skills`. Действующих
пакетов и установленных копий нет; последний shared owner —
[`versions/retired-shared-2026-10-30/`](versions/retired-shared-2026-10-30/).
Всё ниже — история до снятия, работу она не направляет.

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

## Форма из двух документов — 2026-09-15

По уточнению владельца форма отделена от подробных материалов. Каждый вопрос
содержит свёрнутый контекст о причине и последствиях выбора, вопрос, варианты
и поле своего ответа. Оба файла остаются архивными свидетельствами.

[Образец формы](work/template-reading-2026-09-15/demo-pair/interview.md),
[материалы образца](work/template-reading-2026-09-15/demo-pair/interview-materials.md),
[граница проверки](work/template-reading-2026-09-15/evidence-pair.md).

[^removal]: [Слова владельца, 2026-10-30](../../_ops/chat-recall/2026-10-30-143023-claude-20b43aed.md#recall-a4f0045b2c6f4cd783ba8618dd356655).
