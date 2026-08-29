# Cut — рефактор 1handoff 2026-08-09

Baseline: skills/shared/1handoff/portable/SKILL.md@ba25ffa (Claude) и
baseline-2026-08-09-codex-SKILL.md (Codex). Потери против baseline:

- Раздел «Closeout Gate» — растворён в Критерии+Завершение (смысл цел,
  носителей стало один).
- «Ни одна ветка не осталась unresolved» ×3 → один критерий.
- «claude-opus-5 или claude-fable-5» — снят как протухающее знание; generic
  формулировка (взята из Codex-копии).
- Проверка «frontmatter, timestamp, #, обязательные разделы, непустой файл»
  как отдельный абзац — свёрнута в Механику 6 (каркас) и Завершение.

# Усиление 2026-08-18 — потери против версии 2026-08-09

- «При изменении контракта самого скила — consumer-side resume в чистом
  контексте» — снята из тела: адресат — автор скила, не исполнитель хендофа;
  правило живёт здесь и в контракте 1skill-shaping (evidence по claim).
- Субагентный consumer proof + fallback `proof: self` — утверждены в v4, сняты
  коррекцией владельца до записи: «сам скил хендоф уже мета анализ диалога…
  не нужен мета анализ мета анализа другим субагентом».
- Вводные фразы «Проект агентный: … уборка за собой» и «якорь … связывает
  летопись в цепочку» — вычеркнуты аудитом (рассказ без меняемого решения);
  операции остались в Механике 2 и 7.
- Из Цели и Дельты сняты дубли осей проверено/непроверено и proof (аудит:
  один смысл — один владелец); владельцы — Критерии + Механика 4 и 8.

# Усиление 2026-08-23 — потери против версии 2026-08-18

- «будущие правки инструкций сделают выводы сами» (Механика 6) — снята:
  опровергнута корпусом, один урок оплачен трижды за четыре дня, ни одна
  правка инструкций из хендофов не последовала.
- «предотвращение (точный owner или check)» как текстовое поле — снято как
  текст, заменено действием: что изменено и где, либо причина, по которой
  бортик не ставится.
- Карточка «несущие посылки сессии» (Холмс, наблюдение против умозаключения) —
  не вошла отдельной строкой: поглощена рабочей моделью Механики 6.
- Карточка D «инверсия вперёд: где вероятнее всего погибнет следующий агент»
  (Мангер) — не вошла: измеренного провала нет, а правило без него добавляет
  вес без эффекта. Вернуть, если хендоф начнёт передавать состояние, на
  котором преемник стабильно ошибается новым способом.
- Форма «сжатая история общения по ходу диалога» — заменена на адресуемые
  блоки: нарратив пишется в конце, задним числом, и ложится в слабейшую зону
  окна; предъявлено владельцу тремя рисками, форма принята.

## Английский смысловой рефактор — потери 2026-08-24

- Русский runtime-текст снят полностью; Product Frame и история скила не
  переводились, потому что не являются исполняемым телом.
- Повторы Goal / Criteria / Completion, отдельные `Delta` и пустой
  `Known failures` сняты; их действующие смыслы принадлежат Outcome, Closeout,
  Consumer Check и Completion.
- Author-facing запрет копировать recall procedure снят из runtime; исполнитель
  уже получает операцию «следовать контракту и не имитировать recall».
- Три независимых команды ставить guardrail слиты в одну cleanup-операцию;
  Incident и Advice теперь только ссылаются на её исход.
- Безусловные `commit and push` и удаление мусора сняты; вместо них действует
  project-authorized и recoverable Git/cleanup boundary.
- Обязательные вопросы о dead end и terrain trap получили `if any`, чтобы
  чистая сессия подтверждала отсутствие, а не выдумывала историю.
- Платформенные строки `$1chat-recall` / Claude Skill tool слиты в переносимое
  `current runtime’s skill mechanism`; поведенческой дельты между runtime
  больше нет.

Не потеряно: ручная доставка пути, две независимые ветки, cleanup всего
затронутого слоя, recall-only owner anchors, два ярлыка состояния, incident,
terrain model, отдельный advice, трёхстрочная преамбула и consumer proof.

## Outcome-first пересборка — потери 2026-08-24

- Нумерованный четырёхшаговый `Closeout` снят; остался один причинный порядок:
  recall и live state до packet, consumer evidence до delivery.
- Перечень cleanup-операций перестал быть знаменателем выполненности; его
  поглотил outcome «каждый затронутый management owner current либо точно
  передан», а названные поверхности остались неограничивающей ориентировкой.
- Трёхветочный алгоритм отбора каждой candidate-delta снят; его поглотил один
  action-changing gate.
- Команды `mkdir`/`date`, квоты `3–5` строк и `2–4` traps,
  Markdown-микроправила и повторные списки packet content сняты как procedural
  scaffolding.
- Consumer questions переписаны как способности clean-window reader; наличие
  всех headings прямо объявлено недостаточным stop-condition.
