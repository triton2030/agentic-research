# Gate 1 — Построй Effective Chain Map

1. Назови runtime и будущий task/path context: одна и та же папка может иметь
   разные chain в Codex, Claude Code или другом runner-е.
2. Перечисли только реально загружаемые global → root → relevant subtree
   instructions; отдели `file exists` от `text reaches this task`.
3. Подтверди loading, fallback, imports и truncation через
   `discovery-loading.md` / `discovery-limits-placement.md`, только когда они
   спорны; не переноси привычку одного runtime в другой.
4. Расположи loaded sources по precedence и назови место, где их rules
   конфликтуют, дублируются или оставляют gap.
5. Для каждого material meaning назови live semantic owner; runtime winner и
   semantic owner могут оказаться разными фактами.
6. Разреши текущий effective winner из loading + precedence, а не из имени файла
   или уверенности автора.
7. Если спорны root/subtree topology, duplicate или placement, прочитай
   `placement-scope.md` / `placement-protocol.md`
   до owner-решения.

**Результат gate:** `runtime + task/path + loaded sources + precedence +
conflicts/gaps + effective winner`. Не можешь доказать loading или precedence →
назови gap; не выбирай owner из воображаемой chain.

Далее: `gate2-owner.md`.
