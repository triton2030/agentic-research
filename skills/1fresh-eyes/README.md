# История 1fresh-eyes

Живые runtime owners — [Codex](../codex/1fresh-eyes/SKILL.md) и
[Claude](../claude/1fresh-eyes/SKILL.md). Действующая продуктовая пара
остаётся у [Claude owner](../claude/1fresh-eyes/product-frame.md);
она общая по смыслу и не входит в installed package. Эта папка — история.

- Последние самостоятельные снимки: [Codex](versions/installed-codex-2026-09-12/SKILL.md)
  и [Claude](versions/installed-claude-2026-09-12/SKILL.md).
- [Карта изменений](cut.md).
- [Намерение, источники и решения](work/refactor-2026-09-12/intent-and-preservation.md).
- [Проверка и её границы](work/refactor-2026-09-12/verification.md).
- [Состав финальной доставки](work/refactor-2026-09-12/final-runtime-manifest.json).
- [Состояние работы](work/refactor-2026-09-12/state.md).

2026-09-12: автономный рефактор установлен в обе среды. Общий вход отделён
от главных зон поиска; состояние проверки различает содержательный пробел
и незавершённость. Состав панели, named-исключение, свежие окна и порядок
межмодельного Premortem сохранены. Вердикт unchanged не требует возражений.

Для этой пары доставка использует явный manifest: общий sync-helper пока
не различает два source-only product-frame файла и runtime. Не устанавливай
их вслед за SKILL.md и references ради прохождения generic check.
