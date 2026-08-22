---
name: 1hermes
description: >
  Вызывай, когда пользователь просит Hermes, Kimi K3, DeepSeek или Ox Alpha;
  когда нужно продолжить их session, выбрать model/provider route либо
  проверить здоровье уже настроенного Hermes/OpenRouter вызова. Не вызывай
  для справочных вопросов о Hermes или OpenRouter, общего сравнения моделей,
  Gemini/Claude second opinion, OpenAI-вызова или задачи, где внешний model
  run вообще не требуется.
---

# Hermes Advisor

## Выбери Маршрут

| Запрос пользователя | Действие |
| --- | --- |
| Мнение, review или задача через Hermes | Запусти Golden Path ниже |
| «Работает ли Hermes?» | Сначала выполни бесплатный static health check |
| Явный end-to-end/live health | Выполни платный `--live` probe |
| Продолжить session | Используй `--resume`; прочитай advanced reference |
| Другая model/provider/reasoning | Начни fresh run; прочитай advanced reference |
| Явно названа Ox Alpha | Выполни бесплатный preflight и exact override ниже |
| Hermes должен писать или исполнять команды | Прочитай advanced reference до вызова |
| MoA, fallback, skills или расширенные toolsets | Прочитай advanced reference до вызова |

Выбери роль по задаче и передай обычные Hermes flags; отдельного role-router в
коде нет:

| Роль | Runtime | Когда |
|---|---|---|
| Умный советник | `moonshotai/kimi-k3`, reasoning `max` | сложная развилка |
| Обычный советник | `moonshotai/kimi-k3`, reasoning `medium` | обычный совет; default свежего run |
| Исполнитель | `deepseek/deepseek-v4-flash-0731`, reasoning `max` | писать, перебирать, вычитывать |

Provider по умолчанию — `nous`, toolsets — `file,web`.

## Ox Alpha Через Hermes

Ox Alpha — явный runtime override роли Исполнителя, не четвёртая роль, default
или fallback. Route жёстко закреплён за `nous`, reasoning `max`. Wrapper до
model call проверяет официальный live Nous catalog: exact model,
обязательные `prompt`/`completion` и каждая возвращённая компонента `pricing`
должны быть числовым нулём. Любая неизвестность отключает route.

```bash
python3 "$HERMES_ADVISOR" --cwd "$PWD" \
  --model stealth/ox-alpha --provider nous --reasoning max \
  --max-turns 2000 --timeout-sec 10800 <<'HERMES_BRIEF'
<самодостаточный brief>
HERMES_BRIEF
```

Wrapper передаёт `--ignore-user-config`, поэтому пользовательский fallback-chain
не загружается, и отдельно отвергает `--allow-fallback`. После fresh и resume
он принимает Ox только когда `session_model_usage` доказывает exact
model/provider/base URL/billing mode для main и всех auxiliary calls. Права у Ox
те же, что у любой другой роли: terminal, code_execution и запись проходят общий
контроль `validate`, отдельного запрета для неё нет. Гейт цены — единственное,
что относится только к ней, и он про деньги, а не про права. Для writes/worktree
и resume прочитай [advanced-usage.md](references/advanced-usage.md).

## Golden Path

До команды учти две границы:

- Hermes отправляет brief и прочитанные материалы provider-у; run может быть
  платным и сохраняется в локальном session store.
- Wrapper технически блокирует `write_file`/`patch` через
  `HERMES_WRITE_SAFE_ROOT`: read-only run получает пустой временный root, write
  run — exact project/worktree root. Это не sandbox для terminal; поэтому
  execution-capable toolsets требуют отдельный `--allow-write` — одинаково для
  всех моделей, включая Ox.

Передай реальный project `cwd`. Brief должен содержать роль, цель, точные
пути/URLs, границы, нужное evidence, формат ответа и stop. Не передавай
credentials или сырой chat dump.

```bash
HERMES_ADVISOR="${CODEX_HOME:-$HOME/.codex}/skills/1hermes/scripts/hermes_advisor.py"
python3 "$HERMES_ADVISOR" --cwd "$PWD" <<'HERMES_BRIEF'
<самодостаточный brief>
HERMES_BRIEF
```

Wrapper блокирует до terminal result и возвращает compact JSON. Если вызывающий
агент открыл delegation/execution toolsets, необходимость и способ декомпозиции
определяет Hermes по brief и этому skill, а не Python-wrapper.

Дефолт — 2000 tool-итераций и 3 часа. Это потолок автономности, не требование
использовать бюджет: brief задаёт цель, evidence и stop, а порядок чтения,
глубину исследования и рабочий маршрут выбирает Hermes.

