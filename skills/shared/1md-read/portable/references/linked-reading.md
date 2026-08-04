# Чтение Linked Thought

## Содержание

- Inline wikilinks
- Одна wiki-цепочка
- Ограничения dialect
- Evidence и stop

Linked readers выгодны только когда связь сама несёт мысль. Для обычного
Markdown link с известным target `toc → extract` дешевле и точнее.

## Inline Wikilinks

Когда source section строит мысль через несколько
`[[target#Heading|alias]]`, используй:

```bash
md coherence-audit PATH \
  --anchor "Source heading" \
  --scan CORPUS_ROOT \
  --depth 1 \
  --token-budget 6000 \
  --json
```

`coherence-audit`:

- сохраняет source prose;
- разворачивает **все** inline anchored wikilinks в месте упоминания;
- возвращает `source`, `blocks`, `issues`, assembled `text` и `stats`;
- сообщает `unresolved_wikilinks` и `token_budget_exhausted`;
- оставляет bare wikilinks видимыми, но не разворачивает их.

Выбирай `depth=1` для чтения непосредственной мысли. Увеличивай depth только
если nested linked premise способен изменить текущий вывод.
Для compact agent packet сначала читай `source`, `blocks`, `issues` и `stats`;
assembled `text` часто дублирует те же bodies и нужен только для цельного
перечитывания прозы.

## Одна Wiki-Цепочка

Когда нужен последовательный first-link trail, используй:

```bash
md walk PATH \
  --anchor "Source heading" \
  --scan CORPUS_ROOT \
  --depth 3 \
  --token-budget 3000 \
  --json
```

`walk` извлекает start section и следует за **первой anchored wikilink** в
каждом block. Это chain reader, не fan-out. Bare wikilinks пропускаются.
Подпиши `stopped_reason`, `links_followed` и `token_total`.

Не выбирай `walk`, если автор поместил несколько равноправных links в одном
paragraph: используй `coherence-audit`.

## Широкий Neighborhood

`read-related` — preview для одного low-degree anchor, когда действительно
нужны outgoing links и backlinks одного шага. Не запускай его как default на
INDEX, README, registry или другом navigation hub: полный outline каждого
neighbor быстро раздувает reply, а token budget начинает отбрасывать прямые
targets. Проверяй `items`, reasons и `dropped_by_budget`; затем выбирай concrete
targets для `toc → extract`.

## Ограничения Dialect

- `coherence-audit` и `walk` разворачивают anchored **wikilinks**.
- Обычный Markdown destination `[text](file.md#Heading)` раскрывай через
  `toc → extract`.
- Bare `[[file]]` не задаёт section boundary и автоматически не раскрывается.
- Broken/unresolved anchor — gap. Не заменяй его похожим heading по догадке.
- Fixed line window вокруг heading не эквивалентен section subtree.

## Evidence И Stop

Удерживай как evidence state:

- source `path#heading`;
- каждый реально раскрытый target `path#heading`;
- выбранный route и depth;
- token total/budget;
- unresolved, skipped и dropped blocks.

Не повторяй assembled text или полный linked packet в final, если пользователь
не просил reading report: покажи только blocks, которые изменили вывод, и gaps.

Остановись после непосредственного linked context, если следующий hop не может
изменить claim. Для holder/impact question передай работу в `1md-graph`; для
неизвестного semantic target — в `1md-search`.
