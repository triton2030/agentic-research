# Проверка черновика 1readable-code

## Раунд 1

Проверяемая версия: SHA-256
`4ea37c8e825c04d9b575128af191bdecf3b79cba8271ea57d58d1f0fa85f089b`.

### Буквальный аудитор

Принято и исправлено:

- активный набор был 28 единиц без `agents/openai.yaml`, а не заявленные 14;
- удалены ошибочно возвращённые `remaining structural risk` и
  unrelated-cleanup stop;
- `public contract` оставлял внутренние contract decisions внутри skill;
- `removes more … than it adds` не имело общей наблюдаемой меры;
- data-edge rule ошибочно зависел от изменения callers;
- Codex UI prompt продолжал старый six-step protocol;
- route `1codebase-design` был битым в Claude runtime;
- current description не имеет нового routing receipt;
- адрес текущих owner-слов исправлен с `:16-17` на `:18-20`.

### Проверяющий траекторию

Принято и исправлено:

- owner/falsifier gates распространены на read-only review;
- разрешён proposed private owner, пока его выбор не меняет contract;
- net-reduction gate сужен до surface, добавляемой только ради readability;
  required surface теперь не обязана выдумывать удалённую сложность.

### Behavioral probe и comparator

Одинаковый fixture: active enterprise export через API и batch без изменения
сигнатур.

- Draft: до edit назван `exporter/eligibility.py::can_export`; изменены только
  owner и тесты; `python3 -m unittest -v` — 3/3 `OK`.
- No-skill baseline: тот же owner, тот же diff shape и 3/3 `OK`.

Вердикт: probe подтверждает совместимость и наблюдаемый evidence packet, но не
улучшение решения относительно baseline. Improvement остаётся gap-ом; раунд 2
проверяет исправленный текст на новом сценарии.

## Раунд 2

Проверяемая версия: SHA-256
`ece11306a88986fdfa0363f04318b916ff8ecdf471d01039acf339226ee97975`.

### Буквальный аудитор

Принято для следующей версии:

- owner-gate должен покрывать любую нетривиальную review-claim, не только
  structural finding;
- evidence должен быть falsifier-ом каждого claim на owning boundary;
- contract stop обязан назвать runtime-соседа, а не только прекратить skill;
- readability-only condition сформулирован так, чтобы не захватывать required
  surface;
- независимые предикаты разнесены по строкам, обязательный порядок оформлен
  нумерованным protocol;
- UI prompt стал нейтрален к change/refactor/review;
- routing receipts для точного description ещё нужны;
- history-map теперь адресует navigation/safety в `Unique Context`.

Отклонено: вернуть `remaining structural risk` и unrelated-cleanup stop.
Finding возник из двусмысленного receipt раунда 1; `cut.md` фиксирует эти
правила снятыми как global-baseline дубли, нового owner-решения вернуть их нет.

### Проверяющий траекторию

Принято для следующей версии:

- data-edge read должен предшествовать owner choice, edit и нетривиальной
  review-claim;
- completion требует именно опровергающий owning-boundary check/observation;
- UI prompt не должен превращать review в edit.

### Behavioral review-probe

Read-only request: проверить CSV export против repository conventions.

- Назван owner `reporting/formatting.py::format_amount`.
- Claim: `csv_export.py` воспроизводит правило валюты и обходит owner.
- Falsifier: подмена owner до импорта не изменила CSV output; claim выдержал.
- Обычный suite остался 2/2 `OK`, поэтому он не проверял owner delegation.

Вердикт: исправленная версия породила адресуемую review-находку и
claim-specific falsifier там, где зелёный suite был недостаточен. Полезная
Delta для review наблюдалась; probabilistic improvement не доказан.

## Routing receipts перед финальным повтором

Проверялось буквальное `description` версии SHA-256
`4bfa41669d17eb4b7fc89a8918ca20ad57251ea3d5d28cd5d405422879bb5b6c`
в холодном выборе между `1readable-code`, `1codebase-design` и `none`:

