---
kind: runbook
protocol: quotes-to-wiki
version: v2
date: 2026-08-23
---

# Как собрать библиотеку из чужой папки цитат

Протокол `PROTOCOL.md` говорит, что делать и почему. Этот файл говорит, чем —
по шагам, командами. Смысловые решения живут в `prompts/*.md`, механика в
`scripts/*.py`, а исполнение — в волне агентов.

Всё написано так, чтобы работать над **любой** папкой `_ops/chat-recall/`, а не
только над своей. Единственное, что меняется от проекта к проекту, — три
переменные:

```bash
CORPUS=/путь/к/чужому/проекту/_ops/chat-recall   # только читается
ART=experiments/openviking-chat-recall/artifacts/<имя-проекта>
WORK=_workspace/ox-<имя-проекта>                 # рабочие файлы, не в git
```

Исходная папка не правится, не переименовывается и не удаляется — инвариант 1.
Все артефакты живут отдельно и пересобираемы.

## Устройство одного шага

Каждый шаг устроен одинаково и это не совпадение, а вывод, оплаченный дважды:

```
build_*.py   собирает брифы    ← механика: пути, состав, нумерация
ox_wave.sh   разводит агентов  ← суждение: что решить по каждой единице
apply_*.py   кладёт результат  ← механика: адреса, ссылки, проверка баланса
```

Модель получает **решение, а не объём**. Первый заход отдал ей указатель
целиком: прогон шёл больше часа и не вернул ничего, потому что работа была не
сложной, а огромной, и почти вся механической. Разделив, получаем сорок коротких
суждений и один детерминированный сборщик.

Волна запускается **только фоном**: прогон Ox идёт от минут до часов.

```bash
TASKS=<брифы> OUT=<прогоны> PAR=6 RETRIES=6 MODE=read CWD="$PWD" \
  nohup bash experiments/hermes-ox-alpha/ox_wave.sh > <лог> 2>&1 &
```

`MODE=read` — агент только читает и возвращает текст; кладёт скрипт.
`MODE=write` нужен, лишь когда агент обязан писать сам.

## Стадия 0 — снимок

```bash
git add -A && git commit -m "снимок корпуса <имя-проекта> перед сборкой"
git rev-parse --short HEAD          # запиши: этим коммитом судится покрытие
```

Корпус живёт дальше: появляются разговоры, а старые дорастают строками в шапке.
Судить полноту по сегодняшней папке нечестно вдвойне, поэтому снимок — коммит.

## Стадия 1 — пофайловое сжатие

```bash
python3 scripts/build_flatten_tasks.py "$CORPUS" "$WORK-flat/tasks"
# волна
python3 scripts/apply_flatten.py "$WORK-flat/runs" "$CORPUS" "$ART/flat"
```

`apply_flatten.py` сразу печатает баланс: сколько записей перенесено, сколько
уронено и в каких строках. Не откладывай этот счёт на конец — в первый раз
стадия уронила 90 записей из 1207, и узналось это через сутки.

## Стадия 2 — карта тем

```bash
python3 scripts/build_topicmap_task.py "$ART/flat" "$WORK-topics/tasks"
# волна, PAR=1
python3 scripts/apply_topicmap.py "$WORK-topics/runs/topics.json" "$ART/flat" "$ART/topics.json"
```

На вход идут только строки «о чём» из шапок сжатых файлов. Цитаты в эту стадию
не входят: владелец 2026-08-22 остановил ход, где агенты строили карту по всем
файлам цитат разом.

`apply_topicmap.py` отказывается записывать карту, которая не является
разбиением: файл без темы или названный дважды — стоп, а не предупреждение.

## Стадия 3 — слияние по темам

```bash
python3 scripts/build_stage_tasks.py merge "$ART/topics.json" "$ART/flat" "$WORK-merge/tasks"
# волна
python3 scripts/apply_stage.py merge "$WORK-merge/runs" "$ART/flat" "$ART/topics"
python3 scripts/check_topics.py "$ART"
```

Раскладка сверяет якоря входа и выхода и отвергает тему целиком, если они не
сходятся. Переписанный по памяти якорь выглядит правдоподобно — ловится только
счётом.

## Стадия 4 — страницы

