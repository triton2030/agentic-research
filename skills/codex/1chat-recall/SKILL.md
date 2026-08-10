---
name: 1chat-recall
description: >
  Вызывай, когда в текущем чате появляется важный самостоятельный тезис
  владельца: сохрани его и недодумываемую контекстную дельту в том же ходе.
  Также вызывай, когда прежние слова владельца из этой или другой задачи
  текущего проекта могут закрыть существенный пробел текущей просьбы,
  пользователь спрашивает, что говорил, либо требуется repair/backfill recall.
  Не применяй цитату буквально без проверки контекста, scope, chronology и
  более свежего owner-а.
---

# Chat recall

## Цель

Будущий агент закрывает неполноту текущей просьбы применимыми словами владельца
и принимает корректное следующее решение без повторного сбора уже сказанного.
Для consequential утверждения он способен назвать файл и процитировать owner
evidence, изменившее понимание или решение.

Capture — обязательная supply-часть того же продукта: важный тезис сохраняется
в том же ходе, иначе будущему retrieval нечего читать.

Дословность защищает evidence, но не заменяет понимание. Намерение
восстанавливается по source context, scope, речевому акту, хронологии,
контекстной дельте и более свежим owner-файлам. Собственная интерпретация
помечается как вывод агента; неразрешённая существенная неоднозначность приводит
к abstain или вопросу владельцу.

Рабочий контекст остаётся временным synthesis над источниками. Он не создаёт
постоянный профиль владельца и не превращает датированный лог в текущий канон.

## Критерии успеха

- Каждый самостоятельный полезный тезис текущего хода записан один раз.
- Quote сохраняет лексику владельца; сокращение только deletion-only.
- Вид evidence различим: `quote`, `selection`, `note` или повреждённый `raw`.
- Source timestamp, session и agent позволяют проверить происхождение записи.
- У owner quote есть `context-note` только с внешней surprise-дельтой.
- Retrieval заканчивается применимым context packet, прямым ответом на запрос
  цитаты либо честным abstain — не списком top hits.
- Consequential применение предъявляет полную цитату и адрес файла.
- Repair/backfill сохраняет тексты, provenance и исходную хронологию.
- Evidence параллельной задачи меняет только названный текущий claim и не
  выдаётся за live-status той задачи.

## Инварианты

Owner quote — source-bound evidence. Agent-authored option, summary или вывод не
становится цитатой владельца. `selection` фиксирует выбранный agent-authored
вариант без притворства дословной речью.

Usefulness gate проходит тезис, чьи собственные слова вне соседних сообщений
способны изменить будущее решение, границу, критерий, предпочтение или
понимание владельца. Согласие вроде «да, давай так» не проходит. Credentials,
вставленный чужой материал и недолговечная команда не записываются.

У каждой quote обязателен однострочный `context-note`: внешний referent, scope,
прежнее состояние или сцена решения, потерянные при изоляции. Повтор,
перефразирование, новая мотивация, URL и ссылка на transcript запрещены.
Произвольного числового лимита нет; заметка ограничивается только необходимой
дельтой. Заметка возвращает цитату в её сцену и не укрупняет сказанное:
реплике нельзя приписывать больший scope или commitment, чем она несла в
источнике, — ситуативная правка не становится постоянным предпочтением
владельца. Заметка индексируется поиском: называй референты устойчивыми
именами — скил, файл, документ, дата решения; сессионные указатели вроде
«дефект №3» будущий запрос не наберёт. Поисковое дружелюбие не оправдывает
пересказ — добавляй имена сцены, не синонимы цитаты.

Exact provenance ставится только после чтения native record. Observation time,
filename, память агента и semantic match остаются approximate с честным
`source/precision`.

Один разговор/session пишет один recall-файл и не добавляет туда evidence из
другого окна. Retrieval читает общий project-local corpus всех агентов.

Ошибка даты, type, topic или синтаксиса не уничтожает запись. Quote или
selection остаётся asset, а проблема становится diagnostic.

По умолчанию scope только текущий проект. Cross-project recall требует явного
scope владельца. Цитаты и transcript evidence не отправляются в сеть.

Live owner сильнее recall. Новизна сама по себе не отменяет прежнюю позицию:
нужны тот же claim и scope, реальное исправление или замена и различимая
хронология.

## Дельта

Модель умеет копировать текст и запускать поиск. Без скила она:

- продолжает работу, не сохранив важный тезис текущего хода;
- принимает видимый, первый семантический или самый новый hit за позицию
  владельца;
- понимает двусмысленную фразу буквально, не сверяя ситуацию и прежние
  коррекции;
- показывает quote dump вместо изменившегося решения;
- принимает историческую цитату параллельной задачи за её текущий статус.

Недостающий оператор:

```text
fresh evidence → usefulness gate → source-bound capture
material gap → bounded claim → full records
→ context + scope + commitment + chronology + live owner
→ decision-ready context | abstain
```

## Известные сбои

`когда → сбой → цена → куда`

