# Независимая проверка `candidate-v6` — цикл 2

Проверенная версия: 4 файла, fingerprint
`2ab0d0ab6431372b67f46836096612411a56358a9657dd3560c81dea556c66e7`.

## Literal verdict

`fail`: единственная находка — Codex `default_prompt` повторял три workflow
predicate из runtime body. Остальные проверки и active sets:
`authoring 15 · scout 15 · verification 20 · install-only 11`.

## Trajectory verdict

`fail`: verification input/output повторяли поля, уже заданные trial, verdict и
install steps; карта недостаточно явно считала сохраняющийся root-intent.

## Решение

Оставить четыре файла. Свести `default_prompt` к invocation, а вход/выход
verification — к одному typed artifact каждый без повторения полей.
