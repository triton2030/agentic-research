# Reading the recall log

Открывай этот reference, когда обычный retrieval дал пустой, слишком широкий
или конфликтующий route. `SKILL.md` владеет применением и full-holder /
later-holder postcondition; здесь только coverage перед abstain.

## Coverage

По умолчанию ищи в corpus текущего проекта; другой project-local corpus
разрешён только явным owner scope.

Используй только search budget и варианты запроса, уже заданные Retrieval
`SKILL.md`. Собери уникальные holder-файлы из `records` и
`session_candidates`; record, snippet и rank ответом не являются. Один пустой
route не доказывает отсутствие.

Вернись в Retrieval `SKILL.md` и закрой его postcondition. Если предмет не
найден, сохрани названные проверенные routes как coverage gap и abstain.

## Structural validation

```bash
python3 "$ROOT/scripts/chat_digest.py" \
  "$PWD/_ops/chat-recall" --check --strict
```

Validator проверяет структуру corpus и diagnostics, но не выбирает и не
применяет evidence.
