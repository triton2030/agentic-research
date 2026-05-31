---
description: "Thermo-nuclear code-quality audit of md-embedding-server: structural findings, code-judo moves, remediation sequence."
read-before-edit: []
edit-after-edit: []
---
# Code Quality Audit — md-embedding-server

Аудит по методологии `thermo-nuclear-code-quality-review`: жёсткий структурный
обзор с упором на упрощение, удаление целых слоёв, границы абстракций и
утечки CLI-формы в библиотеку. Судил против собственных контрактов проекта
(`docs/architecture-lock.md`, `docs/navigator-public-api.md`, `AGENTS.md`), а не
против абстрактных best practices.

- Объём: ~18.5k строк `src` в ~110 файлах, ~6.5k строк тестов.
- Состояние: **292 теста зелёные** (24.7s, `.venv`). Рефакторинг-в-процессе
  (декомпозиция `api.py` 1886→237 строк) завершён и стабилен.
- Дата: 2026-05-29.

---

## Вердикт

**Кодовая база структурно здоровая и необычно хорошо защищённая** — у неё есть
исполняемые архитектурные тесты, которые форсируют почти весь
`architecture-lock`. Это редкость и большой плюс.

Но она **тащит крупный параллельный legacy-слой**, который, как теперь
показывает evidence, можно удалить целиком, плюс кластер CLF-измов (CLI-формы,
протёкшие в библиотечный слой). Это не «грязный код» — это **отложенное
завершение миграции** и несколько мест, где структура сложнее, чем того требует
задача.

Главная рекомендация одной строкой: **закрыть migration window и удалить
legacy CLI-слой** (~1750+ строк и целая вторая архитектура исчезают). Это и есть
тот code-judo ход, ради которого нужен такой аудит.

По шкале приёмки скила: **не блокер на merge** (поведение корректно, тесты
зелены, границы держатся), но **есть явный упущенный code-judo и пачка
boundary-утечек**, которые надо адресовать отдельной волной чистки.

---

## Что сделано сильно (отдаю должное)

Честный аудит начинается с того, что работает. Здесь много правильного:

1. **Исполняемые архитектурные тесты** ([`tests/test_architecture_boundaries.py`](tests/test_architecture_boundaries.py)).
   Это лучшее, что есть в репо. Тесты форсируют: handlers не печатают
   JSON / не зовут `sys.exit` / не импортят envelope; `runner` — единственный
   владелец `envelope.wrap`; `navigator/*` не импортит `md_cli`; `api.py < 300`
   строк; **ни один файл `src` не ≥ 1000 строк**; audit-split; atomic
   write-plan; переиспользование канонического парсера. Граница не на словах в
   доке, а проверяется на каждом прогоне. Это де-рискует всё остальное.

2. **Декомпозиция `api.py`**: монстр-фасад 1886→237 строк, разрезан на
   `api_graph` / `api_search` / `api_audit` / `api_profile` / `api_index_context`.
   Это движение в правильную сторону — ровно то, что методология одобряет.

3. **Catalog-driven generic dispatch** ([`handlers/_generic.py`](src/md_cli/handlers/_generic.py)).
   Один generic-handler гоняет все 32 инструмента через метаданные каталога —
   хорошая, не магическая абстракция. (Парадоксально соседствует с находкой
   №2 ниже — см. там.)

4. **Атомарные graph-записи** через `write_doc_plan` / `DocWrite`: staging всех
   целей и откат при сбое. Именно та «atomic, not half-applied» структура,
   которую требует методология.

5. **Канонический парсер один** (`markdown_io`) — нет второго wikilink-парсера,
   и это форсится тестом.

---

## Находки (по приоритету методологии)

### 🔴 Tier 1 — упущенный code-judo: удалить legacy CLI-слой целиком

**Это находка №1. Здесь можно удалить сложность, а не переставить её.**

В репо живут **две параллельные архитектуры**:

| | Новый путь (продукт) | Legacy путь |
|---|---|---|
| Вход | `md` (`md_cli.main:main`) | `scripts/md_navigator.py`, `scripts/md_graph.py` |
| Слой | `md_cli` → `navigator.api.*` → `api_*` адаптеры | `navigator/cli.py` (797), `navigator/graph.py` (657) |
| Обработчики | `_generic.run_tool` + catalog | 19 рассыпанных `cmd_*` функций |

