# Fix Mid-Pipeline Not At Edge

## Observation

Когда баг проходит через несколько модулей (A → B → C → D, output D неверный), default impulse — **расширить API edge-модуля** (D принимает новый kind of identifier). Это раздувает контракт и переносит fix-cost на всех caller'ов. Cheaper move — **трансформировать данные на ближайшем mid-pipeline frame, где они ещё correct**.

Pattern: bug-surface bias. Модель видит manifestation в D и проектирует там же, не дойдя до traceback по data flow до точки, где данные ещё правильные.

## Counter

- 2026-05-20 [Claude Opus 4.7]: фикс stale `file_id` в md_navigator (`search` → `pick` handoff пулил неверный файл). Первый impulse — расширить `pick.py` CLI флагами `--paths` / `--sections` (stable identifiers), плюс изменения в `cli.py`, плюс правка `render_search` + `SKILL.md` примеры. 6 task'ов. После трассировки `cmd_search → _hydrate_rows → render_search` понял: между hydrate и render есть момент, где есть и fresh `map_data`, и stale-id'ные results. Remap там одним блоком — 2 task'а, без расширения downstream API. Удалил 4 task'а, написал минимальный фикс.

## Possible upgrade

Перед тем как проектировать новый API surface для устранения симптома — **протрассировать data flow от bug-surface до источника**. Найти ближайший frame, где данные ещё correct относительно того, что нужно downstream. Fix там. Это same logic, что Lattice-of-Repair / Choose your seam точкой максимальной обратной совместимости.

Конкретные cues для остановки и трассировки:

- «Нужен новый identifier kind в receiver» — почти всегда симптом, что upstream раздаёт wrong identifier. Лечи источник.
- «Нужен новый flag для opt-in поведения» — почти всегда симптом, что default behavior должен быть исправлен, не расширен.
- «Нужно сделать pick принимать что-то новое» — вопрос: а что precisely shifted in input, и можно ли transform его обратно в существующий контракт.

Релевантно: любой multi-module bug в pipeline (parsers, renderers, ETL, query builders, search-to-action flows).
