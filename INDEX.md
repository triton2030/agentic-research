# INDEX — оплаченные маршруты

Не оглавление и не вторая правда. Каждая строка — короткий путь, за который
уже заплатил поиском предыдущий агент: знание лежит **не там**, где холодный
агент стал бы его искать. Полноту не заявляет; промах падает в обычную
навигацию (`1md-search`, `md`, grep). Владелец файла — `1index`.

## Правлю скил — где живой владелец, а где архив

- [`skills/shared/README.md#живые-owners`](skills/shared/README.md) — реестр
  cross-runtime владельцев: какой пакет живёт в `shared/<name>/portable/`, а
  какой — runtime-owner в `claude/`/`codex/`. Проверять **до** первой правки.
- `skills/1<name>/` — **архив истории снятого или переписанного скила**:
  `origin.md`, `cut.md`, `evidence.md`, снапшоты `live-*`/`tracked-*`. Не живой
  контракт. Ловушка: `skills/1lossy-product-refactor/` содержит
  `product-frame*.md` снятого скила — за действующий Frame не принимать.
- [`skills/claude/README.md`](skills/claude/README.md) — контракт «сначала
  registry, потом runtime owner», требования к глобальной правке.
- [`skills/shared/sync_simple_projections.py`](skills/shared/sync_simple_projections.py)
  — сборка projection после правки shared owner-а; `--check` останавливается на
  неизвестных лишних файлах вместо тихого удаления.
- **`1hermes` и `1codex` синхронизируются по-разному, и это стоит проверки.**
  `~/.claude/skills/1hermes` — симлинк, правка tracked owner-а видна сразу.
  `~/.claude/skills/1codex` — **настоящая папка**: после правки
  `skills/claude/1codex/` копируй `SKILL.md` и `references/` руками, иначе
  живой скил останется старым. Ловушка рядом: `skills/shared/1hermes/` — не
  runtime owner, а Product Owner (только `product-frame*.md`); `cut.md` и
  `origin.md` внутри относятся к shaping рамки, не к снятому скилу.
- Бэкенд Codex-моста — `experiments/codex-bridge/` (правится от своего
  `AGENTS.md`), operator/router — `skills/claude/1codex/`. Витрина прогонов:
  `codex_watch.py` там же, `hermes_watch.py` — в `scripts/` скила Hermes.

## Ищу, что владелец говорил или решал

- `_ops/chat-recall/` — дословные выдержки, файл на разговор. Читать не глазами,
  а запросом:

  ```bash
  uv run --locked --script \
    ~/.claude/skills/1chat-recall/scripts/chat_digest.py \
    _ops/chat-recall --query "<предмет решения>" --json
  ```

- `_ops/user-said/` — замороженный предшественник (по 2026-05-28), read-only.
  Отсутствие цитаты там не доказывает отсутствия позиции.
- [`_ops/product-frames/agentic-research.principles.md`](_ops/product-frames/agentic-research.principles.md)
  — принципы, применяемые к развилкам через `1use-principles`.

## Пишу или переписываю скил

- [`knowledge/practical-guides/how-to-write-skills/authoring-canon.md`](knowledge/practical-guides/how-to-write-skills/authoring-canon.md)
  — канон: когда скил вообще писать, форма `description`, тело, progressive
  disclosure, жёсткость, типовые провалы.
- [`.../mid-trajectory-trigger-descriptions.md`](knowledge/practical-guides/how-to-write-skills/mid-trajectory-trigger-descriptions.md)
  — почему скил не поднимается в середине траектории и как это чинит
  `description`.
- [`.../platform-deltas.md`](knowledge/practical-guides/how-to-write-skills/platform-deltas.md)
  — где Claude и Codex расходятся, чтобы не копировать дельту в тело скила.

## Записанное правило не доходит до поведения