**Точное evidence, что legacy мёртв со стороны потребителя:**

- Единственный установленный entry point — `md = md_cli.main:main`
  ([`pyproject.toml:21`](pyproject.toml)). Скрипты `md_navigator.py` /
  `md_graph.py` не устанавливаются.
- Глобальные скилы `1md-navigator` и `1md-graph` (реальные потребители) зовут
  **только `md`** (`md orient`, `md status`, `md search`, `md preflight`...).
  Ноль ссылок на `md_navigator.py` / `md_graph.py` в скилах.
- Каталог диспатчит **все 32 инструмента** на `navigator.api.*` /
  `navigator.workflows.*` — никогда на legacy `cmd_*`.
- Grep по новому пути (`md_cli` + `api_*` + `workflows`) на `cmd_*` — **пусто**.
  Продукт не касается legacy ни в одной точке.
- `CHANGELOG.md` фиксирует уже выпущенный `2.0.0 — Simpler agent-facing CLI`.

**Чем legacy жив сейчас:** только собственными тестами. `cmd_search`
импортируется в 6 тест-файлах (`test_search_smoke`, `test_rerank`,
`test_path_filters`, `test_schemas`, `test_contract_fixes`); `navigator.cli` и
`navigator.graph` — в `test_contract_fixes`, `test_graph_mutators`,
`test_real_world_complaints`. То есть **тесты приколочены к legacy-слою → слой
жив → тесты держат слой**. Самоподдерживающаяся петля долга.

**Масштаб удаления:** `cli.py` + `graph.py` = **1454 строки**, + 58 строк
скриптов, + 19 `cmd_*` функций (их тела сейчас раздувают `search.py`,
`index_build.py`, `audit_cli.py`, `overlaps.py`, `repeated_concepts.py`,
`index_cluster.py`, `index_status.py`, `schemas.py` — то есть и четвёрку
файлов «у стены 1000 строк»).

**Remedy:** перецелить тесты с `cmd_search(args)` на `api.search(...)` /
`search_payload(...)`; удалить `navigator/cli.py`, `navigator/graph.py`,
`scripts/md_navigator.py`, `scripts/md_graph.py`, все `cmd_*` / `register_*` /
`build_parser` функции в feature-модулях. Архитектурные доки уже описывают это
как «big-bang migration window» — evidence говорит, что окно пора закрыть.
Тесты, переведённые на канонический путь, заодно станут честнее (тестируют
продукт, а не legacy-обёртку).

---

### 🔴 Tier 1 — упущенный code-judo: 30 дублирующихся shim-обработчиков

В `src/md_cli/handlers/` лежат **30 идентичных файлов по
10 строк**. Они различаются ровно одним строковым литералом:

```python
@from_catalog('md_audit')
def run(args) -> ToolResult:
    return run_tool('md_audit', args)
```

Это ~300 строк чистого copy-paste — «copy-pasted logic instead of extracted
helpers» из списка «флагать агрессивно».

**Почему они вообще есть:** диспетчер ([`main.py:145-150`](src/md_cli/main.py))
делает `import_module(tool.handler_module)` и зовёт `.run`. Shim существует, лишь
чтобы дать `.run`, который связывает `tool_id`. Но `tool_id` диспетчеру **уже
известен** — он передаёт его на той же строке: `run_tool(tool.tool_id,
module.run, args)`. То есть один и тот же `tool_id` протягивается дважды.

**Remedy:** для инструментов без собственной логики диспетчер должен звать
`_generic.run_tool(tool.tool_id, args)` напрямую (fallback по каталогу). Тогда
30 файлов исчезают, остаются только обработчики с реальной логикой
(`md_extract.py`, `tools.py`, `doctor.py`, `selftest.py`, `_generic.py`).
Побочно: `test_handlers_boundary` сейчас требует «ровно один `def run` на файл»
— этот инвариант надо переписать под generic-fallback (он закрепляет паттерн,
который мы убираем).

---

### 🟠 Tier 2 — магия, прячущая простую структуру: proxy в `__init__.py`

[`navigator/__init__.py:99-131`](src/navigator/__init__.py) переопределяет класс
самого модуля (`sys.modules[__name__].__class__ = _NavigatorPackage`), чтобы
каждое публичное имя было **одновременно callable и модулем**:
`navigator.search(...)` зовёт функцию, `navigator.search.X` — атрибут модуля.

