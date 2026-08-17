# Cut — session-context, 2026-08-14

- Не введены Zep, граф памяти, второй store или автоматический профиль:
  дефицит закрывает одно поле существующего session holder.
- Runtime не требует массового backfill: карточка обязательна при новом capture
  или касании файла, а отсутствие у untouched legacy не diagnostic. Отдельно
  разрешён один owner-requested backfill исторического корпуса для реального
  retrieval-теста: он читает полный transcript и не переписывает записи.
- Карточка не стала summary решений или owner evidence: она только выбирает
  файл для полного чтения.
- Не придуман числовой лимит длины: форма ограничена одним YAML scalar в одну
  строку и короткими поисковыми фрагментами через `;`.
- `context-note` не снят: он владеет сценой одной записи; `session-context` —
  задачей и лексикой целого разговора.
- Карточка не смешана с record ranking или embeddings цитат: два lexical-гейта
  выводят её отдельным `session_candidates`, а `records` сохраняет собственный
  порядок. E5 остаётся у цитат; card ablation не дала ему top-5 прироста.
- Внешний `codex_recall.py` снят из нормативного Retrieval: global skill не
  зависит от project-local experiment, owner corpus не уходит другой модели,
  а full-holder / later-holder postcondition остаётся у одного runtime-owner.
