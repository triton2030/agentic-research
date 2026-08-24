# Evidence — 1handoff

Рефактор 2026-08-09: тело 6.5 → 6.2KB при добавленном разделе «Совет
следующему агенту» и самовызове (чистое сжатие старого ~1KB). Черновик v1 →
коррекция владельца (летопись/мета-анализ) → v2 → «да» + поправка о
самовызове. Обе установки обновлены, parity diff-ом; Codex-дельты проверены
fgrep. Поведенческих прогонов нет — прогоны делает владелец лично.

Усиление 2026-08-18: 120 → 153 строк при семи добавках владельца и слитых
аудитом дублях. Разведка тремя субагентами (инвентарь + 5 реальных хендофов,
веб-практики 2026, knowledge-корпус); аудит двумя линзами в отдельных окнах.
Путь утверждения: карта усилений → «да» на v4 → коррекция (субагентный proof
снят) + критерий главной цели → «да» на v5 → запись. Пять копий: md5 parity
(3× Claude-идентичные, 2× Codex-идентичные), diff Claude↔Codex = 4
платформенные строки, YAML frontmatter валиден, live-каталог сессии подхватил
новый description. Поведенческих прогонов нет — прогоны делает владелец
лично; продолжимость под новым текстом = candidate.

## Английский смысловой рефактор — 2026-08-24

Путь утверждения: owner-evidence + инвентарь функций → триада и карта → «Да,
делай» на черновик → полный английский текст + две независимые линзы → краткий
перечень изменений → «Да ок делай» на запись. Адрес утверждений:
`_ops/chat-recall/raw/2026-08-24-183916-codex-01a033fe.md`.

Baseline → результат: 1,432 → 1,285 слов; 16,598 → 8,328 байт. Строк стало
176 → 209 из-за коротких предложений, списков и явного разделения операций;
мерой упрощения остаются снятые/слитые обязанности, не строки.

Structure/distribution после записи: пять существующих SKILL.md получили один
и тот же SHA-256
`3f6920973219dbf98af33bde37b309a899f30cfd02767a55cec17a6bf1f4c6b8` —
shared portable, tracked Codex/Claude и обе installed-копии. Platform-specific
body delta снята переносимой строкой invocation.

Behavior-preservation до внешнего consumer/comparator case остаётся
`candidate`; чтение текста и parity его не доказывают.

Парный read-only comparator на одной реалистичной closeout-сцене прогнал
старый `HEAD`-текст и новую installed-копию в изолированных окнах. Оба сохранили
тот же следующий validation-шаг, owner anchors, recall/cleanup outcomes и
границу чужих concurrent changes. Старый текст требовал 2–4 trap-блока при
явном отсутствии surviving trap и оставлял безусловный commit/push рядом с
чужими изменениями; новый пропустил Incidents/Advice/traps по гейтам и выбрал
conditional Git outcome. Это source-supported evidence изменения двух
конфликтных решений и сохранения continuation на одном случае, не
probabilistic proof. Остались неоднозначности ширины management/advice scan и
гранулярности claim labels; реальный handoff остаётся следующим behavior test.

## Outcome-first пересборка — 2026-08-24

Baseline → результат: 209 → 168 строк; 1,285 → 1,138 слов; 8,328 → 7,446
байт. Семантическая мера — снятая четырёхшаговая процедура, квоты и
candidate-algorithm при сохранённом consumer contract, а не длина сама по себе.

Pre-edit: три независимых read-only окна вернули outcome-map, loss-map и
adversarial clean-window misreads. Post-draft: architecture audit нашёл два
дефекта центральной модели; acceptance audit — четыре material fail. После
ремонта оба окна подтвердили pass по всем шести находкам.

Paired holdout из двух чистых окон дал старому и новому контракту одну сцену:
неназванный stale lease-owner, owner correction без recall-address, чужие code
edits и 40-минутный disproved route. Обе версии исправили неназванный owner,
не затронули чужие edits и передали causal dead-end history. Новый текст
сначала смешал `recall: no qualifying evidence` с continuation blocker;
явное разделение было добавлено, повторный reader-check подтвердил исправление.

Structure/distribution: `quick_validate.py`, `rumdl` и `git diff --check`
проходят на candidate. Tracked Codex/Claude и обе installed projections имеют
SHA-256 `ef587b7f5f4675a6f1be33abf3fda2518f2e1c7ed1437597c05ecfe66e40c413`.
Ambiguous shared portable body удалён; shared-папка снова содержит только
product truth.