Это ровно «generic magic handling that hides simple structure». Документ сам
перечисляет цену: mypy не выводит типы, pickling ломается,
`inspect.getmembers` врёт.

**Ключевое:** магия **не несущая для продукта**. Каталог диспатчит на явные
`navigator.api.X`; единственная ссылка на callable-форму `navigator.search(...)`
во всём `src` — это docstring самого `__init__.py`. Магия обслуживает только
тестовую эргономику (`monkeypatch.setattr(search_mod, ...)` в `conftest.py:99` и
`test_rerank.py`).

**Remedy (путь уже описан в доке, секция «When safe to remove»):** заменить
re-export функций в `__init__.py` на `from . import <module>`; тесты, которым
нужна callable-форма, переводят на `from navigator.api import X`; тесты с
monkeypatch продолжат работать, потому что `from navigator import search` после
удаления proxy резолвится в реальный модуль, и `setattr` ляжет на него напрямую.
Минус ~35 строк магии и целый класс «странного поведения интроспекции». Этот ход
естественно делать в одной волне с Tier 1 (миграция тестов общая).

---

### 🟠 Tier 2 — boundary-утечка: CLI-формы протекли в библиотеку

Три связанных места, где артефакты CLI (`argparse`, exit-коды, `SystemExit`)
живут в библиотечном слое, который по контракту
([`docs/navigator-public-api.md`](docs/navigator-public-api.md)) должен быть
чистым importable API, возвращающим словари:

1. **`argparse.Namespace` как транспорт данных.**
   [`api_graph.py:32-42`](src/navigator/api_graph.py) фабрикует фейковый
   `argparse.Namespace` (`_graph_args`), чтобы передать его в
   `graph_core.load_docs(args.paths, root, args)`. Библиотечная функция принимает
   CLI-namespace. Симптом виден прямо в lock-правиле «не передавайте
   `types.SimpleNamespace` в helpers, типизированные под `argparse.Namespace`» —
   это лечение симптома, а не корня. **Remedy:** маленький `@dataclass
   GraphArgs` (или явные kwargs в `load_docs`); правило про SimpleNamespace тогда
   исчезает как ненужное.

2. **Exit-код, протащенный сквозь payload.**
   [`api_utils.py:22-25`](src/navigator/api_utils.py) `_exit()` впрыскивает
   `_exit_code` прямо в словарь данных; [`_generic.py:86`](src/md_cli/handlers/_generic.py)
   его вылавливает: `payload.pop("_exit_code", 0)`. Внеполосный канал сквозь
   данные, и неоднородный — только graph-функции его используют, остальные
   возвращают чистый dict. **Remedy:** `ToolResult` уже несёт `exit_code`
   отдельным полем; handler может выводить код из содержимого payload (есть
   `issues` / `blockers`) — магический ключ в данных не нужен.

3. **`SystemExit` как поток ошибок в библиотеке + несогласованная обработка.**
   [`graph_core.py:176,300`](src/navigator/graph_core.py) делают `raise
   SystemExit("Path not found")`, `:26` — `sys.exit(2)`. `_generic._call` ловит
   `Exception`, но **не** `BaseException`, поэтому `SystemExit` пролетает
   насквозь и валит процесс. При этом `deps` ловит его руками
   ([`api_graph.py:181-184`](src/navigator/api_graph.py) → красивый
   `{"error": "path_not_found"}`), а `impact` и `preflight`
   ([`api_graph.py:201,222`](src/navigator/api_graph.py)) зовут ту же
   `load_target_doc` **без** try/except. Итог: `api.deps("нет")` вернёт error-dict,
   а `api.impact("нет")` бросит `SystemExit` — прямое нарушение контракта
   «importable API возвращает dict». **Remedy:** библиотека бросает обычное
   доменное исключение (или возвращает error-payload), `sys.exit` остаётся
   только в CLI-слое; обработка отсутствующего пути одинаковая во всех трёх
   функциях.

---

### 🟡 Tier 3 — хрупкий regex поверх прозы вместо структурных данных

[`main.py:25-88`](src/md_cli/main.py) `_add_signature_args` **regex-парсит
человекочитаемую строку** `cli_signature` (`"md search CORPUS --query QUERY
[--limit N]"`), чтобы реконструировать структуру аргументов argparse —
позиционные vs флаги, порядок. Эвристики вроде «`next_bare.upper() == next_bare`
значит это плейсхолдер значения» хрупкие. При этом типы/required/help берутся из
`input_schema`. Получается **двойной источник правды**: прозаическая сигнатура
(структура) + схема (типы), связанные регэкспом.

