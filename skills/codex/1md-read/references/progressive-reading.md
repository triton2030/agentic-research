# Прогрессивное Чтение Markdown

## Содержание

- Выбор карты
- Default route
- Exact section
- Паттерны
- Coverage и stop

Используй этот route, когда folder уже известна, файлов много или выбранный file
слишком велик для слепого полного чтения. Сначала держи claim и ожидаемую
decision delta; карта нужна только для создания handle. Цель:

```text
claim → map → select → body → decision
```

Выгода проста: map тратит сотни токенов, чтобы не загрузить десятки тысяч
токенов нерелевантного body. Карта не поддерживает claim сама по себе.

## Выбор Карты

| Задача | Команда |
| --- | --- |
| Names, descriptions, heading previews и bounded coverage folder | `md orient FOLDER --json` |
| Flat file inventory, titles и descriptions | `md ls PATH --json` |
| Полный outline одного file, numeric handles и optional `stable_id` | `md toc PATH --json` |
| Known root-scoped stable section | `md extract --section-root ROOT --section-id ID --extract --json` |
| Выбранные section bodies | `md extract FILE` для default toc; исходная map для customized numeric ids |
| Graph-central read order | `md importance CORPUS --json` |

`orient`, `ls`, `toc` и `extract` читают filesystem без index probe,
embeddings и HTTP. До них не нужны `status`, warmup или `corpus-scan`.
Filesystem map при этом не обязана применять includes/excludes semantic index
из `.md-tools.toml`; фактические returned paths сильнее ожидания.

## Default Route

Если exact stable section ID уже известен, map не нужен:

```bash
md extract --section-root ROOT --section-id domain.rule --extract --json
```

Root задаёт denominator уникальности. Missing/duplicate ID — fail-closed gap;
не заменяй его похожим heading text. Marker адресует reading body и сам по себе
не является Markdown link, authority claim или graph dependency. Для
структурной диагностики используй `md check --paths ROOT --json` с тем же root;
file-only check не доказывает namespace uniqueness.

1. Для известного root/folder сразу получи bounded map:

   ```bash
   md orient FOLDER --json
   ```

   Прочитай `files[]`, `folders[]` и `coverage`: normal output ограничивает
   cold-start attention и может не покрывать всю folder.
2. Если scope ещё широк, выбери одно продолжение из
   `_envelope.next_step`: child-folder action сужает scope; same-root action
   продолжает страницу. Копируй `file_offset` / `folder_offset` из live args,
   не вычисляй их вручную.
3. Когда выбран конкретный file, получи numeric map handles и optional stable
   IDs:

   ```bash
   md toc PATH --with-tokens --json
   ```

   Добавляй `--with-link-counts`, только если links помогают выбрать чтение:
   graph scan может стоить заметно дороже outline. Если нужен только верхний
   уровень, используй `--max-heading-level`.
4. Для id из обычного single-file `toc` путь передаётся напрямую; CLI сам
   строит fresh full-depth map:

   ```bash
   md extract PATH --headings 1.2,1.4 \
     --extract --token-budget 3000 --json
   ```

   Если ids взяты из customized map (`--max-heading-level`, `--match`, folder
   map или reusable selection), передай **ту же map**:

   ```bash
   md toc PATH --with-tokens --json \
     | md extract --map-stdin --headings 1.2,1.4 \
       --extract --token-budget 3000 --json
   ```

5. Если `dropped_by_budget` непустой, уменьши selection или продолжи следующей
   bounded-порцией. Heading — atomic addressable unit: section крупнее budget
   может быть отброшена целиком. Не ставь `token_budget=0` автоматически; если
   внутри есть table row/raw block, передай exact unit в `1cli-tools`.

## Exact Section

Если известен stable section ID и root, используй direct stable route выше.
Если известен только heading text, но не line/numeric id, сначала получи
outline:

```bash
md toc PATH --with-tokens --json
```

Выбери exact `headings[].text`. Для default single-file map передай path + id в
`md extract`; для customized map передай её целиком. `md toc --match "Heading
text"` **не фильтрует headings**: live
contract выбирает whole files, если term совпал с path/title/description или
одним из headings, и возвращает их полный eligible outline. На большом file это
может быть дорогим no-op.

Heading-aware extraction возвращает section subtree, а не фиксированное
количество строк: nested headings входят до следующего heading того же или
более высокого уровня.

Не используй `rg -A/-B` как замену section boundary. Но table row или raw block
без собственного heading — законный exact-route
`1cli-tools`; не вытаскивай огромную секцию ради одной addressable записи.

## Паттерны

- **Короткий file:** direct Read дешевле map ceremony, когда размер уже измерен
  или очевиден из bounded context. Ориентир `1–2k` tokens полезен, но не gate.
- **Descriptions:** начни с `orient`; отсутствие description — metadata gap, а
  не пустой file. Переключись на `toc`.
- **Heading внутри известного file:** plain `toc`, exact text/id, затем
  `extract`.
- **Flat inventory:** `ls` полезен в уже узкой folder. Его `--match` —
  whitespace-tokenized OR по file metadata/headings, не semantic search.
- **Несколько files:** `orient` → bounded child/same-root continuation →
  несколько малых extract batches.
- **Целый file:** direct Read только для измеренно короткого файла либо когда
  заранее названа nonlocal dependency между separated sections, способная
  изменить claim. Фразы «вопрос про документ» и «это owner» этого не доказывают.
  `extract --files` может budget-ить metadata и sections отдельно; headingless
  preamble не гарантирован.
- **Central docs:** `importance` помогает упорядочить чтение. Rank не назначает
  authority и не заменяет local owner map.
- **Неизвестный смысл:** прекрати filesystem map и передай query в
  `1md-search`.

## Coverage И Stop

- Presence `coverage` означает, что map продолжима; отсутствие выдуманного поля
  `omitted` не доказывает полноту.
- `orient --expanded` и folder-wide `toc --expanded` — потенциально большие
  escape hatches. Не используй их первым ходом.
- `read-related` на navigation hub/INDEX — ещё один escape hatch: preview может
  вернуть сотни headings и отбросить direct targets по budget. Используй его
  только для low-degree anchor и проверяй `items`/`dropped_by_budget`.
- Token counts оценивают бюджет, headings/descriptions маршрутизируют, bodies
  поддерживают вывод. Не повторяй raw map/JSON в reasoning или final, если его
  поля не меняют selection, coverage либо gap.

Остановись, когда selected bodies изменили или поддержали решение, handles и
scope известны, а оставшиеся pages/budget gaps не скрыты. В обычной задаче не
публикуй отдельный reading packet; вынеси только decision-changing evidence и
материальные gaps.
