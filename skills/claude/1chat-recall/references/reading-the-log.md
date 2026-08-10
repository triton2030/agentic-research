# Reading the recall log

Читай лог ради текущего решения, не ради quote dump. Этот reference владеет
bounded retrieval, coverage, применимостью и параллельными project-local
задачами.

## Bounded route

`SKILL.md` заранее задаёт `DIGEST` и `RECALL_DIR`.

```bash
python3 "$DIGEST" "$RECALL_DIR" --check
python3 "$DIGEST" "$RECALL_DIR"

uv run --offline --locked --script "$DIGEST" "$RECALL_DIR" \
  --query "<claim или варианты формулировки>" \
  --limit 5 --max-chars 4000

python3 "$DIGEST" "$RECALL_DIR" --show <record-id>
```

Hybrid retrieval локален: corpus text не отправляется в сеть. Если cache ещё не
подготовлен, используй `--lexical`. Отдельный `--prepare` скачивает pinned model,
но не читает corpus; выполняй его только когда network bootstrap находится в
scope задачи.

Rank выбирает candidates для чтения. Он не измеряет truth, importance,
commitment или применимость.

## Filters и budget

Доступны `--type`, `--topic`, `--grep`, `--since`, `--until`, `--agent`,
`--session`, `--timeline`, `--lexical`, `--json` и `--verbose`.

Начинай с `--limit 5 --max-chars 4000`. `truncated_by=limit|max_chars` описывает
только presentation window. Если consequential candidates не покрыты, расширь
соответствующий budget; это всё ещё не доказывает полноту semantic recall.

`--show` возвращает полный text, provenance, address, diagnostics и
`context-note`. Именно полный record, а не excerpt, участвует в решении.

## Claim cluster

До query запиши одним предложением live claim или развилку. Ищи:

1. исходными словами;
2. одним paraphrase или synonym/prefix вариантом;
3. по owning topic либо metadata/time/session, когда это меняет coverage.

Не начинай с «что владелец думает вообще». Разделяй независимые claims и scopes.

Внутри кластера сравни:

1. применимость к текущему решению и scope;
2. прямое evidence: `quote|selection` сильнее `note|raw`;
3. commitment: correction/adopted decision сильнее поздней идеи;
4. source time и precision;
5. coverage, truncation и diagnostics;
6. более свежий live owner.

Поздняя запись вытесняет раннюю только при том же claim и scope, реальном
исправлении или замене и различимой chronology. Более узкая запись может быть
exception. `type: факт` фиксирует более новое утверждение владельца, но не
доказывает внешний факт.

## Параллельные задачи

Для другой задачи текущего проекта сначала назови claim, который способен
изменить текущую работу. Сузь candidates по `--agent`, `--session` или времени,
когда metadata известна.

Цитата доказывает только, что было сказано или выбрано в указанной session.
Начало работы, намерение или план не доказывают нынешний status, completion или
состояние live artifact.

Cross-project поиск разрешён только явным scope владельца; его evidence не
смешивается молча с local position.

## Отсутствие и abstain

Один пустой query не доказывает отсутствие owner evidence. До такого вывода
проверь original wording, paraphrase/prefix, topic или metadata route,
presentation truncation и `--show` каждого consequential record.

`selection=none` означает отсутствие candidates в выполненном route, не
отсутствие мысли владельца вообще.

Если scope, commitment, chronology или coverage остаются неразрешёнными,
сохрани конфликт видимым и abstain либо спроси владельца. False application
хуже missed recall.

## Результат чтения

Верни минимальный working context:

- применимые решения, границы, критерии и предпочтения;
- displaced position и основание;
- scoped exceptions, conflicts и gaps;
- агентские inference отдельно;
- полные quote и file address только для consequential claims.

Если recall расходится с активным owner-документом, покажи расхождение. Не
превращай повтор похожих цитат в новое общее правило владельца без пометки
инференса.

## Diagnostics

`--check` показывает repair backlog, не скрывая records. `--check --strict`
является structural gate и завершается non-zero при diagnostics.

Invalid metadata сохраняется как raw значение и repair sentinel. Процедура
исправления принадлежит
[repairing-the-log](repairing-the-log.md).
