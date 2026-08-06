---
name: 1smart-simple
description: >
  Когда существующий текст нужно сделать короче или проще без потери функции:
  «сократи», «убери воду», tighten. Не new writing, summary, code или
  contracts.
---

# Smart Simple

## Результат

Существующий текст, секция или Markdown-файл становится самой короткой usable
формой, которая сохраняет reader job. Нормальный прогон обязан удалить или
сжать хотя бы одну фразу, повтор, секцию, связку или структурный обход.

Короткость считай по символам/словам, не по строкам. В Markdown больше строк
допустимо, если semantic line breaks делают чтение легче и общий объём меньше.
Пустые строки ради "воздуха" не считаются сжатием.

Простота включает порядок. Можно переставлять абзацы, bullets и секции внутри
выбранного текста, когда это делает поток мысли прямее и убирает объяснительный
шум. Нельзя менять порядок, если он сам несёт смысл: chronology, procedure,
priority, cause/effect, legal/order terms или decision history.

Простота также включает важность. Сжимай под компетентного читателя с контекстом:
оставляй signal words, но режь разжёвывание очевидных следствий. Уточнение
остается, если без него можно ошибиться в scope, action, confidence, exception
или owner.

Безопасное сжатие сохраняет нагрузочный смысл: facts, evidence, roles, numbers,
order, conditions, owner boundaries, confidence, quotes, voice и required next
action.

## Route

Используй только для существующего текста / секции / Markdown. Если source text
нет или пользователь просит новый материал, пропускай.

Разрешённые edits: переписать paragraphs/sections; переставить блоки внутри
выбранного текста ради reader flow; заменить derivative detail на one-line
gist + link к известному owner. Запрещённые edits: выбирать owners, переносить
truth или move/split/merge/rename/delete files.

Сначала передай owning skill, если настоящая задача - wording placement,
file/folder IA, graph/frontmatter/blast radius, folder/runtime contract,
README/GOAL strategy, skill-contract design, code, translation-only, visual
critique или approach choice.

## Work Path

1. Назови artifact contract: один reader question, decision или effect, которому
   текст должен служить. Для одной фразы это может остаться implicit.
2. Отметь invariants: thesis, evidence, numbers, conditions, exceptions, order,
   roles, owner, modality, exact terms, quotes, voice и expected reader baseline.
   Для section/file или material-risk текста привяжи protected commitments к
   source spans и назови unresolved ambiguity.
3. При прямом запросе на fresh eyes либо если две правдоподобные трактовки
   artifact contract / invariants ведут к разным cuts или ошибка меняет owner,
   scope, modality либо commitment, вызови `1fresh-eyes` до rewrite. Native
   clean-context subagent run обязателен; локальный reread не считается.
   Длина или плотность сами по себе не trigger. Synthesis и финальный текст
   остаются у основного контекста.
4. Выбери compression method: line tighten, paragraph/section compression,
   importance compression / competent-reader cut, flow rebuild / block reorder,
   purpose-preserving rebuild, section death-test / owner-gate или cross-file
   dedupe, когда известный owner уже держит detail.
5. Разложи материал на `keep`, `compress`, `hint`, `reorder` и `cut`. Режь и
   двигай только доказанно безопасное; при сомнении keep.
6. Перепиши минимально необходимую поверхность без новых claims, owner change
   или confidence loss. Не перефразируй безопасные spans ради stylistic
   consistency. Для Markdown prose используй semantic line breaks, когда они
   снижают reading friction. Если старая последовательность сама создаёт bloat,
   перестрой flow вокруг reader job и перепроверь весь semantic ledger.
7. Проверь `source -> rewrite`: каждый protected commitment сохранился; затем
   `rewrite -> source`: каждое утверждение результата поддержано source. Сверь
   artifact contract и, когда practical, character/word count. Если следующий
   meaningful cut снимет nuance, поменяет owner/structure или удалит полезную
   function, остановись и верни compression plan.

## Reference Routes

- `references/meaning-preservation-check.md` - читай для section/file
  compression, dense text, semantic ledger, independent reading или риска
  принять смысл за воду.
- `references/water-taxonomy.md` - читай, когда water и meaning близко:
  contrast, modality, repeat, numbers, names, terms или owner.
- `references/compression-tools.md` - читай, когда compression method неясен,
  нужны prompt cues или line tightening сохраняет bloat.
- `references/cross-file-dedupe.md` - читай только когда Markdown-файл раздут
  source-of-truth duplication. Этот skill может делать только derivative
  cleanup: gist + link к known owner. Неизвестно место owner-а →
  `1md-search`; спорен owner/structure → `1ia-audit`; есть graph risk →
  `1md-graph`.

## Output

Default: верни только сокращённый текст.

Если безопасный рез неочевиден, добавь одну короткую строку:

```md
Removed: <what was removed>
Risk: <what cannot be cut without loss>
```

Если сильнее сжать можно только после подтверждения:

```md
Compression plan: <what to cut or rebuild>
Cost: <what would be lost or changed>
Confirm: <short confirmation question>
```

## Stop

Остановись, когда текст стал короче по символам/словам и каждый оставшийся block
служит artifact contract, или когда следующая meaningful compression требует
подтверждённой цены.