## Методика Независимого Brief

Если Hermes проверяет уже принятое тобой решение, одного удаления финального
вывода недостаточно: структура brief-а всё ещё может подсказать его. Поэтому:

1. До запуска зафиксируй в чате свой вывод и его premises.
2. Собери brief заново от первички: развилка, симметричные критерии и нейтрально
   названные варианты; не переноси туда свой вывод и его структуру.
3. Удали остаточные подсказки: неравный отбор и порядок фактов, скрытые веса
   критериев, окрашенные слова и вопросы только к одному варианту.
4. Запиши контрфактуал: какой новый факт изменит какое решение.

Вызов добавил независимость, только если после ответа можно назвать premise,
которой не было в исходном выводе.

## Методика Исследования И Декомпозиции

Brief задаёт цель, границы, evidence и stop, но не программирует маршрут.
Hermes сам выбирает порядок чтения, глубину и разбиение задачи. Если ему открыты
delegation/execution tools, brief задаёт только разрешённые side effects и общий
бюджет; число агентов и способ декомпозиции остаются его когнитивным решением.

## Методика Разбора Расхождений

Не решай спор голосованием между агентами:

1. Разложи расхождение на пары конкурирующих premises.
2. Для каждой пары назови проверку, которая их разведёт: файл, команда, тест или
   первичный источник. Непроверяемая пара — вкус, не evidence.
3. Выполни проверки и меняй решение только по выдержавшим premises.
4. Явно назови отклонённые premises и evidence, которое их не подтвердило.

**У каждого прогона есть адрес.** Ещё до первого платного вызова wrapper
заводит квитанцию в `~/.hermes/1hermes-runs/<run_id>/`: brief, manifest и
`result.json` с терминальным исходом. Поле `run_dir` есть в любом ответе,
включая аварийный: неожиданная ошибка теперь возвращает JSON с причиной, а не
traceback, и оплаченный run не исчезает вместе с ним.

## Прими Или Отклони Result

Используй `response` только когда одновременно:

1. `ok` равен `true`;
2. `resolved.model`, `resolved.provider` и `resolved.reasoning` доказывают
   запрошенный runtime;
3. `session.id` присутствует;
4. `warnings` не содержат material gap;
   Для Ox сюда же попадает `Ox Alpha cost evidence rejected` — стоимость
   проверяется дважды: каталогом до запуска и записью сессии после. Каталог
   доказывает цену на момент старта, а run идёт часами;
5. `response` несёт запрошенную форму ответа, а не служебный текст: уведомление
   о достигнутом потолке итераций и ошибка провайдера ответом не являются.

Первые четыре условия проходят и на run, который не ответил вообще: runtime
верный, session есть, `ok` истинно — а внутри уведомление об исчерпанном
бюджете. Без пятого приёмка выдаёт зелёное на пустом результате.

`usage.api_calls` рядом с `resolved.max_turns` — подсказка о причине обрыва, но
не критерий: `usage.scope` равен `session_cumulative`, поэтому после `--resume`
счётчик несёт сумму всей session. Сравнивай их только на свежем run.

При обрыве не перезапускай с нуля: чтение уже оплачено. Продолжи session через
`--resume SESSION_ID` с малым `--max-turns`, запретив в brief открывать
инструменты и потребовав только вердикт.

`resolved` и `usage` проверяешь ты. Пользователю верни свёрнутый вывод: что дал
сторонний агент и что изменилось, без полной цитаты, имени модели и runtime
metadata. При `ok=false`, nonzero exit, пустом response, missing metadata,
runtime mismatch или обрыве по потолку верни точный gap; не заменяй
отсутствующий Hermes result собственным ответом.
Существенные claims Hermes проверь локально и отдели его мнение от вывода
Codex.

## Health

Не дублируй native health в wrapper. Эти проверки не вызывают модель:

```bash
hermes status
hermes portal info
hermes tools list
```

Они доказывают установку, auth и наличие tools, но не model execution. Для
execution evidence выполни bounded `hermes_advisor.py` run и прими только его
session-backed JSON.

## Условные Ветки

Прочитай [advanced-usage.md](references/advanced-usage.md) только для resume,
model override, writes/worktree, execution/delegation tools, Hermes skills,
browser/X research, fallback либо MoA. Не загружай его для обычного review.

## Стоп

Остановись после доказанного wrapper result, локальной проверки существенных
claims и честного closeout. Не печатай сырой `hermes sessions export`, не меняй
global Hermes config и не продолжай polling после завершения процесса.
