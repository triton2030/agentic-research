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

Pending.