- `skills/shared/1handoff/portable/SKILL.md` снят как двусмысленный второй
  source: registry назначает shared-папке только Product Frame.

Не потеряно: one-per-chat, manual path, live-truth priority, независимый
`1chat-recall`, cleanup неназванных session-affected owners, owner anchors,
HEAD и previous handoff, два ярлыка state-claim, causal terrain model,
incident/advice separation, repeated-lesson guardrail, strong-signal placement
и независимые completion outcomes.

## Разрез на стадии — 2026-08-29

Baseline: `skills/{claude,codex}/1handoff/SKILL.md` (168 строк, идентичны, равны
installed-копиям). Дефект — ёмкость: ~56 самостоятельных единиц применимы
одновременно при бюджете 20 (`1skill-creation`, слова владельца
`_ops/chat-recall/2026-08-28-053552-claude-9bb215e3.md:20`). Разрез на
последовательные независимые стадии — механика, изобретённая владельцем там же.

### Поглощено инструкцией высшего порядка

- Преамбула «три независимых исхода» ×1 + перечень исходов в `Completion` ×1 →
  протокол стадий в теле + отчёт исходов в стадии 3.
- «packet is dated delta» ×1, «not a transcript/summary/task plan/user
  profile/canon» ×1, «live state overrides» ×2, «prefer address over copied
  explanation» ×1 → один инвариант тела «dated delta, never a second truth,
  each of those already has its own owner» + строка преамбулы пакета
  (артефакт, не правило автора).
- `Goal` ×5 (means necessary · examples non-exhaustive · boundaries remain
  required · no new permission · authority) → одна строка «Every name, list and
  example orients and does not bound» в теле + authority-граница в стадии 1.
- Recall ×6 (boundary «resolve through 1chat-recall» + «never imitate» +
  `Owner Evidence` ×4) → 3 единицы стадии 1 + carrier-правило стадии 2.
- Cleanup ×5 → 4 единицы стадии 1 («follow owning contract» выводится из
  «change a surface only through its own owning contract»).
- `Continuation Delta` causal chain + `## Terrain Model` минимальная модель → 
  одна единица стадии 2: форма цепочки объявлена там, где она пишется.
- «Omit optional sections when gate not met» + «Confirm absence instead of
  inventing» + «one addressable `###` block» → одна единица стадии 2.

### Снято

- `Required State Before Delivery` как отдельный раздел: причинный порядок стал
  нумерованным протоколом тела, где он и исполняется.
- «Follow the owning contract for every managed surface» как отдельная строка
  `Boundaries` — дубль стадии 1.
- «Record the actual running model … Do not invent a subversion» как отдельная
  строка `Boundaries` — переехало внутрь единицы про frontmatter, туда, где
  `model` пишется.
- «It exposes where work stopped, …» как отдельное предложение — слито с
  единицей о четырёх разделах.

### Не потеряно

Один хендоф на чат; ручная передача пути; запрет lifecycle-surface; примат live
truth; независимый `1chat-recall` и запрет пересказа владельца;
`no recall address` как отдельный blocker; уборка неназванных session-affected
owners (планы, находки, INDEX, инструкции, git, temp); recoverability и
veto-граница; guardrail вместо повторного совета; action-changing gate дельты;
`_ops/handoffs/<timestamp>-<actual-model>.md` и frontmatter; трёхстрочная
преамбула; четыре раздела; сильные сигналы вне середины; два ярлыка claim-а;
модель местности и опровергнутое прочтение; `Incidents` по гейту; отдельный
`Advice` только с наблюдениями; адресуемые `###`; consumer-перечтение чистым
окном; «разделы заполнены» не является stop-condition; четыре независимых
исхода; residual risk и stop.

### Новое ограничение

Три чтения стадийных файлов вместо одного тела.
Закрываемый провал: ~56 одновременных единиц против измеренного порога
управляемости; накопление текста прогона
(`_ops/chat-recall/2026-08-28-183116-claude-0713a127.md:25`).
Вытесненная свобода: агент больше не видит весь контракт в момент вызова и
платит три чтения; стадию нельзя пропустить «по памяти о теле».

### Правки по ходу режимов

- «Record a misleading reading … Invent no traps and write no chronological
  diary» снята отдельной единицей: полностью выводится из единицы про
  `## Terrain Model` (модель, которую сессия держала и оставила), из запрета
  выдумывать в единице про гейты разделов и из action-changing gate. Смысл
  «не хронологический дневник» оставлен пояснением внутри единицы Terrain Model.
- Локальное «that list orients you and does not bound the outcome» в стадии 1
  снято: тело говорит это про все списки скила.
- `description` 234 → 188 символов: сняты «file transfer» (нет такого соседа) и
  «a second handoff in the same chat» (инструкция тела); добавлен реальный
  сосед `task plan`.
- Раздел «Протокол поведения» не заводился: вход режима не выполнен, владелец
  для этого скила требовал обратного (2026-08-24 19:42).
