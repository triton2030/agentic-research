---
name: 1md-graph
description: >
  Use when claim/heading/anchor/depends-on affects holders/cycles, or
  graph-frontmatter/move/merge/rename/delete needs impact. Search→nav; shape→IA.
---

# 1md-graph

Центральный вопрос скила — не «какие файлы вернул preflight», а: **какой
конкретный смысл меняется, где он спроецирован, и какое прочитанное evidence
доказывает или опровергает распространение изменения**.

## Результат — change-contract packet

- change claim: что именно станет иначе (`before → after` или область delta);
- прочитанные sources и держатели с evidence «какая проекция задета»;
- ветви держателей: `affected` / `unaffected` / `unread` (явная очередь);
- semantic probes (claim + consumer) и их retrieval outcome;
- находки гнили: `duplicate-truth`, `owner-conflict`;
- gaps и handoff правильному owner-у.

Graph JSON — structural evidence, не semantic вердикт и не permission расширять
write scope. Не говори `safe-to-edit`. Непустая `unread`-очередь = работа не
закрыта, а остановлена названным решением.

## Границы

| Момент | Owner |
|---|---|
| `depends-on`, reverse holders, anchor drift, cycles, destructive impact | `1md-graph` |
| Где живёт semantic owner или какие blocks связаны по смыслу | `1md-navigator` |
| Нужно ли split/merge/move/rename или менять container/placement | `1ia-audit`; после решения вернись сюда за impact/closeout |
| Exact refs/counts, stale strings или shell cleanup | `1cli-tools` |
| Ordinary prose/formatting или known read без graph risk | direct Read/edit |
| `SKILL.md` frontmatter | `1skill-architect` |

Эта граница определяет graph semantics, а не универсальный whitelist
frontmatter. `depends-on` — единственное поле, которое этот skill трактует как
hard invalidation edge. Другие metadata (`kind`, execution-order field,
`derived-from`, `supersedes`, type/lifecycle fields) могут иметь собственную
функцию по local document/planning contract. Не переименовывай их в
`depends-on` и не удаляй только потому, что graph их не потребляет; их
допустимость и validation принадлежат live path/zone profile. Runtime mismatch
разрешай через route ниже.

## Default Path

1. **Зафиксируй change claim до команд**: одно предложение — что станет иначе.
   Правка без смыслового изменения и без graph risk — обычный edit без этого
   пути. Если мотив правки — противоречие между файлами или неясно, где
   правда, — проблема глубже связей: сначала shape-вердикт `1ia-audit`, связи
   потом.

2. **Сними карту из `GRAPH_ROOT`**. Запускай из `cwd=GRAPH_ROOT`, а `--scan`
   явно фиксирует reverse-scan scope:

   ```bash
   md preflight PATH --scan GRAPH_ROOT --json
   ```

   Для незнакомого target с нужным linked context —
   `md edit-context PATH --scan GRAPH_ROOT --json` (вложенный `.preflight`;
   bodies читай direct Read). Роли полей:

   - `edit_plan.must_read` — источники смысла; прочитай затронутые delta;
   - **полный рабочий список держателей — `edit_plan.must_update`** (direct +
     каскад); raw graph-проекции доступны только через `--expanded`;
   - `edit_plan.cascade_summary` — размер/overload signal; unique files не
     смешивай с repeated occurrences или пересекающимися branch totals;
   - `edit_plan.also_check` — soft-кандидаты, не hard-обязательства;
   - `blockers.has_blockers` — hard gate; разреши `blockers.issues` до правки;
   - `blockers.anchor_drift_risk` — **hard gate при правке heading**:
     держателей входящих якорей разреши до rename;
   - non-null `cycle_membership` — structural blocker; scoped `md cycles`
     показывает полное SCC. Нулевой count действует только в effective graph
     scope и не доказывает semantic owner-а.