**Remedy:** позиционность и порядок аргументов — структурные данные, им место в
каталоге (например, поле `cli_args: list[{name, positional, type}]`), а не в
прозаической строке, которую парсят обратно. `cli_signature` тогда генерируется
из структуры для показа, а не парсится для восстановления структуры.

---

### 🟡 Tier 3 — размер и границы: `audit.py` у стены, `**kwargs` вместо контрактов

- **`audit.py` = 955/1000 строк.** Лимит 1000 форсится тестом
  (`test_source_files_stay_under_1000_lines`), и lock прямо просит «не раздувать
  `audit.py` обратно за 1000 строк». Файл на 95.5% к стене. В нём семь
  `severity_for_*` функций; по букве lock «severity scoring» — это они, и их
  место в `audit_severity.py` (где уже живут константы severity и
  `compute_health`). **Remedy:** перенести `severity_for_*` в `audit_severity.py`
  — это и честит границу по lock, и снимает давление размера. (Либо явно уточнить
  в lock, что per-finding severity остаётся с детекцией — но тогда это решение,
  а не дрейф.)

- **`**kwargs` + ручная валидация.** Публичный API широко использует `**kwargs`
  (`audit`, `cluster`, `search`, `index`, `strip`, `status`...), а потом руками
  отвергает неизвестное через `_reject_unknown_kwargs`
  ([`api_utils.py:47-51`](src/navigator/api_utils.py)) — переизобретая то, что
  явные типизированные сигнатуры дают бесплатно. Часть `**kwargs` оправдана
  forward-compat, но там, где набор параметров известен, явная сигнатура
  легибельнее и самодокументируется. **Remedy:** явные параметры там, где набор
  фиксирован; `**kwargs` оставить только для реально открытых наборов.

### ⚪ Мелочь (не блокер, чинится в проброс)

- [`api.py:40`](src/navigator/api.py): `__import__("os").walk(...)` вместо
  обычного `import os`. Магический динамический импорт без причины — заменить на
  нормальный import.

---

## Связность находок и порядок чистки

Находки **сцеплены** — это одна координированная волна, а не девять отдельных
правок:

1. **Волна A (главная, code-judo).** Перецелить тесты с `cmd_*` / `cli` / `graph`
   на `api.*` / `*_payload` → удалить proxy-магию (Tier 2.1) → удалить legacy-слой
   `cli.py` / `graph.py` / `cmd_*` / скрипты (Tier 1). Миграция тестов —
   общий разблокировщик для обоих. Эффект: −~1750 строк, минус целая вторая
   архитектура, минус класс магии. Делать как одну серию с зелёными тестами на
   каждом шаге.

2. **Волна B (handlers).** Generic-fallback в диспетчере → удалить 30 shim'ов →
   переписать `test_handlers_boundary`. −~300 строк, −30 файлов.

3. **Волна C (boundary-гигиена).** `GraphArgs` dataclass вместо
   `argparse.Namespace`; `SystemExit`/`sys.exit` только в CLI-слое + единая
   обработка path-not-found в `deps`/`impact`/`preflight`; убрать `_exit_code`
   из payload. Снимает CLF-измы и нарушение «API возвращает dict».

4. **Волна D (точечно).** `severity_for_*` → `audit_severity.py`;
   `_add_signature_args` на структурные данные каталога; `__import__("os")`.

Волны A–B не меняют поведение продукта (legacy не в продукте; shim'ы
тождественны). Волна C меняет наблюдаемое поведение библиотечного API на
отсутствующих путях (в лучшую сторону — структурный error вместо краха) —
поправить соответствующие тесты в том же ходу.

---

## Чего этот аудит НЕ касался

- Корректность алгоритмов поиска/эмбеддингов/графа по существу (RRF-веса,
  чанкинг, severity-пороги) — это domain-валидация, не структурный аудит.
- Производительность за пределами очевидной сериализации/оркестрации.
- Безопасность как отдельный проход (тут нет внешнего ввода кроме путей и
  Markdown; `_generic._call` ловит исключения в envelope — fence на месте).

Эти зоны выглядят разумно при беглом проходе, но заслуживают отдельной проверки,
если станут критичными.
