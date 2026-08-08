# INDEX Contract

## Information Job

`INDEX.md` отвечает: «для намерения X что открыть, в каком порядке и зачем».
Он не инвентарь, не semantic index, не owner registry и не источник истины.

В начале файла оставь один guard:

```markdown
> Navigation cache only: linked sources own the truth. A missing route does not
> mean missing information.
```

Язык guard следует local document contract.

## Compact Schema

```markdown
## <Намерение словами исполнителя>

Зачем: <одна строка о reader job>.
Ищут как: <синонимы и вероятные RU/EN формулировки>.
Читать: [<owner>](<path>) — <роль> →
  [<next>](<path>) — <роль>
  + [<conditional>](<path>) — если <условие>.
```

- `→` задаёт порядок чтения; ссылки внутри intent идут по убыванию важности.
- `+` добавляет conditional branch.
- Роль ссылки — короткое действие: что там узнать, увидеть или сделать;
  не claim документа.
- Section anchor указывай, когда нужный материал — раздел внутри файла или
  лежит не в том файле, где его будут искать; file-level link достаточно,
  когда target — файл целиком.
- Не повторяй frontmatter, status, decision, rules, числа или rationale owner-а.

## Admission And Pruning

Допусти intent, если верно хотя бы одно:

- Founder явно назвал эту будущую работу;
- current GOAL/task/roadmap/backlog делает её ближайшей;
- тот же reader job наблюдался минимум дважды.

Не допускай:

- названия зон, папок и типов файлов без reader intent;
- одноразовый cleanup или текущий случайный target;
- model-only прогноз будущей работы;
- reading set, уже очевидный из root navigation без дополнительного discovery;
- ссылку «для полноты», если она не меняет следующий ход.

Внутри intent сильнейший кандидат на ссылку — информация, лежащая не там, где
её станут искать: не тот файл или незаметный раздел большого файла. Такая
находка по ходу любой работы — событие для добавления route: INDEX передаёт
дельту следующей сессии.

Deletion test: если удалить секцию, станет ли повторяемая задача заметно дороже
или менее надёжной? Если нет — секция не нужна.

Truth test: станет ли строка ложной от изменения содержания linked owner-а при
неизменном маршруте? Если да — это повтор truth; сократи до роли ссылки.

## Example

```markdown
## Работаю над интерфейсом

Зачем: восстановить ограничения, поведение и текущую UI-поверхность.
Ищут как: интерфейс, UI, frontend, экран, wireframe, prototype.
Читать: [product owner](docs/product.md) — customer outcome →
  [interface spec](docs/interface.md) — behavior contract →
  [prototype](workspace/prototype/) — current surface
  + [implementation status](ops/status.md) — если меняется live code.
```

## Root Instruction Pointer

Помести pointer в effective root instruction owner каждого intended runtime.
Не копируй полный lifecycle contract в несколько files, если один owner
достижим из остальных.

```markdown
## INDEX — маршруты по намерениям

Если reading set задачи неизвестен, сначала проверь [INDEX.md](INDEX.md).
Это неполный navigation cache, не источник истины: miss или битая ссылка
переходит в live owner discovery и ничего не блокирует.

Обновляй INDEX в той же разрешённой работе, когда меняется owner, path,
reading order или состав существующего set. Обычная правка содержания owner-а
INDEX не затрагивает, пока маршрут верен. Замеченная устарелость в read-only
режиме сообщается, но молча не исправляется.
```

Перед substantive change набор из INDEX сверяется с live owner/navigation
contract; INDEX сокращает discovery, но не доказывает его полноту.