- [`exa-results/frontier-model-failures-2026-08-25.md#жёсткий-фильтр`](exa-results/frontier-model-failures-2026-08-25.md#жёсткий-фильтр)
  — проверить model-release cutoff, актуальное evidence и исключённые старые
  панели до переноса исследования в root instructions или skills.
- [`science/how-to-make-llm-obey.md#четыре-механизма-отказа`](science/how-to-make-llm-obey.md)
  — обвал по числу одновременных правил, затухание по длине траектории,
  нечитаемый носитель, конкуренция формы вывода с мышлением.
- [`science/how-to-make-llm-obey.md#что-опровергнуто`](science/how-to-make-llm-obey.md)
  — расписывание когнитивных шагов за модель, формулировки-усилители, видимый
  ход мысли как доказательство соблюдения. Читать **до** того, как усиливать
  инструкцию словами.
- [`science/how-to-make-llm-obey.md#числовые-ориентиры`](science/how-to-make-llm-obey.md)
  — пороги и числа; там же `#чего-нельзя-складывать`.

## Нужна физика: как модель думает

- [`knowledge/how-llms-think.md`](knowledge/how-llms-think.md) — единственный
  владелец физики: вероятностная машина → перекосы → контекст → траектория.
  Совпадения в скилах — намеренные спицы одной оси, не дубли под удаление.
- [`science/how-to-steer-llm-thinking.md#семь-рычагов`](science/how-to-steer-llm-thinking.md)
  — рычаги управления мышлением с evidence-статусами; статусы меняются только
  вместе с evidence.
- Развилка владения: *как сделать нужное продолжение вероятным* →
  `how-to-steer-llm-thinking.md`; *как носитель довести правило до поведения* →
  `how-to-make-llm-obey.md`; *физика машины* → `knowledge/how-llms-think.md`.

## Куда положить временный файл или находку

- [`_ops/AGENTS.md`](_ops/AGENTS.md) — контракты всех папок `_ops` и красные
  линии: `findings/` не backlog, `rules/` не shadow-`AGENTS.md`, `interviews/`
  не постоянная память, выдержки `chat-recall/` не редактируются.

## Дельты моделей и рантаймов

- `knowledge/wisdom-claude-opus-5.md`, `wisdom-claude-fable-5.md`,
  `wisdom-gpt-5.6.md`, `wisdom-codex.md`, `wisdom-claude-code.md` — routing и
  prompting-дельты живут здесь, а не копируются в каждый скил.
- `knowledge/wisdom-skills-plugins.md`, `wisdom-systems-thinking.md`,
  `wisdom-llm.md` — общие оси.
- [`knowledge/practical-guides/hooks-runtime-guardrails.md`](knowledge/practical-guides/hooks-runtime-guardrails.md)
  — хуки как слой принуждения, когда прозы недостаточно.

## Артефакты прошлых проверок

- `science/verification/<дата>/` — постоянный архив: тезисы, прокурорский
  вердикт, литературная сводка, батареи E7–E10. Архив live-статусами не владеет.
- `_workspace/codex-packets/`, `_workspace/codex-artifacts/` — рабочие пакеты и
  выходы кросс-модельных прогонов.
- `_workspace/orchestration/<дата>-<тема>/` — снапшоты волн субагентов, включая
  чужие проекты-подопытные.

## Ищу позицию владельца по предмету

- [`_ops/chat-recall/AGENTS.md`](_ops/chat-recall/AGENTS.md) — контракт корпуса:
  цитаты ищутся напрямую запросом выше, промежуточного слоя нет.
- Производный слой тем снят владельцем 2026-08-28 вместе со всей его
  машинерией; его прогоны в `experiments/openviking-chat-recall/` остаются
  снятой веткой и evidence замера, а не рабочим маршрутом.

## Зову Ox Alpha или чиню 1hermes — где доказательства прогона

- `~/.claude/skills/1hermes` — **симлинк** на `skills/claude/1hermes/`. Правка
  скила сразу под git этого репо, отдельной синхронизации нет; искать второй
  source tree не надо.
- `~/.hermes/1hermes-runs/<run_id>/` — квитанция каждого прогона: `manifest.json`
  (что запрошено), `result.json` (`ok`, `resolved`, `usage`, `warnings`),
  `prompt.md`. Лежит **вне репозитория**: в проекте следов оплаченного прогона
  нет вообще.
- `_workspace/ox-*/runs/*.err` — **сырой stderr** прогонов волны. Обёртка кладёт
  в `warnings` только непустые строки, поэтому при молчащем CLI единственное
  наблюдение живёт здесь. Ловушка: при отказе маршрута файл пуст — это и есть
  сигнал, а не поломка записи.
- [`experiments/hermes-ox-alpha/route_started.py`](experiments/hermes-ox-alpha/route_started.py)
  — отпечаток вероятностного отказа маршрута Ox (`provider: null` плюс ноль
  вызовов) и его признание. Проходит на повторе; причина неизвестна, см.
  `_ops/findings/2026-08-23-134711-62714-3302.md`.
