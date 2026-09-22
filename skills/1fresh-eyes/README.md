# История 1fresh-eyes

Живые runtime owners — [Codex](../codex/1fresh-eyes/SKILL.md) и
[Claude](../claude/1fresh-eyes/SKILL.md). Действующая продуктовая пара
остаётся у [Claude owner](../claude/1fresh-eyes/product-frame.md);
она общая по смыслу и не входит в installed package. Эта папка — история.

- Последние самостоятельные снимки: [Codex](versions/installed-codex-2026-09-22-full-panel/SKILL.md)
  и [Claude](versions/installed-claude-2026-09-22-full-panel/SKILL.md).
- [Карта изменений](cut.md).
- [Намерение и состояние](work/expansionist-2026-09-22/state.md).
- [Решения по проверкам](work/expansionist-2026-09-22/review-decisions.md).
- [Проверка и её границы](work/expansionist-2026-09-22/verification.md).
- [Все участники и совместный результат](work/expansionist-2026-09-22/panel-audit/report.md).
- [Состав финальной доставки](work/expansionist-2026-09-22/final-runtime-manifest.json).
- [Предыдущая проверка](work/refactor-2026-09-12/verification.md).

2026-09-22: Expansionist добавлен пятой линзой. Метод ищет дополнительную
пользу доступных опор для исходной цели, учитывает цену отвлечения и проверку
гипотезы. Результат может поддержать текущий ход. Профиль установлен также
в native agents обеих сред. После проверки остальных участников уточнён
Premortem: он удерживает успех текущего плана и отличает цену защиты от
предположения. Методы Ladder, Solvent и Prospector сохранены.

2026-09-12: автономный рефактор установлен в обе среды. Общий вход отделён
от главных зон поиска; состояние проверки различает содержательный пробел
и незавершённость. Состав панели, named-исключение, свежие окна и порядок
межмодельного Premortem сохранены. Вердикт unchanged не требует возражений.

Для этой пары доставка использует явный manifest: общий sync-helper пока
не различает два source-only product-frame файла и runtime. Не устанавливай
их вслед за SKILL.md и references ради прохождения generic check.
