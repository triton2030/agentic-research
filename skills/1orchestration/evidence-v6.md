# Evidence v6

Status: candidate evidence; не runtime contract.

## Naked-trigger routing

Clean routers читали только frontmatter участвующих skills.

| Запрос | Наблюдаемый route | Topology owner | Вердикт |
| --- | --- | --- | --- |
| поручить одному субагенту независимую проверку | `1orchestration` | `1orchestration` | ordinary delegation достижима |
| исправить одну строку самому без делегирования | никакой skill | root | `no-delegation` достижим |
| провести fresh-eyes аудит траектории | `1fresh-eyes` | `1fresh-eyes` | specialized controller не получает вторую topology |
| вынести анализ в фоновый Codex-тред после cognitive contract | `1orchestration`, `1codex-bg-threads` | `1codex-bg-threads` | orchestration формирует contract, runtime controller владеет topology |

Exact clean-router returns:

```text
ordinary
activate: 1orchestration
first decision: need specialized controller
topology owner: 1orchestration
why: direct delegation of cognitive work.

skip
activate: никаких
first decision: no-delegation
topology owner: root
why: «сам» задаёт прямое самостоятельное исправление, без назначения субагента или деления когнитивной работы.

specialized
activate: 1fresh-eyes
first decision: вызвать trajectory-critic
topology owner: 1fresh-eyes
why: запрос прямо требует fresh-eyes аудита траектории, а не разбиения работы.

managed
activate: 1orchestration, 1codex-bg-threads
first decision: сформировать выполнимый cognitive contract для анализа логов
topology owner: 1codex-bg-threads
why: 1orchestration формирует contract, а специализированный 1codex-bg-threads владеет topology фонового Codex-треда.
```

`ordinary` назвал specialized-controller check первым решением, но topology
оставил `1orchestration`; это не меняет route и остаётся наблюдаемой оговоркой.

## Full executor

Clean executor прочитал тело, а затем только routed references в порядке:

`orient → brief → count → budget → shape → map → carrier → execute → accept → integrate`.

`decompose` не читался: оба verdict-а были `manageable`.

Наблюдаемый lifecycle:

1. Root принял owner map и provisional brief.
2. Root записал раздельные оценки `worker: 14`, `root: 18`.
3. `shape` выбрал одного ordinary read-only worker-а; capability обоснована
   локальным bounded textual audit.
4. До launch создан [executor carrier](executor-carrier-v6.md), записаны map и
   `ready_to_launch`.
5. Реально запущен один nested worker; root ждал на mandatory barrier.
6. Return записан как `return_received_root_verification_pending`; barrier
   удержан.
7. Root отдельно перечитал target и owners, после чего записал acceptance.
8. Только затем записан final transition и выполнена integration.

Exact nested return, root-check и пять причинно упорядоченных transitions
сохранены в carrier. Candidate, tracked owners и projections executor не
редактировал.

### Непринятые выводы executor-а

- Scoped audit назвал `brief.md` failed за отсутствие обязанностей `count`,
  `budget` и `decompose`. Это не finding пакета: staged runtime намеренно
  распределяет эти обязанности по следующим routed references.
- Planning-owner требует повторять критичные строки внутри task-файла. Для
  общего orchestration brief это не безусловный default: `brief.md` сохраняет
  адресуемую выдержку, когда её требует live receiving owner, и считает её в
  active set.
- Executor показал только числа `14/18`, хотя nested return развернул 27
  source-specific rows. Это nonadherence самому `count.md:6–9`: файл уже
  требует переносить независимо забываемые units по одной и запрещает снижать
  число склейкой. Новое дублирующее runtime-правило не добавлено; расхождение
  остаётся falsifier-ом для финальных checker-ов.
