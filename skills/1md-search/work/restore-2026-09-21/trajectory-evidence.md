<!-- rumdl-disable MD013 -->

# Проверка маршрута `1md-search`

## Вердикт

Новый draft провёл разрешённую пробу от неизвестного состояния индекса до
ответа из прочитанного тела. Фильтры корпуса сохранились при восстановлении,
`drafts/**` не попал в выдачу, dense-канал работал. Ответ подтверждён
`docs/recovery.md`, а его текущий статус — корпусным `AGENTS.md`.

На этой одной пробе новый и прежний варианты приводят по существу к одному
безопасному маршруту: scope и разрешение → `NO_INDEX` recovery → карта → тело →
проверка статуса источника. Проба не подтверждает, что новый вариант исполняется
надёжнее прежнего.

## Проверенный ответ

После сбоя нужно продолжить с последней зафиксированной контрольной точки.
Повторно обрабатываются только незавершённые записи; уже завершённые записи
запускать снова нельзя.

Основание: `docs/recovery.md#Recovery policy > Resume interrupted work`, строки
3–5. Корпусный `AGENTS.md` объявляет только `docs/**` текущей документацией и
исключает `drafts/**`. Противоположный текст в `drafts/obsolete.md` прямо
помечен отклонённым и не является текущей политикой.

## Реальная проба

Во всех командах `md` использован разрешённый loopback backend:

```bash
env MD_EMBEDDING_API_URL=http://127.0.0.1:61143/v1 \
  MD_EMBEDDING_MODEL_ID=test/synthetic-recovery \
  md search-read /var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-search-proof-ncbu2o2m \
  --query 'Как продолжать обработку после сбоя процесса?' --limit 5 --json
```

Ответ: `index_warmup_required`, `corpus_state.state: NO_INDEX`; `next_step`
сохранил `docs/**` и исключил `drafts/**`.

```bash
env MD_EMBEDDING_API_URL=http://127.0.0.1:61143/v1 \
  MD_EMBEDDING_MODEL_ID=test/synthetic-recovery \
  md index /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-search-proof-ncbu2o2m \
  --dry-run --path-include 'docs/**' --path-exclude 'drafts/**' --json
```

План: три новых section/chunk, `cleanup_enabled: false`; выдан
`transaction_id: txn_037172d67818104c`.

```bash
env MD_EMBEDDING_API_URL=http://127.0.0.1:61143/v1 \
  MD_EMBEDDING_MODEL_ID=test/synthetic-recovery \
  md index /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-search-proof-ncbu2o2m \
  --confirm --transaction-id txn_037172d67818104c \
  --path-include 'docs/**' --path-exclude 'drafts/**' --json
```

Ответ: `embedded: 3`, `corpus_state.state: FRESH`.

```bash
env MD_EMBEDDING_API_URL=http://127.0.0.1:61143/v1 \
  MD_EMBEDDING_MODEL_ID=test/synthetic-recovery \
  md status /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-search-proof-ncbu2o2m --json
```

Ответ: `FRESH`; фактический `path_scope` — include `docs/**`, exclude
`drafts/**`, `declared_by_corpus: true`.

Исходный русский запрос повторён с теми же фильтрами сначала как карта, затем
как тела:

```bash
env MD_EMBEDDING_API_URL=http://127.0.0.1:61143/v1 \
  MD_EMBEDDING_MODEL_ID=test/synthetic-recovery \
  md search-read /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-search-proof-ncbu2o2m \
  --query 'Как продолжать обработку после сбоя процесса?' --limit 5 \
  --path-include 'docs/**' --path-exclude 'drafts/**' --json

env MD_EMBEDDING_API_URL=http://127.0.0.1:61143/v1 \
  MD_EMBEDDING_MODEL_ID=test/synthetic-recovery \
  md search-read /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-search-proof-ncbu2o2m \
  --query 'Как продолжать обработку после сбоя процесса?' --limit 3 \
  --expanded --token-budget 3000 \
  --path-include 'docs/**' --path-exclude 'drafts/**' --json
```

