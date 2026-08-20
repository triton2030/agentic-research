# Recovering recall coverage

Открывай только когда обычный Retrieval дал пустой, чрезмерно широкий,
конфликтующий или усечённый route либо hybrid-поиск недоступен. Файл даёт
bounded recovery и coverage packet; применение owner evidence остаётся в
`SKILL.md`.

## Сначала диагностика, потом перезапрос

`matched`, `returned`, `truncated`, `retrieval` и список уникальных holder files
говорят, что именно пошло не так. `matched` и `returned` — объём кандидатов до и
после `--limit`, не мера широты claim-а: узкий и широкий запрос одинаково дают
`62/10`. Широту суди по содержанию найденных holder-ов; при `truncated_by=limit`
поднимай `--limit` осознанно.

## Четыре хода, меняющих candidate set

Новых вариантов запроса без изменения candidate set не добавляй. Фильтры CLI
(`--since`, `--type`, `--topic`, `--agent`, `--session`, `--grep`) кандидатов
тоже меняют, но служат другим задачам, не восстановлению покрытия.

1. **Переформулировать тот же claim** короткой естественной фразой о предмете,
   не об имени артефакта.
2. **Лексический повтор — максимум один.** Три-четыре различающих корня;
   русские основы ставь отдельно со `*` после устойчивой части:
   `корнев* папочн* инструкц* ссылк*`, точные имена целиком.
3. **Разложить широкую тему на материальные фасеты** (копия правила тела — правь
   вместе). Лексику следующего фасета бери из snippets и `session-context`
   предыдущей выдачи; хотя бы один фасет формулируй языком текущей задачи. Два
   фасета подряд без новых holder-ов — эвристика остановки, оставляющая gap.
4. **Сменить канал.** Hybrid недоступен — `--lexical` сохраняет file-level BM25
   и lexical context-gate; в такой выдаче ключа `query_domain` нет вовсе.
   `--timeline` переключает выдачу на records выбранных holder-ов, но тот же
   `--limit` режет уже records — десять записей могут прийти из одного holder-а,
   поэтому сверяй `truncated` и поднимай limit.

```bash
uv run --locked --script "${CLAUDE_SKILL_DIR}/scripts/chat_digest.py" \
  _ops/chat-recall --query "<claim или корни>" --lexical --json
```

Локальная модель не подготовлена — запусти `--prepare` **отдельной командой**,
без пути к корпусу и без retrieval-флагов, иначе прогон падает:

```bash
uv run --locked --script "${CLAUDE_SKILL_DIR}/scripts/chat_digest.py" --prepare
```

## Возврат в Retrieval

Назови проверенные routes, уникальные holder files, спрошенные фасеты,
truncation status и unresolved gaps. Empty recovery — тоже результат: пустая
выдача говорит, что названные routes ничего не нашли, и не доказывает, что
позиции нет.

## Structural validation

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/chat_digest.py" \
  "$PWD/_ops/chat-recall" --check --strict
```

Validator проверяет структуру corpus и diagnostics, но не применимость позиции.
Ненулевой exit при живых diagnostics — нормальный ответ о состоянии корпуса, а
не поломка команды.
