# INDEX Contract

## Information Job

`INDEX.md` отвечает: «для намерения X что открыть, в каком порядке и зачем».
Он не инвентарь, semantic index, owner registry или источник истины. Ценность
файла — handoff сохранённой дельты между ожидаемым и фактическим маршрутом к
следующей сессии, а не число покрытых зон.

В начале файла оставь один guard на языке local document contract:

```markdown
> Navigation cache only: linked sources own the truth. A missing route does not
> mean missing information.
```

## Compact Schema

```markdown
## <Reader intent действием>

Зачем: <reader job, только если он неясен из heading>.
Ищут как: <aliases, только если они меняют findability>.
Читать: [<owner>](<path>) — <действие> →
  [<unexpected section>](<path#anchor>) — <действие>
  + [<conditional>](<path>) — если <условие>.
```

- `→` задаёт необходимый порядок; `+` добавляет conditional branch.
- Ссылки идут по убыванию важности для reader job.
- Роль ссылки говорит, что там узнать, увидеть или сделать; не пересказывает
  claim документа.
- Section anchor обязателен, когда material delta — участок файла. File-level
  link достаточен, когда target — файл целиком.
- `Зачем` и `Ищут как` не являются обязательными полями. Не заполняй schema
  ради симметрии.
- Не повторяй frontmatter, status, decision, rules, числа или rationale owner-а.

## Output Pruning

Admission принадлежит controller-у в `SKILL.md`; форма output не может заменить
его route-delta proof. После admission:

- оставь ссылку, только если она меняет следующий read/action или необходимый
  порядок;
- допускай очевидную ссылку как вход к неожиданной, но не как самостоятельное
  оправдание секции;
- допускай order-only delta, только если другая последовательность меняет
  корректность следующего действия или уже приводила к rework;
- удаляй cosmetic aliases, reader-job prose и links «для полноты».

Deletion test: если удалить секцию, станет ли повторяемая задача заметно дороже
или менее надёжной? Если нет — секция не нужна.

Truth test: станет ли роль ссылки ложной от изменения содержания linked owner-а
при неизменном маршруте? Если да — это повтор truth; сократи до действия.

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
anchor, reading order или состав существующего set, либо появился новый
admitted intent с доказанной route delta, включая дельту, обнаруженную по ходу
другой работы. Обычная правка содержания owner-а INDEX не затрагивает, пока
маршрут верен. Замеченная устарелость в read-only режиме сообщается, но молча
не исправляется.
```

Перед substantive change набор из INDEX сверяется с live owner/navigation
contract; INDEX сокращает discovery, но не доказывает его полноту.
