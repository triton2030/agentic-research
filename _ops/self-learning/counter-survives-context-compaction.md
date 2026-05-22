# Counter survives context compaction

## Observation

После context compaction или reanimation сессии модель видит только compressed / recent slice контекста, а Stop hook читает persistent `~/.claude/state/session-{id}.json` с `turn_id` и `file_changes` за всю реальную сессию. Когда счётчик `skipped_review_count` уже накопил долг в "невидимых" для модели ходах, hook срабатывает на первом аналитическом read-only ходе в видимой части — для модели это читается как false-positive ("я ничего не писал в этом ходу"), и она уходит в defensive verification (`git diff`, чтение hook source) вместо честного closeout прошлой работы.

Корень: модель и hook оперируют разными окнами истории. Hook видит truth за всю сессию, модель видит только compressed slice. Closeout получает странную форму — "diff моего хода пуст, но review нужен" — где модель технически права в своём окне, но wrong про реальный долг сессии.

## Counter

- 2026-05-21 [Claude Opus 4.7]: Запрос пользователя — аудит контекстного окна. Мой visible ход содержал только Bash для замеров (wc, ls, cat, python3 HEREDOC) + чтения хуков. Stop hook fired с directive "второй ход подряд с substantive write без 1work-review". `session-state.json` показал `turn_id: 19` и file_changes из ходов с sqlite3 / md_navigator refactor-candidates — следы работы, которой в моём видимом контексте не было. Время на verification (git diff, head stop-work-review.py) ушло, прежде чем стало понятно: это не мой долг, это накопленный долг сессии до compaction. Closeout всё равно нужен.

## Possible upgrade

Stop hook сейчас формулирует directive как "это второй ход подряд с substantive write без review" — после compaction это читается моделью как обвинение про её непосредственные действия. Более точная формулировка для compacted-session случая: "У сессии накоплен review-долг с предыдущих ходов (last_review_turn=N, pending_changes_turns=[…]), текущий ход без writes — но долг сессии закрыть надо". Это перевело бы модель из defensive "я не писал" в честный closeout прошлой работы по `file_changes` записям.

Альтернатива: в hook output добавлять `last_review_turn` и список `pending_changes_turns` из session-state — модель видит конкретику и не тратит ходы на доказательство своей невиновности.