- «Убери дублирование правила в трёх обработчиках» → `1readable-code`:
  нетривиальный рефактор внутри уже выбранной границы.
- «Исправь опечатку в комментарии» → `none`: механическая правка.
- «Выбери новый интерфейс адаптера…» → `1codebase-design`: решение меняет
  contract/interface seam.

Это offline routing receipt точного текста, не runtime discovery test. Реальная
активация Claude/Codex остаётся непроверенной.

## Коррекция функции владельцем

Слова владельца от 2026-08-29 16:24 +05:00 материально сменили Commander's
intent: automatic strategic-programming trigger на переходе к коду вместо
локального owner/falsifier contract. Раунды 1–3 и behavioral fixtures выше
остаются evidence о снятой версии, но не проверяют новый черновик. Проверка
новой версии начинается заново.

## Strategic-programming версия — раунд 1

Проверяемая версия: SHA-256
`1559b8185c9126140637d52ff04c2ac94869995919b5a477fe06313b5b22cafc`.

Принято из буквального и trajectory-аудитов:

- tentative owner wording про subagent нельзя превращать в обязательный turn
  для любой неочевидной правки; новый trigger — только material strategic
  uncertainty либо прямой запрос владельца;
- named practices должны менять engineering decision при реальной развилке, а
  не требовать `strategic choice`, avoided-cost и future-change отчёты;
- conceptual integrity, deep modules и strategic programming разнесены по
  самостоятельным строкам;
- contract choice целиком остаётся у runtime-соседа, который получает приоритет
  до решения;
- глобальный `unverified`-гейт повторно снят из active body;
- current automatic trigger требует новых use/skip/near-miss receipts, потому
  что mechanical code edit теперь use, а не skip.

Принятое направление подтверждено новой live-границей владельца:
`_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:17` — сохранять идею и
слова без вредного буквального ритуала.

### Clean executor на исправленной версии

Проверяемая версия: SHA-256
`db0e9914f5807dd28be8ef1955e9297dac2dd5e8ac555b221f532a7678195912`.

Holdout: перевести API-delete и purge на soft delete без изменения публичных
сигнатур и без реализации restore.

- Исполнитель сам признал material strategic uncertainty: должна ли повторная
  purge снова выбирать уже удалённую запись.
- Поэтому exact conditional gate вызвал одного fresh read-only subagent.
- Strongest objection: marker только в `delete()` и filter только в `get()`
  оставят `expired_ids()` неидемпотентным и позволят перетирать первый
  `deleted_at`.
- Это изменило engineering decision: repository стал владельцем полного
  инварианта — первый marker сохраняется, `get()` и `expired_ids()` скрывают
  deleted records; API/jobs и их сигнатуры не менялись.
- `python3 -m unittest -v` — 3/3 `OK`; compileall прошёл; signatures
  подтверждены прежними.

Наблюдаемая Delta есть: fresh view добавил повторную purge и сохранение первого
marker в решение до edit. Остаток fixture: локальный `datetime.now()` без
injected clock; restore/read-with-deleted намеренно не реализованы.

### Cold routing на исправленном description

Проверялся exact `description` SHA
`db0e9914f5807dd28be8ef1955e9297dac2dd5e8ac555b221f532a7678195912`;
все prompts содержат 5–10 слов:

- «Переименуй локальную переменную в функции расчёта» → `1readable-code`.
- «Исправь опечатку в тексте отчёта» → `none`.
- «Выбери интерфейс адаптера между API и хранилищем» → `1codebase-design`.

Offline selection различила automatic code use, non-code skip и contract
near-miss. Runtime activation ещё не доказана.

## Strategic-programming версия — повтор 1

Проверяемая версия checker-ов: SHA-256
`db0e9914f5807dd28be8ef1955e9297dac2dd5e8ac555b221f532a7678195912`.

### Два независимых checker-а

