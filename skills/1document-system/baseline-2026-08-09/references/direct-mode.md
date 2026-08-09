# Direct Mode

Используй только после явного `$1document-system`. Результат — один цельный
typed standard artifact с authority `canon | decision | ops | evidence` либо
одна source-bound projection, а не автоматически разложенный пакет документов.

## Вход

Собери доступные: пользовательский outcome, raw material, ближайшие project
instructions, local docs map/registry, existing owner artifacts и local
template. Короткий известный owner/target читай напрямую; известную folder с
множеством файлов читай через progressive route `1md-read`, а неизвестного
owner ищи через `1md-search`, не последовательным Read всего corpus. Не читай
весь global catalog. Большой source draft не загружай одним куском: построй
heading map, читай bounded extracts и веди source coverage ledger до синтеза.

## Ход

1. Классифицируй результат: typed standard artifact или projection. Не повышай
   reader view до standard type.
2. Для typed standard artifact выбери entry через [catalog.md](catalog.md),
   проверь purpose/authority/near-misses, затем прочитай
   [metadata-contract.md](metadata-contract.md) и ровно один
   `template-<code>.md`. При material mismatch объясни и предложи лучший type;
   не заменяй выбор молча. Live local type, metadata и section contracts
   выигрывают целиком; global profile — только fallback.
3. Для projection прочитай [projections.md](projections.md), зафиксируй reader,
   canon lineage и output format. Не применяй standard template; форматную
   реализацию передай подходящему skill/tool.
4. Спроси только то, что меняет type, authority, scope или ключевое решение.
   Другие пробелы закрой по live local section contract. Только если его нет,
   используй точный marker:

   ```text
   SECTION-STATUS: unresolved | not-evidenced | not-applicable — причина
   ```

5. Создай один cohesive artifact. Примени retrieval-label contract из
   [metadata-contract.md](metadata-contract.md): default `description`, а при
   явном local prohibition — только назначенная альтернатива или честно
   отмеченная потеря retrieval capability. Другие самостоятельные gaps назови
   в ответе, но не материализуй без просьбы.
6. Standard filename: `<CODE> — <Standard English Type> — <scope>.md`. CODE и
   English type возьми из catalog/local registry; scope и body — на языке
   проекта. Projection следует local projection naming/format и не получает
   выдуманный standard code.
7. Typed standard artifact пиши decision-dense: короткие sections, точные
   mappings в списках/таблицах, prose только для rationale, ambiguity и argument.
   Projection оптимизируй для reader-а, не ослабляя lineage/claim boundary.
8. Если local docs map уже существует, зарегистрируй artifact и его отношения.
   Не создавай control layer ради одного понятного файла.

## Coverage Before Compression

Для typed standard artifact используй local sections либо fallback standard
sections как cognitive checklist, не как декоративное TOC. До финального письма
сопоставь evidence со всеми обязательными и выбранными conditional sections;
для каждого определи closure по действующему contract. Разреши видимые
противоречия между sections.

Section считается заполненным только по своему mode:

- `OWNER` — полный изменяемый ответ в этом section либо явный `SECTION-STATUS`;
  один pointer section не закрывает;
- `REFERENCE` — точный owner pointer + минимальный контекст либо
  `SECTION-STATUS`, если owner не подтверждён;
- `LOCAL` — точный relevant owner pointer + принадлежащая этому artifact
  application/delta нужной для reader/test глубины; если relevant owner не
  подтверждён, только `SECTION-STATUS`.

Live local section contract может задать другой набор modes и closure rules;
они заменяют fallback `OWNER`/`REFERENCE`/`LOCAL` целиком. «Заполнено» не значит
«написана проза»: жанровая норма полноты corporate template не является
требованием.

Только после coverage сокращай текст. Не удаляй heading, обязательный по live
local section contract; optional empty heading не создавай ради coverage. Точные
знания выражай requirements,
IDs, tables, mappings и models; prose оставляй для rationale и ambiguity.
Каждое решение формулируй один раз в его home-section; другие sections
ссылаются на его ID, а не пересказывают.
Если logical unit представлен prose, table и machine spec, до заполнения выбери
stable ID, одну normative representation и направление
`normative → derived/generated/conformance`; ручная сверка двух editable forms
не является validation.

Для одного большого source draft полное coverage обязательно, но выполняется
progressively: `heading map → bounded extracts → source coverage ledger →
artifact`. Ledger сопоставляет каждую исходную heading/область с target section,
owner pointer, `SECTION-STATUS` или осознанным exclusion; непрочитанный остаток
блокирует claim `decision-complete`.

## Section Ownership

При отсутствии live local section contract standard template помечает каждый
section внутренним mode:

- `OWNER`: храни полный изменяемый ответ.
- `REFERENCE`: форма — ссылка на owner плюс минимальный контекст; не копируй
  спецификацию.
- `LOCAL`: точный relevant owner pointer + artifact-owned application/delta.
  Форма — bounded pointer-table или список
  `owner link → application/delta`; строк может быть столько, сколько нужно для
  decision-relevant behavior и validation. Не копируй owner truth и не
  превращай section в самостоятельную narrative/specification.

Не выводи эти labels в документ. Выводи сами headings. Временное владение
допустимо только в section с mode `OWNER`. Для `REFERENCE`/`LOCAL` без
подтверждённого relevant owner ставь `SECTION-STATUS: unresolved — owner not
confirmed`; если cohesive artifact действительно должен владеть ответом,
сначала явно переназначь mode через local template/registry или System decision.

## Lifecycle И Approval

Для truth-bearing artifact используй `draft`, когда artifact остаётся proposal
или owner не разрешён.
Используй `active`, когда запрос устанавливает/обновляет текущего owner-а и
uniqueness gate пройден. `approved` не меняет authority или lifecycle:
положительный ответ пользователя о текущем artifact может поставить `true`, а
любая смысловая правка возвращает `false`.

## Closeout

Typed standard artifact: один type/scope, authority из
`canon | decision | ops | evidence`, retrieval-label outcome соответствует
metadata contract, правильный admitted home, все core и selected sections, нет
invented claims/duplicate owner; каждый section закрыт по своему mode, а каждый
multiply represented unit имеет одну normative direction. Два дешёвых сигнала
перед finish (сигнал, не stop):
section пересказывает решения чужого owner-а вместо ссылки, либо artifact
заметно превышает типовой размер своего type — перепроверь формы sections.
Projection: один reader view, retrieval-label outcome соответствует metadata
contract, явный `derived-from`, claims сверены с sources, standard type не создан.