```bash
python3 scripts/build_stage_tasks.py pages "$ART/topics.json" "$ART/topics" "$WORK-pages/tasks"
# волна
python3 scripts/apply_stage.py pages "$WORK-pages/runs" "$ART/topics" "$ART/wiki"
python3 scripts/check_wiki.py "$ART/wiki"
```

`check_wiki.py` запускай **после каждой темы**, а не в конце: проверка ссылок
здесь не формальность. В первой сборке не открывалась ни одна из 1693 ссылок, и
прожило это сорок прогонов.

## Стадия 5 — указатель

```bash
python3 scripts/build_index_skeleton.py "$ART/wiki" "$ART/topics.json" "$ART/index-skeleton.json"
python3 scripts/build_index_task.py "$ART/index-skeleton.json" "$WORK-index/tasks"
# волна, PAR=1
python3 scripts/apply_index.py "$ART/index-skeleton.json" "$WORK-index/runs/index.json"
```

Модель называет разделы и задаёт порядок; состав и пути ставит скелет.

## Стадия 6 — покрытие и добор

```bash
python3 scripts/check_coverage.py <коммит-снимка>
python3 scripts/build_backfill_tasks.py "$WORK-backfill/tasks"
# волна
python3 scripts/apply_backfill.py --dry "$WORK-backfill/runs"
python3 scripts/apply_backfill.py "$WORK-backfill/runs"
```

Пропуск не оценивается выборкой, а вычитается: у каждой записи есть адрес.
Каждая недошедшая запись получает одну из трёх судеб — место на странице, новая
страница или отказ с названной причиной. Отказ полноправен; молчание — нет.

## Стадия 7 — аудит смысла, дрейф якорей, правки

```bash
python3 scripts/build_audit_tasks.py "$WORK-audit/tasks"
# волна
python3 scripts/build_repair_tasks.py "$WORK-audit/runs" "$WORK-repair/tasks"
# волна
python3 scripts/apply_repair.py "$WORK-repair/runs"

python3 scripts/build_split_tasks.py "$ART/audit-structural.tsv" "$WORK-split/tasks"
# волна
python3 scripts/apply_split.py "$WORK-split/runs"
```

Дрейф якорей проверяй, только если `check_coverage.py` назвал висячие адреса:

```bash
python3 scripts/build_drift_tasks.py "$WORK-drift/tasks" <имена разговоров>
# волна
python3 scripts/apply_drift.py "$WORK-drift/runs"
```

## Обслуживание — когда корпус вырос

Ссылки библиотеки указывают на номера строк живых файлов, а файлы растут и в
конце, и в шапке. Один раз после сборки снимается карта отпечатков, дальше она
чинит ссылки сама:

```bash
python3 scripts/reanchor.py map    # один раз после сборки
python3 scripts/reanchor.py fix    # после любого роста корпуса
```

`fix` отказывается работать при неоднозначных отпечатках и ничего не трогает.
Проверить, насколько библиотека отстала от корпуса, — `check_coverage.py`,
последние строки вывода.

## Стадия 8 — приёмка поиском

```bash
# вопросы пишет окно, видящее ТОЛЬКО разговоры
TASKS=... CWD="$CORPUS" ...   # волна
python3 scripts/build_accept_tasks.py "$WORK-accept/runs/questions.json" "$WORK-answer/tasks"
# два прогона: CWD="$ART/wiki" и CWD="$CORPUS"
python3 scripts/build_grade_task.py <library.json> <corpus.json> "$WORK-grade/tasks"
# волна
```

Судья не знает, где библиотека: колонки называются `A` и `B`, порядок выбирается
жребием от номера вопроса. Оценивать самому нельзя — тот, кто строил, искренне
засчитает своей стороне ничью.

## Что делать, когда прогон не принят

Волна сама повторяет три класса отказа: маршрут не стартовал, сессия не
доказала ответ ассистента, вызовы не подтвердили маршрут. Остальное — твоя
работа:

- **ответ не в формате** — чини бриф, а не число повторов;
- **упёрся в потолок итераций** — смотри, на чём крутился; бюджет тут ни при чём;
- **`ok=true`, а ответ пустой** — обёртка кладёт заглушку, гейт её ловит;
  если проскочило, проверь `route_started.py`;
- **прогон затёрт повтором** — сырой результат лежит в
  `~/.hermes/1hermes-runs/<run_id>/result.json`.
