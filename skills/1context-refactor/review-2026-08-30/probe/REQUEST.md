# Контекст

Это чистая поведенческая проба двух exact candidate-пакетов:

- `/Users/triton/Documents/GitHub/agentic-research/skills/1index/candidate-2026-08-30/SKILL.md`;
- `/Users/triton/Documents/GitHub/agentic-research/skills/1context-refactor/candidate-2026-08-30/SKILL.md`.

Не читай другие версии этих скиллов, review/history, ожидаемый ответ или
прежние receipts. Прочитай только два указанных `SKILL.md`, эту папку probe и
её подпапки.

# Exact input

- `1index/SKILL.md`: `1314f3cccb237206c2d5c1f7d5ed4837ba52a26a21bdd661957f666afe0b94c1`;
  package: `6c8f0af1a15a9ac1d55a5dd442a90be343d9040ef7d6e1b53c4588b474625d4b`.
- `1context-refactor/SKILL.md`: `c1e85a65762d764f4a3a9f20b9835045758e7d344a793da911dd50664a6c8bc1`;
  package: `172f2648c4c99a65a9190f4d32ce1add2ce631fcbc6fdf8f99c2058213a5737f`.

Повтори эти fingerprint-ы в `RESULT.md` как проверенный вход.

# Цель

Примени оба exact candidate к `SESSION.md` как холодный агент. Покажи, ведут ли
они к правильным решениям без недоказанной причинности и без лишних артефактов.

# Разрешённые действия

- Можешь изменить только существующий `workspace/INDEX.md`.
- Можешь создать только `workspace/FINDING.md` и `RESULT.md` в этой папке.
- Не меняй source-документы, candidates и всё вне этой probe-папки.

# Проверяемый результат

В `RESULT.md` назови causal verdict, сильнейшую альтернативу, контрфакт,
применённые и пропущенные ветки, выполненные прямые проверки и остаточные
неизвестные. Не подгоняй ответ под предполагаемые ожидания.