- появился важный тезис → работа продолжена без capture → будущему recall
  нечего читать → механика, Capture
- context-note повторяет цитату → агентский груз выглядит полезным контекстом →
  загрязнение каждого будущего чтения → Инварианты, context-note
- ситуативное согласие в задаче → context-note обобщает его до постоянного
  предпочтения → будущий агент применяет несуществующее правило → Инварианты,
  context-note
- найден top/newest hit → он объявлен текущей позицией → false application →
  [reading-the-log](references/reading-the-log.md)
- один query пуст → объявлено «владелец не говорил» → ложное отсутствие →
  [reading-the-log](references/reading-the-log.md)
- найдена цитата параллельной задачи → ей приписан нынешний status →
  координация строится на прошлом → [reading-the-log](references/reading-the-log.md)
- проект существовал до recall либо metadata повреждена → дата придумана или
  evidence потеряно → ложная история →
  [repairing-the-log](references/repairing-the-log.md)

## Механика

В одном ходе могут сработать несколько ветвей. Сначала сохрани свежее evidence;
затем используй прежнее evidence для текущего решения. Repair/backfill не
является обычным retrieval.

### Evidence текущего чата

```bash
ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"
SESSION="$CODEX_THREAD_ID"
AGENT="codex"
RECALL="$ROOT/scripts/chat_recall.py"

python3 "$RECALL" read
python3 "$RECALL" search "<точный фрагмент>" --scope user
python3 "$RECALL" search "<свежий фрагмент>" \
  --scope user --include-current-turn --json
python3 "$RECALL" show <record-id>
```

Для свежей реплики найди exact native record. Если runtime ещё не показывает
текущий turn, используй observation timestamp с
`source=turn-context`, `precision=minute|date`; не называй его transcript-exact.

Plan/AskUserQuestion option написан агентом. Сохраняй выбранное значение как
`selection`, а не owner quote.

### Capture

Перед командой назови одно внешнее обстоятельство, которое исчезнет без
соседних сообщений. Затем запиши каждый самостоятельный тезис отдельно:

```bash
CAPTURE="$ROOT/scripts/chat_capture.py"

python3 "$CAPTURE" \
  --quote "<слова владельца или выбранный вариант>" \
  --context-note "<внешняя дельта, не пересказ>" \
  --source-timestamp "<timestamp источника>" \
  --type <речевой-акт> --topic <retrieval-owner> \
  --agent "$AGENT" --project "$PWD" --session "$SESSION"
```

Для agent-authored выбора добавь `--kind selection`; для repair explanation —
`--kind note`. Если type/topic неочевидны:

```bash
python3 "$CAPTURE" --list-metadata
```

Классифицируй речевой акт и долгоживущий retrieval-owner, не грамматику
предложения и не название текущей задачи.

Свою ошибочную запись исправляй обычной правкой recall-файла: context-note,
type/topic, собственный дубль. Текст owner-цитаты меняется только deletion-only
по native record; удаление записи целиком — только по явному слову владельца.
Чужие или повреждённые записи — маршрут repair.

### Retrieval

До query назови текущий claim, который прежние слова способны изменить:

```bash
DIGEST="$ROOT/scripts/chat_digest.py"
RECALL_DIR="$PWD/_ops/chat-recall"

uv run --offline --locked --script "$DIGEST" "$RECALL_DIR" \
  --query "<claim, слова или варианты формулировки>" \
  --limit 5 --max-chars 4000

python3 "$DIGEST" "$RECALL_DIR" --show <record-id>
```

Если local hybrid cache недоступен, используй `--lexical`; обычный retrieval не
получает разрешение на network bootstrap.

Раскрой каждый consequential candidate полностью. Сравни применимость, kind,
commitment, source time/precision, coverage и live owner. Верни минимальный
packet:

- применимые решения, границы, критерии и предпочтения;
- вытесненную позицию и основание вытеснения;
- scoped exceptions, conflicts и gaps;
- агентские интерпретации отдельно от owner words;
- полные цитаты и адреса только для consequential claims.

Для параллельной задачи того же проекта допустимы filters
`--agent`, `--session`, `--since` и `--until`. Результат говорит, что было
сказано или выбрано; он не доказывает нынешний статус задачи.

Прямой запрос «что я говорил?» может закончиться source-bound цитатами без
decision packet, если текущей развилки действительно нет.

### Repair/backfill

Открывай
[repairing-the-log](references/repairing-the-log.md) только когда существующая
запись повреждена либо владелец явно просит восстановить полезные owner-сигналы
из проекта/session, существовавших до нормального capture.

Не используй repair/backfill как скрытый импорт всех старых разговоров.

## Завершение

Остановись, когда:

- свежие самостоятельные тезисы сохранены;
- material claim получил decision-ready context либо явный abstain;
- прямой запрос цитаты получил source-bound ответ;
- repair/backfill сохранил исходные тексты и честную chronology;
- provenance, diagnostics, owner inference и material gaps видны.

Quote dump, top hit без applicability gate, owner quote без context-note и
непомеченный агентский вывод не являются завершением.
