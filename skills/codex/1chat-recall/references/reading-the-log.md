# Reading the recall log

Открывай этот reference, когда обычный retrieval дал пустой, слишком широкий
или конфликтующий route. `SKILL.md` владеет применением и результатом; здесь
только coverage и structural validation.

## Coverage

По умолчанию ищи в corpus текущего проекта; другой project-local corpus
разрешён только явным owner scope.

Читай полный record по адресу: snippet или rank не являются evidence. Проверь
исходную формулировку, одну альтернативную и один metadata-route. Затем сохрани
coverage gap и abstain; один пустой route не доказывает отсутствие.

## Structural validation

```bash
python3 "$ROOT/scripts/chat_digest.py" \
  "$PWD/_ops/chat-recall" --check --strict
```

Validator проверяет структуру corpus и diagnostics, но не выбирает и не
применяет evidence.