3. **Пройди держателей как ветви, не как плоский список.** Каждому прямому
   держателю — один статус с body evidence (`path#heading` + проекция):

   - `affected` — назови, какая проекция изменяемого смысла устаревает →
     раскрой следующий hop только этой ветви;
   - `unaffected` — назови контракт, который держатель применяет, и почему
     delta его не трогает → ветвь останавливается;
   - `unread` — честное состояние в явной очереди, не разновидность
     `check-only`. Батч-вердикт без прочитанной проекции = не вердикт.

   `cascade_summary.overloaded == true` — triage signal, не blocker и не
   verdict. Иди от крупнейших branches батчами уникальных files, сохраняя
   `unread`, либо остановись как `graph-overloaded` с явной очередью. Sampling
   не закрывает impact hard contract.

4. **Semantic second-look обязателен при material claim change** канона или
   contract-файла: два probe (claim + consumer) —
   [`references/section-blast-radius.md`](references/section-blast-radius.md).
   Незадекларированный межслойный downstream не появится в graph traversal —
   его ловит только этот шаг.

5. **Перед delete/rename/move/merge** (после принятого shape-решения):

   ```bash
   md impact PATH --scan GRAPH_ROOT --json
   md deps PATH --scan GRAPH_ROOT --depth 2 --json
   ```

   **Все три массива `impact` — обязательства**: `dependent_breaks`,
   `body_wikilink_refs`, `body_markdown_refs`. Пустые holders при живых
   body-ссылках ≠ разрешение. Exact counts — `1cli-tools` c тем же graph
   scope.

6. **Closeout — op-specific, закрой только изменённый риск**:

   - edit: повторный `md preflight PATH` + `md check --paths SCOPE --json` +
     `md cycles --paths SCOPE --json`;
   - rename/move: `preflight` НОВОГО path + scoped `check`;
   - delete: старый path мёртв (`path_not_found` — норма) — scoped `check` +
     проверка, что бывшие держатели не несут stale ссылок.

   `edit_plan.to_clear` — summary, не done gate.

## Постановка и ревизия связи

Hard edge требует адресуемую пару: изменение **X** в source делает конкретный
**Y** в holder ложным/misleading; source владеет X, holder его применяет.
Не можешь назвать X/Y — это navigation, не `depends-on`. Полный admission test
и verdicts — [`references/semantic-edge-audit.md`](references/semantic-edge-audit.md).

## Гниль вне механики

Чтение тел держателей не пропадает зря: замеченный shape-smell фиксируй в
packet, даже если он вне текущего graph risk, — не глотай.

- **Ручной список держателей в теле** («кто на меня ссылается») =
  `duplicate-truth`: сравни с вычисляемым reverse graph; расходятся — правда у
  графа. Список не «подправляй» как второй реестр: generated view, явная
  non-exhaustive навигация или удаление — shape-решение у `1ia-audit`.
- **Смысловая owner-петля**: A и B называют друг друга каноном одного
  инварианта — `owner-conflict` finding + handoff `1ia-audit`, даже при
  `cycles == 0`.
- **Несовместимые утверждения** в прочитанных телах — тест владельца: владелец
  утверждения ясен → это stale-проекция, обычная `affected`-ветвь; владелец
  неясен или оба претендуют → `owner-conflict` → `1ia-audit`, связи и контент
  не правь до вердикта.

## Восстановление графа

Накопленные ошибки (инфляция edges, петли, пропущенные межслойные связи) —
отдельный маршрут [`references/graph-recovery.md`](references/graph-recovery.md),
не расширение чек-листа правки.

## Runtime и schema mutation

Composite errors/side effects (`edit-context`, `section-blast-radius`,
`index_busy`), `md init` / `md strip` и графовый frontmatter —
[`references/runtime-gates.md`](references/runtime-gates.md). При расхождении
команды, поля или cost с памятью — `md tools <cmd> --json` /
`md <cmd> --help`; live payload сильнее текста скила. Полный catalog открывай
только для catalog-wide вопроса.

## Остановка

Стоп, когда change claim закрыт: затронутые sources прочитаны; каждая
`affected`-ветвь закрыта или остановлена named-решением; очередь `unread` пуста
либо явно передана; destructive-обязательства (все три массива) разрешены;
scoped `check`/`cycles` пройдены; `duplicate-truth` / `owner-conflict` findings
переданы owner-у. Ordinary edit без graph risk этого closeout не требует.