Trajectory checker не нашёл отклонений: тривиальная правка проходит без
ритуала, contract-развилка сначала уходит runtime-соседу, а fresh subagent
остаётся только для unresolved material uncertainty или прямого запроса.

Буквальный checker нашёл и минимально исправлено:

- отрицательное условие `no A or B` не задавало однозначной границы;
- два самостоятельных subagent-шага могли буквально вызвать двух исполнителей;
- `falsify the requested behavior` можно было прочитать как «сломать поведение»;
- evidence-address указывал на заголовок, а не owner-boundary.

Исправленная версия: SHA-256
`80336a5c53f73dc0cf7509791b991b15a2ef429e9637ed3865d861d56b11f4b7`;
`quick_validate.py` — `Skill is valid!`.

### Clean executor после checker-ов

Holdout: переименовать локальную переменную `value` в `total` без изменения
поведения.

- Strategic programming, conceptual integrity и deep modules были применены,
  но не обнаружили material future cost, contract choice или uncertainty.
- Subagent не вызывался; исполнитель сразу сделал один локальный rename.
- Самостоятельная проверка: старое имя отсутствует, `python3 -m unittest -v` —
  1/1 `OK`.

Наблюдаемая Delta отрицательной ветки: automatic coding trigger не превращает
простую правку в отчёт или обязательный внешний review.

## Strategic-programming версия — повтор 2

Проверяемая версия checker-ов: SHA-256
`80336a5c53f73dc0cf7509791b991b15a2ef429e9637ed3865d861d56b11f4b7`.

### Два независимых checker-а

Trajectory checker не нашёл дефекта в направлении, но потребовал missing
validator: положительная subagent-траектория ещё не была проверена на exact
исправленном SHA.

Буквальный checker нашёл и минимально исправлено:

- прямой owner-request одновременно разрешал `proceed without ceremony` и
  требовал fresh subagent;
- `map.md` обрывал correction-address до строки с принятой owner-границей.

Финальная кандидатная версия: SHA-256
`5ebb79da8ddd2e62c8974e9f548a31e238faaf9ac5a8c04b311141283c958dd8`;
`quick_validate.py` — `Skill is valid!`.

### Clean positive executor после checker-ов

Holdout: добавить cache повторных profile reads при двух независимых
write-paths, сохранив публичные сигнатуры и поведение.

- Исполнитель обнаружил material strategic uncertainty в ownership cache и
  вызвал ровно одного fresh read-only subagent.
- Strongest objection: service-local cache пропустит importer writes, а
  write-through cache станет второй изменяемой истиной; менять `loads` на
  miss-counter также нарушило бы наблюдаемую семантику.
- До решения contract choice был передан `1codebase-design`; выбран simplest
  no-new-public-seam route.
- Решение после objection: cache и coherence принадлежат `ProfileStore`,
  `save()` инвалидирует один ключ, `load()` возвращает copy, `loads` сохраняет
  прежний смысл, cache miss скрыт за private `_load_uncached`.
- Самостоятельная проверка: публичные сигнатуры сохранены, exact draft SHA не
  менялся, `python3 -m unittest discover -v` — 5/5 `OK`.

Наблюдаемая Delta положительной ветки: внешний взгляд не создал отчётный
артефакт, а предотвратил stale-read path и изменил owner/invalidation strategy
до edit. Остаток fixture: concurrency не проверялась и не входила в исходный
контракт.

## Runtime routing финального candidate

Exact candidate SHA-256:
`5ebb79da8ddd2e62c8974e9f548a31e238faaf9ac5a8c04b311141283c958dd8`.
Обе project-local probe surfaces побайтово совпали с candidate; live/global
owners были явно отключены либо перекрыты, но не изменены.

### Claude Code 2.1.245 · Fable 5

- Coding use: «Переименуй `value` в `total` в `calc.py`» → runtime вызвал
  `Skill(1readable-code)` и загрузил exact project-local body до чтения кода.
  Сам probe остановился по budget после activation; редактирование не входило в
  routing receipt.