Карта вернула `docs/recovery.md` и нерелевантный `docs/retention.md`;
`engine.dense: true`. Только expanded-ответ дал используемое тело. Усечения по
бюджету не было: `token_total: 98`, `token_budget: 3000`.

Второй аспект проверен отдельным запросом на обнаруженном языке источника,
также картой и телами:

```bash
env MD_EMBEDDING_API_URL=http://127.0.0.1:61143/v1 \
  MD_EMBEDDING_MODEL_ID=test/synthetic-recovery \
  md search-read /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-search-proof-ncbu2o2m \
  --query 'What should happen to completed records after a process failure?' \
  --limit 5 --path-include 'docs/**' --path-exclude 'drafts/**' --json

env MD_EMBEDDING_API_URL=http://127.0.0.1:61143/v1 \
  MD_EMBEDDING_MODEL_ID=test/synthetic-recovery \
  md search-read /private/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/md-search-proof-ncbu2o2m \
  --query 'What should happen to completed records after a process failure?' \
  --limit 3 --expanded --token-budget 3000 \
  --path-include 'docs/**' --path-exclude 'drafts/**' --json
```

Оба канала работали (`bm25f: true`, `dense: true`), а expanded-тело повторило
правило о незавершённых и завершённых записях. После retrieval источник прочитан
напрямую; карта и snippet доказательством не использовались.

## Действующий набор требований в ключевых моментах

| Момент | Доступные требования | Наблюдаемое действие |
| --- | --- | --- |
| До semantic-команды | Draft `SKILL.md:30–48`; корпусные `AGENTS.md` и `.md-tools.toml`; текущее разрешение на loopback и cache | Прочитаны scope и разрешение; выбран абсолютный корень и `docs/**` |
| `NO_INDEX` | Draft `SKILL.md:63–67`; `references/index-lifecycle.md:40–62`; `_envelope.next_step` | Выполнены dry-run, confirm с ID того же плана, status и replay |
| После карты | Draft `SKILL.md:69–85`; `references/retrieval-engine.md:28–34` | Запрошены expanded-тела, проверены каналы, пути и отсутствие усечения; затем прочитан файл |
| Перед выводом | Draft `SKILL.md:82–85,100–110`; корпусный `AGENTS.md` | Текущим признан только источник из `docs/**`; ответ возвращён с адресом и границами пробы |

Добавленный в текущие байты fallback без разрешения доступен вовремя в
`draft/SKILL.md:42–48`: агент должен продолжать filesystem или точным поиском.
Эта ветка не выполнялась, потому что разрешение в пробе было дано заранее.

## Сравнение прежнего и нового маршрута

Прежний `SKILL.md:95–133` уже требовал разделять аспекты, читать corpus rules,
проводить карту перед телами и останавливать семантическую петлю после второй
промашки. Его `references/index-lifecycle.md` также задавал тот же безопасный
dry-run/confirm/status/replay. Поэтому доступное evidence показывает
сохранение ключевого поведения, а не его улучшение.

Новый draft делает вызов неявным и заменяет обязательный формальный packet
кратким ответом с адресами и существенными ограничениями
(`draft/SKILL.md:100–110`). В этой пробе этого хватило: статус источника был
явно задан `AGENTS.md`, а тело полностью отвечало на вопрос. Ветка без
разрешения стала исполнимой после добавления filesystem/exact fallback, но
реальным запуском здесь не проверялась.

## Закрытая находка

В проверенной версии до коррекции требование первого запроса на языке источника
появлялось раньше обязательного способа узнать язык. В этой пробе русский
запрос нашёл английские фрагменты через dense-канал, после чего аспект был
повторён по-английски; это не гарантировало маршрут при cross-language no-hit.

Текущие байты закрывают разрыв в `draft/SKILL.md:52–55`: если язык неизвестен,
агент начинает с языка вопроса и уточняет язык по найденным фрагментам или
доступной карте файлов. Коррекция проверена чтением актуального текста; новый
retrieval-прогон после неё не выполнялся, потому что наблюдаемый командный путь
не изменился. Открытых находок по проверенному маршруту нет.