- Non-code skip: «Исправь опечатку в тексте отчёта» → `Skill` не вызывался.
- Contract near-miss: «Выбери интерфейс адаптера между API и хранилищем» →
  runtime вызвал `Skill(codebase-design)`.

### Codex CLI 0.150.0-alpha.12.2

`codex debug prompt-input` показал exact project-local paths для
`1readable-code` и `1codebase-design`.

- Coding use → агент назвал `1readable-code` обязательным до правки и прочитал
  exact project-local `SKILL.md`.
- Non-code skip → агент явно исключил `1readable-code`, потому что отчёт не код.
- Contract near-miss → агент выбрал `1codebase-design` и прочитал exact
  project-local `SKILL.md` до решения.

Runtime receipts подтверждают discovery и взаимную границу descriptions; они
не являются доказательством вероятностного улучшения любого будущего coding
run.

## Approval packet

### Буквальное соответствие

- «автоматически, когда переходим к программированию» → `description`:
  `Use before writing or changing any code`;
- CTO/архитектор и bird's-eye future development → `Unique Context` +
  strategic-programming gate до первого edit;
- «упоминание практик должно обрезать инструкции» → три named handles без
  tutorial: Ousterhout's strategic programming, Brooks's conceptual integrity,
  Ousterhout's deep modules;
- tentative subagent idea + поздняя owner-коррекция → ровно один fresh view
  только при material strategic uncertainty или прямом запросе;
- readable/stable future code → цели coherence и local readable future change.

### Эталонная и фактическая траектории

Эталон: coding transition → named practices до edit → material future cost
меняет approach → без uncertainty сразу coding; с unresolved uncertainty либо
owner-request ровно один fresh view → strongest objection учтён → contract
choice до решения у runtime-соседа → requested-behavior check.

Фактическая отрицательная ветка: local rename → practices применены → material
uncertainty нет → subagent `0` → один rename → 1/1 `OK`.

Фактическая положительная ветка: profile cache → material owner/invalidation
uncertainty → subagent `1` → objection снял service-local/write-through route →
`1codebase-design` до решения → store-owned invalidating cache без нового
public seam → 5/5 `OK`.

### Активный набор, лишнее и escape paths

Активный набор — 19 самостоятельных единиц по правилу `agent-defaults`, включая
`agents/openai.yaml`; runtime-варианты contract route посчитаны раздельно.
Лишних owner-неподтверждённых ограничений после двух повторов не осталось.

Escape paths:

- нет material uncertainty и прямого запроса → proceed without ceremony;
- contract choice → сосед получает приоритет, этот skill не проектирует
  contract;
- named practice не раскрывается в handbook;
- completion проверяет только requested behavior, без глобального отчёта
  `unverified` и без unrelated cleanup.

Остатки перед установкой: exact text требует owner approval; product frame у
пакета отсутствует; topology не зарегистрирована как shared owner и отдельного
`skills/codex/1readable-code` нет, хотя текущие live Claude/Codex copies и
tracked Claude owner исторически поддерживали побайтовую parity.

## Прямая коррекция владельца перед установкой

English-body candidate SHA
`5ebb79da8ddd2e62c8974e9f548a31e238faaf9ac5a8c04b311141283c958dd8` снят до
установки по двум новым решениям владельца:

- terminal outcome обязан включать установку;
- body скила должен быть русским, а `description` — коротким английским
  trigger-only текстом.

Новый draft SHA-256:
`f4d0c9bc5c295d5ed81f360edc1366a949bfdcd6c9d86fbb0f5f512022f89af7`.

Дополнительно снят requested-behavior post-check: `agent-defaults` признал его
общим coding default без уникального readability-решения. Functional clean-run
остаётся acceptance-проверкой пакета, но не active instruction.

Topology-кандидат — `skills/shared/1readable-code/portable/` с Codex UI delta в
`platforms/codex/agents/openai.yaml`: generic sync поддерживает такую форму, а
runtime-specific различий в `SKILL.md` не найдено.
